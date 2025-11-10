"""Provide data models for a blogging application.

This package exports the following modules:
- `Post`: Define a blog post with author, title, content, and likes.
- `Blog`: Define a collection of posts with management methods.
"""
from .blog import Blog
from .post import Post

__all__ = ["Blog", "Post"]
