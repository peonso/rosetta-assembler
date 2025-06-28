# src/bundler/config.py (Overhauled for better heuristics)

# --- Safety Limits ---
MAX_TOTAL_FILES = 10000 
MAX_TOTAL_SIZE_MB = 500
MAX_DIRECTORY_DEPTH = 20

# --- File Handling ---

# A set of common license filenames. These will be included in the
# file tree, but their content will be omitted to save space.
LICENSE_FILENAMES = {
    "license", "license.md", "license.txt",
    "copying", "copying.md", "copying.txt",
}

# NEW: A dictionary of fingerprints to identify common licenses by content.
# The value is a unique string likely to be found in the license file.
LICENSE_FINGERPRINTS = {
    "MIT License": "Permission is hereby granted, free of charge",
    "GNU GPLv3": "GNU GENERAL PUBLIC LICENSE Version 3",
    "GNU GPLv2": "GNU GENERAL PUBLIC LICENSE Version 2",
    "Apache License 2.0": "Apache License, Version 2.0",
    "BSD-3-Clause License": "Redistribution and use in source and binary forms",
}

# A single list of .gitignore-style patterns for universal ignores.
GLOBAL_IGNORE_PATTERNS = [
    # Version Control
    '.git/',
    # Python
    '__pycache__/', '*.pyc', '*.pyo', '*.pyd',
    '.pytest_cache/', '.mypy_cache/', '.ruff_cache/',
    'venv/', '.venv/', 'env/',
    # Node.js
    'node_modules/',
    # Build artifacts
    'build/', 'dist/', 'target/', '*.egg-info/',
    # IDEs and Editors
    '.vscode/', '.idea/', '*.suo', '*.user',
    # Logs and temporary files
    '*.log', '*.tmp', '*.bak', '*.swp',
    # OS-specific
    '.DS_Store', 'Thumbs.db',
]

# --- Heuristic Scoring Configuration ---

# Scores based on file extension.
EXTENSION_SCORES = {
    # Core Source Code (High Score)
    ".cpp": 40, ".hpp": 40, ".h": 40, ".c": 40, ".cc": 40, ".hh": 40,
    ".java": 40, ".cs": 40, ".go": 40, ".rs": 40, ".py": 35, ".js": 30,
    ".ts": 30, ".rb": 30, ".php": 30, ".swift": 30, ".kt": 30,
    # Build & Config (High Score)
    ".cmake": 50, ".json": 15, ".toml": 20, ".yaml": 20, ".yml": 20,
    ".xml": -5,
    # Scripts (Neutral)
    ".sh": 5, ".bat": 5, ".ps1": 5,
    # Data/Text (Low Score)
    ".sql": -5, ".csv": -10, ".txt": -15, ".md": -15, ".lua": -10,
}

# Scores based on specific filenames (case-insensitive).
FILENAME_SCORES = {
    # Build systems
    "cmakelists.txt": 95, "makefile": 90, "pom.xml": 90,
    "dockerfile": 85, "docker-compose.yml": 85, "build.gradle": 85,
    "package.json": 80, "go.mod": 80, "pyproject.toml": 80,
    "requirements.txt": 70, "config.lua.dist": 60,
    # High-level documentation
    "readme.md": 100, "readme": 100,
    "contributing.md": 40, "contributing": 40,
    "changelog.md": 30, "changelog": 30,
    # Core source files
    "main": 50, "app": 50, "index": 50,
    "__init__.py": 20,
}

# Scores based on directory names (exact match, case-insensitive).
DIR_SCORES = {
    # Source code is top priority
    "src": 30, "source": 30, "lib": 20, "include": 20, "app": 15,
    # Config and docs are secondary
    "config": 0, "configs": 0, "docs": -10, "doc": -10, "examples": -15,
    # Data and assets are low priority
    "data": -30, "assets": -30, "database": -25,
    # Tests are important but less so than src
    "tests": -20, "test": -20,
}