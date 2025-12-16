render_ready_main.py

Single-file, Render-friendly entrypoint for your Aiogram bot

Merged routers: start, premium, admin, language

Includes aiohttp health server for Render Web Service

import os import asyncio import logging from datetime import datetime

from aiohttp import web from aiogram import Bot, Dispatcher from aiogram.enums import ParseMode from aiogram.fsm.storage.memory import MemoryStorage

====== ENV ======

BOT_TOKEN = os.getenv("BOT_TOKEN") ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN or ADMIN_ID == 0: raise SystemExit("Set BOT_TOKEN and ADMIN_ID env vars")

====== LOGGING ======

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

====== IMPORT ROUTERS ======

These are your existing modules; keep files as-is

from handlers.start import start_router from handlers.premium import premium_router from handlers.admin import admin_router from handlers.language import language_router

====== HEALTH SERVER (Render requirement) ======

async def health_check(request): return web.Response(text="Bot is running")

async def start_web_server(): app = web.Application() app.router.add_get("/", health_check) app.router.add_get("/health", health_check)

runner = web.AppRunner(app)
await runner.setup()
site = web.TCPSite(runner, "0.0.0.0", PORT)
await site.start()

logger.info(f"Health server started on port {PORT}")

====== MAIN ======

async def main(): bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher(storage=MemoryStorage())

# Register routers
dp.include_router(start_router)
dp.include_router(premium_router)
dp.include_router(language_router)
dp.include_router(admin_router)

await start_web_server()

logger.info("Bot started successfully")
try:
    await dp.start_polling(bot, skip_updates=True)
finally:
    await bot.session.close()

if name == "main": asyncio.run(main())
