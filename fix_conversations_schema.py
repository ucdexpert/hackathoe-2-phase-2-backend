"""
Script to fix the conversations table schema issue
This script drops and recreates the conversations and messages tables with proper auto-incrementing IDs
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set.")
    sys.exit(1)

def fix_database_schema():
    """Fix the conversations table schema to have auto-incrementing IDs"""
    print("Connecting to database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    try:
        # Connect to the database
        with engine.connect() as conn:
            # Begin transaction
            with conn.begin():
                print("Dropping existing tables...")
                
                # Drop messages table first (due to foreign key constraint)
                drop_messages_sql = "DROP TABLE IF EXISTS messages CASCADE;"
                conn.execute(text(drop_messages_sql))
                print("Dropped messages table")
                
                # Drop conversations table
                drop_conversations_sql = "DROP TABLE IF EXISTS conversations CASCADE;"
                conn.execute(text(drop_conversations_sql))
                print("Dropped conversations table")
                
                print("Creating conversations table with proper schema...")

                # Check if users table exists before creating conversations table
                check_users_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('user', 'users')
                );
                """
                result = conn.execute(text(check_users_sql))
                users_table_exists = result.scalar()

                if not users_table_exists:
                    print("ERROR: users table does not exist. Please ensure the base schema is created first.")
                    sys.exit(1)

                # Create conversations table with SERIAL PRIMARY KEY
                create_conversations_sql = """
                CREATE TABLE conversations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    title VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                conn.execute(text(create_conversations_sql))
                print("Created conversations table with auto-incrementing ID")

                print("Creating messages table with proper schema...")

                # Create messages table with proper foreign keys
                create_messages_sql = """
                CREATE TABLE messages (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                conn.execute(text(create_messages_sql))
                print("Created messages table with proper foreign keys")
                
                # Create indexes for performance
                create_indexes_sql = """
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id_created_at ON messages(conversation_id, created_at);
                """
                conn.execute(text(create_indexes_sql))
                print("Created indexes for performance")
                
        print("\nDatabase schema fixed successfully!")
        print("- conversations table now has auto-incrementing SERIAL PRIMARY KEY")
        print("- messages table has proper foreign key constraints")
        print("- indexes created for performance")
        
    except Exception as e:
        print(f"ERROR: Failed to fix database schema: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fix_database_schema()