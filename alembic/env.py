from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
import uav_assistant.infra.db.models as models
from uav_assistant.infra.db.url_builder import build
from dotenv import load_dotenv
import os

env_file = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_file)

url = build(
    "PGSYNCDRIVER",
    "PGROLE",
    "PGPASSWORD",
    "PGHOST",
    "PGPORT",
    "PGDATABASE",
)

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = models.Base.metadata

def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(url, poolclass=pool.NullPool, future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
