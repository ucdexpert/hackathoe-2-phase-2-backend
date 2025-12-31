"""Repository functions for Conversation entity"""

from sqlmodel import Session, select
from typing import List, Optional
from models import Conversation, ConversationCreate, ConversationRead


def create_conversation(session: Session, conversation: ConversationCreate, user_id: str) -> Conversation:
    """Create a new conversation"""
    db_conversation = Conversation(
        title=conversation.title,
        user_id=user_id
    )
    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)
    return db_conversation


def get_conversation_by_id(session: Session, conversation_id: int) -> Optional[Conversation]:
    """Get a conversation by its ID"""
    return session.get(Conversation, conversation_id)


def get_conversations_by_user_id(session: Session, user_id: str, limit: int = 20, offset: int = 0) -> List[Conversation]:
    """Get all conversations for a specific user"""
    statement = select(Conversation).where(Conversation.user_id == user_id).offset(offset).limit(limit)
    results = session.exec(statement)
    return results.all()


def update_conversation(session: Session, conversation_id: int, conversation_data: ConversationCreate) -> Optional[Conversation]:
    """Update a conversation"""
    db_conversation = session.get(Conversation, conversation_id)
    if db_conversation:
        conversation_data_dict = conversation_data.dict(exclude_unset=True)
        for key, value in conversation_data_dict.items():
            setattr(db_conversation, key, value)
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)
        return db_conversation
    return None


def delete_conversation(session: Session, conversation_id: int) -> bool:
    """Delete a conversation"""
    db_conversation = session.get(Conversation, conversation_id)
    if db_conversation:
        session.delete(db_conversation)
        session.commit()
        return True
    return False