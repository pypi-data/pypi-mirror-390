# -*- coding: utf-8 -*-

import os
import sys
from google import genai
from google.genai import errors as genai_errors
from gui.ui import create_message_panel, console
from prompt_toolkit import PromptSession # Import PromptSession
from dotenv import load_dotenv, find_dotenv # Import dotenv functions

import asyncio # Import asyncio for await

async def get_gemini_client():
    """Initializes and returns the Gemini client, handling errors."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        console.print(create_message_panel("It looks like your Google Gemini API Key is not set up yet.", role="info"))
        console.print(create_message_panel("Please enter your Google Gemini API Key. This will be saved to a .env file for future use.", role="info"))
        
        session = PromptSession()
        try:
            api_key = await session.prompt_async("Enter your Google Gemini API Key: ", is_password=True)
            if not api_key.strip():
                console.print(create_message_panel("API Key cannot be empty. Exiting.", role="error"))
                sys.exit(1)
            
            # Save to .env file
            dotenv_path = find_dotenv()
            if not dotenv_path: # .env file does not exist, create it in the current directory
                dotenv_path = os.path.join(os.getcwd(), '.env')
            
            with open(dotenv_path, 'a') as f: # Append to file
                f.write(f'\nGOOGLE_API_KEY="{api_key.strip()}"\n')
            
            # Reload environment variables to make the new key available
            load_dotenv(dotenv_path, override=True)
            os.environ["GOOGLE_API_KEY"] = api_key.strip() # Ensure it's set for the current process
            console.print(create_message_panel(f"API Key saved to {dotenv_path} and loaded.", role="info"))

        except KeyboardInterrupt:
            console.print(create_message_panel("\nAPI Key entry cancelled. Exiting.", role="error"))
            sys.exit(1)
        except Exception as e:
            console.print(create_message_panel(f"Error during API Key input or saving: {e}", role="error"))
            sys.exit(1)
    
    try:
        # Use the Client constructor which is compatible with the user's environment
        client = genai.Client(api_key=api_key)
        # Test the connection by listing models
        _ = client.models.list()
        return client
    except genai_errors.APIError as e:
        console.print(create_message_panel(f"API Error during client initialization. Check your API key and permissions.\nDetails: {e}", role="error"))
        sys.exit(1)
    except Exception as e:
        console.print(create_message_panel(f"An unexpected error occurred during client initialization.\nDetails: {e}", role="error"))
        sys.exit(1)