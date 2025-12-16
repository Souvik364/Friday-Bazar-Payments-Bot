import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN

# IMPORT ROUTERS - ORDER MATTERS
# Ensure these files exist in your directory structure
from handlers.language import language_router 
from handlers.start import start_router
from handlers.premium import premium_router
from handlers.admin import admin_router

# 1. Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. Bot Setup with Global HTML Parse Mode
# This saves you from typing parse_mode="HTML" in every message
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Warning: MemoryStorage wipes data on restart. 
# For production (Render/Heroku), consider using RedisStorage.
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# 3. Error Handler
@dp.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Unhandled error: {event.exception}", exc_info=True)

# 4. Web Server Logic (For Render Health Checks)
async def health_check(request):
    """Health check endpoint for Render."""
    return web.Response(text="Bot is running! ✅")

async def start_web_server():
    """Start web server for Render health checks."""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    await site.start()
    logger.info(f"Web server started on port {port}")
    return runner # Return runner to close it later

async def main():
    # REGISTER ROUTERS - Language must be first to catch new users!
    dp.include_router(language_router) 
    dp.include_router(start_router)
    dp.include_router(premium_router)
    dp.include_router(admin_router)
    
    logger.info("Bot started successfully! 🚀")
    
    # Start Render Web Server
    runner = await start_web_server()
    
    try:
        # DROP PENDING UPDATES (Fix for skip_updates=True)
        # This prevents the bot from spamming old messages on restart
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start Polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    finally:
        # Cleanup
        await bot.session.close()
        await runner.cleanup() # Close web server gracefully
        logger.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        
