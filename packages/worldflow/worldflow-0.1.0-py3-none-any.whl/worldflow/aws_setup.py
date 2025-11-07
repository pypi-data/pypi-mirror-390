"""AWS infrastructure setup utilities."""

import json
from typing import Any

try:
    import boto3
except ImportError:
    boto3 = None  # type: ignore


def create_dynamodb_tables(
    events_table_name: str = "worldflow-events",
    runs_table_name: str = "worldflow-runs",
    region: str = "us-east-1",
) -> dict[str, Any]:
    """
    Create DynamoDB tables for Worldflow.
    
    Args:
        events_table_name: Name for events table
        runs_table_name: Name for runs table
        region: AWS region
        
    Returns:
        Dictionary with table ARNs
    """
    if boto3 is None:
        raise ImportError('Install AWS dependencies: pip install "worldflow[aws]"')

    dynamodb = boto3.client("dynamodb", region_name=region)

    # Create events table
    events_table = dynamodb.create_table(
        TableName=events_table_name,
        KeySchema=[
            {"AttributeName": "run_id", "KeyType": "HASH"},  # Partition key
            {"AttributeName": "event_idx", "KeyType": "RANGE"},  # Sort key
        ],
        AttributeDefinitions=[
            {"AttributeName": "run_id", "AttributeType": "S"},
            {"AttributeName": "event_idx", "AttributeType": "N"},
        ],
        BillingMode="PAY_PER_REQUEST",  # On-demand pricing
        Tags=[
            {"Key": "Application", "Value": "Worldflow"},
        ],
    )

    # Create runs table
    runs_table = dynamodb.create_table(
        TableName=runs_table_name,
        KeySchema=[
            {"AttributeName": "run_id", "KeyType": "HASH"},  # Partition key
        ],
        AttributeDefinitions=[
            {"AttributeName": "run_id", "AttributeType": "S"},
            {"AttributeName": "workflow_name", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "workflow-status-index",
                "KeySchema": [
                    {"AttributeName": "workflow_name", "KeyType": "HASH"},
                    {"AttributeName": "status", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
        Tags=[
            {"Key": "Application", "Value": "Worldflow"},
        ],
    )

    print(f"✅ Created table: {events_table_name}")
    print(f"✅ Created table: {runs_table_name}")

    return {
        "events_table_arn": events_table["TableDescription"]["TableArn"],
        "runs_table_arn": runs_table["TableDescription"]["TableArn"],
    }


def create_sqs_queue(
    queue_name: str = "worldflow-steps.fifo",
    region: str = "us-east-1",
    fifo: bool = True,
) -> dict[str, str]:
    """
    Create SQS queue for step execution.
    
    Args:
        queue_name: Queue name
        region: AWS region
        fifo: Whether to create FIFO queue
        
    Returns:
        Dictionary with queue URL and ARN
    """
    if boto3 is None:
        raise ImportError('Install AWS dependencies: pip install "worldflow[aws]"')

    sqs = boto3.client("sqs", region_name=region)

    attributes = {
        "VisibilityTimeout": "300",  # 5 minutes
        "MessageRetentionPeriod": "1209600",  # 14 days
    }

    if fifo:
        attributes["FifoQueue"] = "true"
        attributes["ContentBasedDeduplication"] = "false"  # We provide explicit dedup IDs
        if not queue_name.endswith(".fifo"):
            queue_name += ".fifo"

    response = sqs.create_queue(QueueName=queue_name, Attributes=attributes)

    queue_url = response["QueueUrl"]

    # Get queue ARN
    attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
    queue_arn = attrs["Attributes"]["QueueArn"]

    print(f"✅ Created queue: {queue_name}")
    print(f"   URL: {queue_url}")

    return {"queue_url": queue_url, "queue_arn": queue_arn}


def setup_worldflow_infrastructure(
    region: str = "us-east-1",
    events_table: str = "worldflow-events",
    runs_table: str = "worldflow-runs",
    step_queue: str = "worldflow-steps.fifo",
) -> dict[str, Any]:
    """
    Set up complete Worldflow infrastructure on AWS.
    
    This creates:
    - DynamoDB tables (events, runs)
    - SQS queue (steps)
    
    Args:
        region: AWS region
        events_table: Events table name
        runs_table: Runs table name
        step_queue: Step queue name
        
    Returns:
        Dictionary with all resource ARNs and URLs
    """
    print(f"🚀 Setting up Worldflow infrastructure in {region}...")
    print()

    # Create tables
    print("📊 Creating DynamoDB tables...")
    tables = create_dynamodb_tables(events_table, runs_table, region)
    print()

    # Create queue
    print("📬 Creating SQS queue...")
    queue = create_sqs_queue(step_queue, region)
    print()

    resources = {
        **tables,
        **queue,
        "region": region,
    }

    print("✅ Infrastructure setup complete!")
    print()
    print("📝 Configuration:")
    print(f"   Region: {region}")
    print(f"   Events Table: {events_table}")
    print(f"   Runs Table: {runs_table}")
    print(f"   Step Queue: {step_queue}")
    print()
    print("🔧 Environment variables for your Lambda:")
    print(f'   WORLDFLOW_EVENTS_TABLE="{events_table}"')
    print(f'   WORLDFLOW_RUNS_TABLE="{runs_table}"')
    print(f'   WORLDFLOW_STEP_QUEUE_URL="{queue["queue_url"]}"')
    print(f'   AWS_REGION="{region}"')
    print()

    return resources


def cleanup_worldflow_infrastructure(
    region: str = "us-east-1",
    events_table: str = "worldflow-events",
    runs_table: str = "worldflow-runs",
    step_queue: str = "worldflow-steps.fifo",
) -> None:
    """
    Clean up Worldflow infrastructure.
    
    WARNING: This deletes all tables and queues. Data will be lost!
    """
    if boto3 is None:
        raise ImportError('Install AWS dependencies: pip install "worldflow[aws]"')

    print("⚠️  WARNING: This will delete all Worldflow resources!")
    print(f"   Region: {region}")
    print(f"   Tables: {events_table}, {runs_table}")
    print(f"   Queue: {step_queue}")
    print()

    confirm = input("Type 'DELETE' to confirm: ")
    if confirm != "DELETE":
        print("Cancelled.")
        return

    dynamodb = boto3.client("dynamodb", region_name=region)
    sqs = boto3.client("sqs", region_name=region)

    # Delete tables
    try:
        dynamodb.delete_table(TableName=events_table)
        print(f"✅ Deleted table: {events_table}")
    except Exception as e:
        print(f"⚠️  Failed to delete {events_table}: {e}")

    try:
        dynamodb.delete_table(TableName=runs_table)
        print(f"✅ Deleted table: {runs_table}")
    except Exception as e:
        print(f"⚠️  Failed to delete {runs_table}: {e}")

    # Delete queue
    try:
        # Get queue URL first
        response = sqs.get_queue_url(QueueName=step_queue)
        queue_url = response["QueueUrl"]
        sqs.delete_queue(QueueUrl=queue_url)
        print(f"✅ Deleted queue: {step_queue}")
    except Exception as e:
        print(f"⚠️  Failed to delete {step_queue}: {e}")

    print()
    print("✅ Cleanup complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_worldflow_infrastructure()
    elif len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_worldflow_infrastructure()
    else:
        print("Usage:")
        print("  python -m worldflow.aws_setup setup   # Create infrastructure")
        print("  python -m worldflow.aws_setup cleanup # Delete infrastructure")

