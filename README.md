# Rosetta Assembler

A powerful Python utility that acts as a "context bundler" for AI development. It analyzes a project's source code and assembles the entire folder structure and file contents into a single, readable text file. This file is optimized to be fed to Large Language Models (LLMs), allowing them to grasp the full context of a complex project in a single pass.

## The Problem

Large Language Models have a limited "context window" and cannot browse file systems or Git repositories directly. Providing context for a complex coding question often requires manually copying and pasting multiple files, which is tedious, error-prone, and inefficient.

## The Solution

Rosetta Assembler automates this process. It intelligently walks through a project directory, filters out irrelevant files, and compiles the source code into a single, well-structured document that clearly outlines the project's architecture and implementation details.

## Core Features (v1.0)

*   **Local Directory Analysis:** Point the tool at any local folder, whether it's a Git repository or not.
*   **Intelligent Filtering:** Automatically ignores non-text files and user-defined directories and file patterns (e.g., `node_modules`, `__pycache__`, `*.log`, test files).
*   **Structured Output:** Generates a single `.txt` file with:
    1.  A visual tree of the project structure.
    2.  The content of each relevant file, clearly demarcated with a header.
*   **Customizable Configuration:** Easily edit filtering rules in a central `config.py` file.
*   **Dynamic Naming Convention:** Output files are saved to a `context_files/` directory with a `YYYY_MM_DD_ProjectName.txt` format for easy tracking.
*   **Console Feedback:** Provides real-time progress updates and a final summary of files processed and total output size.

## Future Goals (Post-v1.0)

- [ ] **Chat Log Assembler:** A module to parse and format chat histories.
- [ ] **Magic Linker:** Automatically find and inject file contents referenced within a chat log.
- [ ] **Advanced Summarization:** Use heuristics or a local model to summarize large, non-essential files instead of including their full content.

## Project Structure

```
rosetta-assembler/
├── bundler/
│   ├── __init__.py
│   ├── core.py
│   ├── file_handler.py
│   ├── filter.py
│   └── utils.py
├── context_files/
│   └── .gitignore
├── config.py
├── main.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Usage

To run the assembler, execute the `main.py` script from your terminal, providing the path to the project you want to analyze as an argument.

```bash
# Example usage:
python main.py /path/to/your/project
```

The output will be saved in the `context_files/` directory.

## Configuration

To customize which files and directories are ignored, modify the lists within `config.py`.

```python
# In config.py
IGNORE_DIRS = {
    '__pycache__',
    '.git',
    'node_modules',
}

IGNORE_EXTENSIONS = {
    '.png',
    '.jpg',
    '.jpeg',
}
```