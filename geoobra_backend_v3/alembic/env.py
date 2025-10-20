from logging.config import fileConfig
from alembic import context
import os, sys

# adicionar o path do backend para import "app"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# importar o engine e o metadata do projeto
from app.db import engine
from app.models import Base

# config padrão do alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
