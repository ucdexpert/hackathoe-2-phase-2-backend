"""Google Gemini Agent for Phase III Todo Chatbot"""

import os
import sys
import json
from typing import Dict, Any, List
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

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
    """Google Gemini Agent configured to work with todo application MCP tools"""

    def __init__(self, gemini_api_key: str = None):
        # Initialize Gemini client
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=api_key)

        # Define the tools (functions) that Gemini can use
        function_declarations = [
            genai.protos.FunctionDeclaration(
                name=ADD_TASK_DEF["name"],
                description=ADD_TASK_DEF["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=get_gemini_type(v["type"]),
                            description=v.get("description", "") + (" (Note: user_id is automatically provided)" if k == "user_id" else "")
                        ) for k, v in ADD_TASK_DEF["parameters"]["properties"].items()
                    },
                    required=[param for param in ADD_TASK_DEF["parameters"]["required"] if param != "user_id"]  # Remove user_id from required params for Gemini
                )
            ),
            genai.protos.FunctionDeclaration(
                name=LIST_TASKS_DEF["name"],
                description=LIST_TASKS_DEF["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=get_gemini_type(v["type"]),
                            description=v.get("description", "") + (" (Note: user_id is automatically provided)" if k == "user_id" else "")
                        ) for k, v in LIST_TASKS_DEF["parameters"]["properties"].items()
                    },
                    required=[param for param in LIST_TASKS_DEF["parameters"]["required"] if param != "user_id"]  # Remove user_id from required params for Gemini
                )
            ),
            genai.protos.FunctionDeclaration(
                name=COMPLETE_TASK_DEF["name"],
                description=COMPLETE_TASK_DEF["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=get_gemini_type(v["type"]),
                            description=v.get("description", "") + (" (Note: user_id is automatically provided)" if k == "user_id" else "")
                        ) for k, v in COMPLETE_TASK_DEF["parameters"]["properties"].items()
                    },
                    required=[param for param in COMPLETE_TASK_DEF["parameters"]["required"] if param != "user_id"]  # Remove user_id from required params for Gemini
                )
            ),
            genai.protos.FunctionDeclaration(
                name=UPDATE_TASK_DEF["name"],
                description=UPDATE_TASK_DEF["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=get_gemini_type(v["type"]),
                            description=v.get("description", "") + (" (Note: user_id is automatically provided)" if k == "user_id" else "")
                        ) for k, v in UPDATE_TASK_DEF["parameters"]["properties"].items()
                    },
                    required=[param for param in UPDATE_TASK_DEF["parameters"]["required"] if param != "user_id"]  # Remove user_id from required params for Gemini
                )
            ),
            genai.protos.FunctionDeclaration(
                name=DELETE_TASK_DEF["name"],
                description=DELETE_TASK_DEF["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=get_gemini_type(v["type"]),
                            description=v.get("description", "") + (" (Note: user_id is automatically provided)" if k == "user_id" else "")
                        ) for k, v in DELETE_TASK_DEF["parameters"]["properties"].items()
                    },
                    required=[param for param in DELETE_TASK_DEF["parameters"]["required"] if param != "user_id"]  # Remove user_id from required params for Gemini
                )
            )
        ]

        # Create tools object
        tools = genai.protos.Tool(function_declarations=function_declarations)

        # Create the model with tools - using the stable gemini-pro model
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            generation_config=GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048
            ),
            tools=[tools]
        )

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
        Process a user message using the Google Gemini agent with MCP tools

        Args:
            user_message: The message from the user
            conversation_history: History of the conversation
            user_id: The ID of the authenticated user

        Returns:
            Dictionary with the agent's response and any tool call results
        """
        # Prepare the conversation context
        system_context = (
            "You are a helpful todo list assistant. Your job is to understand user requests "
            "and help them manage their tasks using the available tools. Always be friendly, "
            "concise, and helpful in your responses.\n\n"
            "1. Understand the user's intent from their message\n"
            "2. Select the appropriate tool to fulfill the request\n"
            "3. Use the tool with correct parameters\n"
            "4. Generate a natural language response based on the tool result\n"
            "5. If you're unsure about something, ask the user for clarification\n"
            "6. If a request is invalid or impossible, explain why politely\n\n"
            "IMPORTANT: The user_id is automatically provided with every request, so do not ask the user for their user_id.\n\n"
            "TASK ID GUIDELINES:\n"
            "- Always include task IDs when displaying tasks to the user\n"
            "- Format tasks as: \"1. Task title (✅ completed / ⬜ pending)\"\n"
            "- Extract task IDs from user requests like: 'task 1', 'task 3', 'number 2', 'complete 3', 'delete task 2', 'update task 1 to new title'\n"
            "- When listing tasks, format as: \"You have X tasks:\\n1. Task title (✅ completed)\\n2. Task title (⬜ pending)\\n3. Task title (⬜ pending)\"\n"
            "Available tools: add_task, list_tasks, complete_task, update_task, delete_task"
        )

        # Format conversation history for the API
        formatted_history = []
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"  # Gemini uses "model" instead of "assistant"
            formatted_history.append({
                "role": role,
                "parts": [msg["content"]]
            })

        # Create the full prompt with context
        full_prompt = f"{system_context}\n\n"

        # Add conversation history
        for msg in formatted_history:
            full_prompt += f"{msg['role']}: {msg['parts'][0]}\n"

        # Add the current user message
        full_prompt += f"user: {user_message}\nmodel:"

        try:
            # Configure the request to prefer function calling
            generation_config = GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048
            )

            # Create a chat session
            chat = self.model.start_chat()

            # Send the message to the model
            response = chat.send_message(
                full_prompt,
                generation_config=generation_config,
                safety_settings={
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE'
                }
            )

            # Check if the model decided to call a function
            tool_results = []
            tool_calls = []

            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name

                        # Debug: print what we got
                        print(f"Function called: {function_name}")
                        print(f"Arguments: {dict(function_call.args) if hasattr(function_call, 'args') and function_call.args is not None else {}}")

                        if not function_name:
                            continue  # Skip empty function names

                        # Safely handle function arguments, defaulting to empty dict if None
                        function_args = {}
                        if hasattr(function_call, 'args') and function_call.args is not None:
                            function_args = {k: v for k, v in function_call.args.items()}

                        # CRITICAL: Always add user_id - don't rely on agent to provide it
                        function_args["user_id"] = user_id  # Force override

                        # Convert string parameters to appropriate types for specific tools
                        if function_name in ["complete_task", "update_task", "delete_task"] and "task_id" in function_args:
                            try:
                                # Convert task_id from string to integer
                                function_args["task_id"] = int(function_args["task_id"])
                            except (ValueError, TypeError):
                                print(f"Warning: Could not convert task_id '{function_args['task_id']}' to integer for function {function_name}")

                        # Convert 'completed' parameter for complete_task to boolean
                        if function_name == "complete_task" and "completed" in function_args:
                            completed_value = function_args["completed"]
                            if isinstance(completed_value, str):
                                # Convert string to boolean: 'true'/'True'/'1' -> True, everything else -> False
                                if completed_value.lower() in ['true', '1']:
                                    function_args["completed"] = True
                                elif completed_value.lower() in ['false', '0']:
                                    function_args["completed"] = False
                                else:
                                    # If it's not a recognized boolean string, default to True for 'complete' actions
                                    function_args["completed"] = True
                            elif isinstance(completed_value, int):
                                # Convert integer to boolean
                                function_args["completed"] = bool(completed_value)

                        # Execute the tool
                        try:
                            result = await self.mcp_server.execute_tool(function_name, function_args)
                            tool_results.append({
                                "tool_call_id": function_name,
                                "result": result
                            })
                        except Exception as e:
                            print(f"Tool execution error: {e}")
                            tool_results.append({
                                "tool_call_id": function_name,
                                "result": {"error": str(e)}
                            })

                        tool_calls.append({
                            "id": function_name,
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(dict(function_call.args) if hasattr(function_call, 'args') and function_call.args is not None else {})
                            },
                            "type": "function"
                        })

            # If there were tool calls, get a final response from the model
            if tool_results:
                # Check if this was a list_tasks call to format the response appropriately
                is_list_tasks_call = any(tc["function"]["name"] == "list_tasks" for tc in tool_calls)

                if is_list_tasks_call:
                    # Format the list_tasks response manually to show task IDs with status
                    list_result = next((tr for tr in tool_results if tr["tool_call_id"] == "list_tasks"), None)
                    if list_result and list_result["result"]["success"]:
                        tasks = list_result["result"]["data"]
                        if tasks:
                            formatted_tasks = []
                            for task in tasks:
                                status = "✅" if task["completed"] else "⬜"
                                formatted_task = f"{task['id']}. {task['title']} ({status} { 'completed' if task['completed'] else 'pending'})"
                                formatted_tasks.append(formatted_task)

                            response_text = f"You have {len(tasks)} tasks:\n" + "\n".join(formatted_tasks)
                        else:
                            response_text = "You have no tasks."

                        return {
                            "response": response_text,
                            "tool_calls": tool_calls,
                            "tool_results": tool_results
                        }

                # For other tool calls, send the function results back to the chat
                for tool_result in tool_results:
                    # Create function response part
                    function_response = genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=tool_result["tool_call_id"],
                            response={"result": tool_result["result"]}
                        )
                    )

                    # Send the function response to the model to get the final response
                    final_response = chat.send_message([function_response])

                return {
                    "response": final_response.text if final_response and final_response.text else "I processed your request using the appropriate tools.",
                    "tool_calls": tool_calls,
                    "tool_results": tool_results
                }

            # If no tool calls were made, return the direct response
            response_text = response.text if response and response.text else "I'm here to help with your todo list."
            return {
                "response": response_text,
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


def get_gemini_type(json_type: str):
    """Convert JSON schema type to Gemini type"""
    type_mapping = {
        "string": genai.protos.Type.STRING,
        "number": genai.protos.Type.NUMBER,
        "integer": genai.protos.Type.INTEGER,
        "boolean": genai.protos.Type.BOOLEAN,
        "array": genai.protos.Type.ARRAY,
        "object": genai.protos.Type.OBJECT
    }
    return type_mapping.get(json_type, genai.protos.Type.STRING)