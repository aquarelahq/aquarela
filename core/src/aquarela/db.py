import os
from pathlib import Path

from alembic import command
from alembic.config import Config

MIGRATIONS = Path(__file__).parent / "migrations"


def database_url() -> str:
    return os.environ.get("AQUARELA_DATABASE_URL", "sqlite:///aquarela.db")


def migrate(url: str | None = None) -> None:
    """Bring the database up to the latest schema."""
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    config.set_main_option("sqlalchemy.url", (url or database_url()).replace("%", "%%"))
    command.upgrade(config, "head")
