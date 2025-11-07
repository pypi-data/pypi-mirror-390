# Worldflow AWS CDK Infrastructure

This directory contains AWS CDK code to deploy Worldflow on AWS.

## Prerequisites

```bash
npm install -g aws-cdk
pip install aws-cdk-lib constructs
```

## Quick Deploy

```bash
# Install dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy
cdk deploy
```

## What Gets Deployed

- **DynamoDB Tables**: Events and runs storage
- **SQS Queue**: Step execution queue (FIFO)
- **Lambda Functions**:
  - Orchestrator: Processes workflow events
  - Step Executor: Executes workflow steps
  - API Handler: Handles signals/webhooks
- **API Gateway**: REST API for signals
- **IAM Roles**: Necessary permissions

## After Deployment

CDK will output:
- API Gateway URL
- Table names
- Queue URL
- Lambda function names

Set these as environment variables in your workflow application.

## Cost Estimate

With AWS Free Tier:
- DynamoDB: First 25 GB free, then $0.25/GB
- Lambda: First 1M requests free, then $0.20/1M
- SQS: First 1M requests free, then $0.40/1M
- API Gateway: $3.50/million requests

**Typical cost for small workloads: < $5/month**

