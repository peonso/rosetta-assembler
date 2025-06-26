# bundler/filter.py (Refactored to use pathspec)
import os
from pathspec import PathSpec
from config import DEFAULT_IGNORE_PATTERNS

# We compile the patterns once when the module is imported for efficiency.
# This creates a PathSpec object from our list of .gitignore-style patterns.
ignore_spec = PathSpec.from_lines('gitwildmatch', DEFAULT_IGNORE_PATTERNS)

def is_ignored(path, root_path):
    """
    Check if a file or directory should be ignored using pathspec.
    
    Args:
        path (str): The full, absolute path to the file or directory.
        root_path (str): The absolute path to the root of the project being scanned.
    
    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    # pathspec works with relative paths, so we calculate it.
    relative_path = os.path.relpath(path, root_path)
    
    # For Windows, pathspec expects forward slashes
    if os.sep == '\\':
        relative_path = relative_path.replace('\\', '/')

    return ignore_spec.match_file(relative_path)