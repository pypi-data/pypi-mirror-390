# Contributing to Worldflow

Thanks for your interest in contributing! Worldflow is an early-stage project and we welcome contributions of all kinds.

## Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/worldflow.git
cd worldflow
```

2. **Set up development environment**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

3. **Run tests**

```bash
pytest
```

4. **Type checking**

```bash
mypy worldflow
```

5. **Linting**

```bash
ruff check worldflow
ruff format worldflow
```

## Development Workflow

1. Create a new branch for your feature/fix
2. Make your changes
3. Add tests if applicable
4. Run tests and type checking
5. Submit a pull request

## Project Structure

```
worldflow/
├── worldflow/           # Core package
│   ├── decorators.py   # @workflow, @step decorators
│   ├── primitives.py   # sleep, signal, parallel
│   ├── runtime.py      # Orchestrator and replay logic
│   ├── events.py       # Event types
│   ├── retry.py        # Retry policies
│   ├── world.py        # World protocol
│   ├── worlds/         # World implementations
│   │   └── local.py    # LocalWorld
│   ├── cli/            # CLI commands
│   └── fastapi_integration.py
├── examples/           # Example workflows
├── tests/              # Test suite
└── docs/              # Documentation
```

## Adding a New World

To add support for a new backend (e.g., Azure, Cloudflare):

1. Create `worldflow/worlds/yourworld.py`
2. Implement the `World` protocol
3. Add necessary dependencies to `pyproject.toml` under optional dependencies
4. Add documentation and examples
5. Submit PR

## Code Style

- Use type hints everywhere
- Follow PEP 8
- Write docstrings for public APIs
- Keep functions focused and small
- Prefer async/await over callbacks

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good coverage of critical paths
- Use pytest fixtures for common setup

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new public APIs
- Include examples for new features
- Update CHANGELOG.md

## Questions?

Open an issue or start a discussion!

## Code of Conduct

Be kind, respectful, and constructive. We're all here to build something great together.

