import os
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document

class FileCompleter(Completer):
    """
    A completer that suggests files and directories in the current working directory
    when the user types '@' followed by a filter string.
    """
    def __init__(self, path='.'):
        self.base_path = path

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        text_before_cursor = document.text_before_cursor

        # Find the last '@' symbol
        at_index = text_before_cursor.rfind('@')

        if at_index == -1:
            # No '@' found, no file completion
            return

        # Get the text after the last '@'
        filter_text = text_before_cursor[at_index + 1:]

        files_and_dirs = []
        try:
            # List all files and directories in the base_path
            for entry in os.listdir(self.base_path):
                # Filter based on the text typed after '@'
                if entry.lower().startswith(filter_text.lower()):
                    files_and_dirs.append(entry)
        except OSError:
            # Handle cases where directory might not exist or be accessible
            pass

        for item in sorted(files_and_dirs):
            yield Completion(item, start_position=-len(filter_text))
