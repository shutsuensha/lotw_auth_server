from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.POSTGRES_URL_ASYNC)

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
