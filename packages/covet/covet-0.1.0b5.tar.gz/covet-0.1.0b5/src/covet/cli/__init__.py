"""
CovetPy CLI Module

Command-line interface tools for CovetPy framework.
"""

from .migrations import main as migrations_main

__all__ = ["migrations_main"]
