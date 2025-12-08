"""rename

Revision ID: 3f89e62aa116
Revises: 1d27b555f1bb
Create Date: 2025-11-04 08:55:39.255268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f89e62aa116'
down_revision = '1d27b555f1bb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('good') as batch_op:
        batch_op.add_column(sa.Column('SmsCode', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('Verified', sa.Boolean(), nullable=True))
        batch_op.alter_column('NumberGood', nullable=True)
        batch_op.alter_column('CreatedDate', nullable=False)

    # ایجاد ایندکس‌ها خارج از batch_alter_table
    op.create_index(op.f('ix_good_SmsCode'), 'good', ['SmsCode'], unique=False)
    op.create_index(op.f('ix_good_Verified'), 'good', ['Verified'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_good_Verified'), table_name='good')
    op.drop_index(op.f('ix_good_SmsCode'), table_name='good')

    with op.batch_alter_table('good') as batch_op:
        batch_op.alter_column('CreatedDate', nullable=True)
        batch_op.alter_column('NumberGood', nullable=False)
        batch_op.drop_column('Verified')
        batch_op.drop_column('SmsCode')