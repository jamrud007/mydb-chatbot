"""Backward-compatible structured logging shim."""
from core.structured_logging import (
    CompatibilityWrapper,
    StructuredLogger,
    TimingContext,
    setup_structured_logging,
)

__all__ = [
    "StructuredLogger",
    "TimingContext",
    "setup_structured_logging",
    "CompatibilityWrapper",
]
