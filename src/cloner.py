
# src/cloner.py
import os
import re
import subprocess
import sys

# Define a cache directory for cloned repositories
# os.path.expanduser('~') gets the user's home directory
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.rosetta_assembler_cache')

def _run_command(command, cwd=None):
    """
    Runs a shell command, captures its output, and checks for errors.
    
    Args:
        command (list): The command to run as a list of strings.
        cwd (str, optional): The directory to run the command in. Defaults to None.
    
    Raises:
        Exception: If the command returns a non-zero exit code.
    
    Returns:
        str: The decoded stdout from the command.
    """
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,  # Decodes stdout/stderr as text
            check=True, # Raises CalledProcessError on non-zero exit codes
            cwd=cwd
        )
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed and in your PATH?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Provide a much more informative error message
        print(f"Error executing command: {' '.join(command)}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        raise Exception("Git command failed.") from e

def _get_repo_local_path(url):
    """
    Creates a safe, unique local folder path from a repository URL.
    Example: 'https://github.com/user/repo' -> '.../.rosetta_assembler_cache/github.com_user_repo'
    """
    # Remove protocol and replace unsafe characters
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', url.replace('https://', '').replace('http://', ''))
    return os.path.join(CACHE_DIR, safe_name)

def handle_repo_url(url):
    """
    Manages cloning a new repository or updating an existing one.
    
    Args:
        url (str): The URL of the git repository.
        
    Returns:
        str: The local file path to the cloned/updated repository.
    """
    local_path = _get_repo_local_path(url)
    
    # Ensure the main cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # First, check if the repo is accessible before doing anything else
    print("Checking repository accessibility...")
    _run_command(['git', 'ls-remote', url])
    
    if os.path.exists(local_path):
        # Directory exists, so we update it
        print(f"Repository already exists at {local_path}. Updating...")
        _run_command(['git', 'pull'], cwd=local_path)
    else:
        # Directory does not exist, so we clone it
        print(f"Cloning new repository to {local_path}...")
        _run_command(['git', 'clone', url, local_path])
        
    print("Repository is ready.")
    return local_path