# src/main.py (Final version with correct error handler)
import sys
import os
import datetime
import argparse
import shutil
import stat # Required for changing file permissions

# All other imports are correct
from bundler.core import bundle_project
try:
    from cloner import CACHE_DIR, handle_repo_url
except ImportError:
    handle_repo_url = None
    CACHE_DIR = None

from config import MAX_TOTAL_FILES, MAX_TOTAL_SIZE_MB, MAX_DIRECTORY_DEPTH

def is_url(text):
    """Checks if the provided text string is a URL."""
    return text.startswith("http://") or text.startswith("https://")

def get_unique_filepath(proposed_path):
    """
    Checks if a file path exists. If it does, appends an incrementing
    counter (_2, _3, etc.) until a unique path is found.
    """
    if not os.path.exists(proposed_path):
        return proposed_path
    directory = os.path.dirname(proposed_path)
    filename, extension = os.path.splitext(os.path.basename(proposed_path))
    counter = 2
    while True:
        new_filename = f"{filename}_{counter}{extension}"
        new_filepath = os.path.join(directory, new_filename)
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1

# --- THE CORRECTED ERROR HANDLER ---
def handle_remove_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree that handles read-only files.
    'exc_info' is a tuple from sys.exc_info(), which contains (type, value, traceback).
    """
    # The PermissionError is the second item in the exc_info tuple
    if isinstance(exc_info[1], PermissionError):
        # Change the file to be writable and retry the function.
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        # For all other errors, re-raise the exception
        raise exc_info[1]

def clear_cache():
    """Handles the logic for clearing the repository cache."""
    if CACHE_DIR is None:
        print("Error: Cloner module not available. Cannot clear cache.")
        return

    print(f"The cache directory is located at: {CACHE_DIR}")

    if not os.path.exists(CACHE_DIR) or not os.listdir(CACHE_DIR):
        print("Cache is already empty or does not exist.")
        return

    if os.path.basename(CACHE_DIR) != ".rosetta_assembler_cache":
        print(f"Error: Cache path '{CACHE_DIR}' seems incorrect. Aborting for safety.")
        sys.exit(1)
        
    print("\nContents of the cache to be deleted:")
    cached_repos = [d for d in os.listdir(CACHE_DIR) if os.path.isdir(os.path.join(CACHE_DIR, d))]
    for repo in cached_repos:
        print(f"- {repo}")
    
    try:
        response = input(f"\nAre you sure you want to delete these {len(cached_repos)} directories? [y/N]: ")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

    if response.lower() == 'y':
        print("Deleting cache...")
        try:
            shutil.rmtree(CACHE_DIR, onerror=handle_remove_error)
            print("Cache cleared successfully.")
        except OSError as e:
            print(f"Error: The cache could not be fully cleared. Reason: {e}")
            sys.exit(1)
    else:
        print("Operation cancelled.")

def run():
    parser = argparse.ArgumentParser(
        description="Rosetta Assembler: A context bundler for AI development.",
        # Add a formatter class to show default values in the help message
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --- INPUT AND OUTPUT ---
    parser.add_argument(
        "project_path", type=str, nargs='?', default=None,
        help="The path to the project directory or URL you want to bundle."
    )
    parser.add_argument(
        "-o", "--output", type=str,
        help="The path to the output bundle file."
    )

    # --- FILTERING ARGUMENTS ---
    parser.add_argument(
        "--include", action="append", default=[],
        help="Wildcard pattern for files to include. Can be used multiple times."
    )
    parser.add_argument(
        "--exclude", action="append", default=[],
        help="Wildcard pattern for files/directories to exclude. Can be used multiple times."
    )

    # --- LIMITS ARGUMENTS ---
    parser.add_argument(
        "--max-files", type=int, default=MAX_TOTAL_FILES,
        help="Maximum number of files to include in the bundle."
    )
    parser.add_argument(
        "--max-size-mb", type=int, default=MAX_TOTAL_SIZE_MB,
        help="Maximum total size of files (in MB) to include."
    )
    parser.add_argument(
        "--max-depth", type=int, default=MAX_DIRECTORY_DEPTH,
        help="Maximum directory depth to scan."
    )

    # --- OTHER ACTIONS ---
    parser.add_argument(
        "--clear-cache", action="store_true",
        help="Clear the cache of cloned repositories."
    )

    args = parser.parse_args()

    # --- The rest of the logic now uses these new args ---
    if args.clear_cache:
        clear_cache()
        sys.exit(0)

    if not args.project_path:
        parser.error("The following arguments are required: project_path")

    project_path = args.project_path
    
    if is_url(project_path):
        if handle_repo_url is None:
            print("Error: URL detected, but the cloner module is not implemented.")
            sys.exit(1)
        print(f"URL detected. Cloning/updating repository: {project_path}")
        try:
            local_repo_path = handle_repo_url(project_path)
            project_path = local_repo_path
        except Exception as e:
            print(f"Error handling repository: {e}")
            sys.exit(1)

    if not os.path.exists(project_path):
        print(f"Error: The path '{project_path}' does not exist.")
        sys.exit(1)
    if not os.path.isdir(project_path):
        print(f"Error: The path '{project_path}' is not a directory.")
        sys.exit(1)

    print(f"Starting Rosetta Assembler for project: {project_path}")
    
    # We now pass all the new arguments to the bundler
    bundle_content = bundle_project(
        project_path=project_path,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        max_files=args.max_files,
        max_size_mb=args.max_size_mb,
        max_depth=args.max_depth
    )
    
    if args.output:
        initial_filepath = args.output
        output_dir = os.path.dirname(initial_filepath)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    else:
        project_name = os.path.basename(os.path.abspath(project_path))
        today_date = datetime.date.today().strftime('%Y_%m_%d')
        output_filename = f"{today_date}_{project_name}_bundle.txt"
        output_dir = "context_files"
        os.makedirs(output_dir, exist_ok=True)
        initial_filepath = os.path.join(output_dir, output_filename)

    output_filepath = get_unique_filepath(initial_filepath)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(bundle_content)

    file_size_kb = os.path.getsize(output_filepath) / 1024
    print("-" * 20)
    print("Assembly Complete!")
    print(f"Output file created at: {output_filepath}")
    print(f"Final file size: {file_size_kb:.2f} KB")

if __name__ == "__main__":
    run()