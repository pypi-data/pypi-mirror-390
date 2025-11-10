"""Core shared utilities and foundational components for the Giskard library ecosystem.

This package provides minimal, essential building blocks that are shared across
all Giskard packages, including discriminated unions, error handling, type
definitions, configuration patterns, and serialization utilities.
"""

from .discriminated import DISCRIMINATOR, Discriminated, discriminated_base
from .errors import Error

__all__ = [
    # Discriminated unions
    "Discriminated",
    "discriminated_base",
    "DISCRIMINATOR",
    # Error handling
    "Error",
]
