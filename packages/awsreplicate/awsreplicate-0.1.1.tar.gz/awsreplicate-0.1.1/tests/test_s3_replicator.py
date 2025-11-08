"""Tests for S3 replicator."""

import pytest
import boto3
from moto import mock_aws
import asyncio

from awsreplicate import AWSConfig, S3Replicator


@pytest.mark.asyncio
async def test_s3_bucket_replication(aws_credentials):
    """Test S3 bucket replication with mocked S3."""
    # Run the entire test inside the moto mock context so all boto3 calls are intercepted
    with mock_aws():
        # Setup mock S3 buckets
        s3_east = boto3.client("s3", region_name="us-east-1")
        s3_west = boto3.client("s3", region_name="us-west-1")

        source_bucket = "test-source-bucket"
        target_bucket = "test-target-bucket"

        # Create buckets
        s3_east.create_bucket(Bucket=source_bucket)
        s3_west.create_bucket(
            Bucket=target_bucket,
            CreateBucketConfiguration={"LocationConstraint": "us-west-1"},
        )

        # Add test objects to source bucket
        test_objects = {
            "file1.txt": b"Hello World",
            "file2.txt": b"Test Content",
            "folder/file3.txt": b"Nested File",
        }

        for key, content in test_objects.items():
            s3_east.put_object(
                Bucket=source_bucket,
                Key=key,
                Body=content,
            )

        # Configure replicator
        config = AWSConfig()
        replicator = S3Replicator(
            config=config,
            source_region="us-east-1",
            target_region="us-west-1",
            max_concurrent=5,
        )

        # Perform replication
        result = await replicator.replicate_bucket(
            source_bucket=source_bucket,
            target_bucket=target_bucket,
        )

        # Verify results
        assert result["total_objects"] == len(test_objects)
        assert result["successful"] == len(test_objects)
        assert result["failed"] == 0

        # Verify objects exist in target bucket
        target_objects = s3_west.list_objects_v2(Bucket=target_bucket)
        assert target_objects["KeyCount"] == len(test_objects)

        # Verify content
        for key, expected_content in test_objects.items():
            obj = s3_west.get_object(Bucket=target_bucket, Key=key)
            actual_content = obj["Body"].read()
            assert actual_content == expected_content


@pytest.mark.asyncio
async def test_s3_replication_with_prefix(aws_credentials):
    """Test S3 replication with prefix filter."""
    # Run the whole test inside the moto mock
    with mock_aws():
        # Create clients for the mocked regions
        s3_east = boto3.client("s3", region_name="us-east-1")
        s3_west = boto3.client("s3", region_name="us-west-1")

        source_bucket = "test-source-prefix"
        target_bucket = "test-target-prefix"

        s3_east.create_bucket(Bucket=source_bucket)
        s3_west.create_bucket(
            Bucket=target_bucket,
            CreateBucketConfiguration={"LocationConstraint": "us-west-1"},
        )

        # Add objects with different prefixes
        s3_east.put_object(Bucket=source_bucket, Key="data/file1.txt", Body=b"Data 1")
        s3_east.put_object(Bucket=source_bucket, Key="data/file2.txt", Body=b"Data 2")
        s3_east.put_object(Bucket=source_bucket, Key="logs/file3.txt", Body=b"Log 1")

        # Replicate only 'data/' prefix
        config = AWSConfig()
        replicator = S3Replicator(
            config=config,
            source_region="us-east-1",
            target_region="us-west-1",
        )

        result = await replicator.replicate_bucket(
            source_bucket=source_bucket,
            target_bucket=target_bucket,
            prefix="data/",
        )

        # Should only replicate 2 files
        assert result["total_objects"] == 2
        assert result["successful"] == 2
