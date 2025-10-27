"""is_disconnected

Revision ID: f935940be757
Revises: add4a084b4a0
Create Date: 2025-10-04 21:30:39.911479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d27b555f1bb'
down_revision = 'e73f2e0bb072'
branch_labels = None
depends_on = None


def upgrade():
    # اضافه کردن ستون is_disconnected به جدول register
    with op.batch_alter_table('register') as batch_op:
        batch_op.add_column(sa.Column('is_disconnected', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # حذف ستون is_disconnected از جدول register
    with op.batch_alter_table('register') as batch_op:
        batch_op.drop_column('is_disconnected')
