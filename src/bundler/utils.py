# src/bundler/utils.py (Corrected Version)
import os

def generate_file_tree(root_dir, valid_files):
    """
    Generates a correct and efficient string representation of the file tree
    based on the final list of included files.
    """
    tree_lines = []
    abs_root_dir = os.path.abspath(root_dir)
    
    # Create a dictionary to hold the tree structure
    tree = {}

    for file_path in valid_files:
        # Get path relative to the root, and split into parts
        relative_path = os.path.relpath(file_path, abs_root_dir)
        parts = relative_path.split(os.sep)
        
        # Traverse the tree dictionary, creating nested dictionaries for dirs
        current_level = tree
        for part in parts[:-1]: # All parts except the last one (the file)
            current_level = current_level.setdefault(part, {})
        
        # Add the file to the last level
        current_level[parts[-1]] = None # Mark as a file

    # Now, recursively build the string representation from the tree dictionary
    def build_tree_string(subtree, prefix=""):
        # Sort items to have directories first, then files
        items = sorted(subtree.items(), key=lambda item: isinstance(item[1], dict), reverse=True)
        for i, (name, content) in enumerate(items):
            is_last = i == (len(items) - 1)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{name}")
            
            if isinstance(content, dict): # It's a directory
                extension = "    " if is_last else "│   "
                build_tree_string(content, prefix + extension)

    tree_lines.append(f"{os.path.basename(abs_root_dir)}/")
    build_tree_string(tree)
    
    return "\n".join(tree_lines)