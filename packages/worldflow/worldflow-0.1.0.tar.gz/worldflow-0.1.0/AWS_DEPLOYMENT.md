# 🚀 Deploying Worldflow on AWS

Complete guide to deploying Worldflow in production on AWS.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                         │
│  (FastAPI/Django/Flask with Worldflow workflows)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      AWSWorld                                │
└────────────────────────┬────────────────────────────────────┘
           │             │             │             │
           ↓             ↓             ↓             ↓
    ┌─────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
    │DynamoDB │   │   SQS    │  │  Lambda  │  │EventBridge│
    │         │   │          │  │          │  │          │
    │ Events  │   │  Steps   │  │Orchestr. │  │  Timers  │
    │  Runs   │   │  Queue   │  │  Steps   │  │          │
    └─────────┘   └──────────┘  └──────────┘  └──────────┘
```

---

## 📦 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured: `aws configure`
3. **Python 3.11+**
4. **Worldflow** installed: `pip install "worldflow[aws]"`

---

## 🚀 Option 1: Quick Setup (Python Script)

### Step 1: Create Infrastructure

```python
from worldflow.aws_setup import setup_worldflow_infrastructure

# Create all resources
resources = setup_worldflow_infrastructure(
    region="us-east-1",
    events_table="worldflow-events",
    runs_table="worldflow-runs",
    step_queue="worldflow-steps.fifo"
)
```

Or via CLI:

```bash
python -m worldflow.aws_setup setup
```

This creates:
- ✅ DynamoDB tables (events, runs)
- ✅ SQS FIFO queue (steps)

### Step 2: Deploy Lambda Functions

You still need to manually deploy Lambda functions:

1. **Package your workflow code**:

```bash
# Create deployment package
mkdir lambda_package
cd lambda_package

# Install worldflow
pip install "worldflow[aws]" -t .

# Copy your workflow code
cp ../my_workflows.py .
cp ../lambda_handler.py .

# Create Lambda handler
cat > handler.py << 'EOF'
from worldflow.worlds import AWSWorld
from worldflow.aws_handlers import create_orchestrator_handler

world = AWSWorld()
lambda_handler = create_orchestrator_handler(world)
EOF

# Zip it
zip -r lambda_package.zip .
```

2. **Create Lambda functions** (orchestrator, step executor):

```bash
# Orchestrator Lambda
aws lambda create-function \
    --function-name worldflow-orchestrator \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT_ID:role/worldflow-lambda-role \
    --handler handler.lambda_handler \
    --zip-file fileb://lambda_package.zip \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables={WORLDFLOW_EVENTS_TABLE=worldflow-events,WORLDFLOW_RUNS_TABLE=worldflow-runs,WORLDFLOW_STEP_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/ACCOUNT_ID/worldflow-steps.fifo}

# Step Executor Lambda
aws lambda create-function \
    --function-name worldflow-step-executor \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT_ID:role/worldflow-lambda-role \
    --handler step_handler.lambda_handler \
    --zip-file fileb://lambda_package.zip \
    --timeout 300 \
    --memory-size 1024
```

---

## 🚀 Option 2: AWS CDK (Recommended)

### Step 1: Install CDK

```bash
npm install -g aws-cdk
cd infrastructure/cdk
npm install
```

### Step 2: Bootstrap CDK

```bash
cdk bootstrap
```

### Step 3: Deploy

```bash
cdk deploy
```

This deploys:
- ✅ DynamoDB tables
- ✅ SQS queue
- ✅ Lambda functions (orchestrator, step executor, API handler)
- ✅ API Gateway (for signals/webhooks)
- ✅ IAM roles & permissions

### Step 4: Get Outputs

CDK will output:
```
Outputs:
WorldflowStack.ApiUrl = https://abc123.execute-api.us-east-1.amazonaws.com/prod/
WorldflowStack.EventsTableName = worldflow-events
WorldflowStack.RunsTableName = worldflow-runs
WorldflowStack.StepQueueUrl = https://sqs.us-east-1.amazonaws.com/.../worldflow-steps.fifo
WorldflowStack.OrchestratorFunctionName = worldflow-orchestrator
```

---

## 🔧 Configuration

### Environment Variables

Set these in your application (Lambda, EC2, ECS, etc.):

```bash
export WORLDFLOW_EVENTS_TABLE="worldflow-events"
export WORLDFLOW_RUNS_TABLE="worldflow-runs"
export WORLDFLOW_STEP_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/123456789/worldflow-steps.fifo"
export WORLDFLOW_ORCHESTRATOR_FUNCTION="worldflow-orchestrator"
export WORLDFLOW_API_GATEWAY_URL="https://abc123.execute-api.us-east-1.amazonaws.com/prod"
export AWS_REGION="us-east-1"
```

### In Your Code

```python
from worldflow import workflow, step
from worldflow.worlds import AWSWorld
from worldflow.runtime import Orchestrator

# Initialize AWSWorld
world = AWSWorld()  # Reads from environment variables

# Use in your workflows
@step
async def my_step():
    # Your code here
    pass

@workflow
async def my_workflow():
    await my_step()

