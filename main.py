import logging
from datetime import time
from pytz import timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config.settings import TELEGRAM_TOKEN, ADMIN_GROUP_ID
from core.scheduler import post_education_morning, post_education_afternoon, post_softsell, post_motivation
from handlers.private import handle_private_message
from handlers.group import handle_group_message

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

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN tidak ditemukan di .env!")
        return

    # Inisialisasi bot dengan Job Queue
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Daftarkan Handlers

    # [0] DIAGNOSTIC catch-all — log SEMUA pesan yang diterima bot (GROUP + PRIVATE)
    application.add_handler(MessageHandler(filters.ALL, diagnostic_handler), group=0)

    # [1] Handler untuk private message (DM) -> Customer Support
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & (~filters.COMMAND), handle_private_message), group=1)

    # [1] Handler untuk group message -> Monitoring Topik & Auto-Post
    # Support: foto, video, dokumen, dan teks murni dari admin group
    group_content_filter = (
        filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.TEXT
    )
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & group_content_filter, handle_group_message), group=1)

    # Setup APScheduler Jobs
    job_queue = application.job_queue

    # Waktu (Asia/Jakarta)
    # Jadwal Konten (08:00, 13:00, 17:00, 20:00)
    
    # 08:00 - Edukasi Pagi
    job_queue.run_daily(post_education_morning, time=time(hour=8, minute=0, tzinfo=timezone('Asia/Jakarta')))
    
    # 13:00 - Edukasi Siang
    job_queue.run_daily(post_education_afternoon, time=time(hour=13, minute=0, tzinfo=timezone('Asia/Jakarta')))

    # 17:00 - Motivasi
    job_queue.run_daily(post_motivation, time=time(hour=17, minute=0, tzinfo=timezone('Asia/Jakarta')))

    # 20:00 - Softsell
    job_queue.run_daily(post_softsell, time=time(hour=20, minute=0, tzinfo=timezone('Asia/Jakarta')))

    logger.info("Bot GP_Agent telah berjalan...")

    # Jalankan polling — allowed_updates eksplisit agar semua tipe pesan diterima
    application.run_polling(
        allowed_updates=[
            "message",
            "edited_message",
            "channel_post",
            "callback_query",
        ]
    )

if __name__ == '__main__':
    main()
