# -*- coding: utf-8 -*-

from typing import List, Any, Dict
from google.genai import types
from mcp.types import Tool as MCPTool

def mcp_tool_to_genai_tool(mcp_tool: MCPTool) -> types.FunctionDeclaration:
    """Converts an MCP Tool object to a Gemini FunctionDeclaration."""
    gemini_properties: Dict[str, Any] = {}
    required_params: List[str] = []
    
    if mcp_tool.inputSchema:
        schema = mcp_tool.inputSchema
        if 'properties' in schema and isinstance(schema['properties'], dict):
            for param_name, param_details in schema['properties'].items():
                param_type = param_details.get('type', 'STRING').upper()
                param_description = param_details.get('description', f'Parameter {param_name}')
                
                # The 'type' parameter for Schema expects a string, not an enum.
                gemini_properties[param_name] = types.Schema(
                    type=param_type,
                    description=param_description
                )
        if 'required' in schema and isinstance(schema['required'], list):
            required_params = schema['required']
            
    return types.FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description,
        parameters=types.Schema(type='OBJECT', properties=gemini_properties, required=required_params)
    )
