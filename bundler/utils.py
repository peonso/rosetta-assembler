# bundler/utils.py (Updated to pass root_dir)
import os
from .filter import is_ignored

def generate_file_tree(root_dir):
    """
    Generates a string representation of the file tree, ignoring specified files/dirs.
    """
    tree_lines = []
    abs_root_dir = os.path.abspath(root_dir)
    
    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), abs_root_dir)]
        
        # Calculate level relative to the original root_dir
        relative_root = os.path.relpath(root, abs_root_dir)
        level = relative_root.count(os.sep) if relative_root != '.' else 0
        indent = ' ' * 4 * (level)
        
        tree_lines.append(f"{indent}├── {os.path.basename(root)}/")

        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            if not is_ignored(file_path, abs_root_dir):
                tree_lines.append(f"{sub_indent}├── {f}")
                
    if tree_lines:
        tree_lines[0] = f"{os.path.basename(abs_root_dir)}/"
        
    return "\n".join(tree_lines)