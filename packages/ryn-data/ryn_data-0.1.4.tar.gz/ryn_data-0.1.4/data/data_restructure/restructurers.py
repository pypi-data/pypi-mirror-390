import abc
import logging
import math
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
import shutil
from pyspark.sql.functions import col, lit, concat_ws, element_at, split as F_split
import json

from fastapi import HTTPException



logger = logging.getLogger(__name__)


TEMPLATE_COLUMN_MAPPINGS = {
    "text_generation": {

            "doc_url": "https://huggingface.co/docs/trl/main/en/dataset_formats#prompt-completion",
            "required_columns": {
                "instruction": [
                    "prompt",
                    "instruction",
                    "query", 
                    "question"
                ],
                "response": [
                    "completion",
                    "response",
                    "output", 
                    "answer",
                    "answers",
                    "target",
                    "summary"
                ]
            },
            "optional_columns": {
                "input": [
                    "input", 
                    "context"
                ]
            }
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
            # "image": [ 
            #     "image", 
            #     "img"
            # ],
            "label": [
                "label", 
                "labels",
                "class", 
                "category", 
                "target"
            ],
            "file_path": [
                "image_path",
                "img_path",
                "file_path",
                "filepath",
            ]
        },
        "optional_columns": {
            
        }
    },
    "image_segmentation": {
        "required_columns": {
            "image": [ 
                "image", 
                "img",
                "pixel_values"
            ],
            "mask": [
                "mask", 
                "segmentation_mask",
                "label_mask",
                "annotation",
                "gtFine",
                "label"
            ]
        },
        "optional_columns": {
            "image_path": [
                "image_path",
                "img_path"
            ]
        }
    }
}

class BaseRestructurer(abc.ABC):
    """Abstract base class for dataset restructurers."""

    def __init__(self, spark_session: SparkSession = None):
        self.spark = spark_session or self._get_spark_session()
        self._created_session = (
            spark_session is None
        )  # Flag to know if we should stop it

    def stop(self):
        # Only stop the session if this class created it
        if self.spark and self._created_session:
            self.spark.stop()

    def _get_spark_session(self) -> SparkSession:
        """Initializes and returns a Spark session."""
        return (
            SparkSession.builder.appName("DatasetRestructuring")
            .master("local[*]")
            .config("spark.driver.memory", "4g")
            .config(
                "spark.sql.execution.arrow.pyspark.enabled", "true"
            )  # Recommended for performance
            .getOrCreate()
        )
    def check_schema(self,task :str,columns) -> None:
        """
        Validates that the DataFrame contains all required columns.
        Raises ValueError if any are missing.
        """

        if task not in TEMPLATE_COLUMN_MAPPINGS:
            raise ValueError(f"Unsupported task type: {task}")

        required_columns = TEMPLATE_COLUMN_MAPPINGS[task]["required_columns"]

        print(required_columns)

        missing_columns = []
        renameable_columns = []
        for logical_col, possible_names in required_columns.items():
            if not any(col in columns for col in possible_names):
                missing_columns.append((logical_col, possible_names))

        if missing_columns:
            error_messages = [
                f"Missing required column for role '{role}': expected one of {names}"
                for role, names in missing_columns
            ]
            full_error_message = (
                f"Dataset schema validation failed for tag '{task}'. "
                f"Details: " + "; ".join(error_messages)
            )
            logger.error(full_error_message)
            raise HTTPException(
                status_code=400,
                detail=full_error_message,
            )
        else:
            # return renamable columns
            for role, possible_names in required_columns.items():
                for name in possible_names:
                    if name in columns:
                        logger.info(f"Mapping column '{name}' to logical role '{role}'.")
                        renameable_columns.append((name, role))
                        break
            logger.info(f"Dataset schema validation passed for tag '{task}'.")
        
        return renameable_columns

    
    @abc.abstractmethod
    def restructure(self, input_path: Path, output_path: Path) -> None:
        """
        Reads data from input_path, transforms it, and writes to output_path.
        """
        pass
    @property
    @abc.abstractmethod
    def task_type(self) -> str:
        """
        Returns the task type this restructurer handles.
        """
        pass




