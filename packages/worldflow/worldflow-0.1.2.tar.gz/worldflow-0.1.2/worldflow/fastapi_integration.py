"""FastAPI integration for Worldflow."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from worldflow.world import World


class SignalPayload(BaseModel):
    """Payload for signal endpoint."""

    value: Any


def create_app(world: World) -> FastAPI:
    """Create a FastAPI app with Worldflow endpoints."""
    app = FastAPI(title="Worldflow", description="Durable workflow orchestration")

    @app.post("/worldflow/signal/{run_id}/{signal_name}")
    async def receive_signal(run_id: str, signal_name: str, payload: SignalPayload):
        """Receive a signal/webhook for a workflow."""
        try:
            await world.publish_signal(run_id, signal_name, payload.value)
            return {"status": "ok", "run_id": run_id, "signal_name": signal_name}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/worldflow/runs")
    async def list_runs(workflow: str | None = None, status: str | None = None, limit: int = 100):
        """List workflow runs."""
        runs = await world.list_runs(workflow, status, limit)
        return {"runs": runs}

    @app.get("/worldflow/runs/{run_id}")
    async def get_run(run_id: str):
        """Get run details."""
        try:
            status = await world.get_run_status(run_id)
            events = await world.load_events(run_id)
            return {
                "run": status,
                "events": [
                    {
                        "event_id": e.event_id,
                        "event_type": e.event_type.value,
                        "timestamp": e.timestamp.isoformat(),
                        "payload": e.payload,
                    }
                    for e in events
                ],
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Simple dashboard."""
        runs = await world.list_runs(limit=50)
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Worldflow Dashboard</title>
            <style>
                body { font-family: system-ui; margin: 40px; background: #f5f5f5; }
                h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #4a90e2; color: white; }
                .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
                .status.running { background: #fff3cd; color: #856404; }
                .status.completed { background: #d4edda; color: #155724; }
                .status.failed { background: #f8d7da; color: #721c24; }
                a { color: #4a90e2; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🌍 Worldflow Dashboard</h1>
            <p>Durable workflow orchestration for Python</p>
            <h2>Recent Runs</h2>
            <table>
                <thead>
                    <tr>
                        <th>Run ID</th>
                        <th>Workflow</th>
                        <th>Status</th>
                        <th>Started At</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        if not runs:
            html += "<tr><td colspan='4' style='text-align:center; color: #999;'>No runs yet</td></tr>"
        else:
            for run in runs:
                status_class = run['status']
                html += f"""
                    <tr>
                        <td><a href='/worldflow/runs/{run["run_id"]}'>{run["run_id"]}</a></td>
                        <td>{run["workflow_name"]}</td>
                        <td><span class='status {status_class}'>{run["status"]}</span></td>
                        <td>{run["started_at"]}</td>
                    </tr>
                """
        
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html)

    return app


def signal_router():
    """Create a router for signal endpoints (for including in existing apps)."""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/worldflow")
    
    # This would be configured with a World instance
    # For now, it's a placeholder
    
    return router

