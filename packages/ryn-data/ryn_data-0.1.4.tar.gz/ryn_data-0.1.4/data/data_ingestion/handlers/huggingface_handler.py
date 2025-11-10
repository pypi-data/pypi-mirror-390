import gc
import logging
import math
import os
import uuid
from datetime import datetime

import pandas as pd
from datasets import ClassLabel, load_dataset
from fastapi import HTTPException
from huggingface_hub import HfApi

from data.data_ingestion.handlers.conditions import DatasetConditionChecker
from data.data_ingestion.models.metadata import DatasetMetadata
from data.data_ingestion.storage_handler import DatasetStorageHandler

logger = logging.getLogger(__name__)


TEMPLATE_COLUMN_MAPPINGS = {
    "text_generation": {
        "doc_url": "https://huggingface.co/docs/trl/main/en/dataset_formats#prompt-completion",
        "required_columns": {
            "instruction": ["prompt","instruction", "query", "question"],
            "response": [
                "completion",
                "response",
                "output",
                "answer",
                "answers",
                "target",
                "summary",
            ],
        },
        "optional_columns": {"input": ["input", "context"]},
    },
    # "preference_tuning": {
    #     "doc_url": "https://huggingface.co/docs/trl/main/en/dataset_formats#preference",
    #     "required_columns": {
    #         "prompt": [
    #             "prompt",
    #             "instruction",
    #             "query",
    #             "question"
    #         ],
    #         "chosen": [
    #             "chosen"
    #         ],
    #         "rejected": [
    #             "rejected"
    #         ]
    #     },
    #     "optional_columns": {},
    #     "special_handlers": {}
    # },
    # "pre_training": {
    #     "doc_url": "https://huggingface.co/docs/trl/main/en/dataset_formats#language-modeling",
    #     "required_columns": {
    #         "text": [
    #             "text",
    #             "input",
    #             "source_text"
    #         ]
    #     },
    #     "optional_columns": {},
    #     "special_handlers": {}
    # },
    # },
    "image_classification": {
        "required_columns": {
            "image": ["image", "img"],
            "label": ["label", "labels", "class", "category", "target"],
        },
        "optional_columns": {"image_path": ["image_path", "img_path"]},
    },
    "image_segmentation": {
        "required_columns": {
            "image": ["image", "img", "pixel_values"],
            "mask": [
                "mask",
                "segmentation_mask",
                "label_mask",
                "annotation",
                "gtFine",
                "label",
            ],
        },
        "optional_columns": {"image_path": ["image_path", "img_path"]},
    },
}


