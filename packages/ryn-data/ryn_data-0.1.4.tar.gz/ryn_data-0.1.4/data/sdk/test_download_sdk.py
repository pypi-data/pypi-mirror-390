import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from data.sdk.download_sdk import s3_download


@pytest.fixture
def test_inputs(tmp_path):
    """Fixture with exactly the same inputs as in runner.py."""
    return {
        "clearml_access_key": "8113C94C6A387E90477E58B89CCE0547",
        "clearml_secret_key": "C60E7BD316A59D867D083BABD50B161EF2BFB8BDAADD59935978E546009F923E",
        "s3_access_key": "3386LN5KA2OFQXPTYM9S",
        "s3_secret_key": "AALvi6KexAeSNCsOMRqDHTRf10BQzNyy5BQnGIfO",
        "s3_endpoint_url": "http://144.172.105.98:7000",
        "dataset_name": "hotpotqa-hotpot_qa",
        "absolute_path": tmp_path / "downloaded_datasettt",
        "user_name": "datauserv3",
    }


@pytest.fixture
def mock_s3_client():
    """Mock boto3 s3 client."""
    mock = MagicMock()

    # Mock paginator (used in presigned_urls and download)
    paginator = MagicMock()
    mock.get_paginator.return_value = paginator
    paginator.paginate.return_value = [
        {"Contents": [{"Key": "some/prefix/file1.txt", "Size": 10}]}
    ]

    # Mock download_file behavior
    mock.download_file.side_effect = lambda bucket, key, path, Callback=None: Path(path).write_text("dummy")

    # Mock presigned URL generation
    mock.generate_presigned_url.return_value = "http://fake-presigned-url"

    # Mock get_object for streaming_zip
    mock.get_object.return_value = {"Body": io.BytesIO(b"data for zip")}

    return mock

@pytest.mark.integration
def test_real_s3_download(tmp_path):
    """
    Real integration test: actually connects to your S3 endpoint and downloads files.
    Requires valid access keys and an existing ClearML dataset.
    """

    # --- Configuration from env vars for security ---
    clearml_access_key = "8113C94C6A387E90477E58B89CCE0547"
    clearml_secret_key = "C60E7BD316A59D867D083BABD50B161EF2BFB8BDAADD59935978E546009F923E"
    s3_access_key ="3386LN5KA2OFQXPTYM9S"
    s3_secret_key = "AALvi6KexAeSNCsOMRqDHTRf10BQzNyy5BQnGIfO"
    s3_endpoint_url = "http://144.172.105.98:7000"
    dataset_name = "hotpotqa-hotpot_qa"
    user_name ="datauserv3"

    # --- Local destination ---
    absolute_path = tmp_path / "real_downloaded_dataset"
    absolute_path.mkdir(parents=True, exist_ok=True)

    # --- Run the actual download ---
    s3_download(
        clearml_access_key=clearml_access_key,
        clearml_secret_key=clearml_secret_key,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_endpoint_url=s3_endpoint_url,
        dataset_name=dataset_name,
        absolute_path=absolute_path,
        user_name=user_name,
        method="download"
    )

    # --- Verify that files actually downloaded ---
    downloaded_files = list(absolute_path.rglob("*"))
    assert downloaded_files, f"No files found in {absolute_path}"


    # Check that each file has nonzero content
    for f in downloaded_files:
        if f.is_file() and not str(f).endswith('.lock'):
            size = f.stat().st_size
            assert size > 0, f"File {f} is empty!"

    print(f"Downloaded {len(downloaded_files)} files to {absolute_path}")


@patch("data.sdk.download_sdk.get_s3_path_from_clearml_dataset", return_value="s3://datauserv2-bucket-bucket/some/prefix")
@patch("boto3.client")
def test_streaming_zip(mock_boto_client, mock_get_s3_path, test_inputs, mock_s3_client, tmp_path):
    """Test the streaming_zip method end-to-end with mocks."""
    mock_boto_client.return_value = mock_s3_client

    zip_bytes = s3_download(
        **test_inputs,
        method="streaming_zip"
    )

    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0

    # Validate contents of the zip
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = z.namelist()
        assert "file1.txt" in names


@patch("data.sdk.download_sdk.get_s3_path_from_clearml_dataset", return_value="s3://datauserv2-bucket-bucket/some/prefix")
@patch("boto3.client")
def test_presigned_urls(mock_boto_client, mock_get_s3_path, test_inputs, mock_s3_client):
    """Test presigned_urls method."""
    mock_boto_client.return_value = mock_s3_client

    urls = s3_download(
        **test_inputs,
        method="presigned_urls"
    )

    assert isinstance(urls, list)
    assert len(urls) == 1
    assert "filename" in urls[0]
    assert urls[0]["download_url"].startswith("http://fake-presigned-url")


@patch("data.sdk.download_sdk.get_s3_path_from_clearml_dataset", return_value="s3://datauserv2-bucket-bucket/some/prefix")
@patch("boto3.client")
def test_download_method(mock_boto_client, mock_get_s3_path, test_inputs, mock_s3_client):
    """Test download method calls download_file properly."""
    mock_boto_client.return_value = mock_s3_client

    s3_download(
        **test_inputs,
        method="download"
    )

    # Expected output path
    expected_file = test_inputs["absolute_path"] / "file1.txt"

    # Check that the file exists and contains correct data
    assert expected_file.exists(), f"Expected file not found: {expected_file}"
    assert expected_file.read_text() == "dummy"

    # Confirm boto3's download_file was invoked correctly
    mock_s3_client.download_file.assert_called_once()

    # Verify folder structure creation
    assert expected_file.parent.exists()
    assert expected_file.parent.name == "downloaded_datasettt"


def invalid_dataset_name():
    """Test that an invalid dataset name raises ValueError."""
    with pytest.raises(ValueError):
        s3_download(
            clearml_access_key="key",
            clearml_secret_key="secret",
            s3_access_key="s3key",
            s3_secret_key="s3secret",
            s3_endpoint_url="http://endpoint",
            dataset_name="nonexistent-dataset",
            absolute_path=Path("/tmp/somepath"),
            user_name="user",
            method="download"
        )