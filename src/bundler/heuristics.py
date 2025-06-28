# src/heuristics.py
import os
from .config import FILENAME_SCORES, DIR_SCORES

def calculate_importance_score(relative_path):
    """
    Calculates an importance score for a file based on its path and name.
    """
    score = 0
    path_parts = relative_path.lower().split(os.sep)
    filename = path_parts[-1]
    
    # 1. Score based on exact filename
    if filename in FILENAME_SCORES:
        score += FILENAME_SCORES[filename]
        
    # 2. Score based on directory names
    # We check all parts of the path for dir scores
    for part in path_parts[:-1]:
        if part in DIR_SCORES:
            score += DIR_SCORES[part]
            
    # 3. Apply a small penalty for depth
    depth = len(path_parts) - 1
    score -= depth
    
    return score