# bundler/utils.py
import os
from .filter import is_ignored

def generate_file_tree(root_dir):
    """
    Generates a string representation of the file tree, ignoring specified files/dirs.
    """
    tree_lines = []
    
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Filter directories in place to prevent os.walk from descending into them
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Add the directory to the tree
        tree_lines.append(f"{indent}├── {os.path.basename(root)}/")

        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            if not is_ignored(file_path):
                tree_lines.append(f"{sub_indent}├── {f}")
                
    # The first line is the root itself, let's format it nicely
    if tree_lines:
        tree_lines[0] = f"{os.path.basename(root_dir)}/"
        
    return "\n".join(tree_lines)