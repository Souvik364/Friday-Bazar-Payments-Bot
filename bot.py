import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN
from handlers.start import start_router
from handlers.premium import premium_router
from handlers.admin import admin_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Unhandled error: {event.exception}", exc_info=True)
    try:
        if event.update.message:
            await event.update.message.answer(
                "⚠️ An error occurred. Please try again or contact support."
            )
        elif event.update.callback_query:
            await event.update.callback_query.answer(
                "⚠️ An error occurred. Please try again.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


async def health_check(request):
    """Health check endpoint for Render and monitoring services."""
    return web.Response(text="Bot is running! ✅")


async def start_web_server():
    """Start a simple web server for Render's health checks."""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port} for health checks")


async def main():
    dp.include_router(start_router)
    dp.include_router(premium_router)
    dp.include_router(admin_router)
    
    logger.info("Bot started successfully! 🚀")
    
    await start_web_server()
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
