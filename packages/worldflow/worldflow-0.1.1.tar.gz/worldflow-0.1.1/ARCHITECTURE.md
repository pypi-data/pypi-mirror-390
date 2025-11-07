# Worldflow Architecture

## Overview

Worldflow is a durable workflow orchestration framework that uses **deterministic replay** with an **event-sourced** architecture, inspired by Temporal but designed for Python-first DX.

## Core Design Principles

1. **Deterministic Replay**: Workflows are pure functions that replay from event logs
2. **Event Sourcing**: All state changes are captured as append-only events
3. **At-Least-Once Execution**: Steps execute at least once with idempotency
4. **Pluggable Backends**: Same code runs on local, AWS, GCP, K8s via "Worlds"
5. **Developer Experience First**: Write normal async Python, minimal boilerplate

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Code                        │
│  • Workflows (@workflow decorated functions)                │
│  • Steps (@step decorated functions)                        │
│  • Primitives (sleep, signal, parallel)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Layer                        │
│  • Event Log Replay Engine                                  │
│  • Determinism Enforcement                                  │
│  • Primitive Implementation (sleep/signal/parallel)         │
│  • Workflow State Machine                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      World Protocol                          │
│  • Persistence Interface                                    │
│  • Compute Interface                                        │
│  • Scheduling Interface                                     │
│  • Messaging Interface                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬──────────────┐
         ↓               ↓               ↓              ↓
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐
│ LocalWorld  │  │  AWSWorld   │  │ GCPWorld │  │ K8sWorld │
│             │  │             │  │          │  │          │
│ • SQLite    │  │ • DynamoDB  │  │ • Store  │  │ • Pgsql  │
│ • Async     │  │ • SQS       │  │ • Pub/Sub│  │ • Redis  │
│ • APSched   │  │ • Lambda    │  │ • C.Run  │  │ • Jobs   │
└─────────────┘  └─────────────┘  └──────────┘  └──────────┘
```

## Components

### 1. Decorators (`decorators.py`)

**Responsibility**: Mark functions as workflows or steps

```python
@workflow
async def my_workflow(input: str):
    result = await my_step(input)
    return result

@step(retries=RetryPolicy(max_attempts=3))
async def my_step(input: str) -> str:
    # Side effects here
    return result
```

**Implementation**:
- Registers functions in global registries
- Wraps step functions to route through orchestrator
- Validates async functions
- Stores metadata (retry policies, etc.)

### 2. Runtime (`runtime.py`)

**Responsibility**: Core orchestration engine

**Key Classes**:

- **`Orchestrator`**: Main execution engine
  - Loads event log
  - Replays workflow function
  - Schedules steps/timers/signals
  - Appends new events
  - Handles workflow completion/failure

**Replay Algorithm**:

```
1. Load event history for run_id
2. Reset counters (step, timer, signal)
3. Re-execute workflow function from start
4. For each primitive:
   a. Generate deterministic ID
   b. Check if event exists in history:
      - YES → Return recorded result
      - NO → Schedule operation & suspend
5. On external completion → goto 1
```

**Context Variables**:
- `_current_run_id`: Current workflow run
- `_current_world`: Backend interface
- `_current_orchestrator`: Orchestrator instance

### 3. Events (`events.py`)

**Responsibility**: Event types for the durable log

**Event Schema**:
```python
Event {
    event_id: str          # Unique ID
    run_id: str           # Workflow run ID
    event_type: EventType # Type of event
    timestamp: datetime   # When it happened
    payload: dict         # Event-specific data
}
```

**Event Types**:
- Workflow: `Started`, `Completed`, `Failed`
- Step: `Scheduled`, `Completed`, `Failed`, `Retrying`
- Timer: `Scheduled`, `Fired`
- Signal: `Requested`, `Received`
- Parallel: `Started`, `Completed`
- Marker: For versioning/feature flags

### 4. World Protocol (`world.py`)

**Responsibility**: Backend abstraction interface

**Interface Methods**:

```python
class World(Protocol):
    # Persistence
    async def append_events(run_id, events) -> None
    async def load_events(run_id) -> list[Event]
    
    # Compute
    async def invoke_step(step_payload) -> None
    async def invoke_orchestrator(run_id) -> None
    
    # Scheduling
    async def schedule_timer(run_id, timer_id, fire_at) -> None
    async def publish_signal(run_id, name, payload) -> None
    
    # URLs
    def signal_url(run_id, name) -> str
    
    # Management
    async def create_run(run_id, workflow_name, inputs) -> None
    async def get_run_status(run_id) -> dict
    async def list_runs(...) -> list[dict]
