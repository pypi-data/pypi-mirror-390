"""Core runtime: orchestrator, replay mechanism, and execution context."""

import asyncio
import contextvars
import hashlib
import inspect
import json
import traceback
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, TypeVar
from uuid import uuid4

from worldflow.events import (
    Event,
    EventType,
    StepScheduledEvent,
    StepCompletedEvent,
    StepFailedEvent,
    TimerScheduledEvent,
    TimerFiredEvent,
    SignalRequestedEvent,
    SignalReceivedEvent,
    ParallelStartedEvent,
    ParallelCompletedEvent,
    WorkflowStartedEvent,
    WorkflowCompletedEvent,
    WorkflowFailedEvent,
    MarkerEvent,
)
from worldflow.retry import RetryPolicy
from worldflow.world import World

T = TypeVar("T")

# Context vars for accessing runtime state from within workflows
_current_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "_current_run_id", default=None
)
_current_world: contextvars.ContextVar[World | None] = contextvars.ContextVar(
    "_current_world", default=None
)
_current_orchestrator: contextvars.ContextVar["Orchestrator | None"] = contextvars.ContextVar(
    "_current_orchestrator", default=None
)


def get_current_run_id() -> str:
    """Get the current workflow run ID."""
    run_id = _current_run_id.get()
    if run_id is None:
        raise RuntimeError("Not executing within a workflow context")
    return run_id


def get_current_world() -> World:
    """Get the current World backend."""
    world = _current_world.get()
    if world is None:
        raise RuntimeError("Not executing within a workflow context")
    return world


def get_current_orchestrator() -> "Orchestrator":
    """Get the current orchestrator instance."""
    orch = _current_orchestrator.get()
    if orch is None:
        raise RuntimeError("Not executing within a workflow context")
    return orch


class WorkflowSuspended(Exception):
    """Raised when workflow needs to suspend (waiting for step/timer/signal)."""

    pass


