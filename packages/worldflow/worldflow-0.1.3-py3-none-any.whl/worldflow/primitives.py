"""Durable primitives for use within workflows."""

from typing import Any, Callable, Coroutine, TypeVar

from worldflow.runtime import get_current_orchestrator

T = TypeVar("T")


async def sleep(duration: str) -> None:
    """
    Durable sleep: survives restarts.
    
    Args:
        duration: Duration string like "3d", "2h", "30m", "10s"
        
    Usage:
        await sleep("3d")  # Sleep for 3 days
    """
    orchestrator = get_current_orchestrator()
    await orchestrator.sleep(duration)


async def signal(name: str, timeout: str | None = None) -> Any:
    """
    Wait for an external signal/webhook.
    
    Args:
        name: Signal name
        timeout: Optional timeout duration (e.g., "7d")
        
    Returns:
        The signal payload
        
    Usage:
        choice = await signal("user_choice", timeout="7d")
    """
    orchestrator = get_current_orchestrator()
    return await orchestrator.signal(name, timeout)


async def parallel(
    tasks: list[Callable[[], Coroutine[Any, Any, Any]]],
    concurrency: int | None = None,
) -> list[Any]:
    """
    Execute tasks in parallel (fan-out/fan-in).
    
    Args:
        tasks: List of async callables
        concurrency: Optional max concurrency limit
        
    Returns:
        List of results in the same order as tasks
        
    Usage:
        results = await parallel([
            lambda: send_email(user_id, "receipt"),
            lambda: send_email(user_id, "survey"),
        ])
    """
    orchestrator = get_current_orchestrator()
    return await orchestrator.parallel(tasks, concurrency)


def marker(key: str, value: Any) -> None:
    """
    Add a versioning marker for deterministic branching.
    
    Args:
        key: Marker key
        value: Marker value
        
    Usage:
        marker("version", "2025-11-01")
        if marker_value == "2025-11-01":
            # new code path
        else:
            # old code path
    """
    orchestrator = get_current_orchestrator()
    orchestrator.marker(key, value)


def rate_limit(max_in_flight: int) -> int:
    """
    Create a concurrency limit for parallel execution.
    
    Args:
        max_in_flight: Maximum concurrent tasks
        
    Returns:
        Concurrency limit value
        
    Usage:
        await parallel(tasks, concurrency=rate_limit(50))
    """
    return max_in_flight

