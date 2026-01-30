import asyncio
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import async_engine
from src.db.models import User, Note, Category
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def clear_database():
    print("⚠️  Warning: This will delete ALL users and ALL notes from the database.")
    print("Connecting to database...")

    async with AsyncSession(async_engine) as session:
        try:
            # Delete notes first to avoid foreign key violations
            print("Deleting all notes...")
            await session.execute(delete(Note))

            print("Deleting all categories...")
            await session.execute(delete(Category))

            print("Deleting all users...")
            await session.execute(delete(User))

            await session.commit()
            print("✅ Database cleared successfully!")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error clearing database: {e}")
            logger.error(f"Failed to clear database: {e}")


if __name__ == "__main__":
    asyncio.run(clear_database())
