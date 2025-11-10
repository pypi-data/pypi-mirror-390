"""Provide functions for persistent data storage.

This package exports the following functions:
- `read_json_file`: Read data from a JSON file.
- `write_json_file`: Write data to a JSON file.
- `get_next_id`: Return a new id for a model.
- `save_id_to_sequence`: Save current id persistently.

"""
from .filestore import read_json_file, write_json_file
from .sequence import get_next_id, save_id_to_sequence

__all__ = ["read_json_file", "write_json_file", "get_next_id", "save_id_to_sequence"]
