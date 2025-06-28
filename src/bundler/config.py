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

# --- Heuristic Scoring Configuration ---
# Scores are added to files based on these rules to determine importance.
# Higher scores are prioritized when culling for --target-size.

FILENAME_SCORES = {
    "readme.md": 100,
    "pyproject.toml": 80,
    "package.json": 80,
    "go.mod": 80,
    "pom.xml": 80,
    "main.py": 50,
    "app.py": 50,
    "index.js": 50,
    "__init__.py": 20, # Important for package structure
    "license": 10,
    "contributing.md": 10,
}

DIR_SCORES = {
    # Directory names (exact match)
    "src": 20,
    "lib": 20,
    "docs": -10,
    "examples": -10,
    "tests": -20,
    "test": -20,
}