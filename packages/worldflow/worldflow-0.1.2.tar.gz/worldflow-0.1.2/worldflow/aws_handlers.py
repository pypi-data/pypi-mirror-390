"""AWS Lambda handlers for Worldflow."""

import asyncio
import json
import traceback
from datetime import datetime
from typing import Any
from uuid import uuid4


def create_orchestrator_handler(world):
    """
    Create Lambda handler for orchestrator.
    
    Usage in your Lambda:
        from worldflow.worlds import AWSWorld
        from worldflow.aws_handlers import create_orchestrator_handler
        
        world = AWSWorld()
        lambda_handler = create_orchestrator_handler(world)
    """

    def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
        """Lambda handler for orchestrator invocations."""
        try:
            # Extract run_id from event
            run_id = event.get("run_id")
            if not run_id:
                return {"statusCode": 400, "body": "Missing run_id"}

            # Run orchestrator
            from worldflow.runtime import Orchestrator

            orchestrator = Orchestrator(world)
            asyncio.run(orchestrator.run_orchestrator(run_id))

            return {"statusCode": 200, "body": f"Orchestrated run {run_id}"}

        except Exception as e:
            print(f"Orchestrator error: {e}")
            print(traceback.format_exc())
            return {"statusCode": 500, "body": str(e)}

    return lambda_handler


def create_step_handler(world):
    """
    Create Lambda handler for step execution.
    
    This handler processes messages from SQS queue.
    
    Usage in your Lambda:
        from worldflow.worlds import AWSWorld
        from worldflow.aws_handlers import create_step_handler
        
        world = AWSWorld()
        lambda_handler = create_step_handler(world)
    """

    def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
        """Lambda handler for step execution from SQS."""
        results = []

        for record in event.get("Records", []):
            try:
                # Parse SQS message
                body = json.loads(record["body"])
                
                run_id = body["run_id"]
                step_id = body["step_id"]
                function_name = body["function"]
                args = body["args"]
                kwargs = body["kwargs"]
                attempt = body["attempt"]
                retry_config = body.get("retry_policy", {})

                # Execute step
                result = asyncio.run(
                    _execute_step(
                        world,
                        run_id,
                        step_id,
                        function_name,
                        args,
                        kwargs,
                        attempt,
                        retry_config,
                    )
                )

                results.append(
                    {
                        "messageId": record["messageId"],
                        "status": "success",
                        "result": result,
                    }
                )

            except Exception as e:
                print(f"Step execution error: {e}")
                print(traceback.format_exc())
                results.append(
                    {
                        "messageId": record.get("messageId"),
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {"statusCode": 200, "results": results}

    return lambda_handler


async def _execute_step(
    world,
    run_id: str,
    step_id: str,
    function_name: str,
    args: list[Any],
    kwargs: dict[str, Any],
    attempt: int,
    retry_config: dict[str, Any],
) -> Any:
    """Execute a step and record result."""
    from worldflow.decorators import get_step_function
    from worldflow.events import StepCompletedEvent, StepFailedEvent
    from worldflow.retry import RetryPolicy, BackoffStrategy

    retry_policy = RetryPolicy(
        max_attempts=retry_config.get("max_attempts", 3),
        backoff=BackoffStrategy(retry_config.get("backoff", "exponential")),
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
                "result": _serialize(result),
                "duration_ms": duration_ms,
            },
        )
        await world.append_events(run_id, [event])

        # Trigger orchestrator
        await world.invoke_orchestrator(run_id)

        return result

    except Exception as e:
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
        await world.append_events(run_id, [event])

        if will_retry:
            # Re-enqueue with delay (SQS visibility timeout)
            # In practice, you'd set message visibility timeout
            import asyncio
            delay = retry_policy.get_delay_seconds(attempt)
            await asyncio.sleep(min(delay, 15))  # Max 15s in Lambda

            # Re-invoke step
            await world.invoke_step(
                {
                    "run_id": run_id,
                    "step_id": step_id,
                    "function": function_name,
                    "args": args,
                    "kwargs": kwargs,
                    "attempt": attempt + 1,
                    "retry_policy": retry_config,
                }
            )
        else:
            # No more retries; trigger orchestrator
            await world.invoke_orchestrator(run_id)

        raise


def create_timer_handler(world):
    """
    Create Lambda handler for timer events from EventBridge.
    
    Usage in your Lambda:
        from worldflow.worlds import AWSWorld
        from worldflow.aws_handlers import create_timer_handler
        
        world = AWSWorld()
        lambda_handler = create_timer_handler(world)
    """

    def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
        """Lambda handler for timer events."""
        try:
            run_id = event.get("run_id")
            timer_id = event.get("timer_id")

            if not run_id or not timer_id:
                return {"statusCode": 400, "body": "Missing run_id or timer_id"}

            # Fire timer
            asyncio.run(_fire_timer(world, run_id, timer_id))

            return {"statusCode": 200, "body": f"Timer {timer_id} fired for run {run_id}"}

        except Exception as e:
            print(f"Timer handler error: {e}")
            print(traceback.format_exc())
            return {"statusCode": 500, "body": str(e)}

    return lambda_handler


async def _fire_timer(world, run_id: str, timer_id: str) -> None:
    """Fire a timer."""
    from worldflow.events import TimerFiredEvent

    # Record timer fired
    event = TimerFiredEvent(
        event_id=f"evt_{uuid4().hex[:16]}",
        run_id=run_id,
        payload={"timer_id": timer_id},
    )
    await world.append_events(run_id, [event])

    # Trigger orchestrator
    await world.invoke_orchestrator(run_id)


def create_api_handler(world):
    """
    Create Lambda handler for API Gateway (signals/webhooks).
    
    Usage in your Lambda:
        from worldflow.worlds import AWSWorld
        from worldflow.aws_handlers import create_api_handler
        
        world = AWSWorld()
        lambda_handler = create_api_handler(world)
    """

    def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
        """Lambda handler for API Gateway requests."""
        try:
            # Extract path parameters
            path_params = event.get("pathParameters", {})
            run_id = path_params.get("run_id")
            signal_name = path_params.get("signal_name")

            if not run_id or not signal_name:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing run_id or signal_name"}),
                }

            # Parse body
            body = json.loads(event.get("body", "{}"))
            payload_value = body.get("value")

            # Publish signal
            asyncio.run(world.publish_signal(run_id, signal_name, payload_value))

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"status": "ok", "run_id": run_id, "signal_name": signal_name}
                ),
            }

        except ValueError as e:
            return {"statusCode": 404, "body": json.dumps({"error": str(e)})}
        except Exception as e:
            print(f"API handler error: {e}")
            print(traceback.format_exc())
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return lambda_handler


def _serialize(obj: Any) -> Any:
    """Serialize object to JSON-compatible format."""
    if obj is None:
        return None
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)

