import os
import mimetypes
from typing import Optional
from swe_tools.instance import mcp
from swe_tools.utils import is_ignored, DEFAULT_IGNORE_PATTERNS

@mcp.tool(name="read_codebase_snapshot", description="""This tool creates a comprehensive, detailed string representation (a 'snapshot') of a specified directory's contents, including all files and their line-numbered content. It is invaluable for capturing the exact state of a codebase, a specific module, or a set of files for various purposes such as:
*   **Code Analysis:** Providing a complete view of code for review, understanding, or debugging.
*   **State Preservation:** Saving the current state of files before making significant changes, allowing for easy restoration using the `write_files_from_snapshot` tool.
*   **Context Provisioning:** Supplying the AI with a detailed and structured view of code files to inform its decisions and actions.

The snapshot output format is highly structured: each file's content is preceded by a `$` followed by its relative path (from the specified `path` argument), and then the content itself is presented with line numbers, enclosed within triple backticks (```). This format ensures clarity and easy parsing.

The tool intelligently handles directory traversal and can exclude files and directories based on predefined and user-specified ignore patterns. By default, it respects common ignore patterns (e.g., `.git`, `node_modules`, `__pycache__`). Users can extend these exclusions by providing additional glob patterns via the `ignore` parameter.""")
def read_codebase_snapshot(path: str = ".", ignore: Optional[str] = None) -> str:
    """
    Creates a detailed string snapshot of a specified directory, including file paths and line-numbered content. This is useful for capturing the current state of a codebase or specific files for analysis or restoration. Ignored files and directories can be excluded.

    Args:
        path: The root directory to snapshot (e.g., '.'). Defaults to current directory.
        ignore: Optional comma-separated string of glob patterns to ignore.
    """
    user_ignore_patterns = [p.strip() for p in ignore.split(',')] if ignore is not None else []
    all_ignore_patterns = list(set(DEFAULT_IGNORE_PATTERNS + user_ignore_patterns))
    abs_root = os.path.abspath(path)
    if not os.path.isdir(abs_root): return f"Error: Source directory not found: {abs_root}"
    snapshot_parts = []
    for dirpath, dirnames, filenames in os.walk(abs_root, topdown=True):
        dirs_to_remove = {d for d in dirnames if is_ignored(os.path.relpath(os.path.join(dirpath, d), abs_root), all_ignore_patterns)}
        dirnames[:] = [d for d in dirnames if d not in dirs_to_remove]
        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)
            relative_filepath = os.path.relpath(filepath, abs_root).replace("\\", "/")
            if is_ignored(relative_filepath, all_ignore_patterns): continue
            snapshot_parts.append(f"${relative_filepath}\n```\n")
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type and not mime_type.startswith('text/'):
                snapshot_parts.append(f"Binary file: {mime_type} (content skipped)\n")
            else:
                try:
                    with open(filepath, "r", encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            snapshot_parts.append(f"{i + 1}:{line.rstrip()}\n")
                except Exception as e:
                    snapshot_parts.append(f"Error reading file: {e}\n")
            snapshot_parts.append("```\n\n")
    return "".join(snapshot_parts) if snapshot_parts else "Snapshot could not be generated because the directory is empty or contains no matching files."
