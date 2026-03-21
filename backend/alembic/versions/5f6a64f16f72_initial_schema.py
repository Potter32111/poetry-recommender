"""Initial schema

Revision ID: 5f6a64f16f72
Revises: 
Create Date: 2026-03-21

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5f6a64f16f72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure pgvector extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('language_pref', sa.String(length=10), server_default='both', nullable=False),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('last_mood', sa.String(length=255), nullable=True),
        sa.Column('xp', sa.Integer(), server_default='0', nullable=False),
        sa.Column('level', sa.Integer(), server_default='1', nullable=False),
        sa.Column('streak', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('ui_language', sa.String(length=10), server_default='ru', nullable=False),
        sa.Column('notification_time', sa.String(length=5), server_default='10:00', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    # Create poems table
    op.create_table(
        'poems',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('difficulty', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('lines_count', sa.Integer(), nullable=False),
        sa.Column('themes', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('era', sa.String(length=50), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True), # Will fix with raw SQL below for pgvector
        sa.PrimaryKeyConstraint('id')
    )
    # Add vector column using raw SQL to avoid import issues in migration environment if pgvector is missing
    op.execute('ALTER TABLE poems ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)')

    # Create memorizations table
    op.create_table(
        'memorizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('poem_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='new', nullable=False),
        sa.Column('ease_factor', sa.Float(), server_default='2.5', nullable=False),
        sa.Column('interval_days', sa.Integer(), server_default='0', nullable=False),
        sa.Column('repetitions', sa.Integer(), server_default='0', nullable=False),
        sa.Column('next_review_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score_history', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('recommended_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['poem_id'], ['poems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('memorizations')
    op.drop_table('poems')
    op.drop_table('users')
