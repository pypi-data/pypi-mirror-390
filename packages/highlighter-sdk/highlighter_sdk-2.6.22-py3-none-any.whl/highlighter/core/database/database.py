from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from highlighter.core.config import HighlighterRuntimeConfig

__all__ = [
    "Database",
]


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Configure SQLite connection for better concurrent access.

    This function is called automatically on each new database connection.
    """
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster with WAL mode
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
    finally:
        cursor.close()


class Database:
    def __init__(self):
        hl_cfg = HighlighterRuntimeConfig.load()
        self.highlighter_path_to_database_file = str(hl_cfg.agent.db_file())
        self._engine = create_engine(
            f"sqlite:///{self.highlighter_path_to_database_file}",
            connect_args={
                "check_same_thread": False,
                "timeout": 30,  # 30-second busy timeout
            },
        )

        # Configure SQLite for better concurrent access
        event.listens_for(self._engine, "connect")(_set_sqlite_pragma)

        SQLModel.metadata.create_all(self._engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    def get_session(self):
        return Session(self.engine)

    def close(self):
        self._engine.dispose()  # Call this when shutting down your app
