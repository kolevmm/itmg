"""Added monthly maintenance price to AssetType

Revision ID: a9d2f1d6c8d8
Revises: 5d2a850fbc36
Create Date: 2024-11-10 15:04:48.699367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9d2f1d6c8d8'
down_revision = '5d2a850fbc36'
branch_labels = None
depends_on = None


def upgrade():
    # Добавяне на колоната monthly_maintenance_price в asset_type
    with op.batch_alter_table('asset_type', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monthly_maintenance_price', sa.Float(), nullable=False, server_default="0"))



def downgrade():
    # Премахване на колоната monthly_maintenance_price при downgrade
    with op.batch_alter_table('asset_type', schema=None) as batch_op:
        batch_op.drop_column('monthly_maintenance_price')
