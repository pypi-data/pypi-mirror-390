# a simple script to download the latest SDK package
import os
import boto3
import logging
from clearml import Dataset
from fastapi import HTTPException
from pathlib import Path
from data.sdk.download_sdk import  s3_download


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)




def main():

    s3_access_key = "3386LN5KA2OFQXPTYM9S"
    s3_secret_key = "AALvi6KexAeSNCsOMRqDHTRf10BQzNyy5BQnGIfO"
    s3_bucket_name = "datauserv2-bucket-bucket"
    s3_endpoint_url = "http://144.172.105.98:7000"
    absolute_path = Path(__file__).parent/ "downloaded_datasettt"
    dataset_name = "hotpotqa-hotpot_qa"
    clearml_access_key = "8113C94C6A387E90477E58B89CCE0547"
    clearml_secret_key = "C60E7BD316A59D867D083BABD50B161EF2BFB8BDAADD59935978E546009F923E"

    user_name="datauserv3"

    #download 
    
    # s3_download(
    # clearml_access_key,
    # clearml_secret_key,
    # s3_access_key,
    # s3_secret_key,
    # s3_endpoint_url,
    # dataset_name,
    # absolute_path,
    # user_name)

    # presigned_urls method


    # url = s3_download(
    # clearml_access_key,
    # clearml_secret_key,
    # s3_access_key,
    # s3_secret_key,
    # s3_endpoint_url,
    # dataset_name,
    # absolute_path,
    # user_name,
    # method="presigned_urls")


    
    # print("Downloaded SDK package is available at:", url)

    #zip_streaming method

    zip_data = s3_download(
        clearml_access_key,
        clearml_secret_key,
        s3_access_key,
        s3_secret_key,
        s3_endpoint_url,
        dataset_name,
        absolute_path,
        user_name,
        method="streaming_zip")

    print(type(zip_data))
    if zip_data:
        path = Path(__file__).parent / "dataset.zip"
        with open(path, "wb") as f:
            f.write(zip_data)
        print("Successfully saved dataset.zip")

if __name__ == "__main__":
    main()



