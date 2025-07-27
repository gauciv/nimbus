"""
Health check endpoint for monitoring bot status.
"""
import asyncio
from aiohttp import web
from utils.logging_config import get_logger

logger = get_logger(__name__)

class HealthCheck:
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/status', self.status_handler)
        
    async def health_handler(self, request):
        """Basic health check endpoint."""
        if self.bot.is_ready():
            return web.json_response({
                'status': 'healthy',
                'bot_ready': True,
                'guild_count': len(self.bot.guilds)
            })
        else:
            return web.json_response({
                'status': 'unhealthy',
                'bot_ready': False
            }, status=503)
    
    async def status_handler(self, request):
        """Detailed status endpoint."""
        return web.json_response({
            'bot_name': str(self.bot.user) if self.bot.user else 'Not connected',
            'guild_count': len(self.bot.guilds),
            'latency': round(self.bot.latency * 1000, 2),
            'ready': self.bot.is_ready()
        })
    
    async def start_server(self, port=8001):
        """Start the health check server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"Health check server started on port {port}")
        return runner