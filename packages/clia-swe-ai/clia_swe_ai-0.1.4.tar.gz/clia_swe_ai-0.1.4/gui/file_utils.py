# -*- coding: utf-8 -*-

import os
import fnmatch
from typing import List

DEFAULT_IGNORE_PATTERNS = [
    ".git", ".gitignore", ".svn", "node_modules", "venv", ".venv",
    "__pycache__", "build", "dist", "*.log", ".tmp", ".DS_Store",
    "*.pyc", "*.pyo", "*.pyd", "*.db", "*.sqlite",
    "*.egg", "*.egg-info", "*.whl", "*.zip", "*.tar.gz",
    "*.tar.bz2", "*.tar.xz", "*.rar", "*.7z",
    "*.bak", "*.swp", "*.swo", "*.tmp", "*.temp",
    "*.out", "*.o", "*.obj", "*.class", "*.jar",
    "*.exe", "*.dll", "*.so", "*.dylib",
    "*.pdb", "*.lib", "*.a", "*.dSYM",
    "*.log", "*.log.*", "*.log.gz", "*.log.bz2",
    "*.log.xz", "*.log.zip", "*.log.tar.gz",
    "*.log.tar.bz2", "*.log.tar.xz", "*.log.7z",
    "*.log.rar", "*.log.7zip", "*.log.7z.xz",
    "*.log.7z.bz2", "*.log.7z.gz",".next"
]

def is_ignored(relative_path: str, ignore_patterns: List[str]) -> bool:
    normalized_path = relative_path.replace("\\", "/")
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(normalized_path, pattern) or fnmatch.fnmatch(os.path.basename(normalized_path), pattern):
            return True
    return False

def get_local_file_list(path: str = ".", max_depth: int = 999) -> str:
    """
    Generates a list of full relative paths for all files in a directory,
    respecting ignore patterns.
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    all_ignore_patterns = DEFAULT_IGNORE_PATTERNS
    if not os.path.isdir(path):
        return f"Error: The specified path does not exist or is not a directory: {path}"

    file_paths = []
    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        # Prune directories to respect max_depth
        if dirpath != path:
            rel_depth = os.path.relpath(dirpath, path).count(os.sep)
            if rel_depth >= max_depth:
                dirnames[:] = [] # Don't go deeper
                continue

        # Filter ignored directories
        dirs_to_remove = {d for d in dirnames if is_ignored(os.path.relpath(os.path.join(dirpath, d), path), all_ignore_patterns)}
        dirnames[:] = [d for d in dirnames if d not in dirs_to_remove]

        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)
            relative_filepath = os.path.relpath(filepath, path).replace("\\", "/")
            if not is_ignored(relative_filepath, all_ignore_patterns):
                file_paths.append(relative_filepath)

    if not file_paths:
        if not os.listdir(path):
             return f"The directory at '{path}' is empty."
        else:
             return f"The directory at '{path}' contains no files (only empty directories or ignored files)."

    return "\n".join(file_paths)
