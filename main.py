import logging
import os
import asyncio
from contextlib import asynccontextmanager
from pytz import timezone

# Fix for Pyrogram RuntimeError: There is no current event loop in thread 'MainThread'
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import uvicorn
from fastapi import FastAPI
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import API_ID, API_HASH, SESSION_STRING
from core.scheduler import post_morning, post_night
from handlers.private import handle_private_message
from core.api import router as mt5_router

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram Client
if SESSION_STRING:
    telegram_client = Client("my_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    # Jika tidak ada session_string, ia akan membuat file my_account.session dan meminta login interaktif
    telegram_client = Client("my_account", api_id=API_ID, api_hash=API_HASH)

# Register Handlers
@telegram_client.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def private_handler(client, message):
    await handle_private_message(client, message)

scheduler = AsyncIOScheduler(timezone=timezone('Asia/Jakarta'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not API_ID or not API_HASH:
        logger.error("API_ID atau API_HASH tidak ditemukan di .env!")
        yield
        return

    # Start Pyrogram Client
    await telegram_client.start()
    app.state.bot = telegram_client
    logger.info("Userbot TF Engine telah berjalan...")

    # Setup APScheduler
    scheduler.add_job(post_morning, 'cron', hour=7, minute=30, args=[telegram_client])
    scheduler.add_job(post_night, 'cron', hour=20, minute=0, args=[telegram_client])
    scheduler.start()
    logger.info("Scheduler telah dijalankan.")

    yield
    
    # Shutdown sequence
    logger.info("Mematikan Userbot TF Engine...")
    scheduler.shutdown()
    await telegram_client.stop()

# Initialize FastAPI App
api_app = FastAPI(lifespan=lifespan)
api_app.include_router(mt5_router, prefix="/api")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:api_app", host="0.0.0.0", port=port, reload=False)
