import asyncio
from sqlmodel import SQLModel
from src.db.database import async_engine, create_db_and_tables
from src.db.models import User, Note, Category  # noqa: F401
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def reset_database():
    print("⚠️  Warning: This will DROP and RECREATE all tables.")
    print("This is necessary to sync the schema changes (age, gender, category).")

    async with async_engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(SQLModel.metadata.drop_all)

    print("Recreating all tables...")
    await create_db_and_tables()

    print("✅ Database reset successfully with new schema!")


if __name__ == "__main__":
    asyncio.run(reset_database())
