import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv


load_dotenv()


def _build_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./team_task_manager.db").strip()

    # Some platforms expose postgres:// which SQLAlchemy does not accept.
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)

    # Railway deployments often require SSL for external Postgres connections.
    if raw_url.startswith("postgresql://"):
        ssl_mode = os.getenv("DATABASE_SSLMODE")
        if not ssl_mode and os.getenv("RAILWAY_ENVIRONMENT"):
            ssl_mode = "require"
        if ssl_mode and "sslmode=" not in raw_url:
            separator = "&" if "?" in raw_url else "?"
            raw_url = f"{raw_url}{separator}sslmode={ssl_mode}"

    return raw_url


DATABASE_URL = _build_database_url()

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

