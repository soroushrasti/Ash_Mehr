"""add BirthDate and UnderWhichAdmin to register

Revision ID: b6c7d8e9f0a1
Revises: a1b2c3d4e5f6
Create Date: 2025-09-16 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b6c7d8e9f0a1'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add BirthDate first in its own batch
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.add_column(sa.Column('BirthDate', sa.Date(), nullable=True))

    # Add UnderWhichAdmin and its FK in a separate batch
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.add_column(sa.Column('UnderWhichAdmin', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_register_underwhichadmin_admin',
            'admin',
            ['UnderWhichAdmin'],
            ['AdminID'],
        )


def downgrade() -> None:
    # Drop FK and UnderWhichAdmin first
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.drop_constraint('fk_register_underwhichadmin_admin', type_='foreignkey')
        batch_op.drop_column('UnderWhichAdmin')

    # Drop BirthDate
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.drop_column('BirthDate')
