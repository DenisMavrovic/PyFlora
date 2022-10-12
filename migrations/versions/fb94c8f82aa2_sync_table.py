"""Sync Table

Revision ID: fb94c8f82aa2
Revises: 45de9e3094c5
Create Date: 2022-06-05 14:27:29.381425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb94c8f82aa2'
down_revision = '45de9e3094c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sync',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('humidity', sa.Integer(), nullable=True),
    sa.Column('pH', sa.Float(), nullable=True),
    sa.Column('salinity', sa.Float(), nullable=True),
    sa.Column('temp', sa.Float(), nullable=True),
    sa.Column('light_intensity', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sync')
    # ### end Alembic commands ###
