import aiosqlite
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise ValueError("DB_PATH is missing from environment variables")


async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS totp_secrets "
                "(username TEXT PRIMARY KEY, secret TEXT NOT NULL)"
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


async def store_totp_secret(username: str, secret: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO totp_secrets (username, secret) VALUES (?, ?)",
            (username, secret),
        )
        await db.commit()


async def get_totp_secret(username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT secret FROM totp_secrets WHERE username=?", (username,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None
