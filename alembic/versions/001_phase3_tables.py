"""Add conversations and messages tables for Phase III AI chatbot

Revision ID: 001_phase3_tables
Revises: None
Create Date: 2025-12-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers
revision = '001_phase3_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', sa.Integer, sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create indexes for performance
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'])
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_id_created_at', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_messages_conversation_id_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    
    # Drop tables
    op.drop_table('messages')
    op.drop_table('conversations')