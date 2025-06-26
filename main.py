# main.py (Updated with unique filename logic)
import sys
import os
import datetime
import argparse

from bundler.core import bundle_project

# --- NEW HELPER FUNCTION ---
def get_unique_filepath(proposed_path):
    """
    Checks if a file path exists. If it does, appends an incrementing
    counter (_2, _3, etc.) until a unique path is found.
    """
    if not os.path.exists(proposed_path):
        return proposed_path

    # Separate the directory, filename, and extension
    directory = os.path.dirname(proposed_path)
    filename, extension = os.path.splitext(os.path.basename(proposed_path))
    
    counter = 2
    while True:
        # Create a new filename with the counter
        new_filename = f"{filename}_{counter}{extension}"
        new_filepath = os.path.join(directory, new_filename)
        
        if not os.path.exists(new_filepath):
            return new_filepath
        
        counter += 1
# -------------------------


def run():
    """The main entry point for the script, now using argparse."""

    parser = argparse.ArgumentParser(
        description="Rosetta Assembler: A context bundler for AI development."
    )

    parser.add_argument(
        "project_path",
        type=str,
        help="The path to the project directory you want to bundle."
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="The path to the output bundle file. If not specified, a default name will be used."
    )

    args = parser.parse_args()
    project_path = args.project_path

    if not os.path.exists(project_path):
        print(f"Error: The path '{project_path}' does not exist.")
        sys.exit(1)
        
    if not os.path.isdir(project_path):
        print(f"Error: The path '{project_path}' is not a directory.")
        sys.exit(1)

    print(f"Starting Rosetta Assembler for project: {project_path}")

    bundle_content = bundle_project(project_path)
    
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

    # --- MODIFIED SECTION ---
    # Use our new helper function to get a unique path
    output_filepath = get_unique_filepath(initial_filepath)
    # ----------------------

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(bundle_content)

    file_size_kb = os.path.getsize(output_filepath) / 1024
    print("-" * 20)
    print("Assembly Complete!")
    print(f"Output file created at: {output_filepath}")
    print(f"Final file size: {file_size_kb:.2f} KB")


if __name__ == "__main__":
    run()