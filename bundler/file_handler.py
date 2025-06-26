# bundler/file_handler.py (Updated to pass root_dir)
import os
from .filter import is_ignored

def get_all_files(root_dir):
    """
    Walks through a directory and returns a list of all non-ignored files.
    """
    valid_files = []
    # Ensure root_dir is an absolute path for reliable relative path calculation
    abs_root_dir = os.path.abspath(root_dir)

    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        # We now pass the original root_dir to is_ignored
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), abs_root_dir)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not is_ignored(file_path, abs_root_dir):
                valid_files.append(file_path)
    
    return valid_files