"""Basic tests for Worldflow."""

import asyncio
import pytest
from uuid import uuid4

from worldflow import workflow, step, sleep, parallel, RetryPolicy
from worldflow.worlds import LocalWorld
from worldflow.runtime import Orchestrator


@step
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@step
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@workflow
async def simple_workflow(x: int, y: int) -> int:
    """A simple workflow that adds and multiplies."""
    sum_result = await add(x, y)
    product_result = await multiply(sum_result, 2)
    return product_result


@workflow
async def sleep_workflow() -> str:
    """Workflow with sleep."""
    await sleep("1s")
    return "slept"


@workflow
async def parallel_workflow() -> list[int]:
    """Workflow with parallel execution."""
    results = await parallel([
        lambda: add(1, 2),
        lambda: add(3, 4),
        lambda: add(5, 6),
    ])
    return results


@pytest.mark.asyncio
async def test_simple_workflow():
    """Test a simple workflow execution."""
    world = LocalWorld(db_path=f".test_{uuid4().hex[:8]}.db")
    orchestrator = Orchestrator(world)
    
    run_id = f"test_{uuid4().hex[:8]}"
    
    # Start workflow
    await orchestrator.start_workflow(
        run_id,
        simple_workflow,
        {"x": 5, "y": 3},
        "simple_workflow"
    )
    
    # Wait for completion
    await asyncio.sleep(1)
    
    # Check result
    status = await world.get_run_status(run_id)
    assert status["status"] == "completed"
    assert status["result"] == 16  # (5 + 3) * 2


@pytest.mark.asyncio
async def test_workflow_with_sleep():
    """Test workflow with durable sleep."""
    world = LocalWorld(db_path=f".test_{uuid4().hex[:8]}.db")
    orchestrator = Orchestrator(world)
    
    run_id = f"test_{uuid4().hex[:8]}"
    
    # Start workflow
    await orchestrator.start_workflow(
        run_id,
        sleep_workflow,
        {},
        "sleep_workflow"
    )
    
    # Wait for completion
    await asyncio.sleep(2)
    
    # Check result
    status = await world.get_run_status(run_id)
    assert status["status"] == "completed"
    assert status["result"] == "slept"


@pytest.mark.asyncio
async def test_parallel_workflow():
    """Test workflow with parallel execution."""
    world = LocalWorld(db_path=f".test_{uuid4().hex[:8]}.db")
    orchestrator = Orchestrator(world)
    
    run_id = f"test_{uuid4().hex[:8]}"
    
    # Start workflow
    await orchestrator.start_workflow(
        run_id,
        parallel_workflow,
        {},
        "parallel_workflow"
    )
    
    # Wait for completion
    await asyncio.sleep(1)
    
    # Check result
    status = await world.get_run_status(run_id)
    assert status["status"] == "completed"
    assert status["result"] == [3, 7, 11]


@pytest.mark.asyncio
async def test_workflow_listing():
    """Test listing workflows."""
    world = LocalWorld(db_path=f".test_{uuid4().hex[:8]}.db")
    orchestrator = Orchestrator(world)
    
    # Start multiple workflows
    for i in range(3):
        run_id = f"test_{uuid4().hex[:8]}"
        await orchestrator.start_workflow(
            run_id,
            simple_workflow,
            {"x": i, "y": i + 1},
            "simple_workflow"
        )
    
    await asyncio.sleep(1)
    
    # List workflows
    runs = await world.list_runs(workflow_name="simple_workflow")
    assert len(runs) >= 3


@pytest.mark.asyncio
async def test_event_log():
    """Test event log persistence."""
    world = LocalWorld(db_path=f".test_{uuid4().hex[:8]}.db")
    orchestrator = Orchestrator(world)
    
    run_id = f"test_{uuid4().hex[:8]}"
    
    # Start workflow
    await orchestrator.start_workflow(
        run_id,
        simple_workflow,
        {"x": 2, "y": 3},
        "simple_workflow"
    )
    
    await asyncio.sleep(1)
    
    # Load events
    events = await world.load_events(run_id)
    
    # Should have: WorkflowStarted, 2x StepScheduled, 2x StepCompleted, WorkflowCompleted
    assert len(events) >= 5
    
    # Check event types
    event_types = [e.event_type.value for e in events]
    assert "workflow_started" in event_types
    assert "step_scheduled" in event_types
    assert "step_completed" in event_types
    assert "workflow_completed" in event_types

