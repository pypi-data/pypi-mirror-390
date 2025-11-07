from prompt_toolkit.completion import Completer, CompleteEvent, Completion
from prompt_toolkit.document import Document
from gui.file_completer import FileCompleter
from gui.tool_completer import ToolCompleter

class CombinedCompleter(Completer):
    def __init__(self, file_completer: FileCompleter, tool_completer: ToolCompleter):
        self.file_completer = file_completer
        self.tool_completer = tool_completer

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        text_before_cursor = document.text_before_cursor

        # Check for tool completion trigger '#'
        if '#' in text_before_cursor:
            # Delegate to ToolCompleter
            yield from self.tool_completer.get_completions(document, complete_event)
        # Check for file completion trigger '@'
        elif '@' in text_before_cursor:
            # Delegate to FileCompleter
            yield from self.file_completer.get_completions(document, complete_event)
        else:
            # No specific trigger, provide no completions or default ones if desired
            return
