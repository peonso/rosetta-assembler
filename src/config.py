# src/config.py (Updated with safety limits)

# --- Safety Limits ---
# Stop processing if more than this many files are found.
MAX_TOTAL_FILES = 10000 
# Stop processing if the total size of all file contents exceeds this value in Megabytes.
MAX_TOTAL_SIZE_MB = 500
# Stop walking directories that are deeper than this level.
MAX_DIRECTORY_DEPTH = 20
# --------------------

# A single list of .gitignore-style patterns.
# pathspec will handle the logic for files, directories, and wildcards.
GLOBAL_IGNORE_PATTERNS = [
    # Version Control
    '.git/',
    
    # Python
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.pytest_cache/',
    '.mypy_cache/',
    '.ruff_cache/',
    'venv/',
    '.venv/',
    'env/',
    
    # Node.js
    'node_modules/',
    'package-lock.json',
    'yarn.lock',
    
    # Build artifacts
    'build/',
    'dist/',
    'target/',
    '*.egg-info/',

    # IDEs and Editors
    '.vscode/',
    '.idea/',
    '*.suo',
    '*.user',

    # Logs and temporary files
    '*.log',
    '*.tmp',
    '*.bak',
    '*.swp',

    # OS-specific
    '.DS_Store',
    'Thumbs.db',

    # Common media formats we don't want to read
    '*.png',
    '*.jpg',
    '*.jpeg',
    '*.gif',
    '*.ico',
    '*.svg',
    '*.pdf',
    '*.zip',
]