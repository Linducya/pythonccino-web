import aiosqlite
import logging

# Create a logger
logger = logging.getLogger(__name__)

DB_PATH = "totp_secrets.db"

async def init_db():
    try:
      async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS totp_secrets (username TEXT PRIMARY KEY, secret TEXT NOT NULL)"
            )
        await db.commit()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

async def store_totp_secret(username: str, secret: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO totp_secrets (username, secret) VALUES (?, ?)", (username, secret))
        await db.commit()

async def get_totp_secret(username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT secret FROM totp_secrets WHERE username=?", (username,))
        row = await cursor.fetchone()
        logger.info(f"Retrieving TOTP secret for username: {username}")
        if not row:
            logger.warning(f"No TOTP secret found for username: {username}")
        else:
            logger.info(f"Retrieved TOTP secret for username: {username}: {row[0]}")
        return row[0] if row else None