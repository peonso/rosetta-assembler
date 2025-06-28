# src/bundler/heuristics.py (Updated to use EXTENSION_SCORES)
import os
from .config import FILENAME_SCORES, DIR_SCORES, EXTENSION_SCORES

def calculate_importance_score(relative_path):
    """
    Calculates an importance score based on path, name, and now extension.
    """
    score = 0
    
    # Normalize path for case-insensitive matching
    path_lower = relative_path.lower()
    path_parts = path_lower.split('/')
    filename_lower = path_parts[-1]
    
    # 1. Score based on specific, important filenames (e.g., "readme.md", "makefile")
    if filename_lower in FILENAME_SCORES:
        score += FILENAME_SCORES[filename_lower]
    # Also check without extension
    elif os.path.splitext(filename_lower)[0] in FILENAME_SCORES:
        score += FILENAME_SCORES[os.path.splitext(filename_lower)[0]]
        
    # 2. Score based on file extension (NEW)
    _, extension = os.path.splitext(filename_lower)
    if extension in EXTENSION_SCORES:
        score += EXTENSION_SCORES[extension]
            
    # 3. Score based on directory names
    for part in path_parts[:-1]:
        if part in DIR_SCORES:
            score += DIR_SCORES[part]
            
    # 4. Apply a small penalty for depth
    depth = len(path_parts) - 1
    score -= depth
    
    return score