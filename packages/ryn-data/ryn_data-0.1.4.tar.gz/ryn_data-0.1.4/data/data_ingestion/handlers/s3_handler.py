import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Union

import boto3
from fastapi import HTTPException

from data.data_ingestion.handlers.conditions import DatasetConditionChecker
from data.data_ingestion.handlers.utils import summarize_dataset
from data.data_ingestion.models.metadata import DatasetMetadata
from data.data_ingestion.storage_handler import DatasetStorageHandler
from data.data_restructure.restructure import Restructurer
from data.data_validation.config import validation_config
from data.data_validation.structures import ValidationReport, ValidationResult
from data.data_validation.validation import DirectoryValidator

# from data.data_ingestion.setup_logging import setup_logging

from datetime import datetime, timezone

# setup_logging(
#     service_name="s3-handler-service",
#     es_hosts=["https://144.172.105.98:30092"],
#     auth=("elastic", "1qaz!QAZ"),
#     verify_certs=False,
# )


logger = logging.getLogger(__name__)


class S3Handler:
    def __init__(
        self, *, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        logger.info(
            f"S3Handler initialized for endpoint '{endpoint_url}' and bucket '{bucket_name}'."
        )

    def download_file(self, remote_path: str, local_path: Path, s3_client) -> None:
        if not s3_client:
            raise HTTPException(status_code=503, detail="S3 service is not available.")
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                s3_client.head_object(Bucket=self.bucket_name, Key=remote_path)
            except s3_client.exceptions.NoSuchKey:
                raise ValueError(
                    f"The file or folder '{remote_path}' does not exist in the S3 bucket '{self.bucket_name}'."
                )

            s3_client.download_file(self.bucket_name, remote_path, str(local_path))
            logger.info(
                f"S3 Download: '{remote_path}' -> '{local_path}' (bucket='{self.bucket_name}')"
            )
        except Exception as e:
            logger.error(
                f"S3 download failed for '{remote_path}' in bucket '{self.bucket_name}': {e}"
            )
            raise HTTPException(status_code=500, detail=f"S3 download error: {e}")

    def _validate_and_cleanup_dataset(
        self, local_file: Path, s3_file_path: str,base_extra: dict ,is_soft: bool=True
    ) -> tuple[str, str, list]:
        """
        Validates a local dataset, removes invalid files, and returns validation status.

        Args:
            local_file: The path to the downloaded local file or directory.
            s3_file_path: The original S3 path, used for logging.

        Returns:
            A tuple containing the final status, a descriptive message, and a list of error details.

        Raises:
            HTTPException: If all files in the dataset fail validation.
        """

        start_validation_extra = base_extra.copy()
        start_validation_extra.update({
            "event":{
                "category":"validation",
                "type":"start_validation",
                "status":"success"
            }
        }
        )
        logger.info(f"Starting validation for dataset at: {local_file}",extra=start_validation_extra)

        # Ensure the validator is configured to unzip archives, which is the default
        validator = DirectoryValidator(config=validation_config, unzip_first=True)
        report = validator.validate(Path(local_file))

        # check if local_file is a file and convert to ValidationReport
        if isinstance(report, ValidationResult):
            report = ValidationReport(directory_path=local_file, results=[report])
        
        

        error_details = []
        warning_details = []
        final_status = "success"
        final_message = "Dataset from S3 stored successfully."

        if report.has_failures():
            final_status = "completed_with_errors"
            final_message = (
                "Dataset stored, but some files failed validation and were excluded."
            )
            invalid_file_paths = set()
            warning_file_paths = set()

            for result in report.results:
                if not result.is_valid:
                    error_details.append(
                        {
                            "file": result.file_path,
                            "errors": result.errors,
                            "warnings": result.warnings,
                        }
                    )
                    invalid_file_paths.add(result.file_path)
                elif result.warnings:
                    warning_details.append({
                        "warnings": result.warnings,
                        "file": result.file_path
                    })
                    warning_file_paths.add(result.file_path)
                    

            # Remove the invalid files from the temporary directory
            logger.info(f"warning paths: {warning_file_paths}")
            logger.info(f"Removing {len(invalid_file_paths)} invalid file(s)...")
            logger.info(f"errors: {error_details}")
            for file_path in invalid_file_paths:
                try:
                    os.remove(file_path)
                    logger.debug(f"Removed invalid file: {file_path}")
                except OSError as e:
                    logger.error(f"Error removing invalid file {file_path}: {e}")
            
            if not is_soft:
                for file_path in warning_file_paths:
                    try:
                        os.remove(file_path)
                        logger.debug(f"Removed invalid file: {file_path} (hard validating)")
                    except OSError as e:
                        logger.error(f"Error removing invalid file {file_path}: {e}")



        # Check if all files were invalid and subsequently removed
        files = (
            [
                f
                for f in local_file.rglob("*")
                if f.is_file()
                and f.suffix in (".csv", ".parquet", ".jpg", ".png", ".json")
            ]
            if local_file.is_dir()
            else ([local_file] if local_file.exists() else [])
        )
        if not files:
            final_status = "failed"
            final_message = (
                "All files in the dataset failed validation. No files were stored."
            )
            logger.error(
                f"All files in dataset from S3 path '{s3_file_path}' failed validation. Nothing to store."
            )

        return final_status, final_message, error_details,warning_details

    def validate_dataset_structure(local_folder: Union[str, Path]):
        """
        Validates that a directory has the required dataset structure.

        The structure must be:
        - A required 'train' subdirectory containing at least one .parquet file.
        - Optional 'test' and 'validation' subdirectories.
        - If 'test' or 'validation' directories exist, they must also contain
        at least one .parquet file.

        Args:
            local_folder: The path to the root directory to validate.

        Raises:
            FileNotFoundError: If the root folder or the required 'train' split
                            directory does not exist.
            ValueError: If a split directory exists but is empty of .parquet files.

        Returns:
            True if the validation is successful.
        """
        root_path = Path(local_folder)

        # 1. Check if the root directory itself exists
        if not root_path.is_dir():
            raise FileNotFoundError(f"Root directory not found: '{root_path}'")

        # 2. Check the required 'train' split
        train_path = root_path / "train"
        if not train_path.is_dir():
            raise FileNotFoundError(
                f"Required 'train' split directory not found in '{root_path}'"
            )

        # Check if the 'train' directory has at least one .parquet file
        # next(iterator, default) is an efficient way to check if an iterator is empty
        if not next(train_path.glob("*.parquet"), None):
            raise ValueError(
                "The 'train' split directory exists but contains no .parquet files."
            )

        # 3. Check the optional splits ('test', 'validation')
        for split_name in ["test", "validation"]:
            split_path = root_path / split_name

            # This check only applies IF the optional directory exists
            if split_path.is_dir():
                if not next(split_path.glob("*.parquet"), None):
                    raise ValueError(
                        f"The optional '{split_name}' split directory exists "
                        "but contains no .parquet files."
                    )

        print(f"✅ Validation successful for directory: '{root_path}'")
        return True

    def process_s3_dataset(
        self,
        s3_file_path: str,
        dataset_name: str,
        user_name: str,
        private: bool,
        dataset_tag: str,
        base_extra:dict,
        s3_config_target: dict = None,
        clearml_config: dict = None,
    ) -> dict:
        """
        Download an S3 dataset, persist it to S3-mounted temp directory, and return metadata.
        """

        start_time = datetime.now(timezone.utc)
        
        try:
            mount_dataset_name = dataset_name or Path(s3_file_path).stem
            storage_handler = DatasetStorageHandler(mount_dataset_name)
            print(f"storage_handler:{storage_handler}")
            DatasetConditionChecker().check_s3_size(
                access_key=self.access_key,
                secret_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                bucket_name=self.bucket_name,
                s3_path=s3_file_path,
            )
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
            )

            temp_dir = storage_handler.temp_dir
            logger.info(f"Using S3-mounted temp directory: {temp_dir}")
            s3_filename = Path(s3_file_path).name
            local_file = temp_dir / s3_filename  # Combine directory with filename

            logger.info(f"temp_dir: {temp_dir}")

            print(s3_file_path)

            from aipmodel.model_registry import CephS3Manager

            manager = CephS3Manager(
                endpoint_url=self.endpoint_url,
                access_key=self.access_key,
                secret_key=self.secret_key,
                bucket_name=self.bucket_name,
            )
            print("0" * 10)
            try:
                manager.download(s3_file_path, local_file)
            except Exception as e:
                failed_download_extra = base_extra.copy()
                failed_download_extra.update({
                "event":{
                    "category":"s3_handler",
                    "type":"s3_download",
                    "status":"failed"
                }})
                logger.error(f"error in downloading dataset from source s3 : {e}",extra=failed_download_extra)
                raise


            successful_download_extra = base_extra.copy()

            successful_download_extra.update({
                "event":{
                    "category":"s3_handler",
                    "type":"s3_download",
                    "status":"success"
                }
            }  
            )
            logger.info("downloaded source s3 dataset successfully",extra=successful_download_extra)


            # self.download_file(s3_file_path, local_file, s3_client)

            dataset_id = storage_handler.generate_dataset_id()
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                dataset_name=dataset_name or local_file.stem,
                revision="main",
                last_commit=None,
                last_modified=None,
                user_name=user_name,
                private=private,
                source="s3",
                created_at=datetime.now().isoformat(),
                s3_path="",
                summary=summarize_dataset(local_file),
                dataset_tag=dataset_tag or "ML",
            )

            
            base_extra["dataset"]["id"] = dataset_id

            metadata_extra = base_extra.copy()
            metadata_extra.update({
                "event":{
                    "category":"s3_handler",
                    "type":"metadata",
                    "status":"success"
                }
            }
            )
            logger.info("metadata object created",extra=metadata_extra)

            is_soft = False

            final_status, final_message, error_details,warning_details = (
                self._validate_and_cleanup_dataset(local_file, s3_file_path,base_extra,is_soft=is_soft)
            )
            validation_results = {
                "validation":{
                    "errors":[],
                    "warnings":[],
                    "status":final_status
                }
            }
            for err in error_details:
                for er in err["errors"]:
                    validation_results["validation"]["errors"].append({
                        "file":str(err["file"]).split("/")[-1],
                        "details":er["error"],
                        "removed":True
                    })

            for war in warning_details:
                for wa in war["warnings"]:
                    validation_results["validation"]["warnings"].append({
                        "file":str(war["file"]).split("/")[-1],
                        "details":wa["warning"],
                        "removed":not is_soft
                    })
            validation_results_extra = base_extra.copy()
            validation_results_extra.update(validation_results)

            if final_status=="failed":
                failed_validation_extra = validation_results_extra.copy()
                failed_validation_extra.update({
                    "event":{
                    "category":"validation",
                    "type":"end_validation",
                    "status":"failed"
                    }
                } 
                )
                logger.error("validation completely failed (all files removed)",extra=failed_validation_extra)
                raise
            else:
                passed_validation_extra = validation_results_extra.copy()
                passed_validation_extra.update({
                    "event":{
                    "category":"validation",
                    "type":"end_validation",
                    "status":"success"
                    }
                } 
                )

                logger.info("validation ended",extra=passed_validation_extra)

            acceptable_tags = [
                "text_generation",
                "image_segmentation",
                "image_classification",
            ]

            # is_structured = (
            #     self.validate_dataset_structure(local_file)
            #     if local_file.is_dir()
            #     else False
            # )

            if (
                local_file.is_dir()
                and dataset_tag in acceptable_tags
                #and not is_structured
            ):
                restructurer = Restructurer(task_type=dataset_tag)

                restructurer_input_path = local_file
                restructurer_output_path = temp_dir / f"{local_file.stem}_restructured"
                result = restructurer.restructure(
                    input_path=restructurer_input_path,
                    output_path=restructurer_output_path,
                )
                if not result:
                    failed_restructuring = base_extra.copy()
                    failed_restructuring.update({
                        "event":{
                            "category":"restructure",
                            "type":"restructure_result",
                            "status":"failed"
                        }
                    }
                    )
                    logger.error("restructuring failed: skipping this part",extra=failed_restructuring)
                else:
                    local_file = restructurer_output_path
            else:
                skipping_restructuring = base_extra.copy()
                skipping_restructuring.update({
                    "event":{
                        "category":"restructure",
                        "type":"skip_restructure",
                        "status":"failed"
                    }
                }
                )
                logger.info(
                    f"Skipping restructuring for dataset_tag '{dataset_tag}'. Either not a directory or tag not in {acceptable_tags} or already structured."
                    ,extra=skipping_restructuring)

            # --- Log remaining files and store the dataset ---
            files_to_upload = (
                [f.name for f in local_file.rglob("*") if f.is_file()]
                if local_file.is_dir()
                else [local_file.name]
            )
            logger.info(f"uploading {len(files_to_upload)} files: {files_to_upload}")

            stored_path = storage_handler.store_dataset(
                local_file,
                metadata,
                s3_config=s3_config_target,
                clearml_config=clearml_config,
            )

            successfully_stored = base_extra.copy()

            successfully_stored.update({
                "event":{
                    "category":"store_dataset",
                    "type":"end_storing",
                    "status":"success"
                }
            }
            )

            # --- Construct final response ---
            response = {
                "status": final_status,
                "message": final_message,
                "dataset_id": dataset_id,
                "stored_path": stored_path,
            }
            if error_details:
                response["validation_errors"] = error_details

            return response
        except Exception as e:
            # 2. Log the failure of the entire process
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            process_fail_event = base_extra.copy()
            process_fail_event["event"] = {
                "category": "process",
                "type": "s3_processing_failed",
                "status": "failure",
                "duration": int(duration_ms)
            }
            # Let the logger format the exception automatically
            logger.error(f"Failed to process S3 dataset for job {base_extra['trace']['job_id']}", exc_info=True, extra=process_fail_event)
            
            # Re-raise the appropriate exception
            if not isinstance(e, HTTPException):
                raise HTTPException(status_code=500, detail=str(e))
            raise
    
        finally:
            # 3. Log the completion of the entire process, including duration
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            process_end_event = base_extra.copy()
            process_end_event["event"] = {
                "category": "process",
                "type": "s3_processing_finished",
                "status": "success", # This block only runs on success
                "duration": int(duration_ms)
            }
            logger.info(f"Finished processing S3 dataset for job {base_extra['trace']['job_id']}", extra=process_end_event)
