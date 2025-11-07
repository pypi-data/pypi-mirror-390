# Worldflow Quick Start Guide

## Installation

```bash
pip install worldflow
```

## 5-Minute Tutorial

### 1. Create your first workflow

Create a file `my_workflow.py`:

```python
from worldflow import workflow, step, sleep

@step
async def send_email(to: str, subject: str) -> str:
    print(f"📧 Sending email to {to}: {subject}")
    return f"email_sent_to_{to}"

@workflow
async def welcome_flow(user_email: str):
    # Send welcome email
    email_id = await send_email(user_email, "Welcome!")
    
    # Wait 1 day (durable - survives restarts!)
    await sleep("1d")
    
    # Send follow-up
    await send_email(user_email, "How are you liking it?")
    
    return {"status": "completed", "email_id": email_id}
```

### 2. Run it

```bash
# Start the workflow
worldflow start my_workflow welcome_flow -i user_email=user@example.com

# Check status
worldflow ps

# View detailed logs
worldflow logs <run_id>
```

### 3. Add retry logic

```python
from worldflow import step, RetryPolicy

@step(retries=RetryPolicy(max_attempts=5, backoff="exponential"))
async def charge_card(user_id: str, amount: int) -> str:
    # This will auto-retry on failure!
    return payment_api.charge(user_id, amount)
```

### 4. Parallel execution

```python
from worldflow import parallel, rate_limit

@workflow
async def batch_job(user_ids: list[str]):
    # Process 100 users in parallel, max 10 at a time
    results = await parallel(
        [lambda uid=uid: process_user(uid) for uid in user_ids],
        concurrency=rate_limit(10)
    )
    return results
```

### 5. Wait for external events

```python
from worldflow import signal

@workflow
async def approval_flow(request_id: str):
    # Submit for approval
    await submit_request(request_id)
    
    # Wait for approval (webhook/signal)
    decision = await signal("approval_decision", timeout="7d")
    
    if decision == "approved":
        await process_approval(request_id)
    else:
        await reject_request(request_id)
```

Send signals via CLI:

```bash
worldflow signal <run_id> approval_decision '"approved"'
```

Or via HTTP:

```bash
curl -X POST http://localhost:8000/worldflow/signal/<run_id>/approval_decision \
  -H "Content-Type: application/json" \
  -d '{"value": "approved"}'
```

## Development Dashboard

Start the local dev server:

```bash
worldflow dev
```

Visit http://localhost:8000 to see:
- All workflow runs
- Execution timelines
- Event logs
- Input/output data

## Key Concepts

### Workflows = Orchestration

- ✅ Call steps, sleep, signal, parallel
- ✅ Conditional logic, loops
- ❌ No HTTP, DB, or side effects
- ❌ Must be deterministic

### Steps = Side Effects

- ✅ HTTP calls, database writes
- ✅ Any I/O operations
- ✅ Should be idempotent
- Auto-retry with exponential backoff

### Durable Primitives

| Primitive | Description | Example |
|-----------|-------------|---------|
| `sleep(duration)` | Durable sleep | `await sleep("3d")` |
| `signal(name)` | Wait for webhook | `await signal("user_choice")` |
| `parallel(tasks)` | Fan-out/fan-in | `await parallel([task1, task2])` |

## Common Patterns

### Saga Pattern

```python
@workflow
async def order_workflow(order_id: str):
    try:
        payment = await charge_card(order_id)
        inventory = await reserve_inventory(order_id)
        await ship_order(order_id)
    except Exception:
        # Compensating transactions
        if payment:
            await refund_payment(payment)
        if inventory:
            await release_inventory(inventory)
        raise
```

### Human-in-the-Loop

```python
@workflow
async def review_workflow(document_id: str):
    # AI review
    ai_result = await ai_review(document_id)
    
    if ai_result.confidence < 0.8:
        # Request human review
        human_decision = await signal("human_review", timeout="3d")
        return human_decision
    
    return ai_result
```

### Rate-Limited Processing

```python
@workflow
async def api_scraper(urls: list[str]):
    # Process 1000 URLs, max 5 concurrent to respect rate limits
    results = await parallel(
        [lambda url=url: fetch_url(url) for url in urls],
        concurrency=rate_limit(5)
    )
    return results
```

## FastAPI Integration

```python
from fastapi import FastAPI
from worldflow.fastapi_integration import create_app as create_worldflow_app
from worldflow.worlds import LocalWorld

app = FastAPI()
world = LocalWorld()

# Mount Worldflow dashboard
worldflow_app = create_worldflow_app(world)
app.mount("/workflows", worldflow_app)

# Start workflows from your API
@app.post("/orders")
async def create_order(order_data: dict):
    from worldflow.runtime import Orchestrator
    
    orchestrator = Orchestrator(world)
    run_id = f"order_{order_data['id']}"
    
    await orchestrator.start_workflow(
        run_id,
        order_workflow,
        order_data,
        "order_workflow"
    )
    
    return {"run_id": run_id}
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/](examples/) for more complex workflows
- Join the community discussions
- Star the repo if you find it useful!

## Tips & Best Practices

1. **Make steps idempotent**: Use idempotency keys provided by the framework
2. **Keep workflows simple**: Complex logic should be in steps
3. **Use timeouts**: Always set timeouts on signals
4. **Test locally first**: Use LocalWorld for development
5. **Monitor your workflows**: Check the dashboard regularly

## Troubleshooting

### Workflow stuck?

```bash
# Check current status
worldflow logs <run_id>

# Replay workflow (for debugging)
worldflow replay <run_id>
```

### Step keeps retrying?

- Check the step's retry policy
- Review error messages in logs
- Consider adding a circuit breaker

### Need to cancel a workflow?

Currently in development - coming soon!

## Getting Help

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Examples: See working code

Happy orchestrating! 🌍

