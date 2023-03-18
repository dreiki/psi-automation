from google.cloud import storage
# The ID of your GCS bucket
BUCKET_NAME = "psi_aut_admin_bucket"

def upload_blob(source_file_name):
    """Uploads a file to the bucket."""
    # The local path to your file to upload
    destination_file_name = source_file_name
    # The ID of your GCS object
    # destination_blob_name = "test"
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_file_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_file_name}."
    )
    process_result = {"status":"OK"}
    return process_result