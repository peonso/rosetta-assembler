# bundler/filter.py
import os
from config import IGNORE_DIRS, IGNORE_EXTENSIONS

def is_ignored(path):
    """
    Check if a file or directory should be ignored.
    - Checks against the IGNORE_DIRS set from config.
    - Checks against the IGNORE_EXTENSIONS set from config.
    - Path components are checked (e.g., 'src/components' contains 'components').
    """
    # Check if any part of the path is in the ignore list for directories
    path_parts = path.split(os.sep)
    if any(part in IGNORE_DIRS for part in path_parts):
        return True

    # Check the file extension
    _, extension = os.path.splitext(path)
    if extension in IGNORE_EXTENSIONS:
        return True

    return False