class ImageClassificationRestructurer(BaseRestructurer):
    """
    Restructures a dataset for Image Classification tasks.
    ...
    """

    # NEW: A configurable parameter to control output file size by row count.
    # A larger number means larger, but fewer, files.
    TARGET_ROWS_PER_FILE = 5_000

    def restructure(self, input_path: Path, output_path: Path) -> None:
        """
        Executes the restructuring process.

        Args:
            input_path: The path to the source dataset directory, containing
                        'metadata.csv' and an 'images' folder.
            output_path: The path where the restructured dataset will be saved.
        """
        metadata_path = input_path / "metadata.csv"
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Required 'metadata.csv' not found in {input_path}"
            )

        logger.info(f"Reading metadata from: {metadata_path}")
        df = (
            self.spark.read.option("header", "true")
            .option("inferSchema", "true")
            .csv(str(metadata_path))
        )

        # 1. Ensure a 'split' column exists, defaulting to 'train'
        if "split" not in df.columns:
            df = df.withColumn("split", F.lit("train"))
        else:
            df = df.fillna({"split": "train"})

        
        renameable_columns = self.check_schema("image_classification",df.columns)

        if renameable_columns:
            for original_name, logical_name in renameable_columns:
                df = df.withColumnRenamed(original_name, logical_name)
        

        # 2. Generate the new file paths in the DataFrame
        # Example: 'images/image_01.jpg' -> 'image_01.jpg'
        df_with_new_paths = df.withColumn(
            "filename",
            element_at(F_split(col("file_path"), "/"), -1)
        )
        # Example: 'cat', 'image_01.jpg' -> 'images/cat/image_01.jpg'
        df_with_new_paths = df_with_new_paths.withColumn(
            "new_file_path",
            concat_ws("/", lit("images"), col("label"), col("filename"))
        )

        # 3. Collect file paths to the driver to perform copy operations.
        # This is a necessary step as file system operations are side effects
        # that cannot be performed by Spark executors directly on a DataFrame.
        paths_to_move = df_with_new_paths.select(
            "file_path", "new_file_path", "label"
        ).collect()

        logger.info(f"Restructuring and copying {len(paths_to_move)} image files...")
        copied_count = 0
        for row in paths_to_move:
            # Skip rows where the label is null or empty, as they can't form a directory
            if not row.label:
                logger.warning(
                    f"Skipping file '{row.file_path}' due to missing label."
                )
                continue

            source_path = input_path / row.file_path
            dest_path = output_path / row.new_file_path

            if not source_path.exists():
                logger.warning(f"Source file not found, skipping: {source_path}")
                continue

            # Create the destination directory (e.g., 'output/images/cat/')
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy(str(source_path), str(dest_path))
            copied_count += 1
        
        logger.info(f"Successfully copied {copied_count} files.")

        # 4. Prepare the final DataFrame for saving
        # We only keep the new path, label, and split. Null labels were already handled.
        final_df = (
            df_with_new_paths.filter(col("label").isNotNull())
            .select(
                col("new_file_path").alias("file_path"),
                "label",
                "split"
            )
        )

        # 5. Save the new metadata as a partitioned Parquet file
        total_rows = final_df.count()
        if total_rows == 0:
            logger.warning("No data to write for the final metadata. Skipping.")
            return
            
        num_partitions = max(1, round(total_rows / self.TARGET_ROWS_PER_FILE))
        
        output_metadata_path = output_path 
        logger.info(f"Writing final metadata to {output_metadata_path}")
        
        (
            final_df.write.mode("append")
            .parquet(str(output_metadata_path))
        )

        #check and delete _SUCCESS file
        success_file = output_metadata_path / "_SUCCESS"
        if success_file.exists():
            success_crc = output_metadata_path / "._SUCCESS.crc"
            if success_crc.exists():
                success_crc.unlink()
                logger.info("Deleted _SUCCESS.crc file from output metadata directory.")
            success_file.unlink()
            logger.info("Deleted _SUCCESS file from output metadata directory.")
        
        parquets = sorted(list(output_metadata_path.glob("part-*.parquet")))
        for idx, part_file in enumerate(parquets):
            new_name = (
                output_metadata_path / f"metadata.parquet"
            )
            part_file.rename(new_name)
            logger.info(f"Renamed '{part_file.name}' to '{new_name.name}'")
        
        crc_files = sorted(list(output_metadata_path.glob(".*.parquet.crc")))
        for crc_file in crc_files:
            original_part_name = crc_file.name[
                1:-4
            ]  # remove leading '.' and trailing '.crc'
            try:
                # Find the index of the original part file to maintain numbering
                original_part_file = Path(output_metadata_path, original_part_name)
                idx = parquets.index(original_part_file)
                new_crc_name = (
                    output_metadata_path
                    / f".metadata.parquet.crc"
                )
                crc_file.rename(new_crc_name)
            except (ValueError, IndexError):
                logger.warning(
                    f"Could not find matching part file for {crc_file.name}, deleting it."
                )
                crc_file.unlink()

        
        
        logger.info("Restructuring complete.")

    def task_type(self) -> str:
        return "image_classification"
