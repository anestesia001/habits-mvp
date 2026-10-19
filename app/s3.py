import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
    )


def upload_report(file_path, object_key: str) -> str:
    client = get_s3_client()

    try:
        client.upload_file(
            Filename=str(file_path),
            Bucket=settings.aws_s3_bucket,
            Key=object_key,
            ExtraArgs={"ContentType": "text/csv"},
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Не удалось загрузить отчёт в S3: {exc}") from exc

    if settings.aws_endpoint_url:
        return f"{settings.aws_endpoint_url}/{settings.aws_s3_bucket}/{object_key}"

    return (
        f"https://{settings.aws_s3_bucket}.s3.{settings.aws_region}"
        f".amazonaws.com/{object_key}"
    )