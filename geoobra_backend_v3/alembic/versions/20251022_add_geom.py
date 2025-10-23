"""Add geom columns and spatial indexes for jobs & users."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "3fddd82365de"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS geom geometry(Point,4326);")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS geom geometry(Point,4326);")
    op.execute("UPDATE jobs SET geom = ST_SetSRID(ST_MakePoint(lng,lat),4326) WHERE geom IS NULL AND lat IS NOT NULL AND lng IS NOT NULL;")
    op.execute("UPDATE users SET geom = ST_SetSRID(ST_MakePoint(lng,lat),4326) WHERE geom IS NULL AND lat IS NOT NULL AND lng IS NOT NULL;")
    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_geom ON jobs USING GIST (geom);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_geom ON users USING GIST (geom);")

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_users_geom;")
    op.execute("DROP INDEX IF EXISTS idx_jobs_geom;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS geom;")
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS geom;")
