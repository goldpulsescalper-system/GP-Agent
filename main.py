import logging
from contextlib import asynccontextmanager
from datetime import time
from pytz import timezone
import os

import uvicorn
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from config.settings import TELEGRAM_TOKEN, ADMIN_GROUP_ID
from core.scheduler import post_morning, post_night
from handlers.private import handle_private_message
from handlers.group import handle_group_message
from core.api import router as mt5_router

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def diagnostic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch-all diagnostic: log setiap pesan yang masuk ke bot."""
    msg = update.message
    if not msg:
        return
    logger.info(
        f"[DIAGNOSTIC] chat_id={msg.chat.id} | chat_type={msg.chat.type} | "
        f"thread_id={msg.message_thread_id} | "
        f"has_text={bool(msg.text)} | has_photo={bool(msg.photo)} | "
        f"has_doc={bool(msg.document)} | ADMIN_GROUP_ID={ADMIN_GROUP_ID}"
    )

telegram_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN tidak ditemukan di .env!")
        yield
        return

    # Inisialisasi bot dengan Job Queue
    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Store bot in app state so FastAPI routes can access it
    app.state.bot = telegram_app.bot

    # Daftarkan Handlers
    telegram_app.add_handler(MessageHandler(filters.ALL, diagnostic_handler), group=0)
    telegram_app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & (~filters.COMMAND), handle_private_message), group=1)

    group_content_filter = (
        filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.TEXT
    )
    telegram_app.add_handler(MessageHandler(filters.ChatType.GROUPS & group_content_filter, handle_group_message), group=1)

    # Setup APScheduler Jobs (Asia/Jakarta)
    job_queue = telegram_app.job_queue
    wib = timezone('Asia/Jakarta')
    job_queue.run_daily(post_morning, time=time(hour=7, minute=30, tzinfo=wib))
    job_queue.run_daily(post_night, time=time(hour=20, minute=0, tzinfo=wib))

    # Initialize and start the Telegram Bot
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(
        allowed_updates=["message", "edited_message", "channel_post", "callback_query"]
    )
    logger.info("Bot GP_Agent telah berjalan bersama FastAPI webhook server...")
    
    yield
    
    # Shutdown sequence
    if telegram_app:
        logger.info("Mematikan bot GP_Agent...")
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()

# Initialize FastAPI App
api_app = FastAPI(lifespan=lifespan)
api_app.include_router(mt5_router, prefix="/api")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:api_app", host="0.0.0.0", port=port, reload=False)
