"""World implementations for different backends."""

from worldflow.worlds.local import LocalWorld

__all__ = ["LocalWorld"]

# Optional AWS import
try:
    from worldflow.worlds.aws import AWSWorld
    __all__.append("AWSWorld")
except ImportError:
    pass
