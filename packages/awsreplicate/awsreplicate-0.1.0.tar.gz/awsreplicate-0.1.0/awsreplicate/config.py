"""AWS configuration and session management."""

import boto3
from typing import Optional, Dict
import structlog

logger = structlog.get_logger(__name__)


class AWSConfig:
    """Manages AWS credentials and region-specific sessions."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        profile_name: Optional[str] = None,
    ):
        """
        Initialize AWS configuration.

        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token (optional)
            profile_name: AWS profile name (optional)
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.profile_name = profile_name
        self._sessions: Dict[str, boto3.Session] = {}

        logger.info("AWS configuration initialized", profile=profile_name)

    def get_session(self, region_name: str) -> boto3.Session:
        """
        Get or create a boto3 session for a specific region.

        Args:
            region_name: AWS region name

        Returns:
            boto3.Session for the specified region
        """
        if region_name not in self._sessions:
            if self.profile_name:
                session = boto3.Session(
                    profile_name=self.profile_name,
                    region_name=region_name
                )
            else:
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    aws_session_token=self.aws_session_token,
                    region_name=region_name,
                )
            self._sessions[region_name] = session
            logger.debug("Created new session", region=region_name)

        return self._sessions[region_name]

    def get_client(self, service_name: str, region_name: str):
        """
        Get a boto3 client for a specific service and region.

        Args:
            service_name: AWS service name (e.g., 's3', 'dynamodb')
            region_name: AWS region name

        Returns:
            boto3 client
        """
        session = self.get_session(region_name)
        return session.client(service_name)
