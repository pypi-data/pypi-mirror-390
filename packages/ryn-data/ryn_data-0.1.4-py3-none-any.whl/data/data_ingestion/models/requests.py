from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClearMLCredentials(BaseModel):
    access_key: str
    secret_key: str

class S3Credentials(BaseModel):
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    bucket_name: Optional[str] = None
class KaggleCredentials(BaseModel):
    user_name: str
    key: str

# --- Enum for Download Method ---

class DownloadMethod(str, Enum):
    """Enumeration for the available dataset download methods."""
    PRESIGNED_URLS = "presigned_urls"
    STREAM_ZIP = "stream_zip"
    DIRECT_STREAM = "direct_stream"

class S3DownloadRequest(BaseModel):
    # Core dataset and S3 file information
    s3_file_path: str
    user_name: str
    dataset_name: Optional[str] = None
    private: bool = False
    dataset_tag: Optional[str] = Field(default=None, alias="dataset_tag")
    s3_source: Optional[S3Credentials] = None
    s3_target: Optional[S3Credentials] = None
    clearml: ClearMLCredentials
    queue_name: str = "default"
    
    
class KaggleDownloadRequest(BaseModel):
    dataset_id: str
    user_name: str
    dataset_name: Optional[str] = None
    private: bool = False
    kaggle: KaggleCredentials
    dataset_tag : str
    queue_name: str = "default" 
    clearml: ClearMLCredentials
    s3_config: S3Credentials

class HuggingFaceDownloadRequest(BaseModel):
    # Hugging Face dataset information
    dataset_name: str
    dataset_config: Optional[str] = "default"
    dataset_tag: str
    
    # ClearML dataset metadata
    user_name: str
    private: bool = False
    revision: Optional[str] = "main"
    
    # Nested credentials for the S3 target where the dataset will be stored
    s3_config: S3Credentials
    
    # Nested credentials for ClearML
    clearml: ClearMLCredentials
    
    # ClearML execution parameters
    queue_name: str = "default"
    

class OpenMLDownloadRequest(BaseModel):
    dataset_id: int
    user_name: str
    dataset_name: Optional[str] = None
    private: bool = False
    dataset_tag : str
    queue_name: str = "default" 
    clearml: ClearMLCredentials
    s3_config: S3Credentials

class ListDatasetsRequest(BaseModel):
    clearml_access_key: str
    clearml_secret_key: str
    user_name: Optional[str] = None
    private_only: Optional[bool] = False
    queue_name: str = "default" 
    
class DownloadDatasetRequest(BaseModel):
    dataset_name: str
    user_name: str  # Added user_name for filtering
    # Nested credentials for the S3 target where the dataset will be stored
    s3_config: S3Credentials
    # Nested credentials for ClearML
    clearml: ClearMLCredentials
    download_method: DownloadMethod = DownloadMethod.PRESIGNED_URLS
    expiration: int = 3600  # For presigned URLs, expiration in seconds (default 1 hour)

class TaskStatusRequest(BaseModel):
    task_id: str
    clearml: ClearMLCredentials


class ListTasksRequest(BaseModel):
    user_name: str
    clearml: ClearMLCredentials
    limit: int = 50

class ListClearMLDatasetsRequest(BaseModel):
    user_name: str
    clearml: ClearMLCredentials
    