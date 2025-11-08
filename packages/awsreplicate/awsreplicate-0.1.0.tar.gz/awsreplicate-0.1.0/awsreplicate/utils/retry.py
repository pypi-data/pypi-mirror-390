"""Retry utilities with tenacity."""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from botocore.exceptions import ClientError, BotoCoreError
import structlog

logger = structlog.get_logger(__name__)


def get_retry_decorator(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 10):
    """
    Get a retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)

    Returns:
        Retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((ClientError, BotoCoreError, ConnectionError)),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying after error",
            attempt=retry_state.attempt_number,
            error=str(retry_state.outcome.exception()),
        ),
    )
