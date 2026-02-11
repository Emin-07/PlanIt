from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

from .config import settings

# sync_engine = create_engine(url=settings.DATABASE_url_psycopg, echo=False)
async_engine = create_async_engine(url=settings.POSTGRES_url_asyncpg, echo=False)


# sync_session_factory = sessionmaker(
#     bind=sync_engine, autoflush=False, autocommit=False, expire_on_commit=False
# )
async_session_factory = async_sessionmaker(
    bind=async_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


class Base(DeclarativeBase):
    __abstract__ = True
    cols_amount: int = 100

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    def __repr__(self) -> str:
        table_column_names = self.__table__.columns.keys()
        res: List[str] = []
        for idx, col in enumerate(table_column_names):
            if idx < self.cols_amount:
                res.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__}: {', '.join(res)}>"
