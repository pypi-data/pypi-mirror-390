"""Masterblog-core: reusable blog engine core.

This package provides:
- Blog and Post models
- Storage helpers for JSON persistence

It is intended as a learning project and for reuse in other
projects, not for production use.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("masterblog-core")
except PackageNotFoundError:
    # package is not installed, fallback for local dev
    __version__ = "0.0.0"

from .models import Blog, Post
from . import storage

__all__ = ["Blog", "Post", "storage", "__version__"]
