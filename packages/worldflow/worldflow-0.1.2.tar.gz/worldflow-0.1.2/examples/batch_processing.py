"""Example: Batch processing with parallel execution."""

from worldflow import workflow, step, parallel, rate_limit, RetryPolicy


@step(retries=RetryPolicy(max_attempts=3))
async def process_item(item_id: str) -> dict:
    """Process a single item."""
    print(f"⚙️  Processing item {item_id}")
    import asyncio
    await asyncio.sleep(0.1)
    
    # Simulate some processing
    result = {
        "item_id": item_id,
        "status": "processed",
        "score": len(item_id) * 10,
    }
    
    print(f"✅ Completed item {item_id}: score={result['score']}")
    return result


@step
async def aggregate_results(results: list[dict]) -> dict:
    """Aggregate processing results."""
    print(f"📊 Aggregating {len(results)} results")
    
    total_score = sum(r["score"] for r in results)
    avg_score = total_score / len(results) if results else 0
    
    summary = {
        "total_items": len(results),
        "total_score": total_score,
        "average_score": avg_score,
    }
    
    print(f"✅ Aggregation complete: {summary}")
    return summary


@workflow
async def batch_processing(item_ids: list[str], max_concurrency: int = 10):
    """
    Process a batch of items in parallel with bounded concurrency.
    
    Args:
        item_ids: List of item IDs to process
        max_concurrency: Maximum number of items to process concurrently
    """
    print(f"🚀 Starting batch processing: {len(item_ids)} items")
    print(f"   Max concurrency: {max_concurrency}")
    
    # Process all items in parallel with rate limiting
    results = await parallel(
        [lambda item_id=item_id: process_item(item_id) for item_id in item_ids],
        concurrency=rate_limit(max_concurrency)
    )
    
    # Aggregate results
    summary = await aggregate_results(results)
    
    print(f"🎉 Batch processing complete!")
    return summary


if __name__ == "__main__":
    import asyncio
    from uuid import uuid4
    from worldflow.worlds import LocalWorld
    from worldflow.runtime import Orchestrator
    
    async def main():
        world = LocalWorld()
        orchestrator = Orchestrator(world)
        
        # Create a batch of items
        item_ids = [f"item_{i:03d}" for i in range(20)]
        
        run_id = f"run_{uuid4().hex[:12]}"
        print(f"Starting workflow with run_id: {run_id}\n")
        
        await orchestrator.start_workflow(
            run_id,
            batch_processing,
            {"item_ids": item_ids, "max_concurrency": 5},
            "batch_processing"
        )
        
        # Wait for completion
        await asyncio.sleep(3)
        
        # Check status
        status = await world.get_run_status(run_id)
        print(f"\nWorkflow status: {status['status']}")
        if status.get('result'):
            print(f"Result: {status['result']}")
    
    asyncio.run(main())

