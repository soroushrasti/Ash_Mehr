

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e73f2e0bb072'
down_revision = 'b6c7d8e9f0a1'
branch_labels = None
depends_on = None


def upgrade() -> None:


    with op.batch_alter_table('register') as batch_op:
        batch_op.add_column(sa.Column('UnderSecondAdminID', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_register_under_second_admin',
            'admin',
            ['UnderSecondAdminID'],
            ['AdminID']
        )
        batch_op.drop_column('Age')


def downgrade() -> None:
    with op.batch_alter_table('register') as batch_op:
        batch_op.add_column(sa.Column('Age', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_register_under_second_admin', type_='foreignkey')
        batch_op.drop_column('UnderSecondAdminID')

    with op.batch_alter_table('admin') as batch_op:
        batch_op.add_column(sa.Column('BirthDate', sa.DateTime(), nullable=True))
        batch_op.drop_constraint('fk_admin_created_by', type_='foreignkey')
        batch_op.drop_column('CreatedBy')
