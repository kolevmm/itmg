"""Added OfferAsset model for manually entered assets in offers

Revision ID: 3cb641dada62
Revises: a9d2f1d6c8d8
Create Date: 2024-11-10 15:39:38.718731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cb641dada62'
down_revision = 'a9d2f1d6c8d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('offer_assets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('offer_id', sa.Integer(), nullable=False),
    sa.Column('asset_type_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['asset_type_id'], ['asset_type.id'], ),
    sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
   


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    op.drop_table('offer_assets')
    # ### end Alembic commands ###
