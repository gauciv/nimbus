"""
Error recovery and fallback mechanisms.
"""
import asyncio
from typing import Optional

class ErrorRecovery:
    @staticmethod
    async def retry_with_backoff(func, max_retries=3, base_delay=1):
        """Retry function with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(base_delay * (2 ** attempt))
        return None
    
    @staticmethod
    def safe_execute(func, default_return=None):
        """Execute function safely with fallback."""
        try:
            return func()
        except:
            return default_return