class Orchestrator:
    """
    The orchestrator executes workflows via deterministic replay.
    
    It loads the event log, replays the workflow function, and when it
    encounters a primitive (step, sleep, signal), it either:
    - Returns the recorded result (if event exists in history)
    - Schedules the operation and suspends (if event doesn't exist)
    """

    def __init__(self, world: World):
        self.world = world
        self.events: list[Event] = []
        self.event_index = 0
        
        # Counters for deterministic IDs
        self.step_counter = 0
        self.timer_counter = 0
        self.signal_counter = 0
        self.parallel_counter = 0
        self.marker_counter = 0

    async def start_workflow(
        self,
        run_id: str,
        workflow_fn: Callable[..., Coroutine[Any, Any, T]],
        inputs: dict[str, Any],
        workflow_name: str | None = None,
    ) -> str:
        """Start a new workflow execution."""
        if workflow_name is None:
            workflow_name = workflow_fn.__name__

        # Create run
        await self.world.create_run(run_id, workflow_name, inputs)

        # Append WorkflowStarted event
        event = WorkflowStartedEvent(
            event_id=self._gen_event_id(),
            run_id=run_id,
            payload={"workflow_name": workflow_name, "inputs": inputs},
        )
        await self.world.append_events(run_id, [event])

        # Trigger orchestrator
        await self.world.invoke_orchestrator(run_id)
        
        return run_id

    async def run_orchestrator(self, run_id: str) -> None:
        """
        Execute the orchestrator: load events, replay workflow, advance state.
        """
        # Load events
        self.events = await self.world.load_events(run_id)
        self.event_index = 0
        
        # Reset counters
        self.step_counter = 0
        self.timer_counter = 0
        self.signal_counter = 0
        self.parallel_counter = 0
        self.marker_counter = 0
        
        # Find WorkflowStarted event
        workflow_started = next(
            (e for e in self.events if e.event_type == EventType.WORKFLOW_STARTED), None
        )
        if not workflow_started:
            raise ValueError(f"No WorkflowStarted event found for run {run_id}")

        workflow_name = workflow_started.payload["workflow_name"]
        inputs = workflow_started.payload["inputs"]

        # Check if workflow already completed/failed
        terminal_event = next(
            (
                e
                for e in self.events
                if e.event_type in (EventType.WORKFLOW_COMPLETED, EventType.WORKFLOW_FAILED)
            ),
            None,
        )
        if terminal_event:
            # Workflow already done
            return

        # Get workflow function (this is simplified; real impl would use registry)
        from worldflow.decorators import _workflow_registry

        workflow_fn = _workflow_registry.get(workflow_name)
        if not workflow_fn:
            raise ValueError(f"Workflow {workflow_name} not found in registry")

        # Set context vars
        token_run = _current_run_id.set(run_id)
        token_world = _current_world.set(self.world)
        token_orch = _current_orchestrator.set(self)

        try:
            # Execute workflow function via replay
            result = await workflow_fn(**inputs)
            
            # Workflow completed successfully
            event = WorkflowCompletedEvent(
                event_id=self._gen_event_id(),
                run_id=run_id,
                payload={"result": self._serialize(result)},
            )
            await self.world.append_events(run_id, [event])

        except WorkflowSuspended:
            # Normal: workflow is waiting for something
            pass
        except Exception as e:
            # Workflow failed
            event = WorkflowFailedEvent(
                event_id=self._gen_event_id(),
                run_id=run_id,
                payload={
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            await self.world.append_events(run_id, [event])
        finally:
            _current_run_id.reset(token_run)
            _current_world.reset(token_world)
            _current_orchestrator.reset(token_orch)

    def _gen_event_id(self) -> str:
        """Generate a unique event ID."""
        return f"evt_{uuid4().hex[:16]}"

    def _gen_step_id(self) -> str:
        """Generate a deterministic step ID."""
        self.step_counter += 1
        return f"step_{self.step_counter}"

    def _gen_timer_id(self) -> str:
        """Generate a deterministic timer ID."""
        self.timer_counter += 1
        return f"timer_{self.timer_counter}"

    def _gen_signal_id(self) -> str:
        """Generate a deterministic signal ID."""
        self.signal_counter += 1
        return f"signal_{self.signal_counter}"

    def _gen_parallel_id(self) -> str:
        """Generate a deterministic parallel ID."""
        self.parallel_counter += 1
        return f"parallel_{self.parallel_counter}"

    def _serialize(self, obj: Any) -> Any:
        """Serialize an object to JSON-compatible format."""
        # Simplified; real impl would handle pydantic models, etc.
        if obj is None:
            return None
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)

    def _find_event(self, event_type: EventType, predicate: Callable[[Event], bool]) -> Event | None:
        """Find an event in the history matching the predicate."""
        for event in self.events:
            if event.event_type == event_type and predicate(event):
                return event
        return None

    # Primitives called by workflow code

    async def execute_step(
        self,
        step_fn: Callable[..., Coroutine[Any, Any, T]],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        retry_policy: RetryPolicy,
    ) -> T:
        """Execute a step with replay semantics."""
        step_id = self._gen_step_id()
        step_name = f"{step_fn.__module__}.{step_fn.__qualname__}"
        run_id = get_current_run_id()

        # Look for StepCompleted event
        completed = self._find_event(
            EventType.STEP_COMPLETED, lambda e: e.payload.get("step_id") == step_id
        )
        if completed:
            # Step already completed in history; return recorded result
            return completed.payload["result"]

        # Look for StepScheduled event
        scheduled = self._find_event(
            EventType.STEP_SCHEDULED, lambda e: e.payload.get("step_id") == step_id
        )
        
        if scheduled:
            # Step is scheduled but not completed; suspend
            raise WorkflowSuspended()

        # Schedule step
        attempt = 1
        idempotency_key = f"{run_id}:{step_id}:{attempt}"
        
        event = StepScheduledEvent(
            event_id=self._gen_event_id(),
            run_id=run_id,
            payload={
                "step_id": step_id,
                "step_name": step_name,
                "args": self._serialize(args),
                "kwargs": self._serialize(kwargs),
                "attempt": attempt,
                "idempotency_key": idempotency_key,
            },
        )
        await self.world.append_events(run_id, [event])

        # Invoke step
        await self.world.invoke_step({
            "run_id": run_id,
            "step_id": step_id,
            "function": step_name,
            "args": args,
            "kwargs": kwargs,
            "idempotency_key": idempotency_key,
            "attempt": attempt,
            "retry_policy": {
                "max_attempts": retry_policy.max_attempts,
                "backoff": retry_policy.backoff.value,
                "initial_delay_seconds": retry_policy.initial_delay_seconds,
                "max_delay_seconds": retry_policy.max_delay_seconds,
                "multiplier": retry_policy.multiplier,
            },
        })

        # Suspend; step will complete asynchronously
        raise WorkflowSuspended()

    async def sleep(self, duration: str) -> None:
        """Sleep for a duration (durable timer)."""
        timer_id = self._gen_timer_id()
        run_id = get_current_run_id()

        # Look for TimerFired event
        fired = self._find_event(
            EventType.TIMER_FIRED, lambda e: e.payload.get("timer_id") == timer_id
        )
        if fired:
            # Timer already fired; continue
            return

        # Look for TimerScheduled event
        scheduled = self._find_event(
            EventType.TIMER_SCHEDULED, lambda e: e.payload.get("timer_id") == timer_id
        )
        
        if scheduled:
            # Timer is scheduled but not fired; suspend
            raise WorkflowSuspended()

        # Parse duration and calculate fire time
        fire_at = self._parse_duration(duration)
        fire_at_iso = fire_at.isoformat()

        # Schedule timer
        event = TimerScheduledEvent(
            event_id=self._gen_event_id(),
            run_id=run_id,
            payload={
                "timer_id": timer_id,
                "fire_at_iso": fire_at_iso,
                "duration_str": duration,
            },
        )
        await self.world.append_events(run_id, [event])
        await self.world.schedule_timer(run_id, timer_id, fire_at_iso)

        # Suspend
        raise WorkflowSuspended()

    async def signal(self, name: str, timeout: str | None = None) -> Any:
        """Wait for a signal/webhook."""
        signal_id = self._gen_signal_id()
        run_id = get_current_run_id()

        # Look for SignalReceived event
        received = self._find_event(
            EventType.SIGNAL_RECEIVED,
            lambda e: e.payload.get("signal_id") == signal_id
            and e.payload.get("signal_name") == name,
        )
        if received:
            # Signal already received; return value
            return received.payload.get("value")

        # Look for SignalRequested event
        requested = self._find_event(
            EventType.SIGNAL_REQUESTED,
            lambda e: e.payload.get("signal_id") == signal_id
            and e.payload.get("signal_name") == name,
        )
        
        if requested:
            # Signal is requested but not received; suspend
            raise WorkflowSuspended()

        # Request signal
        timeout_iso = None
        if timeout:
            timeout_dt = self._parse_duration(timeout)
            timeout_iso = timeout_dt.isoformat()

        event = SignalRequestedEvent(
            event_id=self._gen_event_id(),
            run_id=run_id,
            payload={
                "signal_id": signal_id,
                "signal_name": name,
                "timeout_iso": timeout_iso,
            },
        )
        await self.world.append_events(run_id, [event])

        # Suspend
        raise WorkflowSuspended()

    async def parallel(
        self,
        tasks: list[Callable[[], Coroutine[Any, Any, Any]]],
        concurrency: int | None = None,
    ) -> list[Any]:
        """Execute tasks in parallel (fan-out/fan-in)."""
        parallel_id = self._gen_parallel_id()
        run_id = get_current_run_id()

        # Look for ParallelCompleted event
        completed = self._find_event(
            EventType.PARALLEL_COMPLETED,
            lambda e: e.payload.get("parallel_id") == parallel_id,
        )
        if completed:
            # Parallel already completed; return results
            return completed.payload["results"]

        # Look for ParallelStarted event
        started = self._find_event(
            EventType.PARALLEL_STARTED,
            lambda e: e.payload.get("parallel_id") == parallel_id,
        )
        
        if not started:
            # Start parallel execution
            event = ParallelStartedEvent(
                event_id=self._gen_event_id(),
                run_id=run_id,
                payload={
                    "parallel_id": parallel_id,
                    "num_tasks": len(tasks),
                },
            )
            await self.world.append_events(run_id, [event])

        # Execute each task as a step
        # In real impl, each task would be scheduled as a step
        # For now, we'll execute them sequentially in replay
        results = []
        for task in tasks:
            result = await task()
            results.append(result)

        # Record completion
        event = ParallelCompletedEvent(
            event_id=self._gen_event_id(),
            run_id=run_id,
            payload={
                "parallel_id": parallel_id,
                "results": self._serialize(results),
            },
        )
        await self.world.append_events(run_id, [event])

        return results

    def marker(self, key: str, value: Any) -> None:
        """Add a marker for versioning/feature flags."""
        run_id = get_current_run_id()
        
        # Markers are deterministic based on counter
        marker_id = self.marker_counter
        self.marker_counter += 1

        # Check if marker already exists
        existing = self._find_event(
            EventType.MARKER,
            lambda e: e.payload.get("key") == key and e.payload.get("marker_id") == marker_id,
        )
        if existing:
            return

        # This would normally be synchronous in real impl
        # For now, just track it
        pass

    def _parse_duration(self, duration_str: str) -> datetime:
        """Parse duration string like '3d', '2h', '30m', '10s'."""
        import re

        match = re.match(r"(\d+)([smhd])", duration_str)
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")

        value = int(match.group(1))
        unit = match.group(2)

        if unit == "s":
            delta = timedelta(seconds=value)
        elif unit == "m":
            delta = timedelta(minutes=value)
        elif unit == "h":
            delta = timedelta(hours=value)
        elif unit == "d":
            delta = timedelta(days=value)
        else:
            raise ValueError(f"Invalid duration unit: {unit}")

        return datetime.utcnow() + delta


# Global orchestrator instance (simplified; real impl would be per-world)
_global_orchestrator: Orchestrator | None = None


def get_orchestrator(world: World) -> Orchestrator:
    """Get or create the global orchestrator."""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = Orchestrator(world)
    return _global_orchestrator

