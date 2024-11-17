"""Addes Services Category 3

Revision ID: 975c9513042a
Revises: 
Create Date: 2024-11-17 10:21:59.539424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '975c9513042a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_service')
    with op.batch_alter_table('service', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_service_category', 'service_categories', ['category_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service', schema=None) as batch_op:
        batch_op.drop_constraint('fk_service_category', type_='foreignkey')
        batch_op.drop_column('category_id')

    op.create_table('_alembic_tmp_service',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=True),
    sa.Column('price', sa.FLOAT(), nullable=False),
    sa.Column('category_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['service_categories.id'], name='fk_service_category'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
