"""Provide functions to keep track of auto-incremented primary keys."""
from masterblog_core.storage import read_json_file, write_json_file


def get_next_id(seq_file_path, model: str) -> int:
    """Return auto-incremented unique id for the given model
    or None if model is not found.

    Also, update the new id in the sequence dict and save it persistently.
    """
    post_id = read_json_file(seq_file_path).get(model, None)
    if post_id is not None:
        post_id += 1
    return post_id


def save_id_to_sequence(seq_file_path, model: str, post_id: int = None):
    """Save the given id for a model persistently."""
    data = read_json_file(seq_file_path)
    data[model] = post_id
    write_json_file(seq_file_path, data)


def main():
    """Main function for testing."""


if __name__ == "__main__":
    main()
