"""util.py.

Utility functions
"""
import json
import os
import urllib.parse
from typing import Dict


def parse_path(path_or_url: str) -> str:
    """Parse path."""
    parsed_input = urllib.parse.urlparse(path_or_url)
    if parsed_input.netloc != "":
        return parsed_input.path
    elif path_or_url.startswith("/"):
        return path_or_url[1:]
    else:
        raise ValueError(
            ('Could not parse user input (expected either <scheme>://<host>/<path> or "/<path>", ' f"got {path_or_url}")
        )


def get_checked_filepath(raw_filepath: str) -> str:
    """Confirm that a local path is valid and writable, and return the absolute path."""
    try:
        checked_filepath = os.path.abspath(raw_filepath)
    except ValueError:
        raise ValueError(f'Could not resolve valid filepath from "{raw_filepath}"')

    # raise OSError if not writable
    open(checked_filepath, "w+")

    return checked_filepath


def process_data_arg(raw_input: str) -> Dict:
    """Implements a subset of curl-like processing.

    Using --data args, like @path/to/file
    """
    if raw_input.startswith("@"):
        filepath = os.path.abspath(raw_input[1:])
        with open(filepath) as content_f:
            content = json.load(content_f)
    else:
        content = json.loads(raw_input)

    return content
