"""add CreatedBy to admin table

Revision ID: a1b2c3d4e5f6
Revises: 973a8986aa0a
Create Date: 2025-09-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '973a8986aa0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add CreatedBy column (self-referential FK to admin.AdminID)
    op.add_column('admin', sa.Column('CreatedBy', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_admin_createdby_admin',
        source_table='admin',
        referent_table='admin',
        local_cols=['CreatedBy'],
        remote_cols=['AdminID'],
        ondelete=None
    )


def downgrade() -> None:
    op.drop_constraint('fk_admin_createdby_admin', 'admin', type_='foreignkey')
    op.drop_column('admin', 'CreatedBy')

