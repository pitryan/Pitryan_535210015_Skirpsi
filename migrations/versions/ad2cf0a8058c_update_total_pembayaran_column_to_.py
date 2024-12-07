"""Update total_pembayaran column to Numeric

Revision ID: ad2cf0a8058c
Revises: 4de1eb8f0443
Create Date: 2024-11-05 20:25:55.366058

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ad2cf0a8058c'
down_revision = '4de1eb8f0443'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('penjualan_batik', schema=None) as batch_op:
        batch_op.alter_column('total_pembayaran',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('penjualan_batik', schema=None) as batch_op:
        batch_op.alter_column('total_pembayaran',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               existing_nullable=True)

    # ### end Alembic commands ###
