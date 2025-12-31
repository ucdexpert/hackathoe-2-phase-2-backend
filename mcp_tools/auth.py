"""Authentication validation utilities for MCP tools"""

from typing import Dict, Any


def validate_user_access(arguments: Dict[str, Any], authenticated_user_id: str) -> Dict[str, Any]:
    """
    Validate that the user_id in the arguments matches the authenticated user
    Returns a dictionary with validation result
    """
    user_id = arguments.get("user_id")
    
    if not user_id:
        return {
            "valid": False,
            "error": {
                "code": "MISSING_USER_ID",
                "message": "user_id is required in arguments"
            }
        }
    
    if user_id != authenticated_user_id:
        return {
            "valid": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "User ID in arguments does not match authenticated user"
            }
        }
    
    return {
        "valid": True,
        "error": None
    }


def apply_authentication_validation(tool_func):
    """
    Decorator to apply authentication validation to MCP tools
    This is a simplified version - in a real implementation, you'd have more sophisticated auth handling
    """
    async def wrapper(arguments: Dict[str, Any], authenticated_user_id: str = None):
        # If authenticated_user_id is provided, validate it
        if authenticated_user_id is not None:
            validation_result = validate_user_access(arguments, authenticated_user_id)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
        
        # Call the original tool function
        return await tool_func(arguments)
    
    return wrapper