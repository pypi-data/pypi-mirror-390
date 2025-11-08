"""Async S3 cross-region replication."""

import asyncio
from typing import List, Optional, Dict, Any
import boto3
import structlog

from awsreplicate.config import AWSConfig
from awsreplicate.utils.retry import get_retry_decorator
from awsreplicate.utils.concurrency import Semaphore
from awsreplicate.utils.logging import setup_logger

logger = structlog.get_logger(__name__)


class S3Replicator:
    """Handles async cross-region S3 object replication."""

    def __init__(
        self,
        config: AWSConfig,
        source_region: str,
        target_region: str,
        max_concurrent: int = 10,
    ):
        """
        Initialize S3 replicator.

        Args:
            config: AWS configuration
            source_region: Source AWS region
            target_region: Target AWS region
            max_concurrent: Maximum concurrent operations
        """
        self.config = config
        self.source_region = source_region
        self.target_region = target_region
        self.semaphore = Semaphore(max_concurrent)

        logger.info(
            "S3Replicator initialized",
            source_region=source_region,
            target_region=target_region,
            max_concurrent=max_concurrent,
        )

    async def _copy_object(
        self,
        source_bucket: str,
        target_bucket: str,
        key: str,
    ) -> Dict[str, Any]:
        """
        Copy a single S3 object between regions.

        Args:
            source_bucket: Source bucket name
            target_bucket: Target bucket name
            key: Object key
            session: aioboto3 session

        Returns:
            Dict with copy result
        """
        async with self.semaphore:
            # Run synchronous boto3 copy logic in a thread to keep compatibility with moto
            return await asyncio.to_thread(self._copy_object_sync, source_bucket, target_bucket, key)

    @get_retry_decorator(max_attempts=3)
    def _copy_object_sync(self, source_bucket: str, target_bucket: str, key: str) -> Dict[str, Any]:
        """Synchronous helper to copy object using boto3 (safe for moto)."""
        try:
            # Get object from source
            source_s3 = self.config.get_client("s3", self.source_region)
            response = source_s3.get_object(Bucket=source_bucket, Key=key)
            body = response["Body"].read()
            metadata = response.get("Metadata", {})
            content_type = response.get("ContentType", "binary/octet-stream")

            # Put object to target
            target_s3 = self.config.get_client("s3", self.target_region)
            target_s3.put_object(
                Bucket=target_bucket,
                Key=key,
                Body=body,
                Metadata=metadata,
                ContentType=content_type,
            )

            logger.info("Object replicated", key=key, size=len(body))
            return {"key": key, "status": "success", "size": len(body)}

        except Exception as e:
            logger.error("Failed to replicate object", key=key, error=str(e))
            return {"key": key, "status": "failed", "error": str(e)}

    async def replicate_bucket(
        self,
        source_bucket: str,
        target_bucket: str,
        prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Replicate all objects from source bucket to target bucket.

        Args:
            source_bucket: Source bucket name
            target_bucket: Target bucket name
            prefix: Optional prefix to filter objects

        Returns:
            Dict with replication summary
        """
        logger.info(
            "Starting bucket replication",
            source_bucket=source_bucket,
            target_bucket=target_bucket,
            prefix=prefix,
        )


        # Use synchronous boto3 client (via AWSConfig) to list objects — compatible with moto
        source_s3 = self.config.get_client("s3", self.source_region)
        paginator = source_s3.get_paginator("list_objects_v2")
        params = {"Bucket": source_bucket}
        if prefix:
            params["Prefix"] = prefix

        objects_to_copy: List[str] = []
        for page in paginator.paginate(**params):
            if "Contents" in page:
                objects_to_copy.extend([obj["Key"] for obj in page["Contents"]])

        logger.info("Found objects to replicate", count=len(objects_to_copy))

        # Copy objects concurrently
        tasks = [self._copy_object(source_bucket, target_bucket, key) for key in objects_to_copy]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Summarize results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed = len(results) - successful
        total_size = sum(r.get("size", 0) for r in results if isinstance(r, dict))

        summary = {
            "total_objects": len(objects_to_copy),
            "successful": successful,
            "failed": failed,
            "total_size_bytes": total_size,
        }

        logger.info("Bucket replication completed", **summary)
        return summary
