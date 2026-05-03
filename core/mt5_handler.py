import logging
from datetime import datetime
import pytz
from pyrogram import Client
from pyrogram.enums import ParseMode
from config.settings import CHANNEL_ID, VIP_CHANNEL_ID
from core.db import get_signal_message_id, save_signal_message_id, get_free_signal_date, set_free_signal_date
from config.prompts import (
    get_signal_entry_text,
    get_signal_modify_text,
    get_signal_tp_update_text,
    get_signal_tp_hype_text,
    get_signal_sl_update_text,
    get_signal_sl_motivation_text
)

logger = logging.getLogger(__name__)

def can_send_free_signal(symbol: str) -> bool:
    if symbol.upper() != "XAUUSD":
        return False
    today_str = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d")
    last_sent = get_free_signal_date()
    return last_sent != today_str

def mark_free_signal_sent():
    today_str = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d")
    set_free_signal_date(today_str)

async def process_mt5_signal(client: Client, payload: dict):
    """
    Memproses payload webhook dari MT5 dan mengirim/membalas pesan di Channel VIP dan Free.
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
            
            # 1. Send to VIP Channel
            if VIP_CHANNEL_ID:
                try:
                    msg_vip = await client.send_message(
                        chat_id=VIP_CHANNEL_ID,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    save_signal_message_id(ticket, "vip", msg_vip.id)
                except Exception as e:
                    logger.error(f"Error sending to VIP: {e}")

            # 2. Send to Free Channel if eligible
            if can_send_free_signal(symbol):
                try:
                    msg_free = await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    save_signal_message_id(ticket, "free", msg_free.id)
                    mark_free_signal_sent()
                    logger.info(f"ENTRY Signal sent to FREE. Message ID: {msg_free.id}")
                except Exception as e:
                    logger.error(f"Error sending to Free: {e}")

        elif action == "MODIFY":
            text = get_signal_modify_text(sl, tp)
            
            # Update VIP
            if VIP_CHANNEL_ID:
                msg_id_vip = get_signal_message_id(ticket, "vip")
                if msg_id_vip:
                    try:
                        await client.send_message(
                            chat_id=VIP_CHANNEL_ID,
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_to_message_id=msg_id_vip,
                            disable_web_page_preview=True
                        )
                    except Exception as e:
                        logger.error(f"Error modify VIP: {e}")
            
            # Update FREE
            msg_id_free = get_signal_message_id(ticket, "free")
            if msg_id_free:
                try:
                    await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=msg_id_free,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Error modify FREE: {e}")

        elif action == "CLOSE_TP":
            update_text = get_signal_tp_update_text(symbol)
            hype_text = get_signal_tp_hype_text(symbol)
            
            # Update VIP
            if VIP_CHANNEL_ID:
                msg_id_vip = get_signal_message_id(ticket, "vip")
                if msg_id_vip:
                    try:
                        await client.send_message(
                            chat_id=VIP_CHANNEL_ID,
                            text=update_text,
                            parse_mode=ParseMode.HTML,
                            reply_to_message_id=msg_id_vip,
                            disable_web_page_preview=True
                        )
                        # No hype text for VIP
                    except Exception as e:
                        logger.error(f"Error close TP VIP: {e}")

            # Update FREE
            msg_id_free = get_signal_message_id(ticket, "free")
            if msg_id_free:
                try:
                    await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=update_text,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=msg_id_free,
                        disable_web_page_preview=True
                    )
                    # Hype text only for Free
                    await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=hype_text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Error close TP FREE: {e}")

        elif action == "CLOSE_SL":
            update_text = get_signal_sl_update_text(symbol)
            motivation_text = get_signal_sl_motivation_text(symbol)
            
            # Update VIP
            if VIP_CHANNEL_ID:
                msg_id_vip = get_signal_message_id(ticket, "vip")
                if msg_id_vip:
                    try:
                        await client.send_message(
                            chat_id=VIP_CHANNEL_ID,
                            text=update_text,
                            parse_mode=ParseMode.HTML,
                            reply_to_message_id=msg_id_vip,
                            disable_web_page_preview=True
                        )
                        # No motivation text for VIP
                    except Exception as e:
                        logger.error(f"Error close SL VIP: {e}")

            # Update FREE
            msg_id_free = get_signal_message_id(ticket, "free")
            if msg_id_free:
                try:
                    await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=update_text,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=msg_id_free,
                        disable_web_page_preview=True
                    )
                    # Motivation text only for Free
                    await client.send_message(
                        chat_id=CHANNEL_ID,
                        text=motivation_text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Error close SL FREE: {e}")

        else:
            logger.warning(f"Aksi tidak dikenal dari MT5: {action}")

    except Exception as e:
        logger.error(f"Error processing MT5 signal: {e}")
