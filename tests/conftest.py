import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.data.seed_recipes import seed_recipes_if_empty
from app.database.models import Base, User


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed_recipes_if_empty(session)
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    new_user = User(telegram_id=1, username="tester", full_name="Test User")
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user
