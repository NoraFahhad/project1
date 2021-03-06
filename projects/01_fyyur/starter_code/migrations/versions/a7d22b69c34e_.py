"""empty message

Revision ID: a7d22b69c34e
Revises: 1b0993819791
Create Date: 2020-10-07 04:27:52.979708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7d22b69c34e'
down_revision = '1b0993819791'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Show_venue_id_fkey', 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('Show_venue_id_fkey', 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###
