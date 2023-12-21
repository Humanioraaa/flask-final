from google.cloud import storage
from google.oauth2 import service_account


credentials = service_account.Credentials.from_service_account_file(
    './frutyripe-6cbadb798c8c.json'
)

client = storage.Client(credentials=credentials, project='frutyripe')
bucket = client.get_bucket('frutyripe.appspot.com')

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(project='frutyripe')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(
        "File {} uploaded to {}.".format(
            source_file_path, destination_blob_name
        )
    )

# Replace these with your values
bucket_name = "frutyripe.appspot.com"
source_file_path = "./salak.jpg"
destination_blob_name = "./files/detect"

upload_to_gcs(bucket_name, source_file_path, destination_blob_name)
