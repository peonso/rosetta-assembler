# bundler/core.py
import os
from .file_handler import get_all_files
from .utils import generate_file_tree

def bundle_project(project_path):
    """
    Orchestrates the bundling process.
    1. Gets all valid files.
    2. Generates the file tree.
    3. Reads file contents and assembles the final string.
    """
    # Get the absolute path to normalize it
    project_path = os.path.abspath(project_path)
    
    files_to_bundle = get_all_files(project_path)
    file_tree = generate_file_tree(project_path)

    output_content = []
    
    # Add a header and the file tree
    output_content.append("# Project Structure")
    output_content.append("=" * 20)
    output_content.append(file_tree)
    output_content.append("\n" * 2)
    
    # Add the source code content
    output_content.append("# Source Code")
    output_content.append("=" * 20)

    for file_path in files_to_bundle:
        # Create a relative path for cleaner headers
        relative_path = os.path.relpath(file_path, project_path)
        header = f"--- START OF FILE {relative_path} ---"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            output_content.append(header)
            output_content.append(content)
            
        except Exception as e:
            # If we can't read a file for some reason, we note it and move on.
            output_content.append(f"{header}\nError reading file: {e}")

    return "\n".join(output_content)