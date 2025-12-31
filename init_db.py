#!/usr/bin/env python3
"""
Database initialization script for Neon PostgreSQL
This script creates all required tables in the Neon database.
"""

from sqlmodel import SQLModel
from database import engine, create_db_and_tables
from dotenv import load_dotenv
import os
import sys


def main():
    """Initialize the database by creating all required tables."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set.")
        print("Please configure your .env file with the Neon database URL.")
        sys.exit(1)
    
    print("Connecting to Neon PostgreSQL database...")
    print(f"Database URL: {database_url}")
    
    try:
        # Create all tables defined in the models
        create_db_and_tables()
        print("Database tables created successfully!")
        print("Neon PostgreSQL database initialized successfully.")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()