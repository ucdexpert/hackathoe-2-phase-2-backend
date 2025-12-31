"""
Script to create Phase III tables (conversations and messages) directly using SQLModel
"""

from database import engine
from models import Conversation, Message
from sqlmodel import SQLModel

def create_phase3_tables():
    """Create Phase III tables for conversations and messages"""
    print("Creating Phase III tables...")
    
    # Create all tables defined in the SQLModel metadata
    # This includes Conversation and Message tables along with existing tables
    SQLModel.metadata.create_all(engine)
    
    print("Phase III tables created successfully!")
    print("- conversations table")
    print("- messages table")
    print("All required indexes and foreign key constraints have been created.")


if __name__ == "__main__":
    create_phase3_tables()