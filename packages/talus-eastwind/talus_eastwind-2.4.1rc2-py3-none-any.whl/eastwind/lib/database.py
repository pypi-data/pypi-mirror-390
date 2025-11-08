# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError
from eastwind.lib.model import Base
from eastwind.lib.exception import EastwindCriticalError


class Database:
    def __init__(self, db_type: str, db_url: str, **kwargs):
        # Build the database URL based on database type.
        if db_type == "sqlite":
            self.__db_url = f"sqlite+aiosqlite://{db_url}"
        elif db_type == "postgresql":
            self.__db_url = f"postgresql+asyncpg://{db_url}"
        elif db_type == "mysql" or db_type == "oceanbase":
            # OceanBase database provides Oracle/MySQL mode, so we are using MySQL mode.
            self.__db_url = f"mysql+aiomysql://{db_url}"
        else:
            if len(db_type) == 0:
                raise ValueError("Database type not provided")
            raise NotImplementedError(f"Unknown database type: {db_type}")
        # Based on the URL create the async engine.
        self.engine: AsyncEngine = create_async_engine(self.__db_url, echo=False, **kwargs)
        # Create the async database session class.
        self.Session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_all_tables(self) -> None:
        # Initial the database and create all the table currently loaded.
        # Remember use begin() here, it will automatically commit the changes.
        # Using connect() will work in SQLite3, but not work in PostgreSQL.
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all_tables(self) -> None:
        # Drop all the tables of the database.
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        # Close the main DB connection.
        await self.engine.dispose()


async def commit(db: AsyncSession) -> None:
    try:
        await db.commit()
    except IntegrityError as e:
        raise EastwindCriticalError(400, f"user data integrity error occurs: {e}")
    except DBAPIError as e:
        raise EastwindCriticalError(500, f"database API error occurs: {e}")
    except SQLAlchemyError:
        raise EastwindCriticalError(500, "server database error occurs, please retry later.")
