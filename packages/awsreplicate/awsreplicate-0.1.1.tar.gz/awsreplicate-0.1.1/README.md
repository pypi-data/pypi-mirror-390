# awsreplicate

A lightweight Python SDK for cross-region data replication in AWS.

## Features

- Async S3 bucket replication using `aioboto3`
- DynamoDB table replication between regions
- Concurrent operations with configurable limits
- Automatic retry logic with exponential backoff
- Structured logging with `structlog`
- Comprehensive test coverage with `moto`

## Installation

```bash
pip install awsreplicate
```

For development:

```bash
pip install awsreplicate[dev]
```

## Quick Start

```python
import asyncio
from awsreplicate import AWSConfig, S3Replicator

async def main():
    # Configure AWS
    config = AWSConfig()
    
    # Create replicator
    replicator = S3Replicator(
        config=config,
        source_region="us-east-1",
        target_region="us-west-1",
        max_concurrent=20
    )
    
    # Replicate bucket
    result = await replicator.replicate_bucket(
        source_bucket="my-source-bucket",
        target_bucket="my-target-bucket"
    )
    
    print(f"Replicated {result['successful']} objects")

asyncio.run(main())
```

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black awsreplicate tests

# Lint
ruff check awsreplicate tests
```

## License

MIT License
