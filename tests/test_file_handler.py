# tests/test_file_handler.py (Corrected Assertions)
import os
import pytest
from unittest.mock import patch

from bundler.file_handler import get_all_files

@pytest.fixture
def mock_filesystem():
    """Mocks os.walk and other os.path functions to simulate a fake directory."""
    
    file_map = {
        "/fake/project/README.md": 100,
        "/fake/project/app/main.py": 500,
        "/fake/project/app/utils.py": 300,
        "/fake/project/docs/guide.md": 800,
        "/fake/project/config/settings.toml": 50,
    }
    
    dir_set = {os.path.dirname(p) for p in file_map}
    
    walk_data = [
        ("/fake/project", ["app", "docs", "config"], ["README.md"]),
        ("/fake/project/app", [], ["main.py", "utils.py"]),
        ("/fake/project/docs", [], ["guide.md"]),
        ("/fake/project/config", [], ["settings.toml"]),
    ]

    # --- THE FIX: We mock all necessary os functions ---
    # We create side effect functions to simulate the real behavior
    def isfile_side_effect(path):
        return path.replace(os.sep, '/') in file_map

    def isdir_side_effect(path):
        return path.replace(os.sep, '/') in dir_set

    with patch("os.walk", return_value=walk_data), \
         patch("os.path.getsize", side_effect=lambda path: file_map[path.replace(os.sep, '/')]), \
         patch("os.path.abspath", side_effect=lambda path: "/fake/project" if path == "." else path), \
         patch("os.path.isfile", side_effect=isfile_side_effect), \
         patch("os.path.isdir", side_effect=isdir_side_effect), \
         patch("bundler.file_handler.load_gitignore_patterns", return_value=set()) as mocked_load_gitignore:
        yield

def test_target_size_culling(mock_filesystem):
    """
    Verify that files are culled correctly to meet a --target-size.
    We sort alphabetically: config/s.toml(50), app/m.py(500), app/u.py(300), docs/g.md(800), README.md(100)
    """
    result_files = get_all_files(
        root_dir="/fake/project",
        include_patterns=[], exclude_patterns=[], focus_patterns=[],
        target_size_bytes=900, # 900 byte limit
        max_files=100, max_depth=10
    )
    # Expected: s.toml (50) + m.py (500) + u.py (300) = 850. g.md (800) is skipped. README.md(100) is skipped.
    assert len(result_files) == 3
    paths = {os.path.basename(p) for p in result_files}
    assert "settings.toml" in paths
    assert "main.py" in paths
    assert "utils.py" in paths

def test_focus_on_with_target_size(mock_filesystem):
    """
    Verify that --focus-on prioritizes files correctly when culling.
    """
    result_files = get_all_files(
        root_dir="/fake/project",
        include_patterns=[], exclude_patterns=[],
        focus_patterns=["*.md"],
        target_size_bytes=950, # 950 byte limit
        max_files=100, max_depth=10
    )

    # Expected: guide.md(800) + README.md(100) = 900.
    # Then it tries to add other files, but settings.toml (50) makes it 950.
    # main.py (500) would make it 1400, so it's skipped.
    assert len(result_files) == 3
    paths = {os.path.basename(p) for p in result_files}
    assert "guide.md" in paths
    assert "README.md" in paths
    assert "settings.toml" in paths
    assert "main.py" not in paths