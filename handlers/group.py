import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import (
    ADMIN_GROUP_ID, CHANNEL_ID,
    TOPIC_HASIL_TRADING_ID, TOPIC_TESTIMONI_ID, TOPIC_LAINNYA_ID
)
from config.prompts import get_caption_prompt, get_rebrand_prompt
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)


def _detect_forward(message) -> tuple[bool, str]:
    """
    Deteksi apakah pesan adalah forward dan dari mana asalnya.
    Kompatibel dengan PTB v20 dan v21 (Telegram Bot API 6+ & 7+).
    Mengembalikan (is_forwarded: bool, source_name: str).
    """
    # --- PTB v21 / Bot API 7.0+ ---
    try:
        origin = getattr(message, "forward_origin", None)
        if origin is not None:
            # origin bisa bertipe MessageOriginChannel, MessageOriginUser, dll.
            source = ""
            chat = getattr(origin, "chat", None)
            if chat:
                source = getattr(chat, "title", "") or str(getattr(chat, "id", ""))
            sender = getattr(origin, "sender_user", None)
            if not source and sender:
                source = getattr(sender, "username", "") or getattr(sender, "first_name", "")
            sender_name = getattr(origin, "sender_user_name", None)
            if not source and sender_name:
                source = sender_name
            return True, source
    except Exception:
        pass

    # --- PTB v20 / Bot API < 7.0 (fallback) ---
    try:
        if getattr(message, "forward_from_chat", None):
            chat = message.forward_from_chat
            source = getattr(chat, "title", "") or str(getattr(chat, "id", ""))
            return True, source
        if getattr(message, "forward_from", None):
            u = message.forward_from
            source = getattr(u, "username", "") or getattr(u, "first_name", "")
            return True, source
        if getattr(message, "forward_sender_name", None):
            return True, message.forward_sender_name
        # Cek field tambahan untuk forward dari channel tanpa username
        if getattr(message, "forward_date", None):
            return True, "channel tidak diketahui"
    except Exception:
        pass

    return False, ""


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Menangani pesan dari grup admin (topik).
    Support: teks murni, foto, video, dokumen, dan forward dari channel lain.
    Seluruh handler dibungkus try-except agar tidak pernah diam/crash tanpa laporan.
    """
    try:
        message = update.message
        if not message:
            logger.warning("[AutoPost] update.message is None, skip.")
            return

        # ── 1. VALIDASI CHAT ────────────────────────────────────────────────────
        chat_id = message.chat.id
        if chat_id != ADMIN_GROUP_ID:
            logger.debug(f"[AutoPost] Pesan dari chat {chat_id} bukan admin group, skip.")
            return

        # ── 2. IDENTIFIKASI TOPIK ───────────────────────────────────────────────
        thread_id = message.message_thread_id

        logger.info(
            f"[AutoPost] Masuk | chat_id={chat_id} | thread_id={thread_id} | "
            f"TRADING={TOPIC_HASIL_TRADING_ID} | TESTIMONI={TOPIC_TESTIMONI_ID} | "
            f"LAINNYA={TOPIC_LAINNYA_ID}"
        )

        if thread_id == TOPIC_HASIL_TRADING_ID:
            topic_name = "hasil_trading"
        elif thread_id == TOPIC_TESTIMONI_ID:
            topic_name = "testimoni"
        elif thread_id == TOPIC_LAINNYA_ID:
            topic_name = "lainnya"
        else:
            logger.warning(f"[AutoPost] thread_id={thread_id} tidak dikenal, kirim debug info.")
            await message.reply_text(
                f"⚠️ <b>Debug Info</b>\n\n"
                f"Thread ID <code>{thread_id}</code> belum terdaftar.\n\n"
                f"<b>Konfigurasi saat ini:</b>\n"
                f"• HASIL_TRADING = <code>{TOPIC_HASIL_TRADING_ID}</code>\n"
                f"• TESTIMONI = <code>{TOPIC_TESTIMONI_ID}</code>\n"
                f"• LAINNYA = <code>{TOPIC_LAINNYA_ID}</code>\n\n"
                f"Update nilai yang sesuai di Railway → Variables.",
                parse_mode='HTML'
            )
            return

        # ── 3. CEK TIPE KONTEN ──────────────────────────────────────────────────
        has_photo    = bool(message.photo)
        has_video    = bool(message.video)
        has_document = bool(message.document)
        has_text     = bool(message.text or message.caption)
        has_media    = has_photo or has_video or has_document

        if not has_media and not has_text:
            logger.info("[AutoPost] Pesan kosong (sticker/voice/dll), skip.")
            return

        # Ambil teks (caption foto/video atau pesan teks murni)
        admin_text = (message.caption or message.text or "").strip()

        # ── 4. DETEKSI FORWARD ──────────────────────────────────────────────────
        is_forwarded, forward_source = _detect_forward(message)

        logger.info(
            f"[AutoPost] Topik={topic_name} | media={has_media} | "
            f"teks={bool(admin_text)} | forward={is_forwarded} (src={forward_source or '-'})"
        )

        # Kirim sinyal typing ke grup admin
        try:
            await context.bot.send_chat_action(
                chat_id=ADMIN_GROUP_ID,
                action='typing',
                message_thread_id=thread_id
            )
        except Exception:
            pass  # Typing action tidak krusial

        # ── 5. BANGUN PROMPT ────────────────────────────────────────────────────
        if is_forwarded and admin_text:
            prompt = get_rebrand_prompt(topic_name, original_text=admin_text, source=forward_source)
            logger.info("[AutoPost] Mode: RE-BRAND (forward dengan teks)")
        elif admin_text:
            base = get_caption_prompt(topic_name)
            prompt = (
                f"{base}\n\n"
                f"Admin menyiapkan materi/konteks ini — jadikan acuan:\n"
                f"\"{admin_text}\""
            )
            logger.info("[AutoPost] Mode: KONTEKS ADMIN")
        else:
            prompt = get_caption_prompt(topic_name)
            logger.info("[AutoPost] Mode: GENERATE FRESH")

        # ── 6. GENERATE CAPTION ─────────────────────────────────────────────────
        messages_payload = [{"role": "system", "content": prompt}]
        caption = await generate_response(messages_payload, temperature=0.85)

        if not caption or "Sori banget" in caption:
            await message.reply_text(
                "❌ AI gagal generate caption. Coba kirim ulang dalam beberapa detik."
            )
            return

        # ── 7. POST KE CHANNEL ──────────────────────────────────────────────────
        if has_photo:
            file_id = message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=CHANNEL_ID, photo=file_id,
                caption=caption, parse_mode='HTML'
            )
        elif has_video:
            file_id = message.video.file_id
            await context.bot.send_video(
                chat_id=CHANNEL_ID, video=file_id,
                caption=caption, parse_mode='HTML'
            )
        elif has_document:
            file_id = message.document.file_id
            await context.bot.send_document(
                chat_id=CHANNEL_ID, document=file_id,
                caption=caption, parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID, text=caption, parse_mode='HTML'
            )

        memory.update_post_history(topic_name)
        logger.info(f"[AutoPost] ✅ Terkirim ke channel | topik={topic_name} | forward={is_forwarded}")

        # ── 8. KONFIRMASI KE ADMIN ──────────────────────────────────────────────
        label = "🔄 Re-brand & post" if is_forwarded else "✅ Berhasil dipost"
        preview = caption[:220] + ("..." if len(caption) > 220 else "")
        await message.reply_text(
            f"{label} ke channel!\n\n<b>Preview:</b>\n{preview}",
            parse_mode='HTML'
        )

    except Exception as e:
        # Handler level error — selalu laporkan ke admin group
        logger.error(f"[AutoPost] ERROR tidak tertangani: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ <b>Error tidak terduga:</b>\n<code>{e}</code>\n\nCek Railway logs untuk detail.",
                parse_mode='HTML'
            )
        except Exception:
            pass
