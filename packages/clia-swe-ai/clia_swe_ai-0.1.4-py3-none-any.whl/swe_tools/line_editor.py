import os
from collections import defaultdict
from swe_tools.instance import mcp
from swe_tools.utils import parse_multiline_commands

@mcp.tool(name="edit_file_lines", description="""This tool provides a precise mechanism for modifying existing text files by applying line-by-line changes. It allows for granular control over file content, enabling insertion of new lines, updating existing lines, or deleting specific lines. This tool is particularly useful for:
*   **Refactoring Code:** Making targeted changes to function signatures, variable names, or logic within specific lines.
*   **Configuration Updates:** Modifying specific settings in configuration files without rewriting the entire file.
*   **Patching Files:** Applying small, precise changes to files, similar to a patch operation.
*   **Automated Code Generation/Modification:** Integrating into workflows that require programmatic alteration of source code.

The tool operates by taking a multiline string as input, where each line specifies a file path and a corresponding line number with its new content. The format is `$path/to/file.ext` followed by `line_num:new_content`.

**Key behaviors and considerations:**
*   **Line Numbering:** Line numbers are 1-based.
*   **Updating Lines:** If `line_num:new_content` is provided for an existing line number, the content of that line will be replaced with `new_content`.
*   **Inserting Lines:** If `line_num:new_content` is provided for a line number greater than the current number of lines in the file, new lines will be appended to reach that line number, and then `new_content` will be inserted. If there are gaps, they will be filled with empty lines.
*   **Deleting Lines:** To delete a line, provide `line_num:` (i.e., an empty string after the colon). The line at `line_num` will be removed.
*   **Multiple Changes per File:** Multiple changes per file can be specified. The tool processes these changes in the order they appear in the input string, but the internal logic handles replacements based on line numbers, ensuring correct application.
*   **File Not Found:** If a specified file path does not exist, an error will be reported for that file, and the tool will proceed to process other files.
*   **Atomicity:** Changes are applied file by file. If an error occurs while modifying one file, it will be reported, but other files may still be successfully modified.

It is highly recommended to first read the file content using `read_file_content` and carefully construct the `changes` string to avoid unintended modifications.""")
def edit_file_lines(changes: str) -> str:
    """
    Modifies existing files by applying line-by-line changes based on a provided multiline string. This tool is precise and allows for inserting, updating, or deleting specific lines within a file. The format for changes is '$path/to/file.ext\nline_num:new_content'.

    Args:
        changes: A multiline string specifying file paths and line-by-line changes.
                 Format: $path/to/file.ext\nline_num:new_content
    """
    commands = parse_multiline_commands(changes)
    report = []
    for file_path, edits in commands.items():
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)

        if not os.path.isfile(file_path):
            report.append(f"Error for {file_path}: File not found.")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            replacement_map = defaultdict(list)
            for line_num, content in edits:
                replacement_map[line_num].append(content if content.endswith('\n') else content + '\n')
            new_content = []
            processed_lines = set()
            max_line = max(len(original_lines), max(replacement_map.keys()) if replacement_map else 0)
            for i in range(max_line):
                line_num = i + 1
                if line_num in replacement_map:
                    if line_num not in processed_lines:
                        # If content is empty, it's a deletion
                        if replacement_map[line_num][0].strip() == '':
                            pass # Skip adding the line
                        else:
                            new_content.extend(replacement_map[line_num])
                        processed_lines.add(line_num)
                elif i < len(original_lines):
                    new_content.append(original_lines[i])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_content)
            report.append(f"Successfully modified {file_path}")
        except Exception as e:
            report.append(f"Error modifying {file_path}: {e}")
    return "\n".join(report) if report else "No changes specified."


