#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import traceback
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.console import Group
from rich.markdown import Markdown
from rich import box
from datetime import datetime
from google.genai import types
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

import json

from gui.config import MCP_SERVER_SCRIPT, THEME
from core.config import MODEL_NAME
from gui.ui import create_message_panel, show_welcome_screen, console, create_permission_panel
from gui.client import get_gemini_client
from core.tool_utils import mcp_tool_to_genai_tool
from core.ai_core import AICore
from gui.file_completer import FileCompleter
from gui.tool_completer import ToolCompleter
from gui.completers import CombinedCompleter

PERMISSIONS_FILE = "permissions.json"

always_allowed_tools = set()

def load_permissions():
    global always_allowed_tools
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, "r") as f:
            try:
                permissions = json.load(f)
                always_allowed_tools = set(permissions.get("always_allowed", []))
            except json.JSONDecodeError:
                always_allowed_tools = set()
    else:
        # Create an empty permissions file if it doesn't exist
        with open(PERMISSIONS_FILE, "w") as f:
            json.dump({"always_allowed": []}, f)

def save_permissions():
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump({"always_allowed": list(always_allowed_tools)}, f)

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def main():
    """Main function for the stable Polished Scrolling UI."""
    client = await get_gemini_client()
    gemini_history = []

    console.print(show_welcome_screen())
    console.print(create_message_panel("🤖 CLI SWE AI Initializing..."))
    console.print(create_message_panel(f"🧠 Using Model: {MODEL_NAME}"))
    console.print(create_message_panel(f"🛠️ Looking for tool server: {MCP_SERVER_SCRIPT}"))

    load_permissions()

    server_params = StdioServerParameters(command=sys.executable, args=["-m", MCP_SERVER_SCRIPT], env={**os.environ.copy(), 'PYTHONPATH': os.getcwd()})

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                console.print(create_message_panel("✅ MCP Tool Server Connected."))

                mcp_tools_response = await mcp_session.list_tools()
                if not mcp_tools_response or not mcp_tools_response.tools:
                    console.print(create_message_panel("❌ ERROR: No tools found on the MCP server.", role="error"))
                    return

                # Store tool descriptions for permission panel
                tool_descriptions = {t.name: t.description for t in mcp_tools_response.tools}

                gemini_tools = types.Tool(function_declarations=[mcp_tool_to_genai_tool(t) for t in mcp_tools_response.tools])
              
                ai_core = AICore(client, mcp_session, gemini_tools)

                # Define custom styles for prompt_toolkit
                custom_style = Style.from_dict({
                    'completion-menu': 'bg:#1a1a1a #ffffff',
                    'completion-menu.completion': 'bg:#1a1a1a #ffffff',
                    'completion-menu.completion.current': 'bg:#007bff #ffffff',
                    'completion-menu.completion.meta': 'fg:#888888',
                    'completion-menu.completion.meta.current': 'fg:#ffffff bg:#007bff',
                    'bottom-toolbar': 'bg:#333333 #ffffff',
                })

                # Initialize completers
                file_completer = FileCompleter()
                tool_names = [t.name for t in mcp_tools_response.tools]
                tool_completer = ToolCompleter(tool_names=tool_names)
                combined_completer = CombinedCompleter(file_completer, tool_completer)

                # Define a callable for the bottom toolbar
                def get_bottom_toolbar():
                    return HTML(f"<b><style bg=\"#9400D3\" fg=\"#ffffff\">Press Ctrl-C to exit. Type '@' for file completion. Type '#' for tool completion.</style></b>")

                # Setup prompt_toolkit session
                session = PromptSession(
                    completer=combined_completer,
                    auto_suggest=AutoSuggestFromHistory(),
                    bottom_toolbar=get_bottom_toolbar,
                    style=custom_style
                )

                # Define key bindings
                kb = KeyBindings()

                @kb.add(Keys.ControlC)
                def _(event):
                    """Exit when Ctrl-C is pressed."""
                    event.app.exit()



                while True:
                    try:
                        user_task_input = await session.prompt_async(Text(f"{THEME['user_prompt_icon']} ", style=THEME['user_title']).plain, key_bindings=kb)

                        if user_task_input is None:
                            console.print(create_message_panel("Session ended. Goodbye!", role="info"))
                            break
                        if user_task_input.lower() in ["exit", "quit"]:
                            console.print(create_message_panel("Session ended. Goodbye!"))
                            break
                        if not user_task_input.strip():
                            continue

                        console.print(create_message_panel(user_task_input, role="user"))

                        spinner = Spinner("dots", text=Text("Thinking...", style="green"))
                        thought_panel = Panel(
                            Text(""),
                            box=box.DOUBLE,
                            border_style="green",
                            padding=(1, 2),
    
                        )
                        live_group = Group(spinner)
                        
                        live = Live(live_group, console=console, auto_refresh=False, vertical_overflow="visible")
                        live.start()
                        
                        first_thought_received = False
                        
                        try:
                            #render spinner only
                            live.refresh()
                            async for event in ai_core.process_message(gemini_history, user_task_input):
                                if event["type"] == "stream":
                                        live.refresh() 
                                elif event["type"] == "thoughts": 
                                    if not first_thought_received:
                                        live_group.renderables.append(thought_panel)
                                        first_thought_received = True
                                    thought_panel.renderable = Markdown(event["content"], inline_code_lexer="python")
                                elif event["type"] == "tool_call":
                                    live.refresh()
                                   # live.stop()
                                    
                                    tool_name = event["tool_name"]
                                    tool_args = event["tool_args"]
                                    tool_description = tool_descriptions.get(tool_name, "No description available.")

                                    tool_allowed = False
                                    if tool_name in always_allowed_tools:
                                        tool_allowed = True
                                        console.print(create_message_panel(f"Tool `{tool_name}` automatically allowed (always allowed).", role="info"))
                                    else:
                                        live.stop()
                                        console.print(create_permission_panel(tool_name, str(tool_args), tool_description))
                                        while True:
                                            permission_choice = await session.prompt_async(Text("Enter your choice (1, 2, or 3): ", style="bold white").plain)
                                            if permission_choice == "1":
                                                tool_allowed = True
                                                console.print(create_message_panel(f"Tool `{tool_name}` allowed for this turn.", role="info"))
                                                break
                                            elif permission_choice == "2":
                                                tool_allowed = True
                                                always_allowed_tools.add(tool_name)
                                                save_permissions()
                                                console.print(create_message_panel(f"Tool `{tool_name}` always allowed from now on.", role="info"))
                                                break
                                            elif permission_choice == "3":
                                                tool_allowed = False
                                                console.print(create_message_panel(f"Tool `{tool_name}` denied.", role="info"))
                                                break
                                            else:
                                                console.print(create_message_panel("Invalid choice. Please enter 1, 2, or 3.", role="error"))
                                        live.start()
                                        live.refresh()
                                    
                                    if tool_allowed:
                                        console.print(create_message_panel(f"Calling tool `{tool_name}` with arguments: `{tool_args}`", role="tool_call"))
                                        tool_result = await ai_core.mcp_session.call_tool(tool_name, tool_args)
                                        history_part = types.Part.from_function_response(name=tool_name, response={"result": str(tool_result)})
                                        gemini_history.append(history_part)
                                        console.print(create_message_panel(f'''Tool `{tool_name}` returned: 
                                                        ```json
                                                        {str(tool_result)}
                                                        ```''', role="info", title="Tool Result"))
                                    else:
                                        tool_result = {"status": "denied", "message": f"Tool call for `{tool_name}` was denied by the user."}
                                        history_part = types.Part.from_function_response(name=tool_name, response={"result": str(tool_result)})
                                        gemini_history.append(history_part)
                                        console.print(create_message_panel(f'''Tool `{tool_name}` returned: 
                                                        ```json
                                                        {str(tool_result)}
                                                        ```''', role="info", title="Tool Result"))
                                        live.refresh()
                                    # live.start()
                                    # live.refresh()
                                elif event["type"] == "bot_response":
                                    live.stop()  
                                    console.print(create_message_panel(event["content"], role="bot"))
                                    break
                                elif event["type"] == "error":
                                    live.stop()   
                                    console.print(create_message_panel(event["content"], role="error"))
                                    break
                        finally:
    
                            live.stop()

                    except EOFError:
                        break
                    except KeyboardInterrupt:
                        console.print(create_message_panel("\nChat interrupted by user. Exiting.", role="info"))
                        break
                    except Exception as e:
                        error_msg = f"An error occurred: {e}\n{traceback.format_exc()}"
                        console.print(create_message_panel(error_msg, role="error"))
                        continue
    
    except Exception as e:
        console.print(create_message_panel(f"❌ An unexpected error occurred during MCP server connection: {e}\n{traceback.format_exc()}", role="error"))

def run_clia():
    """Entry point for the console script."""
    if "--web" in sys.argv or "-web" in sys.argv:
        try:
            import uvicorn
            console.print(create_message_panel("Starting web UI..."))
            # Ensure the app is run with the correct module path
            uvicorn.run("web_ui.app:app", host="127.0.0.1", port=8000, reload=True)
        except ImportError:
            console.print(create_message_panel("`uvicorn` is not installed. Please run `pip install uvicorn`.", role="error"))
        except Exception as e:
            console.print(create_message_panel(f"❌ A fatal error occurred while starting the web server: {e}", role="error"))
            traceback.print_exc()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            console.print("\n[bold red]CLI terminated.[/bold red]")
        except Exception as e:
            console.print(f"❌ A fatal error occurred: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    run_clia()
