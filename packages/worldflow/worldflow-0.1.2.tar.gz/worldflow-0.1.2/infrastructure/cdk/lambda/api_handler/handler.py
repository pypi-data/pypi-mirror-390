"""Lambda handler for Worldflow API (signals/webhooks)."""

from worldflow.worlds import AWSWorld
from worldflow.aws_handlers import create_api_handler

# Initialize World
world = AWSWorld()

# Create handler
lambda_handler = create_api_handler(world)

