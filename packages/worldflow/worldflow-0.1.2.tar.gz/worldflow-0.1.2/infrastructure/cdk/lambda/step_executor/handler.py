"""Lambda handler for Worldflow step executor."""

from worldflow.worlds import AWSWorld
from worldflow.aws_handlers import create_step_handler

# Initialize World
world = AWSWorld()

# Create handler
lambda_handler = create_step_handler(world)

