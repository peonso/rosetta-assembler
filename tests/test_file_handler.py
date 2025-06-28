# tests/test_file_handler.py (Final Corrected Patch)
import os
import pytest
from unittest.mock import patch
import posixpath # Import for explicit POSIX path manipulation

from bundler.file_handler import get_all_files

@pytest.fixture
def mock_filesystem():
    """
    Mocks the filesystem in an OS-agnostic way.
    It forces all path operations to use POSIX-style paths ('/')
    to ensure tests are consistent across all operating systems.
    """
    
    base = "/fake/project"
    
    # All test data uses POSIX separators.
    walk_data = [
        (base, ["app", "docs", "config"], ["README.md"]),
        (f"{base}/app", [], ["main.py", "utils.py"]),
        (f"{base}/docs", [], ["guide.md"]),
        (f"{base}/config", [], ["settings.toml"]),
    ]
    size_map = {
        "README.md": 100,
        "app/main.py": 500,
        "app/utils.py": 300,
        "docs/guide.md": 800,
        "config/settings.toml": 50,
    }
    score_map = {
        "README.md": 100,
        "app/main.py": 50,
        "app/utils.py": 0,
        "docs/guide.md": -10,
        "config/settings.toml": 0,
    }

    # Side effect functions that are guaranteed to receive clean, POSIX paths
    # because the functions that call them are also mocked.
    def getsize_side_effect(path):
        relative_path = posixpath.relpath(path, base)
        return size_map[relative_path]

    def calculate_score_side_effect(relative_path):
        return score_map[relative_path]

    # Use patch.multiple to replace all necessary os and os.path functions
    # with their POSIX equivalents. This is the key to making the test stable.
    with patch.multiple('os',
        walk=lambda path, topdown=True: walk_data,
        sep=posixpath.sep
    ), patch.multiple('os.path',
        abspath=lambda path: base,
        join=posixpath.join,
        relpath=posixpath.relpath,
        getsize=getsize_side_effect
    ), patch('bundler.file_handler.load_gitignore_patterns', return_value=set()), \
       patch('bundler.file_handler.calculate_importance_score', side_effect=calculate_score_side_effect):
        yield

# The tests themselves are now verified against the stable, OS-agnostic mock.

def test_no_limits(mock_filesystem):
    """Test that all files are returned when no limits are set."""
    result_files = get_all_files(
        root_dir="/fake/project",
        include_patterns=[], exclude_patterns=[], focus_patterns=[],
        target_size_bytes=None, max_files=1000, max_depth=10
    )
    assert len(result_files) == 5

def test_target_size_culling(mock_filesystem):
    """
    Verify files are culled correctly by target size based on importance score.
    Scores: README(100), main.py(50), settings.toml(0), utils.py(0), guide.md(-10)
    """
    result_files = get_all_files(
        root_dir="/fake/project",
        include_patterns=[], exclude_patterns=[], focus_patterns=[],
        target_size_bytes=860, # Allows README(100) + main.py(500) + settings.toml(50) = 650. Next is utils.py(300), too big.
        max_files=100, max_depth=10
    )
    assert len(result_files) == 3
    # Use sets for order-independent comparison
    paths = {posixpath.basename(p) for p in result_files}
    assert {"README.md", "main.py", "settings.toml"} == paths

def test_focus_on_with_target_size(mock_filesystem):
    """
    Verify --focus-on prioritizes files correctly, even with lower base scores.
    """
    result_files = get_all_files(
        root_dir="/fake/project",
        include_patterns=[], exclude_patterns=[],
        focus_patterns=["**/*.md"], # Give huge score boost to markdown
        target_size_bytes=960,  # Allows guide.md(800) + README.md(100) = 900.
                                  # Then allows settings.toml(50), total 950.
        max_files=100, max_depth=10
    )
    assert len(result_files) == 3
    paths = {posixpath.basename(p) for p in result_files}
    assert {"README.md", "guide.md", "settings.toml"} == paths
    assert "main.py" not in paths