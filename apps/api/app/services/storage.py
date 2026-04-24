from __future__ import annotations

import structlog
import boto3
from botocore.config import Config

from app.config import settings

logger = structlog.get_logger()


class StorageService:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )
        self._bucket = settings.R2_BUCKET

    def upload_file(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        logger.info("storage.upload", key=key, size=len(data), content_type=content_type)
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def download_file(self, key: str) -> bytes:
        logger.info("storage.download", key=key)
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        logger.info("storage.presign", key=key, expires_in=expires_in)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )


storage = StorageService()
