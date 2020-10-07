"""empty message

Revision ID: 615ded5c95c6
Revises: 6b4506ce1c4c
Create Date: 2020-10-04 22:26:09.552037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '615ded5c95c6'
down_revision = '6b4506ce1c4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###