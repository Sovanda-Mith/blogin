import boto3
import uuid
from datetime import datetime
from typing import Optional
from botocore.config import Config
from botocore.exceptions import ClientError
from app.config import get_settings


settings = get_settings()


def get_s3_client():
    config = Config(signature_version="s3v4", s3={"addressing_style": "path"})
    return boto3.client("s3", region_name=settings.AWS_REGION, config=config)


def get_s3_key(user_id: str) -> str:
    return f"avatars/{user_id}/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}"


def generate_presigned_upload_url(
    user_id: str, content_type: str = "image/jpeg", expires_in: int = 3600
) -> dict:
    s3_client = get_s3_client()
    key = get_s3_key(user_id)

    try:
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET_NAME,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

        return {
            "upload_url": presigned_url,
            "key": key,
            "bucket": settings.S3_BUCKET_NAME,
            "expires_in": expires_in,
        }
    except ClientError as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")


def get_avatar_url(user_id: str) -> Optional[str]:
    s3_client = get_s3_client()
    prefix = f"avatars/{user_id}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME, Prefix=prefix, MaxKeys=1
        )

        if "Contents" in response and len(response["Contents"]) > 0:
            latest_object = response["Contents"][0]
            key = latest_object["Key"]
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return None
    except ClientError as e:
        return None


def delete_avatar(user_id: str) -> bool:
    s3_client = get_s3_client()
    prefix = f"avatars/{user_id}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME, Prefix=prefix
        )

        if "Contents" not in response:
            return True

        objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]

        if objects_to_delete:
            s3_client.delete_objects(
                Bucket=settings.S3_BUCKET_NAME, Delete={"Objects": objects_to_delete}
            )

        return True
    except ClientError as e:
        raise Exception(f"Failed to delete avatar: {str(e)}")


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_avatar_file(content_type: str, size: int) -> tuple[bool, str]:
    if content_type not in ALLOWED_CONTENT_TYPES:
        return (
            False,
            f"Invalid content type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES.keys())}",
        )

    if size > MAX_FILE_SIZE:
        return (
            False,
            f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    return True, ""
