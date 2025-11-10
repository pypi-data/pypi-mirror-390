import io
import logging
import os
import zipfile
from contextlib import contextmanager
from typing import Dict

import boto3
from botocore.client import BaseClient
from tqdm import tqdm

# Set up logger for consistent output
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --- tqdm Progress Bar Callback for Boto3 ---
class TqdmProgressCallback:
    """
    A boto3 download callback that updates a tqdm progress bar.
    """

    def __init__(self, pbar: tqdm):
        self.pbar = pbar

    def __call__(self, bytes_transferred: int):
        self.pbar.update(bytes_transferred)


@contextmanager
def clearml_client_session(credentials: Dict[str, str]):
    """
    A context manager that creates an explicit, isolated ClearML Session.
    This temporarily overrides the global ClearML configuration for the 'with' block.
    """
    from clearml.backend_api.session import Session
    from clearml import Task

    Task.set_credentials(
        key=credentials.get("access_key"),
        secret=credentials.get("secret_key"),
        api_host=credentials.get("host")
    )
    try:
        # The session is now active for any ClearML calls within this 'with' block.
        yield
    finally:
        # The session is automatically cleaned up when exiting the 'with' block.
        logger.info("Temporary ClearML session closed and context restored.")


def get_s3_path_from_clearml_dataset(
    clearml_access_key: str,
    clearml_secret_key: str,
    dataset_name: str,
    clearml_host: str,
    version: str = "latest",
    user_name: str = "default"
) -> str:
    """
    Retrieve the S3 path of a ClearML dataset using provided credentials.
    """
    from clearml import Dataset

    credentials = {
        "access_key": clearml_access_key,
        "secret_key": clearml_secret_key,
        "host": clearml_host
    }

    with clearml_client_session(credentials):
        datasets = Dataset.list_datasets(partial_name=dataset_name, only_completed=True)
        if not datasets:
            raise ValueError(
                f"No datasets found with name containing '{dataset_name}'."
            )

        logger.info(
            f"Found {len(datasets)} potential dataset(s) matching '{dataset_name}'. Searching for exact match..."
        )

        versions = [d["version"] for d in datasets]
        print("available versions:{versions}")

        if version=="latest":
            datasets = sorted(datasets, key=lambda x: x["version"], reverse=True)

            for i in datasets[0]["tags"]:
                if "s3_path" in i:
                    return ":".join(i.split(":")[1:])
        else:
            for d in datasets:
                if d["version"]==version:
                    for i in d["tags"]:
                        if "s3_path" in i:
                            return ":".join(i.split(":")[1:])



            


def download_dataset_from_s3(s3_client: BaseClient, s3_path: str, absolute_path: str):
    """
    Download dataset files from an S3 path to a local directory with a progress bar.
    """
    if not s3_path.startswith("s3://"):
        raise ValueError(f"Invalid S3 path format: {s3_path}. Must start with 's3://'.")

    s3_path_parts = s3_path[5:].split("/", 1)
    if len(s3_path_parts) < 2:
        raise ValueError(
            f"Invalid S3 path format: {s3_path}. Must be 's3://bucket/key'."
        )

    s3_bucket, s3_key_prefix = s3_path_parts

    # --- Step 1: List all objects and calculate total size ---
    logger.info("Listing files in S3 and calculating total size...")
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key_prefix)

    files_to_download = []
    total_size = 0
    for page in pages:
        for obj in page.get("Contents", []):
            files_to_download.append(obj)
            total_size += obj["Size"]

    if not files_to_download:
        logger.warning(f"No files found at S3 path: {s3_path}. Nothing to download.")
        return

    logger.info(
        f"Found {len(files_to_download)} files. Total size: {total_size / (1024 * 1024):.2f} MB"
    )

    # --- Step 2: Download files with a tqdm progress bar ---
    with tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Downloading dataset"
    ) as pbar:
        progress_callback = TqdmProgressCallback(pbar)

        for obj in files_to_download:
            s3_key = obj["Key"]
            # Create a relative path for the local file system
            relative_path = os.path.relpath(s3_key, start=s3_key_prefix)
            local_file_path = os.path.join(absolute_path, relative_path)

            # Update progress bar description to show the current file
            pbar.set_postfix_str(os.path.basename(local_file_path), refresh=True)

            # Ensure local directory for the file exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the file with the progress callback
            s3_client.download_file(
                s3_bucket, s3_key, local_file_path, Callback=progress_callback
            )


