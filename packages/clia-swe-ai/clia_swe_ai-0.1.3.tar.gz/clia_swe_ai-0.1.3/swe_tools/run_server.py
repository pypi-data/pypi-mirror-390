import sys
import os
from swe_tools.instance import mcp

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import all tool modules to register them with the FastMCP instance
from swe_tools import cli_commander
from swe_tools import codebase_restorer
from swe_tools import codebase_snapshot_generator
from swe_tools import directory_tree_viewer
from swe_tools import file_deleter
from swe_tools import file_fetcher
from swe_tools import line_editor
from swe_tools import process_manager
from swe_tools import utils
from swe_tools import image_viewer

if __name__ == "__main__":
    mcp.run()
