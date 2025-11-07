"""Command-line interface for Worldflow."""

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich import print as rprint

console = Console()


def get_world():
    """Get the configured World (defaults to LocalWorld)."""
    from worldflow.worlds import LocalWorld
    
    # TODO: Support config file to choose different worlds
    return LocalWorld()


@click.group()
def cli():
    """Worldflow: DX-first durable workflow orchestration."""
    pass


@cli.command()
@click.argument("workflow_module")
@click.argument("workflow_name")
@click.option("--input", "-i", multiple=True, help="Input key=value pairs")
@click.option("--run-id", help="Custom run ID (auto-generated if not provided)")
def start(workflow_module: str, workflow_name: str, input: tuple[str, ...], run_id: str | None):
    """
    Start a workflow execution.
    
    Example:
        worldflow start myapp.workflows onboarding -i user_id=123
    """
    # Parse inputs
    inputs = {}
    for inp in input:
        if "=" not in inp:
            console.print(f"[red]Invalid input format: {inp} (expected key=value)[/red]")
            return
        key, value = inp.split("=", 1)
        # Try to parse as JSON, fall back to string
        try:
            inputs[key] = json.loads(value)
        except json.JSONDecodeError:
            inputs[key] = value

    # Generate run ID if not provided
    if not run_id:
        run_id = f"run_{uuid4().hex[:12]}"

    async def _start():
        # Import workflow module to register workflows
        import importlib
        try:
            importlib.import_module(workflow_module)
        except ImportError as e:
            console.print(f"[red]Failed to import {workflow_module}: {e}[/red]")
            return

        from worldflow.decorators import get_workflow_function
        from worldflow.runtime import Orchestrator

        try:
            workflow_fn = get_workflow_function(workflow_name)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            return

        world = get_world()
        orchestrator = Orchestrator(world)

        console.print(f"[green]Starting workflow {workflow_name} with run_id={run_id}[/green]")
        await orchestrator.start_workflow(run_id, workflow_fn, inputs, workflow_name)
        console.print(f"[green]Workflow started! Run ID: {run_id}[/green]")
        console.print(f"[dim]Track progress with: worldflow logs {run_id}[/dim]")

    asyncio.run(_start())


@cli.command()
@click.option("--workflow", "-w", help="Filter by workflow name")
@click.option("--status", "-s", help="Filter by status")
@click.option("--limit", "-n", default=20, help="Number of runs to show")
def ps(workflow: str | None, status: str | None, limit: int):
    """List workflow runs."""
    async def _ps():
        world = get_world()
        runs = await world.list_runs(workflow, status, limit)

        if not runs:
            console.print("[yellow]No workflow runs found[/yellow]")
            return

        table = Table(title="Workflow Runs")
        table.add_column("Run ID", style="cyan")
        table.add_column("Workflow", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Started At", style="blue")

        for run in runs:
            status_color = {
                "running": "yellow",
                "completed": "green",
                "failed": "red",
            }.get(run["status"], "white")
            
            table.add_row(
                run["run_id"],
                run["workflow_name"],
                f"[{status_color}]{run['status']}[/{status_color}]",
                run["started_at"],
            )

        console.print(table)

    asyncio.run(_ps())


@cli.command()
@click.argument("run_id")
def logs(run_id: str):
    """Show detailed logs for a workflow run."""
    async def _logs():
        world = get_world()
        
        try:
            status = await world.get_run_status(run_id)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            return

        # Print run info
        console.print(f"\n[bold]Run: {run_id}[/bold]")
        console.print(f"Workflow: {status['workflow_name']}")
        console.print(f"Status: {status['status']}")
        console.print(f"Started: {status['started_at']}")
        if status['ended_at']:
            console.print(f"Ended: {status['ended_at']}")

        console.print("\n[bold]Inputs:[/bold]")
        rprint(status['inputs'])

        if status['result']:
            console.print("\n[bold]Result:[/bold]")
            rprint(status['result'])

        if status['error']:
            console.print("\n[bold red]Error:[/bold red]")
            console.print(status['error'])

        # Print event log
        events = await world.load_events(run_id)
        
        console.print(f"\n[bold]Event Log ({len(events)} events):[/bold]")
        table = Table()
        table.add_column("#", style="dim")
        table.add_column("Type", style="cyan")
        table.add_column("Timestamp", style="blue")
        table.add_column("Details", style="white")

        for i, event in enumerate(events):
            details = _format_event_details(event)
            table.add_row(
                str(i),
                event.event_type.value,
                event.timestamp.strftime("%H:%M:%S"),
                details,
            )

        console.print(table)

    asyncio.run(_logs())


def _format_event_details(event) -> str:
    """Format event payload for display."""
    from worldflow.events import EventType
    
    payload = event.payload
    
    if event.event_type == EventType.STEP_SCHEDULED:
        return f"step={payload.get('step_name', 'unknown')}"
    elif event.event_type == EventType.STEP_COMPLETED:
        return f"step_id={payload.get('step_id')} ({payload.get('duration_ms')}ms)"
    elif event.event_type == EventType.STEP_FAILED:
        return f"step_id={payload.get('step_id')} error={payload.get('error', '')[:50]}"
    elif event.event_type == EventType.TIMER_SCHEDULED:
        return f"duration={payload.get('duration_str')}"
    elif event.event_type == EventType.SIGNAL_REQUESTED:
        return f"name={payload.get('signal_name')}"
    elif event.event_type == EventType.SIGNAL_RECEIVED:
        return f"name={payload.get('signal_name')} value={str(payload.get('value'))[:30]}"
    else:
        return ""


@cli.command()
@click.argument("run_id")
@click.argument("signal_name")
@click.argument("payload")
def signal(run_id: str, signal_name: str, payload: str):
    """Send a signal to a running workflow."""
    # Try to parse payload as JSON
    try:
        payload_value = json.loads(payload)
    except json.JSONDecodeError:
        payload_value = payload

    async def _signal():
        world = get_world()
        
        try:
            await world.publish_signal(run_id, signal_name, payload_value)
            console.print(f"[green]Signal '{signal_name}' sent to {run_id}[/green]")
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    asyncio.run(_signal())


@cli.command()
@click.argument("run_id")
def replay(run_id: str):
    """Replay a workflow from its event log (for debugging)."""
    async def _replay():
        world = get_world()
        
        # Just invoke the orchestrator again
        from worldflow.runtime import Orchestrator
        
        orchestrator = Orchestrator(world)
        
        console.print(f"[yellow]Replaying workflow {run_id}...[/yellow]")
        await orchestrator.run_orchestrator(run_id)
        console.print(f"[green]Replay complete[/green]")

    asyncio.run(_replay())


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def dev(host: str, port: int):
    """Start local development server with dashboard."""
    console.print(f"[green]Starting Worldflow dev server on {host}:{port}[/green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    
    # Start FastAPI server
    import uvicorn
    from worldflow.fastapi_integration import create_app
    
    app = create_app(get_world())
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()