class HuggingFaceHandler:
    def _check_schema(self, features, dataset_tag):
        if dataset_tag is None:
            logger.info("No dataset_tag provided; skipping schema check.")
            return

        if dataset_tag not in TEMPLATE_COLUMN_MAPPINGS:
            logger.warning(
                f"Unknown dataset_tag '{dataset_tag}'; skipping schema check."
            )
            return

        template = TEMPLATE_COLUMN_MAPPINGS[dataset_tag]
        required_columns = template.get("required_columns", {})

        renambale_columns = []

        missing_columns = []
        for role, possible_names in required_columns.items():
            if not any(name in features for name in possible_names):
                missing_columns.append((role, possible_names))

        if missing_columns:
            error_messages = [
                f"Missing required column for role '{role}': expected one of {names}"
                for role, names in missing_columns
            ]
            full_error_message = (
                f"Dataset schema validation failed for tag '{dataset_tag}'. "
                f"Details: " + "; ".join(error_messages)
            )
            logger.warning(full_error_message)
            return None
        else:
            # return renamable columns
            for role, possible_names in required_columns.items():
                if role not in features:
                    for name in possible_names:
                        if name in features:
                            renambale_columns.append((name, role))
                            break
            logger.info(f"Dataset schema validation passed for tag '{dataset_tag}'.")

        return renambale_columns

    def _rename_columns(self, dataset, renamables):
        for original_name, new_name in renamables:
            if original_name != new_name:
                dataset = dataset.rename_column(original_name, new_name)
                logger.info(f"Renamed column '{original_name}' to '{new_name}'")
        return dataset

    def save_images(self, dataset, local_dataset_dir):
        images_output_dir = local_dataset_dir / "images"
        images_output_dir.mkdir(exist_ok=True)

        # Get the label feature to map integer labels to string names
        # We assume the 'train' split is representative of the feature set
        label_feature = dataset["train"].features.get("label")
        has_class_labels = isinstance(label_feature, ClassLabel)

        if has_class_labels:
            logger.info(f"Found class labels: {label_feature.names}")
        else:
            logger.warning(
                "Label column is not of type ClassLabel. "
                "Will treat labels as raw strings."
            )

        def save_image_batch(batch):
            """
            Processes a batch of examples to save images and generate metadata.
            """
            new_file_paths = []
            new_labels = []

            # Get images and labels for the whole batch
            images = batch["image"]
            labels = batch["label"]

            for i in range(len(images)):
                image = images[i]
                label = labels[i]

                if image is None or label is None:
                    # Append placeholders to keep batch size consistent
                    new_file_paths.append(None)
                    new_labels.append(None)
                    continue

                # Determine label name
                if has_class_labels:
                    label_name = label_feature.int2str(label)
                else:
                    label_name = str(label)

                # This check is still needed for non-ClassLabel datasets
                label_dir = images_output_dir / label_name
                label_dir.mkdir(exist_ok=True)

                # Generate path and save image
                filename = f"{uuid.uuid4().hex}.jpg"
                destination_path = label_dir / filename
                relative_path = destination_path.relative_to(local_dataset_dir)

                try:
                    image.convert("RGB").save(destination_path)
                    new_file_paths.append(str(relative_path))
                    new_labels.append(label_name)
                except Exception as e:
                    logger.error(f"Failed to save an image: {e}")
                    new_file_paths.append(None)
                    new_labels.append(None)

            # Return a dictionary with the new columns
            return {"file_path": new_file_paths, "label_name": new_labels}

        num_cores = 4
        logger.info(f"Processing dataset in parallel using {num_cores} cores.")

        # Apply the map function to generate new columns
        updated_ds = dataset.map(
            save_image_batch,
            batched=True,
            batch_size=5000,  # Process 100 images per batch per core
            num_proc=num_cores,
            remove_columns=[
                "image"
            ],  # We don't need the image data in the final metadata
        )

        return updated_ds

    def _process_text_generation(self, dataset, local_dataset_dir):
        expected_rows = 10000

        def convert_to_chatml(example):
            return {
                "messages": [
                    {"role": "user", "content": example["instruction"]},
                    {"role": "assistant", "content": example["response"]},
                ]
            }

        for split_name, split_dataset in dataset.items():
            split_output_dir = local_dataset_dir / split_name
            split_output_dir.mkdir(exist_ok=True)

            split_dataset = split_dataset.map(
                convert_to_chatml,
                remove_columns=["instruction", "response"],
                batch_size=10000,
            )

            num_shards = math.ceil(max(1, split_dataset.num_rows / expected_rows))

            for shard_idx in range(num_shards):
                shard_dataset = split_dataset.shard(num_shards, shard_idx)
                file_path = str(
                    split_output_dir / f"{shard_idx:04d}-of-{num_shards:04d}.parquet"
                )
                shard_dataset.to_parquet(file_path, batch_size=1000)

    def process(
        self,
        dataset_name: str,
        dataset_config: str,
        user_name: str,
        private: bool,
        base_extra: dict,
        s3_config: dict = None,
        clearml_config: dict = None,
        revision: str = "main",
        dataset_tag: str = None,
    ) -> dict:
        """
        Download a Hugging Face dataset, validate files, persist only the valid files
        to PVC/S3, and report any validation failures.
        """
        is_valid = True

        storage_handler = None
        try:
            mount_dataset_name = dataset_name.replace("/", "-")
            storage_handler = DatasetStorageHandler(mount_dataset_name)

            # Step 1: Size Check
            try:
                DatasetConditionChecker().check_huggingface_size(
                    dataset_name, revision=revision
                )
            except ValueError as size_error:
                logger.error(
                    f"Dataset size check failed for '{dataset_name}': {size_error}"
                )
                raise HTTPException(
                    status_code=400, detail=f"Dataset size check failed: {size_error}"
                )

            # Step 2: Download
            api = HfApi()
            info = api.repo_info(dataset_name, repo_type="dataset", revision=revision)

            temp_dir = storage_handler.temp_dir
            logger.info(f"Using PVC-backed temp directory: {temp_dir}")

            local_dataset_dir = temp_dir
            local_dataset_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"Saving dataset splits to '{local_dataset_dir}' in Parquet format..."
            )

            logger.info(
                f"Downloading raw files for dataset '{dataset_name}' at revision '{revision}'..."
            )

            # snapshot_download(
            #     repo_id=dataset_name,
            #     repo_type="dataset",
            #     revision=revision,
            #     cache_dir=str(temp_dir / "cache"),
            #     local_dir=str(local_dataset_dir),
            #     local_dir_use_symlinks=False,
            # )

            ds_stream = load_dataset(dataset_name, dataset_config, streaming=True)

            if ds_stream["train"].features is not None:
                try:
                    ds = load_dataset(
                        dataset_name, dataset_config, cache_dir=str(temp_dir / "cache")
                    )
                except Exception as e:
                    logger.error(
                        f"Error loading dataset '{dataset_name}': {e}", exc_info=True
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error loading dataset '{dataset_name}': {e}",
                    )
                renamables = self._check_schema(ds["train"].features, dataset_tag)

                if renamables:
                    ds = self._rename_columns(ds, renamables)
                    if dataset_tag == "text_generation":
                        self._process_text_generation(ds, local_dataset_dir)
                    elif dataset_tag == "image_classification":
                        logger.info("Processing dataset for Image Classification task.")
                        # This list will collect metadata for all splits before final saving.
                        all_metadata = []

                        updated_ds = self.save_images(ds, local_dataset_dir)

                        # --- Step 4: Combine and save the final metadata ---
                        all_splits_metadata = []
                        for split_name, split_dataset in updated_ds.items():
                            # Convert to pandas to easily add the 'split' column
                            split_df = split_dataset.to_pandas()
                            split_df["split"] = split_name
                            all_splits_metadata.append(split_df)

                        # Concatenate all dataframes from all splits
                        final_metadata_df = pd.concat(
                            all_splits_metadata, ignore_index=True
                        )

                        if final_metadata_df.empty:
                            logger.warning(
                                "No valid images were processed. Metadata file will not be created."
                            )
                        else:
                            logger.info(
                                f"Saving metadata for {len(final_metadata_df)} images to Parquet file."
                            )
                            final_metadata_df.to_parquet(
                                local_dataset_dir / "metadata.parquet", index=False
                            )
                        logger.info(
                            "Image classification dataset restructuring complete."
                        )
                    # raise HTTPException(
                    #     status_code=400,
                    #     detail=f"The dataset '{dataset_name}' with config '{dataset_config}' does not contain any is not inferable data.",
                    # )
                else:
                    logger.info(
                        f"Skipping schema enforcement for dataset '{dataset_name}'."
                    )
            else:
                logger.info(
                    f"Dataset '{dataset_name}' does not have inferable features; skipping schema check."
                )

            api = HfApi()
            info = api.repo_info(dataset_name, repo_type="dataset")

            ds_id = storage_handler.generate_dataset_id()
            metadata = DatasetMetadata(
                dataset_id=ds_id,
                dataset_name=dataset_name.replace("/", "-"),
                dataset_config=dataset_config,
                last_commit=getattr(info, "sha", None),
                last_modified=getattr(info, "last_modified", None).isoformat()
                if getattr(info, "last_modified", None)
                else None,
                user_name=user_name,
                private=private,
                revision=revision,
                source="huggingface",
                created_at=datetime.now().isoformat(),
                s3_path="",
                summary=f"Raw file download of the Hugging Face dataset '{dataset_name}' at revision '{revision}'.",
                dataset_tag=dataset_tag,
            )

            # Store valid files
            stored_path = storage_handler.store_dataset(
                local_dataset_dir,
                metadata,
                s3_config=s3_config,
                clearml_config=clearml_config,
            )

            #  Construct final response
            response = {
                "status": "ok",
                "message": "Hugging Face dataset stored successfully.",
                "dataset_id": ds_id,
                "stored_path": stored_path,
            }
            # if error_details:
            #     response["validation_errors"] = error_details

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error processing Hugging Face dataset '{dataset_name}': {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Error with Hugging Face dataset: {e}"
            )
        finally:
            gc.collect()
            if storage_handler:
                storage_handler.cleanup_temp()


def process_huggingface_dataset(
    dataset_name, dataset_config, user_name, private, dataset_tag, s3_config=None
):
    return HuggingFaceHandler().process(
        dataset_name=dataset_name,
        dataset_config=dataset_config,
        user_name=user_name,
        private=private,
        dataset_tag=dataset_tag,
        s3_config=s3_config,
    )
