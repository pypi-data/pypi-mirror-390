"""Worldflow - Quick example runner."""

import asyncio
from uuid import uuid4

from worldflow import workflow, step, sleep, signal, parallel, RetryPolicy
from worldflow.worlds import LocalWorld
from worldflow.runtime import Orchestrator


@step(retries=RetryPolicy(max_attempts=3))
async def greet(name: str) -> str:
    """Greet someone."""
    print(f"👋 Hello, {name}!")
    await asyncio.sleep(0.1)
    return f"Greeted {name}"


@step
async def farewell(name: str) -> str:
    """Say farewell."""
    print(f"👋 Goodbye, {name}!")
    await asyncio.sleep(0.1)
    return f"Said farewell to {name}"


@workflow
async def demo_workflow(name: str):
    """
    A simple demo workflow.
    
    This demonstrates:
    - Step execution
    - Durable sleep
    - Parallel execution
    """
    print(f"\n🌍 Welcome to Worldflow!")
    print(f"   Running demo workflow for: {name}\n")
    
    # Step 1: Greet
    greeting_result = await greet(name)
    print(f"   Result: {greeting_result}\n")
    
    # Step 2: Sleep (durable - would survive restarts!)
    print(f"   Sleeping for 2 seconds...")
    await sleep("2s")
    print(f"   Sleep complete!\n")
    
    # Step 3: Parallel execution
    print(f"   Executing parallel tasks...")
    results = await parallel([
        lambda: greet(f"{name}'s friend 1"),
        lambda: greet(f"{name}'s friend 2"),
    ])
    print(f"   Parallel results: {results}\n")
    
    # Step 4: Farewell
    farewell_result = await farewell(name)
    print(f"   Result: {farewell_result}\n")
    
    print(f"✅ Demo workflow complete!\n")
    
    return {
        "name": name,
        "greeting": greeting_result,
        "farewell": farewell_result,
        "parallel_results": results,
    }


async def main():
    """Run the demo."""
    print("=" * 60)
    print("  WORLDFLOW - Durable Workflow Orchestration for Python")
    print("=" * 60)
    
    # Initialize world and orchestrator
    world = LocalWorld(db_path=".worldflow.db")
    orchestrator = Orchestrator(world)
    
    # Generate run ID
    run_id = f"run_{uuid4().hex[:12]}"
    
    print(f"\nStarting demo workflow...")
    print(f"Run ID: {run_id}\n")
    
    # Start workflow
    await orchestrator.start_workflow(
        run_id,
        demo_workflow,
        {"name": "World"},
        "demo_workflow"
    )
    
    # Wait for completion (in real app, this would be event-driven)
    await asyncio.sleep(4)
    
    # Check status
    status = await world.get_run_status(run_id)
    
    print("=" * 60)
    print(f"Workflow Status: {status['status'].upper()}")
    if status.get('result'):
        print(f"Result: {status['result']}")
    print("=" * 60)
    
    print(f"\n📚 Next steps:")
    print(f"   • Check out examples/ directory for more complex workflows")
    print(f"   • Run 'worldflow dev' to start the web dashboard")
    print(f"   • Run 'worldflow ps' to list workflow runs")
    print(f"   • Run 'worldflow logs {run_id}' to see detailed logs")
    print(f"\n   Read the docs: README.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
