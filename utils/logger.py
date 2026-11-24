"""Backward-compatible logger shim."""
from core.logging import setup_logger

__all__ = ["setup_logger"]

# Preserve previous side-effect behavior.
setup_logger()