```

### 5. LocalWorld (`worlds/local.py`)

**Responsibility**: Local development backend

**Storage**: SQLite
- `events` table: Event log (run_id, event_idx, event_data)
- `runs` table: Run metadata (status, inputs, results)

**Compute**: In-process async
- Steps execute immediately via `asyncio.create_task`
- Orchestrator invoked on event completions

**Scheduling**: asyncio
- Timers via `asyncio.sleep` + tasks
- Signals via in-memory queues

**Good for**:
- Local development
- Testing
- Single-machine deployments

### 6. Primitives (`primitives.py`)

**Responsibility**: Durable operations within workflows

**`sleep(duration)`**:
1. Generate deterministic timer_id
2. Check for TimerFired event
3. If not found: schedule timer & suspend
4. If found: return immediately

**`signal(name, timeout)`**:
1. Generate deterministic signal_id
2. Check for SignalReceived event
3. If not found: request signal & suspend
4. If found: return signal value

**`parallel(tasks, concurrency)`**:
1. Generate deterministic parallel_id
2. Check for ParallelCompleted event
3. If not found: schedule all tasks
4. If found: return recorded results

### 7. Retry Logic (`retry.py`)

**Responsibility**: Step retry policies

**RetryPolicy**:
```python
RetryPolicy(
    max_attempts: int = 3,
    backoff: "constant" | "linear" | "exponential",
    initial_delay_seconds: float = 1.0,
    max_delay_seconds: float = 3600.0,
    multiplier: float = 2.0
)
```

**Implementation**:
- Step fails → StepFailed event appended
- If should_retry → wait delay, increment attempt, re-enqueue
- If no more retries → workflow continues (raises exception)

## Execution Flow

### Starting a Workflow

```
User calls start_workflow()
  ↓
Create run record
  ↓
Append WorkflowStarted event
  ↓
Invoke orchestrator
  ↓
Orchestrator loads events (just WorkflowStarted)
  ↓
Replay workflow function
  ↓
Hit first step
  ↓
No StepCompleted in history
  ↓
Append StepScheduled event
  ↓
Enqueue step for execution
  ↓
Raise WorkflowSuspended (pause replay)
```

### Step Completes

```
Step executes (in separate task/process)
  ↓
Success: Append StepCompleted event
  ↓
Invoke orchestrator again
  ↓
Orchestrator loads events (WorkflowStarted + StepScheduled + StepCompleted)
  ↓
Replay workflow function from start
  ↓
Hit first step again
  ↓
Found StepCompleted in history!
  ↓
