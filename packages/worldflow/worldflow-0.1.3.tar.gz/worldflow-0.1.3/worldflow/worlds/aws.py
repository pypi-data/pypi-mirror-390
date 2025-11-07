"""AWSWorld: Production-ready backend using AWS services."""

import json
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None  # type: ignore
    ClientError = Exception  # type: ignore

from worldflow.events import Event, EventType
from worldflow.world import World


class AWSWorld:
    """
    AWS-based World implementation for production deployments.
    
    Architecture:
    - DynamoDB: Event log storage
    - SQS: Step execution queue
    - Lambda: Orchestrator and step execution
    - EventBridge: Timer scheduling
    - API Gateway: Signal/webhook endpoints
    
    Environment Variables:
    - WORLDFLOW_EVENTS_TABLE: DynamoDB table for events
    - WORLDFLOW_RUNS_TABLE: DynamoDB table for run metadata
    - WORLDFLOW_STEP_QUEUE_URL: SQS queue URL for steps
    - WORLDFLOW_ORCHESTRATOR_FUNCTION: Lambda function name for orchestrator
    - AWS_REGION: AWS region (optional, defaults to us-east-1)
    """

    def __init__(
        self,
        events_table: str | None = None,
        runs_table: str | None = None,
        step_queue_url: str | None = None,
        orchestrator_function: str | None = None,
        region: str | None = None,
    ):
        if boto3 is None:
            raise ImportError(
                "AWS dependencies not installed. "
                'Install with: pip install "worldflow[aws]"'
            )

        self.events_table = events_table or os.environ.get("WORLDFLOW_EVENTS_TABLE")
        self.runs_table = runs_table or os.environ.get("WORLDFLOW_RUNS_TABLE")
        self.step_queue_url = step_queue_url or os.environ.get("WORLDFLOW_STEP_QUEUE_URL")
        self.orchestrator_function = orchestrator_function or os.environ.get(
            "WORLDFLOW_ORCHESTRATOR_FUNCTION"
        )
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")

        if not all([self.events_table, self.runs_table, self.step_queue_url]):
            raise ValueError(
                "Missing required AWS configuration. Set environment variables or pass to constructor:\n"
                "- WORLDFLOW_EVENTS_TABLE\n"
                "- WORLDFLOW_RUNS_TABLE\n"
                "- WORLDFLOW_STEP_QUEUE_URL"
            )

        # AWS clients
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.sqs = boto3.client("sqs", region_name=self.region)
        self.lambda_client = boto3.client("lambda", region_name=self.region)
        self.events_client = boto3.client("events", region_name=self.region)

        # Tables
        self.events_ddb_table = self.dynamodb.Table(self.events_table)
        self.runs_ddb_table = self.dynamodb.Table(self.runs_table)

    # Persistence

    async def append_events(self, run_id: str, events: list[Event]) -> None:
        """Append events to DynamoDB."""
        # Get current max event_idx
        try:
            response = self.events_ddb_table.query(
                KeyConditionExpression="run_id = :run_id",
                ExpressionAttributeValues={":run_id": run_id},
                ScanIndexForward=False,  # Descending order
                Limit=1,
                ProjectionExpression="event_idx",
            )
            items = response.get("Items", [])
            next_idx = (items[0]["event_idx"] + 1) if items else 0
        except ClientError:
            next_idx = 0

        # Write events in batch
        with self.events_ddb_table.batch_writer() as batch:
            for i, event in enumerate(events):
                batch.put_item(
                    Item={
                        "run_id": run_id,
                        "event_idx": next_idx + i,
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "payload": json.dumps(event.payload),
                    }
                )

        # Update run status if needed
        await self._update_run_status(run_id, events)

    async def load_events(self, run_id: str) -> list[Event]:
        """Load all events from DynamoDB."""
        events = []

        response = self.events_ddb_table.query(
            KeyConditionExpression="run_id = :run_id",
            ExpressionAttributeValues={":run_id": run_id},
            ScanIndexForward=True,  # Ascending order
        )

        for item in response.get("Items", []):
            event = Event(
                event_id=item["event_id"],
                run_id=run_id,
                event_type=EventType(item["event_type"]),
                timestamp=datetime.fromisoformat(item["timestamp"]),
                payload=json.loads(item["payload"]),
            )
            events.append(event)

        # Handle pagination
        while "LastEvaluatedKey" in response:
            response = self.events_ddb_table.query(
                KeyConditionExpression="run_id = :run_id",
                ExpressionAttributeValues={":run_id": run_id},
                ScanIndexForward=True,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            for item in response.get("Items", []):
                event = Event(
                    event_id=item["event_id"],
                    run_id=run_id,
                    event_type=EventType(item["event_type"]),
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    payload=json.loads(item["payload"]),
                )
                events.append(event)

        return events

    # Compute

    async def invoke_step(self, step_payload: dict[str, Any]) -> None:
        """Enqueue step to SQS."""
        message_body = json.dumps(step_payload)

        # Use step_id + attempt as deduplication ID for FIFO queues
        dedup_id = f"{step_payload['run_id']}:{step_payload['step_id']}:{step_payload['attempt']}"

        try:
            self.sqs.send_message(
                QueueUrl=self.step_queue_url,
                MessageBody=message_body,
                MessageGroupId=step_payload["run_id"],  # For FIFO queues
                MessageDeduplicationId=dedup_id[:128],  # Max 128 chars
            )
        except ClientError as e:
            # If not a FIFO queue, send without group/dedup
            if "InvalidParameterValue" in str(e):
                self.sqs.send_message(
                    QueueUrl=self.step_queue_url,
                    MessageBody=message_body,
                )
            else:
                raise

    async def invoke_orchestrator(self, run_id: str) -> None:
        """Invoke orchestrator Lambda function."""
        if not self.orchestrator_function:
            # If no orchestrator function specified, skip (useful for local testing)
            return

        payload = {"run_id": run_id}

        try:
            self.lambda_client.invoke(
                FunctionName=self.orchestrator_function,
                InvocationType="Event",  # Async invocation
                Payload=json.dumps(payload),
            )
        except ClientError as e:
            print(f"Warning: Failed to invoke orchestrator: {e}")

    # Scheduling & messaging

    async def schedule_timer(self, run_id: str, timer_id: str, fire_at_iso: str) -> None:
        """Schedule timer using EventBridge."""
        rule_name = f"worldflow-timer-{run_id}-{timer_id}"[:64]  # Max 64 chars

        # Create one-time scheduled rule
        fire_at = datetime.fromisoformat(fire_at_iso)
        cron_expression = fire_at.strftime("cron(%M %H %d %m ? %Y)")

        try:
            self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                State="ENABLED",
                Description=f"Worldflow timer for run {run_id}",
            )

            # Add target: invoke orchestrator Lambda
            if self.orchestrator_function:
                target_input = json.dumps(
                    {
                        "run_id": run_id,
                        "timer_id": timer_id,
                        "event_type": "timer_fired",
                    }
                )

                self.events_client.put_targets(
                    Rule=rule_name,
                    Targets=[
                        {
                            "Id": "1",
                            "Arn": self._get_lambda_arn(self.orchestrator_function),
                            "Input": target_input,
                        }
                    ],
                )
        except ClientError as e:
            print(f"Warning: Failed to schedule timer: {e}")

    async def publish_signal(self, run_id: str, signal_name: str, payload: Any) -> None:
        """Publish signal by appending event and triggering orchestrator."""
        from worldflow.events import SignalReceivedEvent

        # Find signal request in events
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

        # Append SignalReceived event
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
        """Get API Gateway URL for signal."""
        # This would be configured during deployment
        api_gateway_url = os.environ.get("WORLDFLOW_API_GATEWAY_URL", "")
        return f"{api_gateway_url}/signal/{run_id}/{signal_name}"

    # Run management

    async def create_run(
        self,
        run_id: str,
        workflow_name: str,
        inputs: dict[str, Any],
        tags: dict[str, str] | None = None,
    ) -> None:
        """Create run record in DynamoDB."""
        self.runs_ddb_table.put_item(
            Item={
                "run_id": run_id,
                "workflow_name": workflow_name,
                "status": "running",
                "inputs": json.dumps(inputs),
                "started_at": datetime.utcnow().isoformat(),
                "tags": json.dumps(tags or {}),
            }
        )

    async def get_run_status(self, run_id: str) -> dict[str, Any]:
        """Get run status from DynamoDB."""
        response = self.runs_ddb_table.get_item(Key={"run_id": run_id})

        if "Item" not in response:
            raise ValueError(f"Run {run_id} not found")

        item = response["Item"]
        return {
            "run_id": run_id,
            "workflow_name": item["workflow_name"],
            "status": item["status"],
            "inputs": json.loads(item["inputs"]),
            "result": json.loads(item.get("result", "null")),
            "error": item.get("error"),
            "started_at": item["started_at"],
            "ended_at": item.get("ended_at"),
            "tags": json.loads(item.get("tags", "{}")),
        }

    async def list_runs(
        self,
        workflow_name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List runs from DynamoDB."""
        # TODO: Implement GSI for efficient filtering by workflow_name/status
        # For now, scan with filter (not efficient for production)

        scan_kwargs: dict[str, Any] = {"Limit": limit}

        filter_expressions = []
        expression_values = {}

        if workflow_name:
            filter_expressions.append("workflow_name = :workflow_name")
            expression_values[":workflow_name"] = workflow_name

        if status:
            filter_expressions.append("#status = :status")
            expression_values[":status"] = status
            scan_kwargs["ExpressionAttributeNames"] = {"#status": "status"}

        if filter_expressions:
            scan_kwargs["FilterExpression"] = " AND ".join(filter_expressions)
            scan_kwargs["ExpressionAttributeValues"] = expression_values

        response = self.runs_ddb_table.scan(**scan_kwargs)

        runs = []
        for item in response.get("Items", []):
            runs.append(
                {
                    "run_id": item["run_id"],
                    "workflow_name": item["workflow_name"],
                    "status": item["status"],
                    "started_at": item["started_at"],
                }
            )

        # Sort by started_at descending
        runs.sort(key=lambda x: x["started_at"], reverse=True)

        return runs[:limit]

    async def _update_run_status(self, run_id: str, events: list[Event]) -> None:
        """Update run status based on events."""
        for event in events:
            if event.event_type == EventType.WORKFLOW_COMPLETED:
                self.runs_ddb_table.update_item(
                    Key={"run_id": run_id},
                    UpdateExpression="SET #status = :status, #result = :result, ended_at = :ended_at",
                    ExpressionAttributeNames={"#status": "status", "#result": "result"},
                    ExpressionAttributeValues={
                        ":status": "completed",
                        ":result": json.dumps(event.payload.get("result")),
                        ":ended_at": datetime.utcnow().isoformat(),
                    },
                )
            elif event.event_type == EventType.WORKFLOW_FAILED:
                self.runs_ddb_table.update_item(
                    Key={"run_id": run_id},
                    UpdateExpression="SET #status = :status, #error = :error, ended_at = :ended_at",
                    ExpressionAttributeNames={"#status": "status", "#error": "error"},
                    ExpressionAttributeValues={
                        ":status": "failed",
                        ":error": event.payload.get("error"),
                        ":ended_at": datetime.utcnow().isoformat(),
                    },
                )

    def _get_lambda_arn(self, function_name: str) -> str:
        """Get Lambda function ARN."""
        # Format: arn:aws:lambda:region:account-id:function:function-name
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        return f"arn:aws:lambda:{self.region}:{account_id}:function:{function_name}"

