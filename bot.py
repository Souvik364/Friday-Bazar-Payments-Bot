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

# -------------------- Logging --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------- Bot Setup --------------------

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# -------------------- Error Handler --------------------

@dp.error()
async def error_handler(event: ErrorEvent):
    logger.error("Unhandled error", exc_info=event.exception)
    try:
        if event.update.message:
            await event.update.message.answer(
                "⚠️ An error occurred. Please try again later."
            )
        elif event.update.callback_query:
            await event.update.callback_query.answer(
                "⚠️ An error occurred.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Error while sending error message: {e}")

# =====================================================
# Render Web Service – Health Check Server
# =====================================================

async def health_check(request):
    """Health check endpoint for Render."""
    return web.Response(text="Bot is running!")

async def start_web_server():
    """Start a simple web server for Render's health checks."""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Web server started on port {port}")

# -------------------- Main --------------------

async def main():
    dp.include_router(start_router)
    dp.include_router(premium_router)
    dp.include_router(admin_router)

    logger.info("Bot started")

    # Start web server for Render (IMPORTANT)
    await start_web_server()

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

# -------------------- Entry Point --------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
