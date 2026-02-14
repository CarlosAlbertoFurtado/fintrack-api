"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'USER', name='user_role'), default='USER', nullable=False),
        sa.Column('google_id', sa.String(100), unique=True, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.Enum('INCOME', 'EXPENSE', name='category_type'), nullable=False),
        sa.Column('icon', sa.String(10), nullable=True),
        sa.Column('color', sa.String(7), default='#6366F1', nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_categories_user_type', 'categories', ['user_id', 'type'])

    op.create_table(
        'transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('type', sa.Enum('INCOME', 'EXPENSE', name='transaction_type'), nullable=False),
        sa.Column('date', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), default=False, nullable=False),
        sa.Column('recurring_day', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_transactions_user_date', 'transactions', ['user_id', 'date'])
    op.create_index('ix_transactions_user_type', 'transactions', ['user_id', 'type'])
    op.create_index('ix_transactions_user_category', 'transactions', ['user_id', 'category_id'])

    op.create_table(
        'budgets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('spent', sa.Float(), default=0.0, nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('alert_threshold', sa.Float(), default=0.8, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_budgets_user_month', 'budgets', ['user_id', 'month', 'year'])


def downgrade() -> None:
    op.drop_table('budgets')
    op.drop_table('transactions')
    op.drop_table('categories')
    op.drop_table('users')
