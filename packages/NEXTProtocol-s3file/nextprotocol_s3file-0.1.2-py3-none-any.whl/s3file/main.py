import boto3  # type: ignore[import-untyped]

class OvhS3:
    def __init__(self, endpoint: str, bucket: str, region: str, key_id: str, secret: str):
        self.s3_client = boto3.client( # type: ignore[misc]
            "s3",
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=key_id,
            aws_secret_access_key=secret,
        )
        self.bucket = bucket
        self.virtual_endpoint = f"https://{bucket}.s3.{region}.io.cloud.ovh.net"

    def upload_file_public(self, file_path: str, bucket_file_path: str | None = None) -> str:

        if bucket_file_path is None:
            bucket_file_path = f"default_path/{file_path.split('/')[-1]}"

        try:
            self.s3_client.upload_file(file_path, self.bucket, bucket_file_path, ExtraArgs={'ACL': 'public-read'}) # type: ignore[attr-defined]
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e

        return f"{self.virtual_endpoint}/{bucket_file_path}"