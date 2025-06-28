# src/main.py (Synchronized Version)
import sys
import os
import datetime
import argparse
import shutil
import time
import stat
import re

from bundler.core import bundle_project
from config import MAX_TOTAL_FILES, MAX_DIRECTORY_DEPTH

try:
    from cloner import CACHE_DIR, handle_repo_url
except ImportError:
    handle_repo_url = None
    CACHE_DIR = None

# (All helper functions like is_url, get_unique_filepath, handle_remove_error, clear_cache are unchanged)
def is_url(text):
    return text.startswith("http://") or text.startswith("https://")
def get_unique_filepath(proposed_path):
    if not os.path.exists(proposed_path): return proposed_path
    directory, filename, extension = os.path.dirname(proposed_path), *os.path.splitext(os.path.basename(proposed_path))
    counter = 2
    while True:
        new_filename = f"{filename}_{counter}{extension}"
        new_filepath = os.path.join(directory, new_filename)
        if not os.path.exists(new_filepath): return new_filepath
        counter += 1
def handle_remove_error(func, path, exc_info):
    if not isinstance(exc_info[1], PermissionError): raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    func(path)
def clear_cache():
    if CACHE_DIR is None: print("Error: Cloner module not available."); return
    if not os.path.exists(CACHE_DIR) or not os.listdir(CACHE_DIR): print("Cache is already empty."); return
    if os.path.basename(CACHE_DIR) != ".rosetta_assembler_cache": print(f"Error: Cache path '{CACHE_DIR}' incorrect."); sys.exit(1)
    print("\nContents to be deleted:"); cached_repos = [d for d in os.listdir(CACHE_DIR) if os.path.isdir(os.path.join(CACHE_DIR, d))]; [print(f"- {repo}") for repo in cached_repos]
    try: response = input(f"\nAre you sure? [y/N]: ")
    except KeyboardInterrupt: print("\nCancelled."); sys.exit(0)
    if response.lower() == 'y':
        print("Deleting cache..."); shutil.rmtree(CACHE_DIR, onerror=handle_remove_error); print("Cache cleared.")
    else: print("Operation cancelled.")

def parse_size(size_str):
    if not size_str: return None
    size_str = size_str.lower().strip()
    match = re.match(r'^(\d+)([kmg]?)$', size_str)
    if not match: raise argparse.ArgumentTypeError("Invalid size format. Use a number followed by 'k', 'm', or 'g'.")
    value, unit = int(match.groups()[0]), match.groups()[1]
    if unit == 'k': return value * 1024
    if unit == 'm': return value * 1024 * 1024
    if unit == 'g': return value * 1024 * 1024 * 1024
    return value

def run():
    parser = argparse.ArgumentParser(description="Rosetta Assembler: A context bundler for AI development.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("project_path", type=str, nargs='?', default=None, help="The path to the project directory or URL.")
    parser.add_argument("-o", "--output", type=str, help="The path for the output bundle file.")
    parser.add_argument("--include", action="append", default=[], help="Wildcard pattern for files to ALWAYS include.")
    parser.add_argument("--exclude", action="append", default=[], help="Wildcard pattern for files/directories to exclude.")
    parser.add_argument("--focus-on", action="append", default=[], help="Wildcard pattern to prioritize when using --target-size.")
    parser.add_argument("--target-size", type=parse_size, default=None, help="Target size for the bundle (e.g., '750k', '10M').")
    parser.add_argument("--max-files", type=int, default=MAX_TOTAL_FILES, help="Maximum number of files to include.")
    parser.add_argument("--max-depth", type=int, default=MAX_DIRECTORY_DEPTH, help="Maximum directory depth to scan.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache of cloned repositories.")
    args = parser.parse_args()

    if args.clear_cache:
        clear_cache()
        sys.exit(0)

    if not args.project_path:
        parser.error("The following arguments are required: project_path")

    project_path = args.project_path
    if is_url(project_path):
        # ... (URL handling logic)
        try:
            project_path = handle_repo_url(project_path)
        except Exception as e:
            print(f"Error handling repository: {e}"); sys.exit(1)

    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.")
        sys.exit(1)

    print(f"Starting Rosetta Assembler for project: {project_path}")
    
    bundle_content = bundle_project(
        project_path=project_path,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        focus_patterns=args.focus_on,
        target_size_bytes=args.target_size,
        max_files=args.max_files,
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