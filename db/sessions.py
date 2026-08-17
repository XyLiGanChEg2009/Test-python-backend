from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionsLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)