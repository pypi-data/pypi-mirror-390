"""Example: Running Worldflow on AWS with AWSWorld."""

import asyncio
import os
from uuid import uuid4

# Set environment variables (in production, these would be set in Lambda/ECS)
os.environ.setdefault("WORLDFLOW_EVENTS_TABLE", "worldflow-events")
os.environ.setdefault("WORLDFLOW_RUNS_TABLE", "worldflow-runs")
os.environ.setdefault("WORLDFLOW_STEP_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789/worldflow-steps.fifo")
os.environ.setdefault("WORLDFLOW_ORCHESTRATOR_FUNCTION", "worldflow-orchestrator")
os.environ.setdefault("AWS_REGION", "us-east-1")

from worldflow import workflow, step, sleep, parallel, RetryPolicy


@step(retries=RetryPolicy(max_attempts=5, backoff="exponential"))
async def process_order(order_id: str) -> dict:
    """
    Process an order (calls external API, database, etc.).
    
    In production, this might:
    - Call payment gateway
    - Update inventory
    - Send to fulfillment system
    """
    print(f"💳 Processing order {order_id}")
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    result = {
        "order_id": order_id,
        "status": "processed",
        "amount": 99.99,
        "timestamp": "2025-11-06T12:00:00Z"
    }
    
    print(f"✅ Order {order_id} processed")
    return result


@step
async def send_notification(order_id: str, notification_type: str) -> None:
    """Send notification (email, SMS, push, etc.)."""
    print(f"📧 Sending {notification_type} notification for order {order_id}")
    await asyncio.sleep(0.05)
    print(f"✅ Notification sent")


@step
async def update_analytics(order_data: dict) -> None:
    """Update analytics/reporting systems."""
    print(f"📊 Updating analytics for order {order_data['order_id']}")
    await asyncio.sleep(0.05)
    print(f"✅ Analytics updated")


@workflow
async def order_fulfillment_workflow(order_id: str, customer_email: str):
    """
    Complete order fulfillment workflow.
    
    This workflow demonstrates:
    1. Order processing with retries
    2. Parallel notifications
    3. Durable sleep (reminder after 7 days)
    4. Analytics tracking
    
    In production on AWS:
    - Orchestrator runs in Lambda (triggered by events)
    - Steps run in separate Lambda invocations (from SQS)
    - Events stored in DynamoDB
    - Timers scheduled via EventBridge
    - Survives any Lambda cold starts or failures!
    """
    print(f"\n🚀 Starting order fulfillment for {order_id}")
    
    # Step 1: Process the order
    order_data = await process_order(order_id)
    
    # Step 2: Send immediate notifications in parallel
    print(f"\n📬 Sending immediate notifications...")
    await parallel([
        lambda: send_notification(order_id, "order_confirmation"),
        lambda: send_notification(order_id, "receipt"),
        lambda: update_analytics(order_data),
    ])
    
    # Step 3: Wait 7 days for review reminder (durable - survives restarts!)
    print(f"\n⏰ Scheduling review reminder for 7 days...")
    print(f"   (In demo, sleeping 5 seconds instead)")
    await sleep("5s")  # In production: "7d"
    
    print(f"\n⏰ 7 days passed! Sending review reminder...")
    
    # Step 4: Send review reminder
    await send_notification(order_id, "review_reminder")
    
    print(f"\n🎉 Order fulfillment workflow complete!")
    
    return {
        "order_id": order_id,
        "customer_email": customer_email,
        "order_data": order_data,
        "status": "completed"
    }


async def run_local_demo():
    """
    Run workflow locally for testing.
    
    This uses LocalWorld (SQLite) instead of AWS.
    Once you deploy to AWS, the same workflow code runs there!
    """
    print("=" * 70)
    print("  WORLDFLOW AWS DEMO (Running Locally)")
    print("=" * 70)
    print()
    print("This workflow is AWS-ready! Deploy with:")
    print("  1. Set up AWS infrastructure: python -m worldflow.aws_setup setup")
    print("  2. Deploy Lambda functions (see AWS_DEPLOYMENT.md)")
    print("  3. Run the same code in Lambda - it just works!")
    print()
    print("=" * 70)
    print()
    
    # For local testing, use LocalWorld
    from worldflow.worlds import LocalWorld
    from worldflow.runtime import Orchestrator
    
    world = LocalWorld()
    orchestrator = Orchestrator(world)
    
    run_id = f"order_{uuid4().hex[:12]}"
    
    print(f"Starting workflow with run_id: {run_id}\n")
    
    await orchestrator.start_workflow(
        run_id,
        order_fulfillment_workflow,
        {
            "order_id": "ORD-2025-001",
            "customer_email": "customer@example.com"
        },
        "order_fulfillment_workflow"
    )
    
    # Wait for workflow to complete
    await asyncio.sleep(7)
    
    # Check status
    status = await world.get_run_status(run_id)
    
    print()
    print("=" * 70)
    print(f"Workflow Status: {status['status'].upper()}")
    if status.get('result'):
        print(f"Result: {status['result']}")
    print("=" * 70)
    print()
    
    print("📚 Next Steps:")
    print("  • Read AWS_DEPLOYMENT.md for AWS deployment guide")
    print("  • Set up AWS infrastructure")
    print("  • Deploy to Lambda")
    print("  • Same code, production-ready!")
    print()


async def run_on_aws():
    """
    Run workflow on AWS (after deployment).
    
    Make sure you've:
    1. Set up AWS infrastructure (DynamoDB, SQS, Lambda)
    2. Set environment variables
    3. Deployed your workflow code to Lambda
    """
    from worldflow.worlds import AWSWorld
    from worldflow.runtime import Orchestrator
    
    # AWSWorld reads configuration from environment variables
    world = AWSWorld()
    orchestrator = Orchestrator(world)
    
    run_id = f"order_{uuid4().hex[:12]}"
    
    print(f"🚀 Starting workflow on AWS: {run_id}")
    
    await orchestrator.start_workflow(
        run_id,
        order_fulfillment_workflow,
        {
            "order_id": "ORD-2025-001",
            "customer_email": "customer@example.com"
        },
        "order_fulfillment_workflow"
    )
    
    print(f"✅ Workflow started! Run ID: {run_id}")
    print(f"   Check status: worldflow logs {run_id}")


if __name__ == "__main__":
    # Run local demo by default
    # To run on AWS: uncomment run_on_aws() and set environment variables
    asyncio.run(run_local_demo())
    
    # For AWS:
    # asyncio.run(run_on_aws())

