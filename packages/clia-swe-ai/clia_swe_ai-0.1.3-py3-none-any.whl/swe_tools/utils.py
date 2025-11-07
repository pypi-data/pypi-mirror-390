import os
import fnmatch
from collections import defaultdict
from typing import List, Dict, Tuple

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

def parse_multiline_commands(text: str) -> Dict[str, List[Tuple[int, str]]]:
    commands = defaultdict(list)
    current_file = None

    for line in text.strip().split('\n'):
        stripped_line = line.strip()
        if stripped_line.startswith('$'):
            current_file = stripped_line[1:].strip()
        elif current_file and ':' in line:
            try:
                line_num_str, content = line.split(':', 1)
                line_num = int(line_num_str)
                commands[current_file].append((line_num, content))
            except ValueError:
                continue
    return commands