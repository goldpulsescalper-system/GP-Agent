import logging
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID
from config.prompts import get_morning_post_prompt, get_night_post_prompt
from core.ai import generate_response

logger = logging.getLogger(__name__)

async def post_morning(context: ContextTypes.DEFAULT_TYPE):
    """Job 07:30 — Sapaan pagi + motivasi + soft-sell."""
    logger.info("[Scheduler] Menjalankan post pagi (07:30)...")
    prompt = get_morning_post_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.85)

    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("[Scheduler] ✅ Post pagi berhasil dikirim.")
        except Exception as e:
            logger.error(f"[Scheduler] Gagal kirim post pagi: {e}")
    else:
        logger.warning("[Scheduler] Post pagi gagal generate, skip.")

async def post_night(context: ContextTypes.DEFAULT_TYPE):
    """Job 20:00 — Sapaan malam + hard-sell psikologi persuasif."""
    logger.info("[Scheduler] Menjalankan post malam (20:00)...")
    prompt = get_night_post_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.9)

    if content and "Sori banget" not in content:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode='HTML')
            logger.info("[Scheduler] ✅ Post malam berhasil dikirim.")
        except Exception as e:
            logger.error(f"[Scheduler] Gagal kirim post malam: {e}")
    else:
        logger.warning("[Scheduler] Post malam gagal generate, skip.")
