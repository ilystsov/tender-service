"""Initial migration

Revision ID: 18a0130a1676
Revises: 
Create Date: 2024-09-13 22:41:44.510127

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '18a0130a1676'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tender',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('service_type', sa.Enum('CONSTRUCTION', 'DELIVERY', 'MANUFACTURE', name='tenderservicetype'), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PUBLISHED', 'CLOSED', name='tenderstatus'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PUBLISHED', 'CANCELED', name='bidstatus'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('tender_id', sa.UUID(), nullable=False),
    sa.Column('author_type', sa.Enum('USER', 'ORGANIZATION', name='authortype'), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['tender_id'], ['tender.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tender_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tender_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('service_type', sa.Enum('CONSTRUCTION', 'DELIVERY', 'MANUFACTURE', name='tenderservicetype'), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PUBLISHED', 'CLOSED', name='tenderstatus'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tender_id'], ['tender.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid_decision',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bid_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('decision', sa.Enum('APPROVED', 'REJECTED', name='biddecisionstatus'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['employee.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid_feedback',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bid_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('feedback', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['employee.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bid_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PUBLISHED', 'CANCELED', name='bidstatus'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('organization_responsible', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('organization_responsible', 'organization_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('organization', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('organization', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('organization', 'type',
               existing_type=sa.Enum('IE', 'LLC', 'JSC', name='organizationtype'),
               type_=postgresql.ENUM('IE', 'LLC', 'JSC', name='organization_type'),
               existing_nullable=True)
    op.alter_column('organization', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('employee', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('employee', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('employee', 'last_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('employee', 'first_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.drop_table('bid_history')
    op.drop_table('bid_feedback')
    op.drop_table('bid_decision')
    op.drop_table('tender_history')
    op.drop_table('bid')
    op.drop_table('tender')
    # ### end Alembic commands ###
