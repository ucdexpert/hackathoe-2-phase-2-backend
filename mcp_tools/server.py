"""MCP Server infrastructure for Phase III AI chatbot"""

import asyncio
from typing import Dict, Any, Callable, Awaitable
import json
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Definition of an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]


class TodoMCPServer:
    """MCP Server for todo application tools"""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler: Callable):
        """Register a new tool with the MCP server"""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "handler": handler
        }

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a registered tool with the given arguments"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")

        tool_info = self.tools[name]
        handler = tool_info["handler"]

        # Execute the handler (could be sync or async)
        if asyncio.iscoroutinefunction(handler):
            result = await handler(arguments)
        else:
            result = handler(arguments)

        return result

    def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all registered tool definitions"""
        definitions = {}
        for name, tool_info in self.tools.items():
            definitions[name] = ToolDefinition(
                name=name,
                description=tool_info["description"],
                parameters=tool_info["parameters"]
            )
        return definitions