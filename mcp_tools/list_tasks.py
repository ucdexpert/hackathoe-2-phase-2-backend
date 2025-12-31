"""list_tasks MCP tool implementation"""

from sqlmodel import Session, select
from models import Task
from database import get_session
from typing import Dict, Any
from .auth import validate_user_access
from .validation import validate_tool_input


async def list_tasks_tool(arguments: Dict[str, Any], authenticated_user_id: str = None) -> Dict[str, Any]:
    """
    MCP tool to retrieve tasks for a user with optional filtering
    Expected arguments:
    - user_id: str (required)
    - status: str (optional, values: "all", "pending", "completed")
    """
    # Validate input
    validation_result = validate_tool_input("list_tasks", arguments)
    if not validation_result["valid"]:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "; ".join(validation_result["errors"])
            }
        }

    # Validate authentication if authenticated_user_id is provided
    if authenticated_user_id is not None:
        auth_validation_result = validate_user_access(arguments, authenticated_user_id)
        if not auth_validation_result["valid"]:
            return {
                "success": False,
                "error": auth_validation_result["error"]
            }

    # Extract arguments
    user_id = arguments.get("user_id")
    status = arguments.get("status", "all")  # Default to "all"

    try:
        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Build query
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter if specified
            if status == "completed":
                query = query.where(Task.completed == True)
            elif status == "pending":
                query = query.where(Task.completed == False)
            # For "all", no additional filtering is needed

            tasks = session.exec(query).all()

            # Convert tasks to dictionary format
            tasks_data = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                tasks_data.append(task_dict)

            # Return success response
            return {
                "success": True,
                "data": tasks_data,
                "count": len(tasks_data)
            }
        finally:
            session.close()
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Failed to retrieve tasks: {str(e)}"
            }
        }


# Tool definition for registration
TOOL_DEFINITION = {
    "name": "list_tasks",
    "description": "Retrieve tasks from the list",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "The ID of the user whose tasks to retrieve"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter tasks by completion status",
                "default": "all"
            }
        },
        "required": ["user_id"]
    }
}