import boto3
from botocore.config import Config

from django.conf import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )
    return _client


def presigned_put_url(key, content_type):
    return _get_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key, "ContentType": content_type},
        ExpiresIn=900,
    )


def presigned_get_url(key):
    return _get_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
        ExpiresIn=900,
    )


def head_object(key):
    return _get_client().head_object(Bucket=settings.S3_BUCKET_NAME, Key=key)


def get_object(key):
    return _get_client().get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)["Body"].read()


def import_object_key(organization_id, lead_import_id, ext):
    return f"org/{organization_id}/imports/{lead_import_id}/original.{ext}"