"""AWS Replicate - Lightweight cross-region data replication SDK."""

__version__ = "0.1.0"

from awsreplicate.config import AWSConfig
from awsreplicate.s3_replicator import S3Replicator
from awsreplicate.dynamodb_replicator import DynamoDBReplicator

__all__ = ["AWSConfig", "S3Replicator", "DynamoDBReplicator"]
