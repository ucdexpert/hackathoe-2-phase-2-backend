"""Repository functions for Message entity"""

from sqlmodel import Session, select
from typing import List, Optional
from models import Message, MessageCreate, MessageRead


def create_message(session: Session, message: MessageCreate, user_id: str) -> Message:
    """Create a new message"""
    db_message = Message(
        user_id=user_id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content
    )
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message


def get_message_by_id(session: Session, message_id: int) -> Optional[Message]:
    """Get a message by its ID"""
    return session.get(Message, message_id)


def get_messages_by_conversation_id(session: Session, conversation_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
    """Get all messages for a specific conversation"""
    statement = select(Message).where(Message.conversation_id == conversation_id).offset(offset).limit(limit)
    results = session.exec(statement)
    return results.all()


def get_messages_by_user_id(session: Session, user_id: str, limit: int = 100, offset: int = 0) -> List[Message]:
    """Get all messages for a specific user"""
    statement = select(Message).where(Message.user_id == user_id).offset(offset).limit(limit)
    results = session.exec(statement)
    return results.all()


def delete_message(session: Session, message_id: int) -> bool:
    """Delete a message"""
    db_message = session.get(Message, message_id)
    if db_message:
        session.delete(db_message)
        session.commit()
        return True
    return False


def delete_messages_by_conversation_id(session: Session, conversation_id: int) -> int:
    """Delete all messages for a specific conversation"""
    statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(statement).all()
    count = 0
    for message in messages:
        session.delete(message)
        count += 1
    session.commit()
    return count