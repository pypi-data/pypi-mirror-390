# NEXTProtocol S3File

Dead-simple OVH S3 file uploader. Upload files, get public URLs back.

## Install

```bash
pip install NEXTProtocol-s3file
```

## Quick Start

```python
from s3file import OvhS3

# Initialize client
s3 = OvhS3(
    endpoint="https://s3.gra.io.cloud.ovh.net",
    bucket="your-bucket-name",
    gra="fr1",
    key_id="YOUR_ACCESS_KEY",
    secret="YOUR_SECRET_KEY"
)

# Upload file and get public URL
url = s3.upload_file_public("local/path/to/file.jpg")
# Returns: https://your-bucket.s3.gra.io.cloud.ovh.net/default_path/file.jpg

# Custom S3 path
url = s3.upload_file_public("photo.jpg", "images/2024/photo.jpg")
# Returns: https://your-bucket.s3.gra.io.cloud.ovh.net/images/2024/photo.jpg
```

## API

### `OvhS3(endpoint, bucket, gra, key_id, secret)`

Initialize S3 client.

**Parameters:**
- `endpoint` - OVH S3 endpoint URL
- `bucket` - S3 bucket name
- `gra` - Region (e.g., "gra", "rbx")
- `key_id` - AWS access key ID
- `secret` - AWS secret access key

### `upload_file_public(file_path, bucket_file_path=None)`

Upload file with public-read ACL.

**Parameters:**
- `file_path` - Local file path
- `bucket_file_path` - Destination path in bucket (optional, defaults to `default_path/{filename}`)

**Returns:** Public URL to the uploaded file

**Raises:** Exception on upload failure

## Requirements

- Python ≥ 3.9
- boto3 ≥ 1.26.0

## License

MIT

