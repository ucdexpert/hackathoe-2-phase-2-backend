"""add_task MCP tool implementation"""

from sqlmodel import Session
from models import TaskCreate, Task
from database import get_session
from typing import Dict, Any
from datetime import datetime
from .auth import validate_user_access
from .validation import validate_tool_input


async def add_task_tool(arguments: Dict[str, Any], authenticated_user_id: str = None) -> Dict[str, Any]:
    """
    MCP tool to create a new task
    Expected arguments:
    - user_id: str (required)
    - title: str (required, 1-200 characters)
    - description: str (optional, max 5000 characters)
    """
    # Validate input
    validation_result = validate_tool_input("add_task", arguments)
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
    title = arguments.get("title")
    description = arguments.get("description", None)

    try:
        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Create task directly using SQLModel
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            # Return success response
            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task created successfully"
            }
        finally:
            session.close()
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Failed to create task: {str(e)}"
            }
        }


# Tool definition for registration
TOOL_DEFINITION = {
    "name": "add_task",
    "description": "Create a new task",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "The ID of the user creating the task"
            },
            "title": {
                "type": "string",
                "description": "The title of the task (1-200 characters)",
                "minLength": 1,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description of the task",
                "maxLength": 5000
            }
        },
        "required": ["user_id", "title"]
    }
}