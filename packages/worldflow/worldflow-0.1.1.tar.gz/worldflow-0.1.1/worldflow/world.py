"""World protocol: pluggable backend interface."""

from typing import Protocol, Any, runtime_checkable
from worldflow.events import Event


@runtime_checkable
class World(Protocol):
    """
    Backend interface for workflow execution.
    
    Implementations provide persistence, compute, scheduling, and messaging
    for different environments (local dev, AWS, GCP, K8s, etc).
    """

    # Persistence
    async def append_events(self, run_id: str, events: list[Event]) -> None:
        """Append events to the durable log for this run."""
        ...

    async def load_events(self, run_id: str) -> list[Event]:
        """Load all events for this run from the durable log."""
        ...

    # Compute
    async def invoke_step(self, step_payload: dict[str, Any]) -> None:
        """
        Enqueue/invoke a step for execution.
        
        step_payload contains:
        - run_id
        - step_id
        - function (module path)
        - args, kwargs
        - idempotency_key
        - attempt
        """
        ...

    async def invoke_orchestrator(self, run_id: str) -> None:
        """Trigger the orchestrator to process events and advance the workflow."""
        ...

    # Scheduling & messaging
    async def schedule_timer(self, run_id: str, timer_id: str, fire_at_iso: str) -> None:
        """Schedule a timer to fire at the specified time."""
        ...

    async def publish_signal(self, run_id: str, signal_name: str, payload: Any) -> None:
        """Publish a signal/webhook to the workflow."""
        ...

    # URLs for webhooks/signals
    def signal_url(self, run_id: str, signal_name: str) -> str:
        """Get the URL to POST a signal to this workflow run."""
        ...

    # Run management
    async def create_run(
        self, 
        run_id: str, 
        workflow_name: str, 
        inputs: dict[str, Any],
        tags: dict[str, str] | None = None
    ) -> None:
        """Create a new workflow run."""
        ...

    async def get_run_status(self, run_id: str) -> dict[str, Any]:
        """Get the current status of a workflow run."""
        ...

    async def list_runs(
        self, 
        workflow_name: str | None = None,
        status: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """List workflow runs with optional filters."""
        ...

