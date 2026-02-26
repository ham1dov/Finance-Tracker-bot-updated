from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import DATABASE_URL_WEB

# Ensure the URL is using the asyncpg driver
if DATABASE_URL_WEB and DATABASE_URL_WEB.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL_WEB.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL_WEB

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
