import logging
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID
from config.prompts import get_education_prompt, get_softsell_prompt, get_motivation_prompt
from core.ai import generate_response

logger = logging.getLogger(__name__)

async def post_education_morning(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post edukasi pagi."""
    logger.info("Menjalankan job post edukasi pagi...")
    prompt = get_education_prompt("morning")
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("Edukasi pagi berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post edukasi pagi: {e}")

async def post_education_afternoon(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post edukasi siang."""
    logger.info("Menjalankan job post edukasi siang...")
    prompt = get_education_prompt("afternoon")
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("Edukasi siang berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post edukasi siang: {e}")

async def post_softsell(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post softsell."""
    logger.info("Menjalankan job post softsell...")
    prompt = get_softsell_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("Softsell berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post softsell: {e}")

async def post_motivation(context: ContextTypes.DEFAULT_TYPE):
    """Job untuk post motivasi."""
    logger.info("Menjalankan job post motivasi...")
    prompt = get_motivation_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.8)
    
    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("Motivasi berhasil di-post.")
        except Exception as e:
            logger.error(f"Gagal mengirim post motivasi: {e}")
