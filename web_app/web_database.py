import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL_WEB = os.getenv("DATABASE_URL_WEB")

engine = create_async_engine(
    DATABASE_URL_WEB,
    echo=False,
    pool_size=20,
    max_overflow=50
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
