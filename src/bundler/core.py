# src/bundler/core.py (Final version with license identification)
import os
import json
from .file_handler import get_all_files
from .utils import generate_file_tree
from .config import LICENSE_FILENAMES, LICENSE_FINGERPRINTS

def bundle_project(project_path, include_patterns, exclude_patterns, focus_patterns, target_size_bytes, max_files, max_depth, output_format='txt'):
    """
    Orchestrates bundling, now with license identification.
    """
    project_path = os.path.abspath(project_path)
    project_name = os.path.basename(project_path)
    
    culled_file_info = get_all_files(
        root_dir=project_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        focus_patterns=focus_patterns,
        target_size_bytes=target_size_bytes,
        max_files=max_files,
        max_depth=max_depth
    )
    
    file_paths_for_tree = [info["path"] for info in culled_file_info]
    file_tree = generate_file_tree(project_path, file_paths_for_tree)

    def get_file_content(info):
        """
        Gets file content, handling binary and license files specially.
        """
        file_path = info["path"]
        relative_path = os.path.relpath(file_path, project_path).replace(os.sep, '/')
        filename_lower = os.path.basename(relative_path).lower()

        if info["is_binary"]:
            return "[Binary file content omitted]"
        
        # Read the file to check for license fingerprints or get full content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        if filename_lower in LICENSE_FILENAMES:
            identified_license = "License" # Default name
            for name, fingerprint in LICENSE_FINGERPRINTS.items():
                if fingerprint in content:
                    identified_license = name
                    break
            return f"[{identified_license} content omitted for brevity]"
        
        return content

    # --- JSON Output Generation ---
    if output_format == 'json':
        file_objects = []
        for info in culled_file_info:
            relative_path = os.path.relpath(info["path"], project_path).replace(os.sep, '/')
            content = get_file_content(info)
            file_objects.append({"path": relative_path, "content": content})
        
        output_data = {
            "projectName": project_name,
            "fileTree": file_tree,
            "files": file_objects
        }
        return output_data

    # --- TXT Output Generation ---
    output_content = []
    output_content.append(f"# Project: {project_name}")
    output_content.append("=" * 20)
    output_content.append(file_tree)
    output_content.append("\n" * 2)
    
    output_content.append("# Source Code")
    output_content.append("=" * 20)

    for info in culled_file_info:
        relative_path = os.path.relpath(info["path"], project_path).replace(os.sep, '/')
        header = f"--- START OF FILE {relative_path} ---"
        content = get_file_content(info)
        
        output_content.append(header)
        output_content.append(content)

    return "\n".join(output_content)