#!/usr/bin/env python3
"""AWS CDK app for Worldflow infrastructure."""

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
)


class WorldflowStack(Stack):
    """CDK Stack for Worldflow infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables
        events_table = dynamodb.Table(
            self,
            "EventsTable",
            table_name="worldflow-events",
            partition_key=dynamodb.Attribute(
                name="run_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="event_idx", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,  # Don't delete data on stack delete
        )

        runs_table = dynamodb.Table(
            self,
            "RunsTable",
            table_name="worldflow-runs",
            partition_key=dynamodb.Attribute(
                name="run_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Add GSI for querying by workflow_name and status
        runs_table.add_global_secondary_index(
            index_name="workflow-status-index",
            partition_key=dynamodb.Attribute(
                name="workflow_name", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
        )

        # SQS Queue for steps
        step_queue = sqs.Queue(
            self,
            "StepQueue",
            queue_name="worldflow-steps.fifo",
            fifo=True,
            content_based_deduplication=False,
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
        )

        # Lambda Layer with Worldflow
        worldflow_layer = lambda_.LayerVersion(
            self,
            "WorldflowLayer",
            code=lambda_.Code.from_asset("../../"),  # Root of worldflow package
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Worldflow package",
        )

        # Orchestrator Lambda
        orchestrator_fn = lambda_.Function(
            self,
            "OrchestratorFunction",
            function_name="worldflow-orchestrator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/orchestrator"),
            handler="handler.lambda_handler",
            timeout=Duration.minutes(5),
            memory_size=512,
            layers=[worldflow_layer],
            environment={
                "WORLDFLOW_EVENTS_TABLE": events_table.table_name,
                "WORLDFLOW_RUNS_TABLE": runs_table.table_name,
                "WORLDFLOW_STEP_QUEUE_URL": step_queue.queue_url,
            },
        )

        # Grant permissions
        events_table.grant_read_write_data(orchestrator_fn)
        runs_table.grant_read_write_data(orchestrator_fn)
        step_queue.grant_send_messages(orchestrator_fn)

        # Step Executor Lambda
        step_executor_fn = lambda_.Function(
            self,
            "StepExecutorFunction",
            function_name="worldflow-step-executor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/step_executor"),
            handler="handler.lambda_handler",
            timeout=Duration.minutes(5),
            memory_size=1024,
            layers=[worldflow_layer],
            environment={
                "WORLDFLOW_EVENTS_TABLE": events_table.table_name,
                "WORLDFLOW_RUNS_TABLE": runs_table.table_name,
                "WORLDFLOW_STEP_QUEUE_URL": step_queue.queue_url,
                "WORLDFLOW_ORCHESTRATOR_FUNCTION": orchestrator_fn.function_name,
            },
        )

        # Grant permissions
        events_table.grant_read_write_data(step_executor_fn)
        runs_table.grant_read_write_data(step_executor_fn)
        orchestrator_fn.grant_invoke(step_executor_fn)

        # SQS trigger for step executor
        from aws_cdk.aws_lambda_event_sources import SqsEventSource

        step_executor_fn.add_event_source(
            SqsEventSource(step_queue, batch_size=10, max_batching_window=Duration.seconds(5))
        )

        # API Handler Lambda
        api_handler_fn = lambda_.Function(
            self,
            "ApiHandlerFunction",
            function_name="worldflow-api-handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/api_handler"),
            handler="handler.lambda_handler",
            timeout=Duration.seconds(30),
            memory_size=256,
            layers=[worldflow_layer],
            environment={
                "WORLDFLOW_EVENTS_TABLE": events_table.table_name,
                "WORLDFLOW_RUNS_TABLE": runs_table.table_name,
                "WORLDFLOW_ORCHESTRATOR_FUNCTION": orchestrator_fn.function_name,
            },
        )

        # Grant permissions
        events_table.grant_read_write_data(api_handler_fn)
        runs_table.grant_read_write_data(api_handler_fn)
        orchestrator_fn.grant_invoke(api_handler_fn)

        # API Gateway
        api = apigateway.RestApi(
            self,
            "WorldflowApi",
            rest_api_name="Worldflow API",
            description="Worldflow signals and webhooks",
        )

        # /signal/{run_id}/{signal_name} endpoint
        signal_resource = api.root.add_resource("signal")
        run_resource = signal_resource.add_resource("{run_id}")
        signal_name_resource = run_resource.add_resource("{signal_name}")

        signal_name_resource.add_method(
            "POST", apigateway.LambdaIntegration(api_handler_fn)
        )

        # EventBridge rule for orchestrator (can be triggered by timers)
        # Note: Timer rules are created dynamically by workflows

        # Outputs
        cdk.CfnOutput(
            self, "ApiUrl", value=api.url, description="API Gateway URL for signals"
        )

        cdk.CfnOutput(
            self,
            "EventsTableName",
            value=events_table.table_name,
            description="DynamoDB events table",
        )

        cdk.CfnOutput(
            self,
            "RunsTableName",
            value=runs_table.table_name,
            description="DynamoDB runs table",
        )

        cdk.CfnOutput(
            self, "StepQueueUrl", value=step_queue.queue_url, description="SQS queue URL"
        )

        cdk.CfnOutput(
            self,
            "OrchestratorFunctionName",
            value=orchestrator_fn.function_name,
            description="Orchestrator Lambda function",
        )


app = cdk.App()
WorldflowStack(app, "WorldflowStack")
app.synth()

