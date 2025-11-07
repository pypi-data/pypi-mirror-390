import os
import shutil
from swe_tools.instance import mcp

@mcp.tool(name="delete_files_and_folders", description="This tool provides the capability to permanently delete one or more specified files or directories (including non-empty ones) from the filesystem. This is a **highly destructive and irreversible action** and must be used with extreme caution. Once a file or directory is deleted using this tool, its contents cannot be recovered.\n\nThe tool processes a comma-separated list of paths. For each path provided:\n*   If the path points to an existing file, that file will be deleted.\n*   If the path points to an existing directory (empty or not), that directory and all its contents will be recursively deleted.\n*   If the path does not exist, a warning will be issued.\n\nA detailed report is generated for each attempted deletion, indicating success, failure, or skipped items, along with any encountered errors. It is strongly recommended to verify the paths and understand the implications before using this tool.")
def delete_files_and_folders(paths: str) -> str:
    """
    Deletes one or more specified files or directories from the filesystem. This action is permanent and should be used with caution. Multiple file paths can be provided as a comma-separated string.

    Args:
        paths: A comma-separated string of file or directory paths to delete.
    """
    if not paths:
        return "Error: No paths provided."
    paths_to_delete = [p.strip() for p in paths.split(',')]
    report = []
    for path in paths_to_delete:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        try:
            if os.path.isfile(path):
                os.remove(path)
                report.append(f"Successfully deleted file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                report.append(f"Successfully deleted directory: {path}")
            else:
                report.append(f"Warning: Path not found: {path}")
        except Exception as e:
            report.append(f"Error deleting {path}: {e}")
    return "\n".join(report)

