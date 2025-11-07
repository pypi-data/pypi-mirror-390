"""Lambda handler for Worldflow orchestrator."""

from worldflow.worlds import AWSWorld
from worldflow.aws_handlers import create_orchestrator_handler

# Initialize World
world = AWSWorld()

# Create handler
lambda_handler = create_orchestrator_handler(world)

