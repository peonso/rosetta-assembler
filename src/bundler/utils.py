# src/bundler/utils.py (Updated to be more efficient)
import os

def generate_file_tree(root_dir, valid_files):
    """
    Generates a string representation of the file tree,
    based on the final list of files that will be included.
    """
    tree_lines = []
    abs_root_dir = os.path.abspath(root_dir)
    
    # Create a set of all directories that should be in the tree
    included_dirs = {os.path.dirname(p) for p in valid_files}
    
    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        # Prune directories that are not in our included set
        dirs[:] = [d for d in dirs if os.path.join(root, d) in included_dirs]

        relative_root = os.path.relpath(root, abs_root_dir)
        level = relative_root.count(os.sep) if relative_root != '.' else 0
        indent = ' ' * 4 * level

        if level == 0:
            tree_lines.append(f"{os.path.basename(abs_root_dir)}/")
        else:
            tree_lines.append(f"{indent}├── {os.path.basename(root)}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            file_path = os.path.join(root, f)
            if file_path in valid_files:
                tree_lines.append(f"{sub_indent}├── {f}")
    
    return "\n".join(tree_lines)