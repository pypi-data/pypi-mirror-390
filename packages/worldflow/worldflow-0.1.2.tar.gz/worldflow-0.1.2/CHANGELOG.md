# Changelog

All notable changes to Worldflow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-11-06

### Fixed
- Fixed `LocalWorld` to properly support `:memory:` databases by using temporary files instead of true in-memory SQLite (which doesn't persist across connections).
- This provides the expected ephemeral database behavior for testing without the connection lifecycle issues.

## [0.1.1] - 2025-11-06 [YANKED]

### Fixed
- Attempted fix for `:memory:` databases (broken - do not use)

## [0.1.0] - 2025-11-06

### Added

#### Core Framework
- Complete event-sourced orchestration engine with deterministic replay
- `@workflow` decorator for defining orchestration logic
- `@step` decorator with automatic retry policies
- Durable primitives: `sleep()`, `signal()`, `parallel()`
- `RetryPolicy` with exponential backoff strategies
- Event types for complete audit trail

#### Worlds (Pluggable Backends)
- **LocalWorld**: SQLite-based backend for local development
  - In-process async step execution
  - Timer scheduling via asyncio
  - Zero configuration required
- **AWSWorld**: Production-ready AWS backend
  - DynamoDB for event log and run metadata
  - SQS FIFO queue for step execution
  - Lambda for serverless orchestration and steps
  - EventBridge for timer scheduling
  - API Gateway for signal/webhook endpoints

#### Developer Tools
- CLI with 6 commands:
  - `worldflow dev` - Start development server with web dashboard
  - `worldflow start` - Start workflow execution
  - `worldflow ps` - List workflow runs
  - `worldflow logs` - View detailed event logs
  - `worldflow signal` - Send signals to workflows
  - `worldflow replay` - Replay workflow for debugging
- Web dashboard (FastAPI-based) with:
  - Run listing and filtering
  - Detailed event timeline
  - Input/output inspection
  - RESTful API endpoints

#### Infrastructure
- Complete AWS CDK stack for one-command deployment
- Lambda handlers for orchestrator, step executor, and API
- Infrastructure setup utilities (`worldflow.aws_setup`)
- IAM permissions and security best practices

#### Documentation
- Comprehensive README with quick start
- QUICKSTART.md - 5-minute tutorial
- ARCHITECTURE.md - Technical deep-dive
- AWS_DEPLOYMENT.md - Complete AWS deployment guide
- CONTRIBUTING.md - Contribution guidelines

#### Examples
- User onboarding workflow (email, payment, signals)
- Batch processing with parallel execution
- FastAPI integration example
- AWS production deployment example

#### Testing
- Complete test suite with pytest
- Test coverage for core functionality

### Technical Details

- **Event Sourcing**: All workflow state changes captured as immutable events
- **Deterministic Replay**: Workflows replay from event log on resume
- **At-Least-Once Semantics**: Steps execute at least once with automatic idempotency keys
- **Type Safety**: Full type hints compatible with mypy/pyright
- **Python 3.11+**: Modern async/await throughout

---

## [Unreleased]

### Planned
- GCP World implementation (Firestore + Cloud Run + Pub/Sub)
- Kubernetes World implementation (Postgres + K8s Jobs)
- Workflow versioning support
- OpenTelemetry integration
- Circuit breakers and dead letter queues
- CRON/scheduled workflows
- Workflow-to-workflow communication
- Enhanced observability features

---

[0.1.0]: https://github.com/ptsadi/worldflow/releases/tag/v0.1.0

