# NEXTProtocol S3File

Petit client OVH S3 pensé pour des uploads publics simples.

## Installation

```bash
pip install NEXTProtocol-s3file
# mettre à jour si besoin
pip install --upgrade NEXTProtocol-s3file
```

## Démarrage rapide

```python
from s3file import OvhS3

s3 = OvhS3(
    endpoint="https://s3.gra.io.cloud.ovh.net",
    bucket="your-bucket-name",
    region="gra",
    key_id="YOUR_ACCESS_KEY",
    secret="YOUR_SECRET_KEY",
)

url = s3.upload_file_public("local/path/to/file.jpg")
# -> https://your-bucket.s3.gra.io.cloud.ovh.net/default_path/file.jpg

url = s3.upload_file_public(
    "photo.jpg",
    "images/2024/photo.jpg",
)
# -> https://your-bucket.s3.gra.io.cloud.ovh.net/images/2024/photo.jpg
```

## API

### `OvhS3(endpoint, bucket, gra, key_id, secret)`
- prépare un client boto3 configuré pour OVH
- garde l'endpoint public dans `virtual_endpoint`

### `upload_file_public(file_path, bucket_file_path=None)`
- crée la clé distante `default_path/<nom>` si aucun chemin n'est donné
- passe l'ACL `public-read`
- renvoie l'URL publique complète

## Bonnes pratiques
- vérifie tes identifiants OVH avant l'appel
- pilote les erreurs via un try/except si tu veux une gestion custom
- lance `pip install --upgrade NEXTProtocol-s3file` pour récupérer la dernière version

## Prérequis
- Python >= 3.9
- boto3 >= 1.26.0

## Licence
MIT

