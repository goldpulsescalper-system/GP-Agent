import logging
from datetime import time
from pytz import timezone
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from config.settings import TELEGRAM_TOKEN
from core.scheduler import post_education, post_softsell, post_motivation
from handlers.private import handle_private_message
from handlers.group import handle_group_message

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN tidak ditemukan di .env!")
        return

    # Inisialisasi bot dengan Job Queue
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Daftarkan Handlers
    # Handler untuk private message (DM) -> Customer Support
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & (~filters.COMMAND), handle_private_message))
    
    # Handler untuk group message -> Monitoring Topik & Auto-Post
    # Kita menggunakan filters.ChatType.GROUPS (termasuk SUPERGROUP) dan mengecek media
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.PHOTO | filters.VIDEO | filters.Document.ALL), handle_group_message))

    # Setup APScheduler Jobs
    job_queue = application.job_queue

    # Waktu (Asia/Jakarta)
    # Jadwal Konten (08:00, 13:00, 17:00, 20:00)
    
    # 08:00 & 13:00 - Edukasi
    job_queue.run_daily(post_education, time=time(hour=8, minute=0, tzinfo=timezone('Asia/Jakarta')))
    job_queue.run_daily(post_education, time=time(hour=13, minute=0, tzinfo=timezone('Asia/Jakarta')))

    # 17:00 - Motivasi
    job_queue.run_daily(post_motivation, time=time(hour=17, minute=0, tzinfo=timezone('Asia/Jakarta')))

    # 20:00 - Softsell
    job_queue.run_daily(post_softsell, time=time(hour=20, minute=0, tzinfo=timezone('Asia/Jakarta')))

    logger.info("Bot GP_Agent telah berjalan...")
    
    # Jalankan polling
    application.run_polling()

if __name__ == '__main__':
    main()
