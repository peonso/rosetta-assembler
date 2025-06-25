# bundler/file_handler.py
import os
from .filter import is_ignored # Note the '.' because it's in the same package

def get_all_files(root_dir):
    """
    Walks through a directory and returns a list of all non-ignored files.
    """
    valid_files = []
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Filter out ignored directories so os.walk doesn't even enter them
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not is_ignored(file_path):
                valid_files.append(file_path)
    
    return valid_files