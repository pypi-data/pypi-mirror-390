import os
from google.cloud import storage


class GCSClient:
    def __init__(self, project_id=None, credentials_path=None, bucket_name=None):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = storage.Client(project=project_id)
        if bucket_name:
            self.set_bucket(bucket_name)

    def set_bucket(self, bucket_name):
        self.bucket = self.client.bucket(bucket_name)

    def get_bucket(self):
        return self.bucket

    def download_blob(self, source_blob_name, destination_file_name):
        """
        Downloads a blob from the bucket.
        """

        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        return destination_file_name

    def upload_blob(self, source_file_name, destination_blob_name):
        """
        Uploads a file to the bucket.
        """
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        return destination_blob_name

    def download_blob_as_string(self, bucket_name, source_blob_name):
        """
        Downloads a blob as a string.
        """
        blob = self.bucket.blob(source_blob_name)
        return blob.download_as_text()

    def upload_blob_from_string(self, bucket_name, data, destination_blob_name):
        """
        Uploads a string as a blob to the bucket.
        """
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(data)
        return destination_blob_name
