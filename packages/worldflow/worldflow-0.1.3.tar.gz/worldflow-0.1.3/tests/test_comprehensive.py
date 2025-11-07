"""Comprehensive test suite for Worldflow core functionality."""
import asyncio
import tempfile
from pathlib import Path

from worldflow import workflow, step, sleep, parallel, RetryPolicy
from worldflow.worlds import LocalWorld
from worldflow.runtime import Orchestrator


# Test 1: Basic workflow
@step
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@workflow
async def basic_workflow(x: int, y: int):
    """Simple addition workflow."""
    result = await add(x, y)
    return result


# Test 2: Multi-step workflow
@step
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@step
async def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

@workflow
async def multi_step_workflow(a: int, b: int, c: int):
    """Complex calculation: (a * b) - c."""
    product = await multiply(a, b)
    result = await subtract(product, c)
    return result


# Test 3: Parallel execution
@step
async def slow_double(x: int) -> int:
    """Double a number slowly."""
    await asyncio.sleep(0.1)
    return x * 2

@workflow
async def parallel_workflow(nums: list[int]):
    """Double numbers in parallel."""
    results = await parallel([
        lambda n=n: slow_double(n) for n in nums
    ])
    return sum(results)


# Test 4: Retry on failure
failure_count = {}

@step(retries=RetryPolicy(max_attempts=3))
async def flaky_operation(op_id: str) -> str:
    """Operation that fails twice then succeeds."""
    if op_id not in failure_count:
        failure_count[op_id] = 0
    
    failure_count[op_id] += 1
    
    if failure_count[op_id] < 3:
        raise ValueError(f"Attempt {failure_count[op_id]} failed")
    
    return f"Success after {failure_count[op_id]} attempts"

@workflow
async def retry_workflow(op_id: str):
    """Test retry logic."""
    result = await flaky_operation(op_id)
    return result


# Test 5: Sleep functionality
@step
async def get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return datetime.utcnow().isoformat()

@workflow
async def sleep_workflow():
    """Test durable sleep."""
    time1 = await get_time()
    await sleep("1s")
    time2 = await get_time()
    return {"before": time1, "after": time2}


# Test runner
async def run_test(name: str, test_func, world_type: str):
    """Run a single test."""
    print(f"\n{'='*60}")
    print(f"TEST: {name} ({world_type})")
    print('='*60)
    
    try:
        result = await test_func(world_type)
        print(f"✅ PASSED: {result}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic(world_type: str):
    """Test basic workflow execution."""
    if world_type == "memory":
        world = LocalWorld(":memory:")
    else:
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        world = LocalWorld(temp.name)
    
    orchestrator = Orchestrator(world)
    
    await orchestrator.start_workflow(
        f"test_basic_{world_type}",
        basic_workflow,
        {"x": 5, "y": 3},
        "basic_workflow"
    )
    
    await asyncio.sleep(1)
    status = await world.get_run_status(f"test_basic_{world_type}")
    
    assert status["status"] == "completed", f"Expected completed, got {status['status']}"
    assert status["result"] == 8, f"Expected 8, got {status['result']}"
    
    return f"5 + 3 = {status['result']}"


async def test_multi_step(world_type: str):
    """Test multi-step workflow."""
    if world_type == "memory":
        world = LocalWorld(":memory:")
    else:
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        world = LocalWorld(temp.name)
    
    orchestrator = Orchestrator(world)
    
    await orchestrator.start_workflow(
        f"test_multi_{world_type}",
        multi_step_workflow,
        {"a": 4, "b": 5, "c": 3},
        "multi_step_workflow"
    )
    
    await asyncio.sleep(1)
    status = await world.get_run_status(f"test_multi_{world_type}")
    
    assert status["status"] == "completed", f"Expected completed, got {status['status']}"
    assert status["result"] == 17, f"Expected 17, got {status['result']}"
    
    return f"(4 * 5) - 3 = {status['result']}"


async def test_parallel(world_type: str):
    """Test parallel execution."""
    if world_type == "memory":
        world = LocalWorld(":memory:")
    else:
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        world = LocalWorld(temp.name)
    
    orchestrator = Orchestrator(world)
    
    await orchestrator.start_workflow(
        f"test_parallel_{world_type}",
        parallel_workflow,
        {"nums": [1, 2, 3, 4, 5]},
        "parallel_workflow"
    )
    
    await asyncio.sleep(2)
    status = await world.get_run_status(f"test_parallel_{world_type}")
    
    assert status["status"] == "completed", f"Expected completed, got {status['status']}"
    # Sum of [2, 4, 6, 8, 10] = 30
    assert status["result"] == 30, f"Expected 30, got {status['result']}"
    
    return f"Parallel sum: {status['result']}"


async def test_retry(world_type: str):
    """Test retry logic."""
    if world_type == "memory":
        world = LocalWorld(":memory:")
    else:
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        world = LocalWorld(temp.name)
    
    orchestrator = Orchestrator(world)
    
    op_id = f"op_{world_type}"
    failure_count[op_id] = 0  # Reset counter
    
    await orchestrator.start_workflow(
        f"test_retry_{world_type}",
        retry_workflow,
        {"op_id": op_id},
        "retry_workflow"
    )
    
    # Retries need more time (3 attempts with backoff)
    await asyncio.sleep(5)
    status = await world.get_run_status(f"test_retry_{world_type}")
    
    assert status["status"] == "completed", f"Expected completed, got {status['status']}"
    assert "Success after 3 attempts" in status["result"], f"Unexpected result: {status['result']}"
    
    return status["result"]


async def test_sleep(world_type: str):
    """Test sleep functionality."""
    if world_type == "memory":
        world = LocalWorld(":memory:")
    else:
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        world = LocalWorld(temp.name)
    
    orchestrator = Orchestrator(world)
    
    await orchestrator.start_workflow(
        f"test_sleep_{world_type}",
        sleep_workflow,
        {},
        "sleep_workflow"
    )
    
    await asyncio.sleep(3)
    status = await world.get_run_status(f"test_sleep_{world_type}")
    
    assert status["status"] == "completed", f"Expected completed, got {status['status']}"
    assert "before" in status["result"], "Missing 'before' timestamp"
    assert "after" in status["result"], "Missing 'after' timestamp"
    
    return f"Sleep completed: {status['result']['before'][:19]} -> {status['result']['after'][:19]}"


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 WORLDFLOW COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Basic Workflow", test_basic),
        ("Multi-Step Workflow", test_multi_step),
        ("Parallel Execution", test_parallel),
        ("Retry Logic", test_retry),
        ("Sleep/Timer", test_sleep),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        # Test with :memory:
        passed = await run_test(f"{test_name}", test_func, "memory")
        results.append((f"{test_name} (:memory:)", passed))
        
        # Test with file-based DB
        passed = await run_test(f"{test_name}", test_func, "file")
        results.append((f"{test_name} (file)", passed))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"Result: {passed_count}/{total_count} tests passed")
    print("="*60)
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

