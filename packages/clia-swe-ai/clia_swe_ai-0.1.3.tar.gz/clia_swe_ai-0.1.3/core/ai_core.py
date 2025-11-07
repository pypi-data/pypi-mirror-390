# -*- coding: utf-8 -*-

import asyncio
from typing import List, Any, Dict, AsyncGenerator

from google.genai import types
from google.genai.client import Client

from core.config import MODEL_NAME, SYSTEM_PROMPT, MAX_TOOL_TURNS
from mcp import ClientSession

class AICore:
    def __init__(self, client: Client, mcp_session: ClientSession, gemini_tools: types.Tool):
        self.client = client
        self.mcp_session = mcp_session
        self.gemini_tools = gemini_tools
        self.generation_config = types.GenerateContentConfig(
            tools=[self.gemini_tools],
            system_instruction=SYSTEM_PROMPT,
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )

    async def process_message(self, history: List[types.Content], user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        history.append(types.Content(role='user', parts=[types.Part.from_text(text=user_input)]))

        turn_count = 0
        while turn_count < MAX_TOOL_TURNS:
            turn_count += 1

            stream = await self.client.aio.models.generate_content_stream(
                model=MODEL_NAME,
                contents=history,
                config=self.generation_config
            )

            bot_response_text = ""
            function_call = None
            response_content_parts = []

            async for chunk in stream:
                if not chunk.candidates:
                    continue
                
                if chunk.candidates[0].content:
                    if chunk.candidates[0].content.parts:
                        response_content_parts.extend(chunk.candidates[0].content.parts)
                    
                        for part in chunk.candidates[0].content.parts:
                            if part.function_call:
                                function_call = part.function_call
                            if part.text:
                                if part.thought:
                                    yield {"type": "thoughts", "content": part.text}
                                else:
                                    bot_response_text += part.text
  
                        
                
                yield {"type": "stream", "content": chunk}

            if response_content_parts:
                history.append(types.Content(role='model', parts=response_content_parts))

            if function_call:
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                yield {"type": "tool_call", "tool_name": tool_name, "tool_args": tool_args}

                tool_result = await self.mcp_session.call_tool(tool_name, tool_args)
                
                history.append(types.Part.from_function_response(name=tool_name, response={"result": str(tool_result)}))
                
                yield {"type": "tool_result", "tool_name": tool_name, "result": tool_result}
                
                continue
            else:
                if bot_response_text:
                    yield {"type": "bot_response", "content": bot_response_text}
                break
        
        if turn_count >= MAX_TOOL_TURNS:
            yield {"type": "error", "content": "Task may be incomplete due to reaching the maximum number of tool turns."}
