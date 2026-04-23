import logging
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID
from config.prompts import get_education_prompt, get_softsell_prompt
from core.ai import generate_response

logger = logging.getLogger(__name__)

async def post_education(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post edukasi."""
    logger.info("Menjalankan job post edukasi...")
    prompt = get_education_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content)
            logger.info("Edukasi berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post edukasi: {e}")

async def post_softsell(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post softsell."""
    logger.info("Menjalankan job post softsell...")
    prompt = get_softsell_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content)
            logger.info("Softsell berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post softsell: {e}")
