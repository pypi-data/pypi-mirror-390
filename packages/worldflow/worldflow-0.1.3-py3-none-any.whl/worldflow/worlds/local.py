"""LocalWorld: SQLite + in-process execution for local development."""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiosqlite

from worldflow.events import Event, EventType
from worldflow.world import World


class LocalWorld:
    """
    Local development World using SQLite for persistence.
    
    - Events stored in SQLite
    - Steps executed in-process (async)
    - Timers handled via asyncio
    - Signals via in-memory queue
    """

    def __init__(self, db_path: str | Path = ".worldflow.db"):
        # For :memory:, use a temporary file instead (simplest solution)
        if db_path == ":memory:":
            import tempfile
            # Create temp file that gets deleted on close
            self._temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=True)
            self.db_path = self._temp_file.name
        else:
            self._temp_file = None
            self.db_path = str(db_path)
        self._initialized = False
        self._signal_queues: dict[str, asyncio.Queue[Any]] = {}
        self._timer_tasks: dict[str, asyncio.Task[None]] = {}

    async def _init_db(self) -> None:
        """Initialize database schema."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            # Events table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    run_id TEXT NOT NULL,
                    event_idx INTEGER NOT NULL,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (run_id, event_idx)
                )
            """)
            
            # Runs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    inputs TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    tags TEXT
                )
            """)
            
            await db.commit()

        self._initialized = True

    # Persistence

    async def append_events(self, run_id: str, events: list[Event]) -> None:
        """Append events to the durable log."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            # Get current max index
            cursor = await db.execute(
                "SELECT COALESCE(MAX(event_idx), -1) FROM events WHERE run_id = ?",
                (run_id,),
            )
            row = await cursor.fetchone()
            next_idx = (row[0] if row else -1) + 1

            # Insert events
            for i, event in enumerate(events):
                await db.execute(
                    """
                    INSERT INTO events (run_id, event_idx, event_id, event_type, timestamp, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        next_idx + i,
                        event.event_id,
                        event.event_type.value,
                        event.timestamp.isoformat(),
                        json.dumps(event.payload),
                    ),
                )

            await db.commit()

        # Update run status based on events
        await self._update_run_status(run_id, events)

    async def load_events(self, run_id: str) -> list[Event]:
        """Load all events for a run."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT event_id, event_type, timestamp, payload
                FROM events
                WHERE run_id = ?
                ORDER BY event_idx
                """,
                (run_id,),
            )
            rows = await cursor.fetchall()

        events = []
        for row in rows:
            event_id, event_type_str, timestamp_str, payload_str = row
            event = Event(
                event_id=event_id,
                run_id=run_id,
                event_type=EventType(event_type_str),
                timestamp=datetime.fromisoformat(timestamp_str),
                payload=json.loads(payload_str),
            )
            events.append(event)

        return events

    # Compute

    async def invoke_step(self, step_payload: dict[str, Any]) -> None:
        """Execute a step in-process."""
        # In local dev, execute immediately
        asyncio.create_task(self._execute_step(step_payload))

    async def _execute_step(self, step_payload: dict[str, Any]) -> None:
        """Execute a step and record result."""
        from worldflow.decorators import get_step_function
        from worldflow.events import StepCompletedEvent, StepFailedEvent
        from worldflow.retry import RetryPolicy
        
        run_id = step_payload["run_id"]
        step_id = step_payload["step_id"]
        function_name = step_payload["function"]
        args = step_payload["args"]
        kwargs = step_payload["kwargs"]
        attempt = step_payload["attempt"]
        retry_config = step_payload.get("retry_policy", {})
        
        retry_policy = RetryPolicy(
            max_attempts=retry_config.get("max_attempts", 3),
            backoff=retry_config.get("backoff", "exponential"),
            initial_delay_seconds=retry_config.get("initial_delay_seconds", 1.0),
            max_delay_seconds=retry_config.get("max_delay_seconds", 3600.0),
            multiplier=retry_config.get("multiplier", 2.0),
        )

        try:
            # Get step function
            step_fn = get_step_function(function_name)
            
            # Execute
            start = datetime.utcnow()
            result = await step_fn(*args, **kwargs)
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

            # Record success
            event = StepCompletedEvent(
                event_id=f"evt_{uuid4().hex[:16]}",
                run_id=run_id,
                payload={
                    "step_id": step_id,
                    "result": self._serialize(result),
                    "duration_ms": duration_ms,
                },
            )
            await self.append_events(run_id, [event])

            # Trigger orchestrator to continue
            await self.invoke_orchestrator(run_id)

        except Exception as e:
            import traceback

            will_retry = retry_policy.should_retry(attempt)
            
            # Record failure
            event = StepFailedEvent(
                event_id=f"evt_{uuid4().hex[:16]}",
                run_id=run_id,
                payload={
                    "step_id": step_id,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "attempt": attempt,
                    "will_retry": will_retry,
                },
            )
            await self.append_events(run_id, [event])

            if will_retry:
                # Schedule retry
                delay = retry_policy.get_delay_seconds(attempt)
                await asyncio.sleep(delay)
                
                # Re-enqueue with incremented attempt
                retry_payload = {**step_payload, "attempt": attempt + 1}
                await self.invoke_step(retry_payload)
            else:
                # No more retries; trigger orchestrator (will fail workflow)
                await self.invoke_orchestrator(run_id)

    async def invoke_orchestrator(self, run_id: str) -> None:
        """Trigger orchestrator to process events."""
        # In local dev, execute immediately
        asyncio.create_task(self._run_orchestrator(run_id))

    async def _run_orchestrator(self, run_id: str) -> None:
        """Run the orchestrator."""
        from worldflow.runtime import Orchestrator
        
        orchestrator = Orchestrator(self)
        await orchestrator.run_orchestrator(run_id)

    # Scheduling & messaging

    async def schedule_timer(self, run_id: str, timer_id: str, fire_at_iso: str) -> None:
        """Schedule a timer."""
        fire_at = datetime.fromisoformat(fire_at_iso)
        delay = (fire_at - datetime.utcnow()).total_seconds()
        
        if delay < 0:
            delay = 0

        # Create task to fire timer
        task = asyncio.create_task(self._fire_timer(run_id, timer_id, delay))
        self._timer_tasks[f"{run_id}:{timer_id}"] = task

    async def _fire_timer(self, run_id: str, timer_id: str, delay: float) -> None:
        """Fire a timer after delay."""
        from worldflow.events import TimerFiredEvent
        
        await asyncio.sleep(delay)
        
        # Record timer fired
        event = TimerFiredEvent(
            event_id=f"evt_{uuid4().hex[:16]}",
            run_id=run_id,
            payload={"timer_id": timer_id},
        )
        await self.append_events(run_id, [event])
        
        # Trigger orchestrator
        await self.invoke_orchestrator(run_id)

    async def publish_signal(self, run_id: str, signal_name: str, payload: Any) -> None:
        """Publish a signal."""
        from worldflow.events import SignalReceivedEvent
        
        # Find the signal request in events to get signal_id
        events = await self.load_events(run_id)
        signal_event = next(
            (
                e
                for e in events
                if e.event_type == EventType.SIGNAL_REQUESTED
                and e.payload.get("signal_name") == signal_name
            ),
            None,
        )
        
        if not signal_event:
            raise ValueError(f"No signal request found for {signal_name} in run {run_id}")
        
        signal_id = signal_event.payload["signal_id"]
        
        # Record signal received
        event = SignalReceivedEvent(
            event_id=f"evt_{uuid4().hex[:16]}",
            run_id=run_id,
            payload={
                "signal_id": signal_id,
                "signal_name": signal_name,
                "value": payload,
            },
        )
        await self.append_events(run_id, [event])
        
        # Trigger orchestrator
        await self.invoke_orchestrator(run_id)

    def signal_url(self, run_id: str, signal_name: str) -> str:
        """Get signal URL (for local dev, just a placeholder)."""
        return f"http://localhost:8000/worldflow/signal/{run_id}/{signal_name}"

    # Run management

    async def create_run(
        self,
        run_id: str,
        workflow_name: str,
        inputs: dict[str, Any],
        tags: dict[str, str] | None = None,
    ) -> None:
        """Create a new workflow run."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO runs (run_id, workflow_name, status, inputs, started_at, tags)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    workflow_name,
                    "running",
                    json.dumps(inputs),
                    datetime.utcnow().isoformat(),
                    json.dumps(tags or {}),
                ),
            )
            await db.commit()

    async def get_run_status(self, run_id: str) -> dict[str, Any]:
        """Get run status."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT workflow_name, status, inputs, result, error, started_at, ended_at, tags
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            )
            row = await cursor.fetchone()

        if not row:
            raise ValueError(f"Run {run_id} not found")

        return {
            "run_id": run_id,
            "workflow_name": row[0],
            "status": row[1],
            "inputs": json.loads(row[2]),
            "result": json.loads(row[3]) if row[3] else None,
            "error": row[4],
            "started_at": row[5],
            "ended_at": row[6],
            "tags": json.loads(row[7]) if row[7] else {},
        }

    async def list_runs(
        self,
        workflow_name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List workflow runs."""
        await self._init_db()

        query = "SELECT run_id, workflow_name, status, started_at FROM runs WHERE 1=1"
        params = []

        if workflow_name:
            query += " AND workflow_name = ?"
            params.append(workflow_name)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

        return [
            {
                "run_id": row[0],
                "workflow_name": row[1],
                "status": row[2],
                "started_at": row[3],
            }
            for row in rows
        ]

    async def _update_run_status(self, run_id: str, events: list[Event]) -> None:
        """Update run status based on events."""
        for event in events:
            if event.event_type == EventType.WORKFLOW_COMPLETED:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute(
                        """
                        UPDATE runs
                        SET status = ?, result = ?, ended_at = ?
                        WHERE run_id = ?
                        """,
                        (
                            "completed",
                            json.dumps(event.payload.get("result")),
                            datetime.utcnow().isoformat(),
                            run_id,
                        ),
                    )
                    await db.commit()
            elif event.event_type == EventType.WORKFLOW_FAILED:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute(
                        """
                        UPDATE runs
                        SET status = ?, error = ?, ended_at = ?
                        WHERE run_id = ?
                        """,
                        (
                            "failed",
                            event.payload.get("error"),
                            datetime.utcnow().isoformat(),
                            run_id,
                        ),
                    )
                    await db.commit()

    def _serialize(self, obj: Any) -> Any:
        """Serialize object to JSON-compatible format."""
        if obj is None:
            return None
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)