class ImageSegmentationRestructurer(BaseRestructurer):
    """
    Restructures a dataset for Image Segmentation tasks.

    This class reads a directory containing an 'images' folder, a 'masks'
    folder, and a 'metadata.csv' file. It joins the image and mask binary
    data with the metadata, and then writes the result into a partitioned
    Parquet dataset suitable for use with libraries like Hugging Face Datasets.

    The final structure will have columns for 'image' and 'mask', where each
    is a struct containing the file path and binary content.
    """

    TARGET_ROWS_PER_FILE = 2_000

    def restructure(self, input_path: Path, output_path: Path) -> None:
        """
        Reads image/mask data, joins with metadata, and writes to a structured
        Parquet format partitioned by data split (e.g., train/validation/test).
        """
        dataset_info = {}
        dataset_info_path = output_path / "dataset_info.json"
        metadata_path = input_path / "metadata.csv"
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Required 'metadata.csv' not found in {input_path}"
            )

        logger.info(f"Reading metadata from: {metadata_path}")
        df = (
            self.spark.read.option("header", "true")
            .option("inferSchema", "true")
            .csv(str(metadata_path))
        )

        # Ensure a 'split' column exists, defaulting to 'train'
        if "split" not in df.columns:
            df = df.withColumn("split", F.lit("train"))
        else:
            df = df.fillna({"split": "train"})

        # --- Read Image and Mask Binary Data ---
        logger.info("Reading raw image files...")
        image_binary_df = (
            self.spark.read.format("binaryFile")
            .load(str(input_path / "images" / "*"))
            .filter(F.col("length") > 0)
            .withColumn(
                "image_path", F.regexp_extract(F.col("path"), r"(images/.*$)", 1)
            )
            .withColumnRenamed("content", "image_content")
            .select("image_path", "image_content")
        )

        logger.info("Reading raw mask files...")
        mask_binary_df = (
            self.spark.read.format("binaryFile")
            .load(str(input_path / "masks" / "*"))
            .filter(F.col("length") > 0)
            .withColumn("mask_path", F.regexp_extract(F.col("path"), r"(masks/.*$)", 1))
            .withColumnRenamed("content", "mask_content")
            .select("mask_path", "mask_content")
        )

        # --- Join Metadata with Binary Data ---
        logger.info("Joining metadata with image and mask data...")
        # Inner join for images: an image must exist.
        joined_df = df.join(image_binary_df, "image_path", "inner")
        # Left join for masks: a mask might be null (e.g., for test set).
        joined_df = joined_df.join(mask_binary_df, "mask_path", "left")

        if joined_df.rdd.isEmpty():
            raise ValueError(
                "Join between metadata, images, and masks resulted in an empty dataset. "
                "Check that file paths in metadata.csv match actual files."
            )

        logger.info("Creating nested 'image' and 'mask' structs.")
        final_df = joined_df.select(
            F.col("split"),
            F.struct(
                F.col("image_path").alias("path"), F.col("image_content").alias("bytes")
            ).alias("image"),
            F.struct(
                F.col("mask_path").alias("path"), F.col("mask_content").alias("bytes")
            ).alias("mask"),
        ).cache()  # Cache for efficient access across multiple splits

        dataset_info["schema"] = final_df.schema.jsonValue()

        splits = [row.split for row in final_df.select("split").distinct().collect()]
        logger.info(f"Found splits to process: {splits}")

        output_path.mkdir(parents=True, exist_ok=True)

        split_stats = {}

        for split_name in splits:
            logger.info(f"Processing split: '{split_name}'")
            split_df = final_df.filter(F.col("split") == split_name)

            split_stats[split_name] = {
                "row_count": split_df.count(),
                }

            row_count = split_df.count()

            if row_count == 0:
                logger.warning(f"Split '{split_name}' is empty. Skipping.")
                continue

            num_partitions = max(1, math.ceil(row_count / self.TARGET_ROWS_PER_FILE))

            logger.info(
                f"Split '{split_name}' has {row_count} rows. Repartitioning into {num_partitions} files."
            )
            final_split_df = split_df.repartition(num_partitions).drop("split")

            target_path = output_path / split_name
            final_split_df.write.mode("overwrite").parquet(str(target_path))

            # --- Rename output files for cleaner formatting ---
            part_files = sorted(list(target_path.glob("part-*.parquet")))
            for idx, part_file in enumerate(part_files):
                new_name = (
                    target_path / f"part-{idx:05d}-of-{len(part_files) - 1:05d}.parquet"
                )
                part_file.rename(new_name)
                logger.info(f"Renamed '{part_file.name}' to '{new_name.name}'")

            # This part is optional but cleans up the checksum files too
            crc_files = sorted(list(target_path.glob(".*.parquet.crc")))
            for crc_file in crc_files:
                original_part_name = crc_file.name[
                    1:-4
                ]  # remove leading '.' and trailing '.crc'
                try:
                    # Find the index of the original part file to maintain numbering
                    original_part_file = Path(target_path, original_part_name)
                    idx = part_files.index(original_part_file)
                    new_crc_name = (
                        target_path
                        / f".part-{idx:05d}-of-{len(part_files) - 1:05d}.parquet.crc"
                    )
                    crc_file.rename(new_crc_name)
                except (ValueError, IndexError):
                    logger.warning(
                        f"Could not find matching part file for {crc_file.name}, deleting it."
                    )
                    crc_file.unlink()

        final_df.unpersist()
        for split_name in splits:
            target_path = output_path / split_name
            split_size_bytes = sum(f.stat().st_size for f in target_path.glob('*.parquet'))
            split_stats[split_name]["num_bytes"] = split_size_bytes
            
        dataset_info["splits"] = split_stats
        with open(dataset_info_path, "w") as f:
            json.dump(dataset_info, f, indent=4)
            logger.info(f"Wrote dataset_info.json to {dataset_info_path}")
        
        logger.info("Dataset restructuring complete.")
    def task_type(self) -> str:
        return "image_segmentation"


