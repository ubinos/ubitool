"""ubitool - A toolbox for ubinos development."""

__version__ = "1.0.0"
__author__ = "ubinos team"
__description__ = "A toolbox for ubinos development"

from .main import app

def cli():
    """CLI entry point for ubitool."""
    app()

__all__ = ["app", "cli"]