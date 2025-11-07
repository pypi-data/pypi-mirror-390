"""Decorators for defining workflows and steps."""

import functools
import inspect
from typing import Any, Callable, Coroutine, TypeVar, cast

from worldflow.retry import RetryPolicy, STANDARD_RETRY
from worldflow.runtime import get_current_orchestrator

T = TypeVar("T")

# Global registry of workflows
_workflow_registry: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}

# Global registry of steps (for execution)
_step_registry: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}


def workflow(
    fn: Callable[..., Coroutine[Any, Any, T]] | None = None,
    *,
    name: str | None = None,
) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorator to mark a function as a workflow.
    
    Workflows are orchestration-only: no side effects, deterministic.
    
    Usage:
        @workflow
        async def my_workflow(user_id: str):
            await send_email(user_id, "welcome")
            await sleep("3d")
            ...
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        workflow_name = name or func.__name__
        
        # Verify it's async
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Workflow {workflow_name} must be an async function")
        
        # Register workflow
        _workflow_registry[workflow_name] = func
        
        # Add metadata
        func.__worldflow_workflow__ = True  # type: ignore
        func.__worldflow_workflow_name__ = workflow_name  # type: ignore
        
        return func

    if fn is None:
        # Called with arguments: @workflow(name="...")
        return decorator
    else:
        # Called without arguments: @workflow
        return decorator(fn)


def step(
    fn: Callable[..., Coroutine[Any, Any, T]] | None = None,
    *,
    retries: RetryPolicy | None = None,
    name: str | None = None,
    unique_on: list[str] | None = None,
) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorator to mark a function as a step.
    
    Steps are where side effects happen. They should be idempotent or use
    the provided idempotency keys.
    
    Usage:
        @step(retries=RetryPolicy(max_attempts=3))
        async def charge_card(user_id: str, amount_cents: int) -> str:
            # do side effects here
            ...
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        step_name = name or f"{func.__module__}.{func.__qualname__}"
        retry_policy = retries or STANDARD_RETRY
        
        # Verify it's async
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Step {step_name} must be an async function")
        
        # Register step
        _step_registry[step_name] = func
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # When called from within a workflow, go through orchestrator
            try:
                orchestrator = get_current_orchestrator()
                return await orchestrator.execute_step(func, args, kwargs, retry_policy)
            except RuntimeError:
                # Not in workflow context; execute directly (useful for testing)
                return await func(*args, **kwargs)
        
        # Add metadata
        wrapper.__worldflow_step__ = True  # type: ignore
        wrapper.__worldflow_step_name__ = step_name  # type: ignore
        wrapper.__worldflow_retry_policy__ = retry_policy  # type: ignore
        wrapper.__worldflow_original_fn__ = func  # type: ignore
        
        return cast(Callable[..., Coroutine[Any, Any, T]], wrapper)

    if fn is None:
        # Called with arguments: @step(retries=...)
        return decorator
    else:
        # Called without arguments: @step
        return decorator(fn)


def get_step_function(step_name: str) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Get a step function by name from the registry."""
    if step_name in _step_registry:
        return _step_registry[step_name]
    
    # Try to import it dynamically
    parts = step_name.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid step name: {step_name}")
    
    module_name, func_name = parts
    try:
        import importlib
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        
        # Get original function if it's wrapped
        if hasattr(func, "__worldflow_original_fn__"):
            return func.__worldflow_original_fn__
        return func
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Step {step_name} not found: {e}")


def get_workflow_function(workflow_name: str) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Get a workflow function by name from the registry."""
    if workflow_name not in _workflow_registry:
        raise ValueError(f"Workflow {workflow_name} not found in registry")
    return _workflow_registry[workflow_name]

