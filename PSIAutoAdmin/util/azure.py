import logging
from datetime import datetime
from pathlib import PurePath
from azure.storage.blob import BlobServiceClient,BlobClient
from azure.identity import DefaultAzureCredential,InteractiveBrowserCredential

logger = logging.getLogger(__name__)
container_name = "psiadminauto-blobstore"
account_url = "https://psiadminauto.blob.core.windows.net"
default_credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url, credential=default_credential)

def upload_az_blob(source_file):
    """
    Uploads a file to the storage container.
    """
    destination_blob = source_file
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=destination_blob)

    logger.debug(f"Uploading file : {source_file}")
    with open(source_file, "rb") as source_data:
        blob_client.upload_blob(source_data)
    logger.debug(f"File uploaded to {destination_blob}")
    return {"status":"OK","detail":"Succesfully uploaded to storage container"}

def download_az_blob(blob_url):
    """
    Download a file from the storage container.
    Pass the blob url as the identifier in the argument.
    """
    blob_client = BlobClient.from_blob_url(blob_url,credential=default_credential)
    blob_name = blob_client.get_blob_properties().name
    logger.debug(f"Download file from azure blob container : {blob_name}")
    with open(blob_name, "wb") as destination_data:
        destination_data.write(blob_client.download_blob().readall())
    logger.debug(f"File downloaded to {blob_name}")
    return {"status":"OK","detail":f"Succesfully downloaded file {blob_name}","path":blob_name}

def list_az_blob(blob_suffix):
    container_client = blob_service_client.get_container_client(container_name)
    blobs = list(container_client.list_blob_names(name_starts_with=blob_suffix))
    list_blobs_url = [blob_service_client.get_blob_client(container=container_name, blob=item).url for item in blobs]
    return list_blobs_url