# src/bundler/core.py (Synchronized Version)
import os
from .file_handler import get_all_files
from .utils import generate_file_tree

def bundle_project(project_path, include_patterns, exclude_patterns, focus_patterns, target_size_bytes, max_files, max_depth):
    """
    Orchestrates the bundling process, passing all configuration down.
    """
    project_path = os.path.abspath(project_path)
    
    files_to_bundle = get_all_files(
        root_dir=project_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        focus_patterns=focus_patterns,
        target_size_bytes=target_size_bytes,
        max_files=max_files,
        max_depth=max_depth
    )
    
    file_tree = generate_file_tree(project_path, files_to_bundle)

    output_content = []
    
    output_content.append("# Project Structure")
    output_content.append("=" * 20)
    output_content.append(file_tree)
    output_content.append("\n" * 2)
    
    output_content.append("# Source Code")
    output_content.append("=" * 20)

    for file_path in files_to_bundle:
        relative_path = os.path.relpath(file_path, project_path).replace(os.sep, '/')
        header = f"--- START OF FILE {relative_path} ---"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            output_content.append(header)
            output_content.append(content)
        except Exception as e:
            output_content.append(f"{header}\nError reading file: {e}")

    return "\n".join(output_content)