# Helper function to generate presigned URLs
def generate_presigned_urls(s3_client, s3_path: str, expiration: int = 3600):
    """Generate presigned URLs for all files under the S3 path"""
    try:
        s3_path_parts = s3_path[5:].split("/", 1)
        bucket_name, s3_key_prefix = s3_path_parts

        paginator = s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=s3_key_prefix)

        presigned_urls = []

        print(s3_key_prefix, bucket_name)

        for page in page_iterator:
            if "Contents" in page:
                for obj in page["Contents"]:
                    obj_key = obj["Key"]
                    obj_size = obj["Size"]

                    # Skip directories
                    if obj_key.endswith("/"):
                        continue

                    try:
                        presigned_url = s3_client.generate_presigned_url(
                            "get_object",
                            Params={"Bucket": str(bucket_name), "Key": str(obj_key)},
                            ExpiresIn=expiration,
                        )

                        # Extract filename from key
                        filename = obj_key.split("/")[-1]
                        relative_path = obj_key[len(s3_key_prefix) :].lstrip("/")
                        if not relative_path:
                            relative_path = filename

                        presigned_urls.append(
                            {
                                "filename": filename,
                                "s3_key": obj_key,
                                "size": obj_size,
                                "download_url": presigned_url,
                            }
                        )
                    except Exception as e:
                        logger.error(
                            f"Error generating presigned URL for {obj_key}: {e}"
                        )
                        continue

        return presigned_urls
    except Exception as e:
        logger.error(f"Error generating presigned URLs: {e}")
        raise


# Helper function to create streaming zip
def create_streaming_zip(s3_client, bucket_name: str, s3_key: str):
    """Create a streaming zip response of S3 files"""

    def generate_zip():
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            try:
                paginator = s3_client.get_paginator("list_objects_v2")
                page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=s3_key)

                for page in page_iterator:
                    if "Contents" in page:
                        for obj in page["Contents"]:
                            obj_key = obj["Key"]

                            # Skip directories
                            if obj_key.endswith("/"):
                                continue

                            try:
                                # Get object from S3
                                response = s3_client.get_object(
                                    Bucket=bucket_name, Key=obj_key
                                )
                                file_data = response["Body"].read()

                                # Add to zip with relative path
                                relative_path = obj_key[len(s3_key) :].lstrip("/")
                                if not relative_path:
                                    relative_path = obj_key.split("/")[-1]

                                zip_file.writestr(relative_path, file_data)
                                logger.info(
                                    f"Added {obj_key.split('/')[-1]} to zip as {relative_path}"
                                )

                            except Exception as e:
                                logger.error(f"Error adding {obj_key} to zip: {e}")
                                continue

            except Exception as e:
                logger.error(f"Error creating zip: {e}")
                raise

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    return generate_zip()


def s3_download(
    clearml_access_key: str,
    clearml_secret_key: str,
    clearml_host: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_endpoint_url: str,
    dataset_name: str,
    absolute_path: str,
    user_name: str = "default",
    method: str = "download",
    version:str = "latest"
):
    """
    Main function to download a ClearML dataset from S3 to a local directory.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_endpoint_url,
    )

    # 1. Get the S3 path from ClearML metadata
    s3_path = get_s3_path_from_clearml_dataset(
        clearml_access_key, clearml_secret_key, dataset_name,clearml_host, user_name=user_name,version=version
    )
    logger.info(f"Retrieved S3 path from ClearML: {s3_path}")

    # 2. Download the dataset from S3
    logger.info(f"Starting download to local directory: {absolute_path}")

    if method == "download":
        download_dataset_from_s3(s3_client, s3_path, absolute_path)
        logger.info("Download complete.")

    elif method == "presigned_urls":
        urls = generate_presigned_urls(s3_client, s3_path)
        logger.info(f"Generated {len(urls)} presigned URLs.")
        return urls

    elif method == "streaming_zip":
        s3_path_parts = s3_path[5:].split("/", 1)
        bucket_name, s3_key_prefix = s3_path_parts
        zip_data = create_streaming_zip(s3_client, bucket_name, s3_key_prefix)
        logger.info("Created streaming zip of dataset.")
        return zip_data
