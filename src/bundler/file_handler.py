# src/bundler/file_handler.py (Synchronized Version)
import os
from pathspec import PathSpec
from config import GLOBAL_IGNORE_PATTERNS

def load_gitignore_patterns(root_path):
    # ... (this function is unchanged)
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


def get_all_files(root_dir, include_patterns, exclude_patterns, focus_patterns, target_size_bytes, max_files, max_depth):
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

        for name in dirs + files:
            full_path = os.path.join(root, name)
            relative_path = os.path.relpath(full_path, abs_root_dir).replace(os.sep, '/')
            
            if exclude_spec.match_file(relative_path) and (not include_spec or not include_spec.match_file(relative_path)):
                if os.path.isdir(full_path):
                    dirs.remove(name) # Don't descend into excluded dirs
                continue

            if os.path.isfile(full_path):
                if not include_spec or include_spec.match_file(relative_path):
                    try:
                        size = os.path.getsize(full_path)
                        candidate_files.append((full_path, size))
                    except OSError:
                        continue
    
    # Step 2: Prioritize files if a focus is specified.
    if focus_spec:
        focused_files = [f for f in candidate_files if focus_spec.match_file(os.path.relpath(f[0], abs_root_dir).replace(os.sep, '/'))]
        other_files = [f for f in candidate_files if not focus_spec.match_file(os.path.relpath(f[0], abs_root_dir).replace(os.sep, '/'))]
        sorted_candidates = focused_files + other_files
    else:
        sorted_candidates = candidate_files

    final_files = []
    total_size = 0
    for file_path, file_size in sorted_candidates:
        # Use the max_files argument here
        if len(final_files) >= max_files:
            print(f"Warning: Reached max file limit of {max_files}. No more files will be added.")
            break
            
        if target_size_bytes and (total_size + file_size) > target_size_bytes:
            continue
            
        final_files.append(file_path)
        total_size += file_size
    
    if target_size_bytes and total_size >= target_size_bytes:
         print(f"Info: Stopped adding files to stay near target size of {target_size_bytes/1024:.2f}k.")
         
    return final_files