import os
from dotenv import load_dotenv
from core.config import MODEL_NAME, SYSTEM_PROMPT, MAX_TOOL_TURNS

load_dotenv()

# --- UI Configuration ---
USER_NAME = "User"
BOT_NAME = "Gemini"
MCP_SERVER_SCRIPT = "swe_tools.run_server"
THEME = {
    "user_prompt_icon": "›",
    "user_title_icon": "●",
    "bot_title_icon": "◆",
    "info_title_icon": "ⓘ",
    "error_title_icon": "✖",
    "tool_call_icon": "🛠",
    "user_title": "bold #00BFFF",  # Deep Sky Blue
    "bot_title": "bold #9370DB",  # Medium Purple
    "error_title": "bold #FF6347",  # Tomato
    "info_title": "bold #3CB371",  # Medium Sea Green
    "thought_title": "#FFD700",  # Gold
    "tool_call_style": "bold #FFA500",  # Orange
    "panel_border": "#555555",
    "accent_border": "#9370DB",  # Medium Purple
    "thinking_spinner": "dots",
    "separator_style": "#555555",
}