import logging
from datetime import datetime
import pytz
from pyrogram import Client
from config.settings import CHANNEL_ID
from config.prompts import get_morning_post_prompt, get_night_post_prompt
from core.ai import generate_response

logger = logging.getLogger(__name__)

wib = pytz.timezone('Asia/Jakarta')

def is_market_holiday() -> bool:
    """Return True jika hari ini Sabtu atau Minggu (waktu WIB)."""
    now = datetime.now(wib)
    # weekday(): 0=Monday, 1=Tuesday, ... 5=Saturday, 6=Sunday
    return now.weekday() >= 5

async def post_morning(client: Client):
    """Job 07:30 — Sapaan pagi + motivasi + soft-sell."""
    if is_market_holiday():
        logger.info("[Scheduler] Hari ini weekend, post pagi dilewati.")
        return

    logger.info("[Scheduler] Menjalankan post pagi (07:30)...")
    prompt = get_morning_post_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.85)

    if content and "Sori banget" not in content:
        try:
            await client.send_message(chat_id=CHANNEL_ID, text=content)
            logger.info("[Scheduler] ✅ Post pagi berhasil dikirim.")
        except Exception as e:
            logger.error(f"[Scheduler] Gagal kirim post pagi: {e}")
    else:
        logger.warning("[Scheduler] Post pagi gagal generate, skip.")

async def post_night(client: Client):
    """Job 20:00 — Sapaan malam + hard-sell psikologi persuasif."""
    if is_market_holiday():
        logger.info("[Scheduler] Hari ini weekend, post malam dilewati.")
        return

    logger.info("[Scheduler] Menjalankan post malam (20:00)...")
    prompt = get_night_post_prompt()
    messages = [{"role": "system", "content": prompt}]
    content = await generate_response(messages, temperature=0.9)

    if content and "Sori banget" not in content:
        try:
            await client.send_message(chat_id=CHANNEL_ID, text=content)
            logger.info("[Scheduler] ✅ Post malam berhasil dikirim.")
        except Exception as e:
            logger.error(f"[Scheduler] Gagal kirim post malam: {e}")
    else:
        logger.warning("[Scheduler] Post malam gagal generate, skip.")