class TextGenerationRestructurer(BaseRestructurer):
    """
    Restructures datasets for Text Generation (Instruction Fine-Tuning) tasks.

    This class reads a directory containing one or more CSV and/or Parquet files.
    It validates the presence of required columns ('instruction', 'output'),
    handles optional columns ('input', 'split'), and writes the processed data
    into a partitioned Parquet dataset suitable for training.
    """

    # Text data is often less bulky per row than image data,
    # so we can aim for larger files.
    TARGET_ROWS_PER_FILE = 50_000

    def _read_input_files(self, input_path: Path) -> DataFrame:
        """
        Scans the input path for .csv and .parquet files and reads them
        into a single Spark DataFrame.
        """
        csv_files = [str(p) for p in input_path.glob("*.csv")]
        parquet_files = [str(p) for p in input_path.glob("*.parquet")]

        if not csv_files and not parquet_files:
            raise FileNotFoundError(
                f"No .csv or .parquet files found in the input directory: {input_path}"
            )

        df = None

        if csv_files:
            logger.info(f"Found {len(csv_files)} CSV file(s) to read.")
            csv_df = (
                self.spark.read.option("header", "true")
                .option("inferSchema", "true")
                .csv(csv_files)
            )
            df = csv_df

        if parquet_files:
            logger.info(f"Found {len(parquet_files)} Parquet file(s) to read.")
            parquet_df = self.spark.read.parquet(*parquet_files)
            if df:
                # Use unionByName to safely merge schemas
                df = df.unionByName(parquet_df, allowMissingColumns=True)
            else:
                df = parquet_df

        return df

    def restructure(self, input_path: Path, output_path: Path) -> None:
        """
        Reads tabular data, validates the schema, and writes to a structured
        Parquet format partitioned by data split (e.g., train/validation/test).
        """

        dataset_info = {}
        dataset_info_path = output_path / "dataset_info.json"

        logger.info(f"Reading all .csv and .parquet files from: {input_path}")
        df = self._read_input_files(input_path)


        renamable_columns = self.check_schema("text_generation",df.columns)

        for original_name, logical_name in renamable_columns:
            df = df.withColumnRenamed(original_name, logical_name)



        # Filter out rows where essential data is missing
        df = df.filter(F.col("instruction").isNotNull() & F.col("response").isNotNull())

        # Ensure optional columns exist for schema consistency
        if "input" not in df.columns:
            df = df.withColumn("input", F.lit(None).cast("string"))

        if "split" not in df.columns:
            df = df.withColumn("split", F.lit("train"))
        else:
            # Fill any null values in the existing split column
            df = df.fillna({"split": "train"})

        if df.rdd.isEmpty():
            raise ValueError(
                "The dataset is empty after loading and validation. Please check the input files."
            )

        # Select and order the columns for the final output
        final_df = df.cache()

        #apply chatML formatting to new messages column
        final_df = df.withColumn(
            "messages",
            F.array(
                # --- Item 1: The User's Message Struct ---
                # This struct is built completely and passed as the first argument to F.array
                F.struct(
                    F.lit("user").alias("role"),
                    F.col("instruction").alias("content")
                ),
                
                # --- Item 2: The Assistant's Message Struct ---
                # This struct is built completely and passed as the second argument to F.array
                F.struct(
                    F.lit("assistant").alias("role"),
                    F.col("response").alias("content")
                )
            )
        )

        final_df = final_df.drop("instruction", "response")

        dataset_info["schema"] = final_df.schema.jsonValue()

        splits = [row.split for row in final_df.select("split").distinct().collect()]
        logger.info(f"Found splits to process: {splits}")

        output_path.mkdir(parents=True, exist_ok=True)

        split_stats = {}

        for split_name in splits:
            logger.info(f"Processing split: '{split_name}'")
            split_df = final_df.filter(F.col("split") == split_name)

            row_count = split_df.count()
            split_stats[split_name] = {
                "row_count": row_count,
                }

            if row_count == 0:
                logger.warning(f"Split '{split_name}' is empty. Skipping.")
                continue

            num_partitions = max(1, math.ceil(row_count / self.TARGET_ROWS_PER_FILE))

            logger.info(
                f"Split '{split_name}' has {row_count} rows. Repartitioning into {num_partitions} files."
            )
            # Drop the split column as it's now represented by the directory structure
            final_split_df = split_df.repartition(num_partitions).drop("split")

            target_path = output_path / split_name
            final_split_df.write.mode("overwrite").parquet(str(target_path))

            # Optional: Rename part-files for a cleaner look
            part_files = sorted(list(target_path.glob("part-*.parquet")))
            for idx, part_file in enumerate(part_files):
                new_name = (
                    target_path / f"part-{idx:05d}-of-{len(part_files) - 1:05d}.parquet"
                )
                part_file.rename(new_name)
                logger.info(f"Renamed '{part_file.name}' to '{new_name.name}'")

            # This part is optional but cleans up the checksum files too
            crc_files = sorted(list(target_path.glob(".*.parquet.crc")))
            for crc_file in crc_files:
                original_part_name = crc_file.name[1:-4]
                try:
                    original_part_file = Path(target_path, original_part_name)
                    idx = part_files.index(original_part_file)
                    new_crc_name = (
                        target_path
                        / f".part-{idx:05d}-of-{len(part_files) - 1:05d}.parquet.crc"
                    )
                    crc_file.rename(new_crc_name)
                except (ValueError, IndexError):
                    logger.warning(
                        f"Could not find matching part file for {crc_file.name}, deleting it."
                    )
                    crc_file.unlink()

        final_df.unpersist()
        for split_name in splits:
            target_path = output_path / split_name
            split_size_bytes = sum(f.stat().st_size for f in target_path.glob('*.parquet'))
            split_stats[split_name]["num_bytes"] = split_size_bytes
            
        dataset_info["splits"] = split_stats
        with open(dataset_info_path, "w") as f:
            json.dump(dataset_info, f, indent=4)
            logger.info(f"Wrote dataset_info.json to {dataset_info_path}")

        logger.info("Dataset restructuring complete.")
    def task_type(self) -> str:
        return "text_generation"
