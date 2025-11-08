"""Concurrency control utilities."""

import asyncio
from typing import Optional


class Semaphore:
    """Async semaphore wrapper for controlling concurrency."""

    def __init__(self, max_concurrent: int):
        """
        Initialize semaphore.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        """Acquire semaphore."""
        await self._semaphore.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release semaphore."""
        self._semaphore.release()
