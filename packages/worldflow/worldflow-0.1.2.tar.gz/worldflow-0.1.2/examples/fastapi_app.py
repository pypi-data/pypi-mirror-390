"""Example: FastAPI app with Worldflow integration."""

from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel

from worldflow import workflow, step, sleep
from worldflow.worlds import LocalWorld
from worldflow.runtime import Orchestrator
from worldflow.fastapi_integration import create_app as create_worldflow_app


# Define workflow
@step
async def send_notification(user_id: str, message: str) -> None:
    """Send a notification."""
    print(f"📬 Notification to {user_id}: {message}")


@workflow
async def scheduled_reminder(user_id: str, message: str, delay: str):
    """Send a reminder after a delay."""
    await sleep(delay)
    await send_notification(user_id, message)
    return {"status": "sent", "user_id": user_id}


# Create FastAPI app
app = FastAPI(title="My App with Worldflow")

# Initialize World
world = LocalWorld()


class ReminderRequest(BaseModel):
    user_id: str
    message: str
    delay_seconds: int


@app.post("/reminders")
async def create_reminder(request: ReminderRequest):
    """Create a scheduled reminder."""
    orchestrator = Orchestrator(world)
    
    run_id = f"reminder_{uuid4().hex[:12]}"
    
    await orchestrator.start_workflow(
        run_id,
        scheduled_reminder,
        {
            "user_id": request.user_id,
            "message": request.message,
            "delay": f"{request.delay_seconds}s",
        },
        "scheduled_reminder"
    )
    
    return {"run_id": run_id, "status": "scheduled"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FastAPI + Worldflow", "worldflow_dashboard": "/worldflow"}


# Mount Worldflow dashboard
worldflow_app = create_worldflow_app(world)
app.mount("/worldflow", worldflow_app)


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI app with Worldflow integration")
    print("Dashboard: http://localhost:8000/worldflow")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

