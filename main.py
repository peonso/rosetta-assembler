# main.py (Updated with argparse)
import sys
import os
import datetime
import argparse # Import the argparse library
from bundler.core import bundle_project

def run():
    """The main entry point for the script, now using argparse."""

    # 1. Create the parser
    parser = argparse.ArgumentParser(
        description="Rosetta Assembler: A context bundler for AI development."
    )

    # 2. Add the arguments
    #    This is our required positional argument.
    parser.add_argument(
        "project_path",
        type=str,
        help="The path to the project directory you want to bundle."
    )
    
    #    This is our optional argument for the output file.
    #    '--output' is the long name, '-o' is the short name.
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="The path to the output bundle file. If not specified, a default name will be used."
    )

    # 3. Parse the arguments from the command line
    args = parser.parse_args()

    # The rest of our logic now uses the 'args' object instead of sys.argv
    project_path = args.project_path

    # --- The validation logic remains the same ---
    if not os.path.exists(project_path):
        print(f"Error: The path '{project_path}' does not exist.")
        sys.exit(1)
        
    if not os.path.isdir(project_path):
        print(f"Error: The path '{project_path}' is not a directory.")
        sys.exit(1)

    print(f"Starting Rosetta Assembler for project: {project_path}")

    bundle_content = bundle_project(project_path)
    
    # --- The output file logic now checks for the optional argument ---
    if args.output:
        # User specified an output file
        output_filepath = args.output
        # Ensure the directory for the custom output file exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    else:
        # Use the default naming convention
        project_name = os.path.basename(os.path.abspath(project_path))
        today_date = datetime.date.today().strftime('%Y_%m_%d')
        output_filename = f"{today_date}_{project_name}_bundle.txt"
        
        output_dir = "context_files"
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, output_filename)

    # --- Writing the file and the final message remain the same ---
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(bundle_content)

    file_size_kb = os.path.getsize(output_filepath) / 1024
    print("-" * 20)
    print("Assembly Complete!")
    print(f"Output file created at: {output_filepath}")
    print(f"Final file size: {file_size_kb:.2f} KB")


if __name__ == "__main__":
    run()