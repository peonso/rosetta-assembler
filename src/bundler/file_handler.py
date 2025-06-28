# src/bundler/file_handler.py (Updated to use arguments)
import os
from pathspec import PathSpec
from config import GLOBAL_IGNORE_PATTERNS

# ... (The load_gitignore_patterns function is unchanged)
def load_gitignore_patterns(root_path):
    """
    Finds all .gitignore files in the directory tree and parses their patterns.
    """
    # ... (no changes here)
    gitignore_patterns = set()
    for dirpath, _, filenames in os.walk(root_path):
        if ".gitignore" in filenames:
            gitignore_path = os.path.join(dirpath, ".gitignore")
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith("#"):
                            relative_dir = os.path.relpath(dirpath, root_path)
                            if relative_dir == ".":
                                gitignore_patterns.add(stripped_line)
                            else:
                                pattern = os.path.join(relative_dir, stripped_line)
                                gitignore_patterns.add(pattern.replace(os.sep, "/"))
            except Exception as e:
                print(f"Warning: Could not read or parse {gitignore_path}: {e}")

    return gitignore_patterns


# --- The get_all_files function is replaced with this new version ---
def get_all_files(
    root_dir, include_patterns, exclude_patterns, max_files, max_size_mb, max_depth
):
    """
    Walks through a directory and returns a list of all non-ignored files,
    now using arguments for configuration.
    """
    abs_root_dir = os.path.abspath(root_dir)

    project_gitignore_patterns = load_gitignore_patterns(abs_root_dir)
    # Combine global patterns with user-provided exclude patterns
    all_exclude_patterns = (
        set(GLOBAL_IGNORE_PATTERNS) | set(exclude_patterns) | project_gitignore_patterns
    )

    # Important: User's include patterns should override any exclusion
    if include_patterns:
        # Create a spec for includes to check against
        include_spec = PathSpec.from_lines("gitwildmatch", include_patterns)
    else:
        include_spec = None

    exclude_spec = PathSpec.from_lines("gitwildmatch", all_exclude_patterns)

    valid_files = []
    total_size = 0
    max_size_bytes = max_size_mb * 1024 * 1024

    for root, dirs, files in os.walk(abs_root_dir, topdown=True):
        depth = root[len(abs_root_dir) + len(os.path.sep) :].count(os.path.sep)
        if depth >= max_depth:
            print(
                f"Warning: Reached max directory depth of {MAX_DIRECTORY_DEPTH}. Skipping subdirectories of {root}."
            )
            dirs[:] = []  # Stop descending further into this branch

        # We need relative paths for pathspec
        paths_to_check = [
            os.path.relpath(os.path.join(root, name), abs_root_dir).replace(os.sep, "/")
            for name in dirs + files
        ]

        # Find all paths that are explicitly excluded
        excluded_by_rule = set(exclude_spec.match_files(paths_to_check))

        # Filter directories and files
        dirs[:] = [
            d
            for d in dirs
            if os.path.relpath(os.path.join(root, d), abs_root_dir).replace(os.sep, "/")
            not in excluded_by_rule
        ]

        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, abs_root_dir).replace(
                os.sep, "/"
            )

            # Final check: Is the file excluded?
            if relative_file_path in excluded_by_rule:
                continue

            # If include patterns exist, the file MUST match them
            if include_spec and not include_spec.match_file(relative_file_path):
                continue

            # If we get here, the file is valid. Now check limits.
            if len(valid_files) >= max_files:
                print(
                    f"Warning: Reached max file limit of {MAX_TOTAL_FILES}. No more files will be added."
                )
                return valid_files  # Stop processing and return what we have

            # --- Total Size Check ---
            try:
                file_size = os.path.getsize(file_path)
                if total_size + file_size > max_size_bytes:
                    print(
                        f"Warning: Reached max total size of {MAX_TOTAL_SIZE_MB}MB. No more files will be added."
                    )
                    return valid_files  # Stop processing and return what we have

                total_size += file_size
                valid_files.append(file_path)
            except OSError as e:
                print(f"Warning: Could not access file {file_path}: {e}")

    return valid_files
