# main.py (Final Version)
import sys
import os
import datetime
from bundler.core import bundle_project

def run():
    """The main entry point for the script."""

    if len(sys.argv) < 2:
        print("Error: No project path provided.")
        print("Usage: python main.py /path/to/your/project")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"Error: The path '{project_path}' does not exist.")
        sys.exit(1)
        
    if not os.path.isdir(project_path):
        print(f"Error: The path '{project_path}' is not a directory.")
        sys.exit(1)

    print(f"Starting Rosetta Assembler for project: {project_path}")

    # Call the core bundler
    bundle_content = bundle_project(project_path)

    # Create the output filename
    project_name = os.path.basename(os.path.abspath(project_path))
    today_date = datetime.date.today().strftime('%Y_%m_%d')
    output_filename = f"{today_date}_{project_name}_bundle.txt"
    
    # Define output directory and ensure it exists
    output_dir = "context_files"
    os.makedirs(output_dir, exist_ok=True)
    output_filepath = os.path.join(output_dir, output_filename)

    # Write the bundle to the file
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(bundle_content)

    # Final success message
    file_size_kb = os.path.getsize(output_filepath) / 1024
    print("-" * 20)
    print("Assembly Complete!")
    print(f"Output file created at: {output_filepath}")
    print(f"Final file size: {file_size_kb:.2f} KB")


if __name__ == "__main__":
    run()