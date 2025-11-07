from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document
from typing import List

class ToolCompleter(Completer):
    """
    A completer that suggests tool names when the user types '#' followed by a filter string.
    """
    def __init__(self, tool_names: List[str]):
        self.tool_names = sorted(tool_names)

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        text_before_cursor = document.text_before_cursor

        # Find the last '#' symbol
        hash_index = text_before_cursor.rfind('#')

        if hash_index == -1:
            # No '#' found, no tool completion
            return

        # Get the text after the last '#'
        filter_text = text_before_cursor[hash_index + 1:]

        for tool_name in self.tool_names:
            if tool_name.lower().startswith(filter_text.lower()):
                yield Completion(tool_name, start_position=-len(filter_text))
