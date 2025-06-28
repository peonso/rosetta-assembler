# src/bundler/utils.py (Updated)
import os
from pathspec import PathSpec
from config import GLOBAL_IGNORE_PATTERNS
from .file_handler import load_gitignore_patterns # Import the new function

def generate_file_tree(root_dir):
    """
    Generates a string representation of the file tree, respecting .gitignore rules.
    """
    tree_lines = []
    abs_root_dir = os.path.abspath(root_dir)

    # This function now has its own, identical filtering logic
    project_gitignore_patterns = load_gitignore_patterns(abs_root_dir)
    combined_patterns = set(GLOBAL_IGNORE_PATTERNS) | project_gitignore_patterns
    spec = PathSpec.from_lines('gitwildmatch', combined_patterns)
    
    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        # Filter directories
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), abs_root_dir).replace(os.sep, '/'))]
        
        # Filter files
        valid_files = [f for f in files if not spec.match_file(os.path.relpath(os.path.join(root, f), abs_root_dir).replace(os.sep, '/'))]

        # Don't add empty directories to the tree
        if not valid_files and not dirs:
            continue
        
        relative_root = os.path.relpath(root, abs_root_dir)
        level = relative_root.count(os.sep) if relative_root != '.' else 0
        indent = ' ' * 4 * (level)
        
        tree_lines.append(f"{indent}├── {os.path.basename(root)}/")

        sub_indent = ' ' * 4 * (level + 1)
        for f in valid_files:
            tree_lines.append(f"{sub_indent}├── {f}")
                
    if tree_lines:
        tree_lines[0] = f"{os.path.basename(abs_root_dir)}/"
        
    return "\n".join(tree_lines)