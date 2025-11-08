"""DynamoDB cross-region replication."""

from typing import List, Dict, Any, Optional
import structlog

from awsreplicate.config import AWSConfig
from awsreplicate.utils.retry import get_retry_decorator

logger = structlog.get_logger(__name__)


class DynamoDBReplicator:
    """Handles DynamoDB item replication between regions."""

    def __init__(
        self,
        config: AWSConfig,
        source_region: str,
        target_region: str,
    ):
        """
        Initialize DynamoDB replicator.

        Args:
            config: AWS configuration
            source_region: Source AWS region
            target_region: Target AWS region
        """
        self.config = config
        self.source_region = source_region
        self.target_region = target_region

        self.source_client = config.get_client("dynamodb", source_region)
        self.target_client = config.get_client("dynamodb", target_region)

        logger.info(
            "DynamoDBReplicator initialized",
            source_region=source_region,
            target_region=target_region,
        )

    @get_retry_decorator(max_attempts=3)
    def replicate_item(
        self,
        source_table: str,
        target_table: str,
        key: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Replicate a single item from source to target table.

        Args:
            source_table: Source table name
            target_table: Target table name
            key: Item key

        Returns:
            Dict with replication result
        """
        try:
            # Get item from source
            response = self.source_client.get_item(
                TableName=source_table,
                Key=key,
            )

            if "Item" not in response:
                logger.warning("Item not found", key=key)
                return {"status": "not_found", "key": key}

            item = response["Item"]

            # Put item to target
            self.target_client.put_item(
                TableName=target_table,
                Item=item,
            )

            logger.info("Item replicated", key=key)
            return {"status": "success", "key": key}

        except Exception as e:
            logger.error("Failed to replicate item", key=key, error=str(e))
            return {"status": "failed", "key": key, "error": str(e)}

    def scan_and_replicate(
        self,
        source_table: str,
        target_table: str,
        batch_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Scan source table and replicate all items to target.

        Args:
            source_table: Source table name
            target_table: Target table name
            batch_size: Batch size for writing

        Returns:
            Dict with replication summary
        """
        logger.info(
            "Starting table scan and replication",
            source_table=source_table,
            target_table=target_table,
        )

        successful = 0
        failed = 0
        items_batch = []

        # Scan source table
        paginator = self.source_client.get_paginator("scan")
        for page in paginator.paginate(TableName=source_table):
            items = page.get("Items", [])

            for item in items:
                items_batch.append(item)

                # Write in batches
                if len(items_batch) >= batch_size:
                    result = self._write_batch(target_table, items_batch)
                    successful += result["successful"]
                    failed += result["failed"]
                    items_batch = []

        # Write remaining items
        if items_batch:
            result = self._write_batch(target_table, items_batch)
            successful += result["successful"]
            failed += result["failed"]

        summary = {
            "successful": successful,
            "failed": failed,
            "total": successful + failed,
        }

        logger.info("Table replication completed", **summary)
        return summary

    @get_retry_decorator(max_attempts=3)
    def _write_batch(
        self,
        table_name: str,
        items: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Write a batch of items to target table."""
        try:
            request_items = {
                table_name: [{"PutRequest": {"Item": item}} for item in items]
            }

            response = self.target_client.batch_write_item(
                RequestItems=request_items
            )

            unprocessed = len(response.get("UnprocessedItems", {}).get(table_name, []))
            successful = len(items) - unprocessed

            return {"successful": successful, "failed": unprocessed}

        except Exception as e:
            logger.error("Batch write failed", error=str(e))
            return {"successful": 0, "failed": len(items)}
