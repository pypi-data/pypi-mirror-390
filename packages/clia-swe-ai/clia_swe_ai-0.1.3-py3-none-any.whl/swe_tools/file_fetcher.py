import os
from swe_tools.instance import mcp

@mcp.tool(name="read_file_content", description="""This tool is designed to retrieve and return the entire textual content of a single specified file from the local filesystem. It is a fundamental utility for gaining a complete understanding of a file's contents, which is crucial for various software engineering tasks such as:
*   **Code Review:** Examining source code files to understand logic, identify bugs, or propose improvements.
*   **Configuration Analysis:** Reading configuration files (e.g., `.ini`, `.json`, `.yaml`, `.xml`) to understand application settings.
*   **Log Inspection:** Viewing log files to diagnose issues or monitor application behavior.
*   **Documentation Access:** Retrieving the content of documentation files (e.g., `README.md`, `.txt` files) for reference.
*   **Pre-modification Review:** Before attempting any modifications to a file, it is highly recommended to read its current content to ensure changes are applied correctly and to avoid unintended overwrites.

The tool attempts to read the file using UTF-8 encoding, with a fallback to ignore characters that cannot be decoded, ensuring that most text files can be processed. It will return an error message if the specified path does not exist or if it points to a directory instead of a file.""")
def read_file_content(path: str) -> str:
    """
    Retrieves and returns the entire content of a single specified file, with line numbers.
    This is useful for examining the exact contents of a file for analysis or modification.

    Args:
        path: The path to the file to fetch.
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    try:
        if not os.path.exists(path):
            return f"The specified path does not exist: {path}"
        if not os.path.isfile(path):
            return f"The specified path is a directory, not a file: {path}"
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        return "".join(f"{i+1}:{line}" for i, line in enumerate(lines))
    except Exception as e:
        return f"Error reading file {path}: {e}"
