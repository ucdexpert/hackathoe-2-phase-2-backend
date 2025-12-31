"""OpenAI Agent for Phase III Todo Chatbot"""

import os
import sys
from typing import Dict, Any, List
from openai import OpenAI

# Add the backend directory to the Python path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle imports for both direct execution and module import
try:
    # Try relative imports first (when used as part of package)
    from ..mcp_tools.server import TodoMCPServer
    from ..mcp_tools.add_task import add_task_tool, TOOL_DEFINITION as ADD_TASK_DEF
    from ..mcp_tools.list_tasks import list_tasks_tool, TOOL_DEFINITION as LIST_TASKS_DEF
    from ..mcp_tools.complete_task import complete_task_tool, TOOL_DEFINITION as COMPLETE_TASK_DEF
    from ..mcp_tools.update_task import update_task_tool, TOOL_DEFINITION as UPDATE_TASK_DEF
    from ..mcp_tools.delete_task import delete_task_tool, TOOL_DEFINITION as DELETE_TASK_DEF
except (ImportError, ValueError):
    # Fall back to absolute imports (when run directly)
    from mcp_tools.server import TodoMCPServer
    from mcp_tools.add_task import add_task_tool, TOOL_DEFINITION as ADD_TASK_DEF
    from mcp_tools.list_tasks import list_tasks_tool, TOOL_DEFINITION as LIST_TASKS_DEF
    from mcp_tools.complete_task import complete_task_tool, TOOL_DEFINITION as COMPLETE_TASK_DEF
    from mcp_tools.update_task import update_task_tool, TOOL_DEFINITION as UPDATE_TASK_DEF
    from mcp_tools.delete_task import delete_task_tool, TOOL_DEFINITION as DELETE_TASK_DEF


class TodoAgent:
    """OpenAI Agent configured to work with todo application MCP tools"""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        
        # Initialize MCP server
        self.mcp_server = TodoMCPServer()
        
        # Register all MCP tools with the server
        self.mcp_server.register_tool(
            ADD_TASK_DEF["name"],
            ADD_TASK_DEF["description"],
            ADD_TASK_DEF["parameters"],
            add_task_tool
        )
        
        self.mcp_server.register_tool(
            LIST_TASKS_DEF["name"],
            LIST_TASKS_DEF["description"],
            LIST_TASKS_DEF["parameters"],
            list_tasks_tool
        )
        
        self.mcp_server.register_tool(
            COMPLETE_TASK_DEF["name"],
            COMPLETE_TASK_DEF["description"],
            COMPLETE_TASK_DEF["parameters"],
            complete_task_tool
        )
        
        self.mcp_server.register_tool(
            UPDATE_TASK_DEF["name"],
            UPDATE_TASK_DEF["description"],
            UPDATE_TASK_DEF["parameters"],
            update_task_tool
        )
        
        self.mcp_server.register_tool(
            DELETE_TASK_DEF["name"],
            DELETE_TASK_DEF["description"],
            DELETE_TASK_DEF["parameters"],
            delete_task_tool
        )
    
    async def process_message(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process a user message using the OpenAI agent with MCP tools
        
        Args:
            user_message: The message from the user
            conversation_history: History of the conversation
            user_id: The ID of the authenticated user
        
        Returns:
            Dictionary with the agent's response and any tool call results
        """
        # Prepare the messages for the OpenAI API
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful todo list assistant. Your job is to understand user requests "
                "and help them manage their tasks using the available tools. Always be friendly, "
                "concise, and helpful in your responses.\n\n"
                "1. Understand the user's intent from their message\n"
                "2. Select the appropriate tool to fulfill the request\n"
                "3. Use the tool with correct parameters\n"
                "4. Generate a natural language response based on the tool result\n"
                "5. If you're unsure about something, ask the user for clarification\n"
                "6. If a request is invalid or impossible, explain why politely\n\n"
                "Available tools: add_task, list_tasks, complete_task, update_task, delete_task"
            )
        }
        
        # Format conversation history for the API
        formatted_history = []
        for msg in conversation_history:
            formatted_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add the current user message
        formatted_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare the messages list with system message first
        messages = [system_message] + formatted_history
        
        try:
            # Call the OpenAI API with function calling
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": ADD_TASK_DEF["name"],
                            "description": ADD_TASK_DEF["description"],
                            "parameters": ADD_TASK_DEF["parameters"]
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": LIST_TASKS_DEF["name"],
                            "description": LIST_TASKS_DEF["description"],
                            "parameters": LIST_TASKS_DEF["parameters"]
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": COMPLETE_TASK_DEF["name"],
                            "description": COMPLETE_TASK_DEF["description"],
                            "parameters": COMPLETE_TASK_DEF["parameters"]
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": UPDATE_TASK_DEF["name"],
                            "description": UPDATE_TASK_DEF["description"],
                            "parameters": UPDATE_TASK_DEF["parameters"]
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": DELETE_TASK_DEF["name"],
                            "description": DELETE_TASK_DEF["description"],
                            "parameters": DELETE_TASK_DEF["parameters"]
                        }
                    }
                ],
                tool_choice="auto"
            )

            # Get the response message
            response_message = response.choices[0].message

            # If the model wants to call a tool
            tool_calls = response_message.tool_calls
            tool_results = []

            if tool_calls:
                # Execute each tool call
                for tool_call in tool_calls:
                    import json
                    function_args = json.loads(tool_call.function.arguments)

                    # Add user_id to function arguments if not present
                    if "user_id" not in function_args:
                        function_args["user_id"] = user_id

                    # Execute the tool with authentication
                    result = await self.mcp_server.execute_tool(tool_call.function.name, function_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "result": result
                    })

                # If there were tool calls, get a final response from the model
                if tool_results:
                    # Add tool results to messages
                    messages.append(response_message)
                    for tool_result in tool_results:
                        messages.append({
                            "role": "tool",
                            "content": str(tool_result["result"]),
                            "tool_call_id": tool_result["tool_call_id"]
                        })

                    # Get final response from the model
                    final_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )

                    return {
                        "response": final_response.choices[0].message.content,
                        "tool_calls": [tc.model_dump() for tc in tool_calls],
                        "tool_results": tool_results
                    }

            # If no tool calls were made, return the direct response
            return {
                "response": response_message.content,
                "tool_calls": [],
                "tool_results": []
            }

        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "tool_calls": [],
                "tool_results": [],
                "error": str(e)
            }