"""MCP Tools module for Phase III AI chatbot"""

from .server import TodoMCPServer
from .add_task import add_task_tool, TOOL_DEFINITION as ADD_TASK_DEF
from .list_tasks import list_tasks_tool, TOOL_DEFINITION as LIST_TASKS_DEF
from .complete_task import complete_task_tool, TOOL_DEFINITION as COMPLETE_TASK_DEF
from .update_task import update_task_tool, TOOL_DEFINITION as UPDATE_TASK_DEF
from .delete_task import delete_task_tool, TOOL_DEFINITION as DELETE_TASK_DEF

__all__ = [
    "TodoMCPServer",
    "add_task_tool", "ADD_TASK_DEF",
    "list_tasks_tool", "LIST_TASKS_DEF",
    "complete_task_tool", "COMPLETE_TASK_DEF",
    "update_task_tool", "UPDATE_TASK_DEF",
    "delete_task_tool", "DELETE_TASK_DEF"
]