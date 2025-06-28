# src/bundler/file_handler.py (With binary detection)
import os
from pathspec import PathSpec
from .config import GLOBAL_IGNORE_PATTERNS
from .heuristics import calculate_importance_score

def is_binary_file(filepath, chunk_size=1024):
    """
    Heuristically determine if a file is binary by checking for null bytes.
    Returns True if the file is likely binary, False otherwise.
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(chunk_size)
        return b'\0' in chunk
    except IOError:
        return True # Can't read, treat as binary/inaccessible

def load_gitignore_patterns(root_path):
    """Finds all .gitignore files and parses their patterns."""
    gitignore_patterns = set()
    for dirpath, _, filenames in os.walk(root_path):
        if '.gitignore' in filenames:
            gitignore_path = os.path.join(dirpath, '.gitignore')
            try:
                with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith('#'):
                            # Patterns in sub-gitignores are relative to that directory
                            relative_pattern_dir = os.path.relpath(dirpath, root_path)
                            if relative_pattern_dir == '.':
                                gitignore_patterns.add(stripped_line)
                            else:
                                pattern = os.path.join(relative_pattern_dir, stripped_line).replace(os.sep, '/')
                                gitignore_patterns.add(pattern)
            except Exception as e:
                print(f"Warning: Could not read or parse {gitignore_path}: {e}")
    return gitignore_patterns

def get_all_files(root_dir, include_patterns, exclude_patterns, focus_patterns, target_size_bytes, max_files, max_depth):
    """
    Finds all valid files, scores them, and culls the list based on limits.
    Now returns a list of dictionaries with file metadata.
    """
    abs_root_dir = os.path.abspath(root_dir)
    
    project_gitignore_patterns = load_gitignore_patterns(abs_root_dir)
    all_exclude_patterns = set(GLOBAL_IGNORE_PATTERNS) | set(exclude_patterns) | project_gitignore_patterns
    
    include_spec = PathSpec.from_lines('gitwildmatch', include_patterns) if include_patterns else None
    exclude_spec = PathSpec.from_lines('gitwildmatch', all_exclude_patterns)
    focus_spec = PathSpec.from_lines('gitwildmatch', focus_patterns) if focus_patterns else None

    candidate_files = []
    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        depth = root[len(abs_root_dir) + len(os.path.sep):].count(os.path.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue

        dirs[:] = [d for d in dirs if not exclude_spec.match_file(os.path.relpath(os.path.join(root, d), abs_root_dir).replace(os.sep, '/'))]
        
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, abs_root_dir).replace(os.sep, '/')

            if exclude_spec.match_file(relative_path):
                if not (include_spec and include_spec.match_file(relative_path)):
                    continue
            
            if include_spec and not include_spec.match_file(relative_path):
                continue
            
            try:
                # NEW: Check if the file is binary.
                is_binary = is_binary_file(full_path)
                size = 0 if is_binary else os.path.getsize(full_path)
                
                score = calculate_importance_score(relative_path)
                if focus_spec and focus_spec.match_file(relative_path):
                    score += 1000
                    
                candidate_files.append({"path": full_path, "size": size, "score": score, "is_binary": is_binary})
            except OSError:
                continue

    candidate_files.sort(key=lambda x: x["score"], reverse=True)

    final_files = []
    total_size = 0
    for file_info in candidate_files:
        if len(final_files) >= max_files:
            print(f"Warning: Reached max file limit of {max_files}.")
            break
        
        # Don't add file if it exceeds target size, unless it's a binary file (size 0)
        if target_size_bytes and file_info["size"] > 0 and (total_size + file_info["size"]) > target_size_bytes:
            continue
            
        final_files.append(file_info)
        total_size += file_info["size"]

    if target_size_bytes and total_size > 0:
        print(f"Info: Bundle created with total size {total_size/1024:.2f}k (target was {target_size_bytes/1024:.2f}k).")
         
    return final_files