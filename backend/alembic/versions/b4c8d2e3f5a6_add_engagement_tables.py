"""Add engagement tables: user_achievements, daily_challenges, streak_freezes

Revision ID: b4c8d2e3f5a6
Revises: a3b7c9d1e2f4
Create Date: 2026-04-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b4c8d2e3f5a6'
down_revision: Union[str, None] = 'a3b7c9d1e2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('badge_slug', sa.String(length=50), nullable=False),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'badge_slug', name='uq_user_achievements_user_badge'),
    )
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])

    # Create daily_challenges table
    op.create_table(
        'daily_challenges',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('goal_type', sa.String(length=50), nullable=False),
        sa.Column('goal_target', sa.Integer(), nullable=False),
        sa.Column('current_progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_daily_challenges_user_date'),
    )
    op.create_index('ix_daily_challenges_user_id', 'daily_challenges', ['user_id'])

    # Add streak freeze columns to users
    op.add_column('users', sa.Column('streak_freezes_available', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('last_freeze_regen', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_freeze_regen')
    op.drop_column('users', 'streak_freezes_available')
    op.drop_table('daily_challenges')
    op.drop_table('user_achievements')
