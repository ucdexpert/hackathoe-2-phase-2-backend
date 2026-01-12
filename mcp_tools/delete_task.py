"""delete_task MCP tool implementation"""

from sqlmodel import Session, select
from models import Task
from database import get_session
from typing import Dict, Any
from .auth import validate_user_access
from .validation import validate_tool_input


async def delete_task_tool(arguments: Dict[str, Any], authenticated_user_id: str = None) -> Dict[str, Any]:
    """
    MCP tool to remove a task from the user's list
    Expected arguments:
    - user_id: str (required)
    - task_id: int (required)
    """
    # Validate input
    validation_result = validate_tool_input("delete_task", arguments)
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
    task_id = arguments.get("task_id")

    try:
        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the task
            task = session.get(Task, task_id)

            # Check if task exists
            if not task:
                return {
                    "success": False,
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found"
                    }
                }

            # Check if task belongs to user
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Task does not belong to user"
                    }
                }

            # Store task data before deletion for the response
            task_data = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            # Delete the task
            session.delete(task)
            session.commit()

            # Return success response
            return {
                "success": True,
                "data": task_data,
                "message": "Task deleted successfully"
            }
        finally:
            session.close()
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Failed to delete task: {str(e)}"
            }
        }


# Tool definition for registration
TOOL_DEFINITION = {
    "name": "delete_task",
    "description": "Remove a task from the list",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "The ID of the user who owns the task"
            },
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to delete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}