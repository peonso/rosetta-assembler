# tests/test_filter.py
import os
from bundler.filter import is_ignored

# All test functions must start with 'test_'
def test_git_directory_is_ignored():
    """
    Verify that a path containing a .git directory is correctly identified as ignored.
    """
    # Arrange: Define the inputs for our test
    project_root = "/fake/project"
    path_to_check = os.path.join(project_root, ".git", "config")
    
    # Act: Call the function we are testing
    result = is_ignored(path_to_check, project_root)
    
    # Assert: Check if the result is what we expect
    assert result is True, "A path within the .git directory should be ignored"

def test_source_file_is_not_ignored():
    """
    Verify that a typical source file is NOT ignored.
    """
    # Arrange
    project_root = "/fake/project"
    path_to_check = os.path.join(project_root, "src", "main.py")
    
    # Act
    result = is_ignored(path_to_check, project_root)
    
    # Assert
    assert result is False, "A standard source file should not be ignored"

def test_log_file_is_ignored():
    """

    Verify that a file matching a wildcard pattern (*.log) is ignored.
    """
    # Arrange
    project_root = "/fake/project"
    path_to_check = os.path.join(project_root, "output.log")
    
    # Act
    result = is_ignored(path_to_check, project_root)
    
    # Assert
    assert result is True, "A .log file should be ignored by our wildcard patterns"