from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import Optional
from auth import get_current_user_payload
from models import Task, TaskCreate, TaskRead, User
from database import get_session
from datetime import datetime

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=list[TaskRead])
def get_tasks(
    user_id: str,
    status_param: Optional[str] = None,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Get all tasks for a specific user with optional status filtering"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter if provided
    if status_param:
        if status_param == "completed":
            query = query.where(Task.completed == True)
        elif status_param == "pending":
            query = query.where(Task.completed == False)
        elif status_param != "all":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'all', 'pending', or 'completed'"
            )

    tasks = session.exec(query).all()
    return tasks


@router.post("/{user_id}/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Create a new task for a user"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    # Validate title length
    if not task_create.title or len(task_create.title) < 1 or len(task_create.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 200 characters"
        )

    # Create task
    task = Task(
        user_id=user_id,
        title=task_create.title,
        description=task_create.description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Get a specific task by ID"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskCreate,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Update a specific task"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Validate title length
    if task_update.title and (len(task_update.title) < 1 or len(task_update.title) > 200):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 200 characters"
        )

    # Update task
    if task_update.title:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Delete a specific task"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    session.delete(task)
    session.commit()

    return task


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
def toggle_complete(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """Toggle the completion status of a task"""
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task