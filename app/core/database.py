from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 1. SQLite multithreading support configuration.
# PostgreSQL or other database engines do not require 'check_same_thread'.
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

# 2. Configure the Async Engine.
# Future database migrations (e.g. to PostgreSQL) only require changing the
# DATABASE_URL in .env to use the correct async driver (e.g. postgresql+asyncpg).
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True for query debugging in development environment
    future=True
)

# 3. Create the Async Sessionmaker factory.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents lazy loading issues when reading attributes after commit
    autocommit=False,
    autoflush=False
)

# 4. Declarative Base class for all model models definitions.
# This serves as the schema metadata registry for migrations (e.g. Alembic).
class Base(DeclarativeBase):
    pass

# 5. Dependency Injector providing database session access.
# Uses async generators to handle clean transaction commits, rollbacks, and session closing.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
