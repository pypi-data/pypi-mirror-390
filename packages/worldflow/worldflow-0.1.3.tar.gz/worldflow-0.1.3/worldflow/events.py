"""Event types for the durable event log."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events in the workflow event log."""

    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    STEP_SCHEDULED = "step_scheduled"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_RETRYING = "step_retrying"
    
    TIMER_SCHEDULED = "timer_scheduled"
    TIMER_FIRED = "timer_fired"
    
    SIGNAL_REQUESTED = "signal_requested"
    SIGNAL_RECEIVED = "signal_received"
    
    PARALLEL_STARTED = "parallel_started"
    PARALLEL_COMPLETED = "parallel_completed"
    
    MARKER = "marker"


class Event(BaseModel):
    """Base event in the workflow event log."""

    event_id: str
    run_id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class WorkflowStartedEvent(Event):
    """Workflow execution started."""

    event_type: EventType = EventType.WORKFLOW_STARTED
    # payload: { workflow_name, inputs }


class WorkflowCompletedEvent(Event):
    """Workflow execution completed successfully."""

    event_type: EventType = EventType.WORKFLOW_COMPLETED
    # payload: { result }


class WorkflowFailedEvent(Event):
    """Workflow execution failed."""

    event_type: EventType = EventType.WORKFLOW_FAILED
    # payload: { error, traceback }


class StepScheduledEvent(Event):
    """Step was scheduled for execution."""

    event_type: EventType = EventType.STEP_SCHEDULED
    # payload: { step_id, step_name, args, kwargs, attempt, idempotency_key }


class StepCompletedEvent(Event):
    """Step completed successfully."""

    event_type: EventType = EventType.STEP_COMPLETED
    # payload: { step_id, result, duration_ms }


class StepFailedEvent(Event):
    """Step execution failed."""

    event_type: EventType = EventType.STEP_FAILED
    # payload: { step_id, error, traceback, attempt, will_retry }


class TimerScheduledEvent(Event):
    """Timer was scheduled."""

    event_type: EventType = EventType.TIMER_SCHEDULED
    # payload: { timer_id, fire_at_iso, duration_str }


class TimerFiredEvent(Event):
    """Timer fired."""

    event_type: EventType = EventType.TIMER_FIRED
    # payload: { timer_id }


class SignalRequestedEvent(Event):
    """Signal/webhook was requested."""

    event_type: EventType = EventType.SIGNAL_REQUESTED
    # payload: { signal_id, signal_name, timeout_iso }


class SignalReceivedEvent(Event):
    """Signal/webhook was received."""

    event_type: EventType = EventType.SIGNAL_RECEIVED
    # payload: { signal_id, signal_name, value }


class ParallelStartedEvent(Event):
    """Parallel execution started."""

    event_type: EventType = EventType.PARALLEL_STARTED
    # payload: { parallel_id, num_tasks }


class ParallelCompletedEvent(Event):
    """Parallel execution completed."""

    event_type: EventType = EventType.PARALLEL_COMPLETED
    # payload: { parallel_id, results }


class MarkerEvent(Event):
    """Marker for versioning/feature flags."""

    event_type: EventType = EventType.MARKER
    # payload: { key, value }

