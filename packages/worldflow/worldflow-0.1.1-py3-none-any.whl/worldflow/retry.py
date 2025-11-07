"""Retry policies for step execution."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BackoffStrategy(str, Enum):
    """Backoff strategy for retries."""

    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryPolicy:
    """Configuration for step retry behavior."""

    max_attempts: int = 3
    backoff: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 3600.0  # 1 hour
    multiplier: float = 2.0
    
    def get_delay_seconds(self, attempt: int) -> float:
        """Calculate delay for the given attempt number (0-indexed)."""
        if attempt == 0:
            return 0.0
            
        if self.backoff == BackoffStrategy.CONSTANT:
            delay = self.initial_delay_seconds
        elif self.backoff == BackoffStrategy.LINEAR:
            delay = self.initial_delay_seconds * attempt
        else:  # EXPONENTIAL
            delay = self.initial_delay_seconds * (self.multiplier ** (attempt - 1))
        
        return min(delay, self.max_delay_seconds)
    
    def should_retry(self, attempt: int) -> bool:
        """Check if we should retry after the given attempt."""
        return attempt < self.max_attempts


# Common retry policies
NO_RETRY = RetryPolicy(max_attempts=1)
QUICK_RETRY = RetryPolicy(max_attempts=3, backoff=BackoffStrategy.CONSTANT, initial_delay_seconds=1.0)
STANDARD_RETRY = RetryPolicy(max_attempts=5, backoff=BackoffStrategy.EXPONENTIAL)
AGGRESSIVE_RETRY = RetryPolicy(max_attempts=10, backoff=BackoffStrategy.EXPONENTIAL, multiplier=1.5)

