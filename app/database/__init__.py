import asyncpg
from app.config import get_settings
from .base import Base, engine, get_db

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Connect to Aiven PostgreSQL"""
        settings = get_settings()
        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=10
            )
            print("✅ Database connected!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    async def close(self):
        if self.pool:
            await self.pool.close()

# Global instance
db = Database()