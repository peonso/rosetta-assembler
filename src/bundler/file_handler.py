# src/bundler/file_handler.py (Updated with safety checks)
import os
from pathspec import PathSpec
# Import the new constants from config
from config import GLOBAL_IGNORE_PATTERNS, MAX_TOTAL_FILES, MAX_TOTAL_SIZE_MB, MAX_DIRECTORY_DEPTH

# ... (The load_gitignore_patterns function is unchanged)
def load_gitignore_patterns(root_path):
    """
    Finds all .gitignore files in the directory tree and parses their patterns.
    """
    # ... (no changes here)
    gitignore_patterns = set()
    for dirpath, _, filenames in os.walk(root_path):
        if '.gitignore' in filenames:
            gitignore_path = os.path.join(dirpath, '.gitignore')
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith('#'):
                            relative_dir = os.path.relpath(dirpath, root_path)
                            if relative_dir == '.':
                                gitignore_patterns.add(stripped_line)
                            else:
                                pattern = os.path.join(relative_dir, stripped_line)
                                gitignore_patterns.add(pattern.replace(os.sep, '/'))
            except Exception as e:
                print(f"Warning: Could not read or parse {gitignore_path}: {e}")

    return gitignore_patterns

# --- The get_all_files function is replaced with this new version ---
def get_all_files(root_dir):
    """
    Walks through a directory and returns a list of all non-ignored files,
    respecting safety limits.
    """
    abs_root_dir = os.path.abspath(root_dir)
    
    project_gitignore_patterns = load_gitignore_patterns(abs_root_dir)
    combined_patterns = set(GLOBAL_IGNORE_PATTERNS) | project_gitignore_patterns
    spec = PathSpec.from_lines('gitwildmatch', combined_patterns)
    
    valid_files = []
    total_size = 0
    max_size_bytes = MAX_TOTAL_SIZE_MB * 1024 * 1024

    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        # --- Depth Check ---
        depth = root[len(abs_root_dir) + len(os.path.sep):].count(os.path.sep)
        if depth >= MAX_DIRECTORY_DEPTH:
            print(f"Warning: Reached max directory depth of {MAX_DIRECTORY_DEPTH}. Skipping subdirectories of {root}.")
            dirs[:] = [] # Stop descending further into this branch

        # Filter ignored paths
        all_paths_relative = [os.path.relpath(os.path.join(root, name), abs_root_dir).replace(os.sep, '/') for name in dirs + files]
        ignored_paths = set(spec.match_files(all_paths_relative))
        
        dirs[:] = [d for d in dirs if os.path.relpath(os.path.join(root, d), abs_root_dir).replace(os.sep, '/') not in ignored_paths]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, abs_root_dir).replace(os.sep, '/')

            if relative_file_path not in ignored_paths:
                # --- File Count Check ---
                if len(valid_files) >= MAX_TOTAL_FILES:
                    print(f"Warning: Reached max file limit of {MAX_TOTAL_FILES}. No more files will be added.")
                    return valid_files # Stop processing and return what we have

                # --- Total Size Check ---
                try:
                    file_size = os.path.getsize(file_path)
                    if total_size + file_size > max_size_bytes:
                        print(f"Warning: Reached max total size of {MAX_TOTAL_SIZE_MB}MB. No more files will be added.")
                        return valid_files # Stop processing and return what we have
                    
                    total_size += file_size
                    valid_files.append(file_path)
                except OSError as e:
                    print(f"Warning: Could not access file {file_path}: {e}")

    return valid_files