Return recorded result (don't re-execute)
  ↓
Continue to next primitive
  ↓
...
```

### Timer Fires

```
Timer scheduled via World.schedule_timer()
  ↓
After delay, timer callback fires
  ↓
Append TimerFired event
  ↓
Invoke orchestrator
  ↓
Replay from start
  ↓
Hit sleep() call
  ↓
Found TimerFired in history!
  ↓
Return immediately (don't wait)
  ↓
Continue workflow
```

## Determinism

### What Makes Workflows Deterministic?

1. **Deterministic IDs**: Step/timer/signal IDs generated via counters
2. **Event Ordering**: Events processed in order
3. **No Hidden State**: All state in event log
4. **Replay Semantics**: Same inputs + same events = same execution

### What's NOT Allowed in Workflows?

```python
# ❌ BAD: Non-deterministic
@workflow
async def bad_workflow():
    now = datetime.now()  # Different each replay!
    rand = random.random()  # Non-deterministic!
    response = requests.get("...")  # Side effect!
    
# ✅ GOOD: Deterministic
@workflow
async def good_workflow():
    result = await get_data()  # Step handles side effect
    await sleep("1h")  # Durable primitive
    return result
```

### Enforcement

- Monkeypatch `datetime.now()`, `random.random()` in workflow context
- Raise error if accessed
- Coming soon: static analysis to detect violations

## Idempotency

### Automatic Idempotency Keys

Each step execution gets a unique key:
```
idempotency_key = f"{run_id}:{step_id}:{attempt}"
```

### Usage

1. Pass in HTTP headers: `Idempotency-Key: ...`
2. Check before DB writes
3. Deduplicate messages

### Step-Level Control

```python
@step(unique_on=["user_id", "action"])
async def process_action(user_id: str, action: str):
    # Framework can generate key from these fields
    pass
```

## Scalability

### LocalWorld

- Single machine
- Good for: Dev, testing, small deployments
- Limits: No horizontal scaling

### AWSWorld (Coming Soon)

- DynamoDB: Event log (partitioned by run_id)
- SQS: Step queue (FIFO or standard)
- Lambda: Step execution + orchestrator
- EventBridge: Timer scheduling
- Scales to millions of concurrent workflows

### GCPWorld (Coming Soon)

- Firestore: Event log
- Pub/Sub: Message queue
- Cloud Run: Serverless execution
- Cloud Scheduler: Timers

## Observability

### Event Log

Every state change is recorded:
```sql
SELECT * FROM events WHERE run_id = 'run_123' ORDER BY event_idx;
```

### Dashboard

- List all runs
- Drill into event timeline
- View inputs/outputs
- Retry history
- Duration metrics

### OpenTelemetry (Coming Soon)

- Traces for workflows
- Spans for steps
- Metrics for durations, failures

## Future Enhancements

1. **Snapshots**: Compact event logs (every N events)
2. **Workflow Versioning**: Safe code changes for running workflows
3. **Child Workflows**: Workflow-to-workflow communication
4. **CRON Workflows**: Scheduled recurring workflows
5. **Circuit Breakers**: Automatic pause on repeated failures
6. **Dead Letter Queues**: Handle poison messages
7. **Workflow Cancellation**: Graceful termination
8. **Distributed Tracing**: Full observability
9. **GraphQL API**: Query workflow state
10. **Visual Workflow Editor**: Build workflows visually

## Security Considerations

1. **Secrets**: Redact SecretStr fields in logs/UI
2. **Auth**: World implementations should verify signatures
3. **Input Validation**: Validate at workflow entry
4. **Rate Limiting**: Prevent DoS via excessive workflows
5. **Audit Log**: Track who started/signaled workflows

## Testing

### Unit Tests

Test steps in isolation:
```python
@pytest.mark.asyncio
async def test_my_step():
    result = await my_step("input")
    assert result == "expected"
```

### Integration Tests

Test workflows with LocalWorld:
```python
@pytest.mark.asyncio
async def test_my_workflow():
    world = LocalWorld(":memory:")
    orchestrator = Orchestrator(world)
    
    run_id = "test_run"
    await orchestrator.start_workflow(run_id, my_workflow, {"input": "test"})
    
    # Wait for completion
    await asyncio.sleep(1)
    
    status = await world.get_run_status(run_id)
    assert status["status"] == "completed"
```

### Replay Tests

Test determinism:
```python
# Start workflow
run_id = "test"
await orchestrator.start_workflow(run_id, my_workflow, inputs)

# Replay multiple times - should get same result
for _ in range(10):
    await orchestrator.run_orchestrator(run_id)
```

## Performance

### Bottlenecks

1. **Event Log Writes**: Mitigated by batching
2. **Replay Cost**: Mitigated by snapshots (future)
3. **Step Scheduling**: Async/concurrent execution

### Optimizations

1. **Batch Event Writes**: Append multiple events at once
2. **In-Memory Caching**: Cache recent event logs
3. **Parallel Step Execution**: Fan-out to workers
4. **Lazy Loading**: Only load events when needed

---

This architecture enables Worldflow to provide **durable**, **scalable**, and **observable** workflow orchestration with a **Python-first developer experience**.

