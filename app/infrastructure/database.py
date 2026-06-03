from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.config import Settings

settings = Settings()

engine = None
SessionLocal = None
if settings.db_enabled:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    if not settings.db_enabled or engine is None:
        return
    from app.adapters.db import models as _models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session():
    if not settings.db_enabled or SessionLocal is None:
        yield None
        return
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
