# Rosetta Assembler

**Version: 1.0.0**

A powerful Python utility that acts as an intelligent "context bundler" for AI development. It analyzes a project's source code, intelligently curates the most relevant files, and assembles them into a single, context-rich file optimized for Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) pipelines.

## The Problem

Large Language Models have a limited "context window" and cannot browse file systems. Providing context for a complex coding question often requires manually copying and pasting multiple files, which is tedious, inefficient, and pollutes the context with irrelevant "noise" like build artifacts, logs, and verbose licenses.

## The Solution: Intelligent Curation

Rosetta Assembler automates this process with an intelligence layer. It acts as a **"System 1" Curator**, applying a set of powerful heuristics to identify and prioritize the most important source files *before* they are fed to an AI or indexed into a vector database.

By filtering out irrelevant files and intelligently omitting bulky, low-value content (like full license texts), it creates a smaller, high-quality, and contextually-dense bundle. This dramatically improves the cost, speed, and accuracy of the final AI agent.

## Core Features (v1.0.0)

*   **Remote & Local Analysis:** Works with both local folders and remote Git repositories, which it automatically clones and caches.
*   **Intelligent Filtering:** Respects `.gitignore` rules found within the project and combines them with a global ignore list and user-defined patterns (`--include`, `--exclude`).
*   **Heuristic Scoring:** A language-agnostic scoring system prioritizes files based on their name (`README.md`, `CMakeLists.txt`), directory (`src/`, `data/`), and file extension (`.cpp`, `.py`, `.xml`), ensuring the most important files are included first.
*   **Smart Culling:** Guarantees the output meets a specific size target (`--target-size`), intelligently removing the lowest-scoring files to create a dense, high-signal bundle. A `--focus-on` flag allows you to protect critical files from being culled.
*   **RAG-Optimized JSON Output:** In addition to plain text, it can generate a structured `.json` file (`--output-format json`) containing the project's file tree and a list of file objects, perfect for programmatic use in RAG pipelines.
*   **Robust File Handling:** Automatically detects binary files and omits their content. Identifies common license files (MIT, GPL, Apache) and replaces their full text with a simple placeholder tag to save space without losing context.
*   **Dynamic Naming & Caching:** Caches remote repos in `~/.rosetta_assembler_cache` and saves output files to a `context_files/` directory with a `YYYY_MM_DD_ProjectName_bundle.ext` format.

## Project Structure

```
rosetta-assembler/
├── src/
│   ├── bundler/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── core.py
│   │   ├── file_handler.py
│   │   ├── heuristics.py
│   │   └── utils.py
│   ├── cloner.py
│   └── main.py
│
├── tests/
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Usage

After installation, the tool is available as `rosetta-assembler`.

```bash
# Analyze a local project and create a default text bundle
rosetta-assembler /path/to/your/project

# Clone a remote repo and create a RAG-optimized JSON bundle
rosetta-assembler https://github.com/user/repo.git --output-format json

# Focus on specific files to ensure they are included when culling
rosetta-assembler . --focus-on "src/core/**" --target-size 500k
```

The output will be saved in the `context_files/` directory unless an output path is specified with `-o`.

## Configuration

Rosetta Assembler is configured via command-line arguments. Run `rosetta-assembler --help` for a full list of all available options and their default values.

*   `--output-format`: Choose between `txt` and `json`.
*   `--include` & `--exclude`: Add custom wildcard patterns for filtering.
*   `--focus-on`: Prioritize files matching this pattern during size culling.
*   `--target-size`: Set a target size for the bundle (e.g., '750k', '10M').
*   `--clear-cache`: Clear the cache of cloned repositories.

## Future Goals (Post-v1.0)

- [ ] **Configuration File:** Support for a `.rosettarc` file to save common settings.
- [ ] **Advanced Summarization:** Option to include the head/tail of large files instead of omitting them entirely.
- [ ] **Dry Run Mode:** A `--dry-run` flag to list files and their scores without creating a bundle.