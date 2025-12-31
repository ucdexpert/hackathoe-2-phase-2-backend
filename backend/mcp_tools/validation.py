"""Input validation utilities for MCP tools"""

from typing import Dict, Any


def validate_add_task_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for add_task tool
    """
    errors = []
    
    # Check required fields
    if "title" not in arguments or not arguments["title"]:
        errors.append("title is required")
    elif not isinstance(arguments["title"], str):
        errors.append("title must be a string")
    elif len(arguments["title"]) < 1 or len(arguments["title"]) > 200:
        errors.append("title must be between 1 and 200 characters")
    
    # Validate description if provided
    if "description" in arguments and arguments["description"] is not None:
        if not isinstance(arguments["description"], str):
            errors.append("description must be a string")
        elif len(arguments["description"]) > 5000:
            errors.append("description must be 5000 characters or less")
    
    # Validate user_id if provided
    if "user_id" in arguments:
        if not isinstance(arguments["user_id"], str):
            errors.append("user_id must be a string")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_list_tasks_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for list_tasks tool
    """
    errors = []
    
    # Check required fields
    if "user_id" not in arguments or not arguments["user_id"]:
        errors.append("user_id is required")
    elif not isinstance(arguments["user_id"], str):
        errors.append("user_id must be a string")
    
    # Validate status if provided
    if "status" in arguments and arguments["status"] is not None:
        if arguments["status"] not in ["all", "pending", "completed"]:
            errors.append("status must be 'all', 'pending', or 'completed'")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_complete_task_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for complete_task tool
    """
    errors = []
    
    # Check required fields
    if "user_id" not in arguments or not arguments["user_id"]:
        errors.append("user_id is required")
    elif not isinstance(arguments["user_id"], str):
        errors.append("user_id must be a string")
    
    if "task_id" not in arguments or arguments["task_id"] is None:
        errors.append("task_id is required")
    elif not isinstance(arguments["task_id"], int):
        errors.append("task_id must be an integer")
    
    # Validate completed if provided
    if "completed" in arguments and arguments["completed"] is not None:
        if not isinstance(arguments["completed"], bool):
            errors.append("completed must be a boolean")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_update_task_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for update_task tool
    """
    errors = []
    
    # Check required fields
    if "user_id" not in arguments or not arguments["user_id"]:
        errors.append("user_id is required")
    elif not isinstance(arguments["user_id"], str):
        errors.append("user_id must be a string")
    
    if "task_id" not in arguments or arguments["task_id"] is None:
        errors.append("task_id is required")
    elif not isinstance(arguments["task_id"], int):
        errors.append("task_id must be an integer")
    
    # Validate title if provided
    if "title" in arguments and arguments["title"] is not None:
        if not isinstance(arguments["title"], str):
            errors.append("title must be a string")
        elif len(arguments["title"]) < 1 or len(arguments["title"]) > 200:
            errors.append("title must be between 1 and 200 characters")
    
    # Validate description if provided
    if "description" in arguments and arguments["description"] is not None:
        if not isinstance(arguments["description"], str):
            errors.append("description must be a string")
        elif len(arguments["description"]) > 5000:
            errors.append("description must be 5000 characters or less")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_delete_task_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for delete_task tool
    """
    errors = []
    
    # Check required fields
    if "user_id" not in arguments or not arguments["user_id"]:
        errors.append("user_id is required")
    elif not isinstance(arguments["user_id"], str):
        errors.append("user_id must be a string")
    
    if "task_id" not in arguments or arguments["task_id"] is None:
        errors.append("task_id is required")
    elif not isinstance(arguments["task_id"], int):
        errors.append("task_id must be an integer")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# Mapping of tool names to their validation functions
VALIDATION_FUNCTIONS = {
    "add_task": validate_add_task_input,
    "list_tasks": validate_list_tasks_input,
    "complete_task": validate_complete_task_input,
    "update_task": validate_update_task_input,
    "delete_task": validate_delete_task_input
}


def validate_tool_input(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input for a specific tool
    """
    if tool_name not in VALIDATION_FUNCTIONS:
        return {
            "valid": False,
            "errors": [f"Unknown tool: {tool_name}"]
        }
    
    validation_func = VALIDATION_FUNCTIONS[tool_name]
    return validation_func(arguments)