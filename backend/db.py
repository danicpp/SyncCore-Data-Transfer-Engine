from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
import datetime
import os

# Fallback to SQLite if Postgres is unavailable or not requested
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./datasync.db")

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(String, primary_key=True) # UUID or manifest hash
    name = Column(String)
    total_size = Column(Integer)
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(String, ForeignKey("transfers.id"))
    chunk_index = Column(Integer)
    data = Column(LargeBinary)
    hash = Column(String)
    offset = Column(Integer)
    size = Column(Integer)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class DBHandler:
    @staticmethod
    async def save_chunk(transfer_id, chunk_index, data, chunk_hash, offset):
        async with AsyncSessionLocal() as session:
            chunk = Chunk(
                transfer_id=transfer_id,
                chunk_index=chunk_index,
                data=data,
                hash=chunk_hash,
                offset=offset,
                size=len(data)
            )
            session.add(chunk)
            await session.commit()
            return True
