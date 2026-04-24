from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

import structlog
import boto3
from botocore.config import Config

from app.config import settings

logger = structlog.get_logger()

# Dedicated thread pool for S3 operations — avoids blocking the async event loop
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="s3")


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

    def _upload_sync(self, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def _download_sync(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def upload_file(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Synchronous upload — use upload_file_async in async contexts."""
        logger.info("storage.upload", key=key, size=len(data), content_type=content_type)
        return self._upload_sync(key, data, content_type)

    async def upload_file_async(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Non-blocking upload via thread pool executor."""
        logger.info("storage.upload_async", key=key, size=len(data))
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._upload_sync, key, data, content_type)

    def download_file(self, key: str) -> bytes:
        logger.info("storage.download", key=key)
        return self._download_sync(key)

    async def download_file_async(self, key: str) -> bytes:
        logger.info("storage.download_async", key=key)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._download_sync, key)

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        logger.info("storage.presign", key=key, expires_in=expires_in)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )


storage = StorageService()
