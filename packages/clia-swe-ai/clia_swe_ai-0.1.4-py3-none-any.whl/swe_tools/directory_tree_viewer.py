import os
from typing import Optional
from swe_tools.instance import mcp
from swe_tools.utils import is_ignored, DEFAULT_IGNORE_PATTERNS

@mcp.tool(name="view_directory_structure", description="""This tool lists all files within a specified directory and its subdirectories, returning a simple, newline-separated list of their relative paths. It is a fundamental utility for getting a flat list of all files in a project or a specific part of it. This is useful for tasks like:
*   **File Inventory:** Getting a complete list of all files in a directory.
*   **Bulk Processing:** Providing a list of files to be processed by other tools.
*   **Context Gathering:** Quickly understanding which files exist in a certain area of the codebase.

The tool can traverse directories up to a specified depth and supports excluding files or directories using glob patterns. By default, it respects common ignore patterns (e.g., `.git`, `node_modules`, `__pycache__`). Users can extend these exclusions by providing additional glob patterns via the `ignore` parameter.""")
def view_directory_tree(path: str = ".", max_depth: int = 999, ignore: Optional[str] = None) -> str:
    """
    Generates a list of full relative paths for all files in a directory.
    This helps in getting a simple list of all files for processing.
    It supports limiting depth and ignoring specific patterns.

    Args:
        path: The root directory to start from. Defaults to '.'.
        max_depth: The maximum depth to traverse. Defaults to 999 (effectively unlimited).
        ignore: Optional comma-separated string of glob patterns to ignore.
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    user_ignore_patterns = [p.strip() for p in ignore.split(',')] if ignore is not None else []
    all_ignore_patterns = list(set(DEFAULT_IGNORE_PATTERNS + user_ignore_patterns))
    if not os.path.isdir(path):
        return f"The specified path does not exist or is not a directory: {path}"

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
