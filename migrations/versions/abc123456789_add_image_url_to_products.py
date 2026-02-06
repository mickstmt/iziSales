"""Add image_url field to products table

Revision ID: abc123456789
Revises: e69fd5685da3
Create Date: 2026-02-06 11:13:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123456789'
down_revision = 'e69fd5685da3'
branch_labels = None
depends_on = None


def upgrade():
    # Add image_url column to products table
    op.add_column('products', sa.Column('image_url', sa.String(length=500), nullable=True))


def downgrade():
    # Remove image_url column from products table
    op.drop_column('products', 'image_url')
