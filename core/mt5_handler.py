import logging
from telegram import Bot
from telegram.constants import ParseMode
from config.settings import CHANNEL_ID
from core.db import get_signal_message_id, save_signal_message_id
from config.prompts import (
    get_signal_entry_text,
    get_signal_modify_text,
    get_signal_tp_update_text,
    get_signal_tp_hype_text,
    get_signal_sl_update_text,
    get_signal_sl_motivation_text
)

logger = logging.getLogger(__name__)

async def process_mt5_signal(bot: Bot, payload: dict):
    """
    Memproses payload webhook dari MT5 dan mengirim/membalas pesan di Channel.
    """
    action = payload.get("action", "").upper()
    ticket = payload.get("ticket")
    symbol = payload.get("symbol", "")
    type_str = payload.get("type", "")
    price = payload.get("price", 0.0)
    sl = payload.get("sl", 0.0)
    tp = payload.get("tp", 0.0)

    if not action or not ticket:
        logger.error(f"Payload MT5 tidak valid: {payload}")
        return

    logger.info(f"Processing MT5 Signal: {action} - Ticket {ticket}")

    try:
        if action == "ENTRY":
            text = get_signal_entry_text(type_str, symbol, price, sl, tp)
            message = await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            # Simpan message_id untuk reply nanti
            save_signal_message_id(ticket, message.message_id)
            logger.info(f"ENTRY Signal sent. Message ID: {message.message_id}")

        elif action == "MODIFY":
            message_id = get_signal_message_id(ticket)
            if not message_id:
                logger.warning(f"Message ID tidak ditemukan untuk ticket {ticket} (MODIFY)")
                return
            
            text = get_signal_modify_text(sl, tp)
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_id,
                disable_web_page_preview=True
            )
            logger.info(f"MODIFY Signal sent as reply to {message_id}.")

        elif action == "CLOSE_TP":
            message_id = get_signal_message_id(ticket)
            if not message_id:
                logger.warning(f"Message ID tidak ditemukan untuk ticket {ticket} (CLOSE_TP)")
                return
            
            # 1. Update text (Reply to signal)
            update_text = get_signal_tp_update_text(symbol)
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=update_text,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_id,
                disable_web_page_preview=True
            )
            
            # 2. Hype / CTA text (New message)
            hype_text = get_signal_tp_hype_text(symbol)
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=hype_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info(f"CLOSE_TP Signal and Hype sent.")

        elif action == "CLOSE_SL":
            message_id = get_signal_message_id(ticket)
            if not message_id:
                logger.warning(f"Message ID tidak ditemukan untuk ticket {ticket} (CLOSE_SL)")
                return
            
            # 1. Update text (Reply to signal)
            update_text = get_signal_sl_update_text(symbol)
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=update_text,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_id,
                disable_web_page_preview=True
            )
            
            # 2. Motivation text (New message)
            motivation_text = get_signal_sl_motivation_text(symbol)
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=motivation_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info(f"CLOSE_SL Signal and Motivation sent.")

        else:
            logger.warning(f"Aksi tidak dikenal dari MT5: {action}")

    except Exception as e:
        logger.error(f"Error processing MT5 signal: {e}")
