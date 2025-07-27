"""
Database utilities for Nimbus Discord Bot.
"""
import aiosqlite
import asyncio
from typing import Any, Dict, List, Optional
from utils.config import config

class Database:
    """Async database manager."""
    
    def __init__(self):
        self.db_path = config.database_url.replace('sqlite:///', '')
        self._connection = None
    
    async def connect(self):
        """Initialize database connection and tables."""
        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
    
    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
    
    async def _create_tables(self):
        """Create necessary tables."""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id INTEGER PRIMARY KEY,
                config_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_data (
                user_id INTEGER,
                guild_id INTEGER,
                data_key TEXT,
                data_value TEXT,
                PRIMARY KEY (user_id, guild_id, data_key)
            );
            
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                event_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await self._connection.commit()
    
    async def get_server_config(self, guild_id: int) -> Dict[str, Any]:
        """Get server configuration."""
        cursor = await self._connection.execute(
            "SELECT config_data FROM server_config WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        if row:
            import json
            return json.loads(row[0])
        return {}
    
    async def save_server_config(self, guild_id: int, config_data: Dict[str, Any]):
        """Save server configuration."""
        import json
        await self._connection.execute(
            "INSERT OR REPLACE INTO server_config (guild_id, config_data) VALUES (?, ?)",
            (guild_id, json.dumps(config_data))
        )
        await self._connection.commit()

# Global database instance
db = Database()