# Start workflow
orchestrator = Orchestrator(world)
await orchestrator.start_workflow(
    run_id="my_run_123",
    my_workflow,
    {},
    "my_workflow"
)
```

---

## 📊 IAM Permissions

### Lambda Execution Role

Your Lambda functions need these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/worldflow-events",
        "arn:aws:dynamodb:*:*:table/worldflow-runs",
        "arn:aws:dynamodb:*:*:table/worldflow-runs/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:*:*:worldflow-steps.fifo"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:worldflow-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutRule",
        "events:PutTargets",
        "events:DeleteRule",
        "events:RemoveTargets"
      ],
      "Resource": "arn:aws:events:*:*:rule/worldflow-timer-*"
    }
  ]
}
```

---

## 🧪 Testing Your Deployment

### 1. Create a Test Workflow

```python
# test_workflow.py
from worldflow import workflow, step, sleep

@step
async def hello(name: str) -> str:
    print(f"Hello, {name}!")
    return f"Greeted {name}"

@workflow
async def test_workflow(name: str):
    result = await hello(name)
    await sleep("10s")  # Durable sleep!
    await hello(f"{name} again")
    return result
```

### 2. Deploy Workflow

```python
from worldflow.worlds import AWSWorld
from worldflow.runtime import Orchestrator
from test_workflow import test_workflow

world = AWSWorld()
orchestrator = Orchestrator(world)

# Start workflow
await orchestrator.start_workflow(
    run_id="test_001",
    test_workflow,
    {"name": "World"},
    "test_workflow"
)
```

### 3. Check Status

```python
# Check run status
status = await world.get_run_status("test_001")
print(f"Status: {status['status']}")

# Load events
events = await world.load_events("test_001")
for event in events:
    print(f"{event.event_type}: {event.payload}")
```

---

## 📈 Monitoring

### CloudWatch Logs

View logs:
```bash
# Orchestrator logs
aws logs tail /aws/lambda/worldflow-orchestrator --follow

# Step executor logs
aws logs tail /aws/lambda/worldflow-step-executor --follow
```

### CloudWatch Metrics

Track:
- Lambda invocations
- Lambda duration
- Lambda errors
- SQS messages (sent/received/deleted)
- DynamoDB read/write capacity

### X-Ray Tracing

Enable X-Ray on Lambda functions for distributed tracing.

---

## 💰 Cost Optimization

### Pay-Per-Request DynamoDB

- First 25 GB storage: Free
- On-demand pricing: $1.25/million writes, $0.25/million reads
- **Estimate**: $5-10/month for moderate usage

### Lambda

- First 1M requests/month: Free
- $0.20/million requests after
- Compute: $0.0000166667 per GB-second
- **Estimate**: $10-20/month for moderate usage

### SQS

- First 1M requests/month: Free
- $0.40/million requests after
- **Estimate**: $1-5/month

### Total Estimate

**Small workload** (1000 workflows/day): **< $20/month**  
**Medium workload** (10,000 workflows/day): **$50-100/month**  
**Large workload** (100,000 workflows/day): **$300-500/month**

### Optimization Tips

1. **Use FIFO queues** to reduce duplicate processing
2. **Batch DynamoDB writes** when possible
3. **Set appropriate Lambda memory** (right-size)
4. **Use Reserved Capacity** for predictable workloads (DynamoDB)
5. **Archive old events** to S3 (lifecycle policy)

---

## 🔒 Security Best Practices

### 1. Encryption

- Enable encryption at rest for DynamoDB
- Enable encryption for SQS queues
- Use AWS KMS for key management

### 2. VPC Configuration

- Deploy Lambda functions in VPC for private resources
- Use VPC endpoints for DynamoDB/SQS access (no internet)

### 3. IAM Least Privilege

- Give Lambda functions only required permissions
- Use separate roles for orchestrator vs step executor

### 4. Secrets Management

- Use AWS Secrets Manager for API keys
- Never hardcode credentials

```python
import boto3

@step
async def call_api():
    # Get secret from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='my-api-key')
    api_key = json.loads(secret['SecretString'])['api_key']
    
    # Use api_key...
```

---

## 🚨 Troubleshooting

### Workflow not starting

1. Check CloudWatch logs for orchestrator Lambda
2. Verify environment variables are set correctly
3. Ensure IAM permissions are correct

### Steps not executing

1. Check SQS queue for messages
2. Check CloudWatch logs for step executor Lambda
3. Verify step functions are importable in Lambda

### Timers not firing

1. Check EventBridge rules
2. Verify orchestrator Lambda has EventBridge invoke permissions
3. Check CloudWatch logs

### Common Errors

**Error**: `Module not found`  
**Fix**: Ensure all dependencies are in Lambda package

**Error**: `Table does not exist`  
**Fix**: Verify table names in environment variables

**Error**: `Access denied`  
**Fix**: Check IAM permissions

---

## 🔄 Updates & Migrations

### Updating Workflow Code

1. Package new code
2. Update Lambda functions:

```bash
zip -r lambda_package.zip .
aws lambda update-function-code \
    --function-name worldflow-orchestrator \
    --zip-file fileb://lambda_package.zip
```

3. Existing workflows continue running (durable!)

### Schema Migrations

Worldflow events are JSON. Add fields with defaults:

```python
# Old
payload = {"step_id": "123"}

# New (backwards compatible)
payload = {"step_id": "123", "new_field": "default"}
```

---

## 🎓 Next Steps

1. **Read** [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
2. **Try** the AWS example: `examples/aws_workflow.py`
3. **Monitor** your workflows with CloudWatch
4. **Scale** by increasing Lambda concurrency
5. **Optimize** based on CloudWatch metrics

---

## 📚 Additional Resources

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)

---

**Ready to deploy!** 🚀

Questions? Open an issue or check the docs.

