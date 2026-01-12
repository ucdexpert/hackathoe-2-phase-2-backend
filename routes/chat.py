"""Chat endpoint for Phase III AI chatbot"""

import os
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from typing import Dict, Any, Optional
from auth import get_current_user_payload
from database import get_session
from models import Message, MessageCreate, ConversationRead, MessageRead
from agents.todo_agent import TodoAgent
from repositories.conversation_repository import get_conversation_by_id, create_conversation, get_conversations_by_user_id
from repositories.message_repository import create_message, get_messages_by_conversation_id
import asyncio

router = APIRouter()


@router.post("/{user_id}/chat")
async def chat(
    user_id: str,
    message_data: Dict[str, Any],
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """
    Process a user's message and return an AI-generated response with any side effects (task operations).
    
    Request body:
    {
        "conversation_id": 123,  // optional, creates new if not provided
        "message": "Add buy groceries to my list"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "conversation_id": 123,
            "response": "I've added 'Buy groceries' to your task list.",
            "tool_calls": [
                {
                    "tool": "add_task",
                    "parameters": {...},
                    "result": {...}
                }
            ]
        }
    }
    """
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Extract message and conversation_id from request
    user_message = message_data.get("message")
    conversation_id = message_data.get("conversation_id")
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # Validate message length
    if len(user_message) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message must be 1000 characters or less"
        )
    
    # Get or create conversation
    if conversation_id:
        # Verify conversation exists and belongs to user
        existing_conversation = get_conversation_by_id(session, conversation_id)
        if not existing_conversation or existing_conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to user"
            )
        conversation = existing_conversation
    else:
        # Create new conversation
        from models import ConversationCreate
        conversation_create = ConversationCreate(title=user_message[:50] + "..." if len(user_message) > 50 else user_message)
        conversation = create_conversation(session, conversation_create, user_id)
        conversation_id = conversation.id
    
    # Store the user's message
    message_create = MessageCreate(
        conversation_id=conversation.id,
        role="user",
        content=user_message
    )
    user_db_message = create_message(session, message_create, user_id)

    # Get conversation history for context
    conversation_history = get_messages_by_conversation_id(session, conversation.id)
    formatted_history = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in conversation_history
    ]

    # Initialize the TodoAgent
    try:
        agent = TodoAgent(gemini_api_key=os.getenv("GEMINI_API_KEY"))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent initialization error: {str(e)}"
        )

    # Process the message with the agent
    result = await agent.process_message(user_message, formatted_history, user_id)

    # Store the AI's response
    ai_message_create = MessageCreate(
        conversation_id=conversation.id,
        role="assistant",
        content=result.get("response", "")
    )
    ai_db_message = create_message(session, ai_message_create, user_id)

    # Return the response
    return {
        "success": True,
        "data": {
            "conversation_id": conversation.id,
            "user_message_id": user_db_message.id,
            "ai_message_id": ai_db_message.id,
            "response": result.get("response", ""),
            "tool_calls": result.get("tool_calls", []),
            "tool_results": result.get("tool_results", [])
        }
    }


@router.get("/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """
    Get all conversations for a user, ordered by most recent first.

    Response:
    [
        {
            "id": 50,
            "created_at": "2026-01-01T10:00:00",
            "title": "hi"
        }
    ]
    """
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these conversations"
        )

    conversations = get_conversations_by_user_id(session, user_id)

    # Convert to the required format
    result = []
    for conv in conversations:
        result.append({
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "title": conv.title
        })

    # Sort by created_at in descending order (most recent first)
    result.sort(key=lambda x: x["created_at"], reverse=True)

    return result


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session),
    token_data: dict = Depends(get_current_user_payload)
):
    """
    Get all messages for a specific conversation.

    Response:
    [
        {
            "id": 99,
            "role": "user",
            "content": "add buy milk",
            "created_at": "2026-01-01T10:00:00"
        },
        {
            "id": 100,
            "role": "assistant",
            "content": "I've added 'buy milk'!",
            "created_at": "2026-01-01T10:00:01"
        }
    ]
    """
    # Verify that user_id matches the token user_id
    if user_id != token_data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Verify conversation exists and belongs to user
    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to user"
        )

    messages = get_messages_by_conversation_id(session, conversation_id)

    # Convert to the required format
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        })

    # Sort by created_at in ascending order (chronological)
    result.sort(key=lambda x: x["created_at"])

    return result