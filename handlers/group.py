import logging
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config.settings import (
    ADMIN_GROUP_ID, CHANNEL_ID,
    TOPIC_HASIL_TRADING_ID, TOPIC_TESTIMONI_ID, TOPIC_LAINNYA_ID
)
from config.prompts import get_caption_prompt, get_rebrand_prompt
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)

def _detect_forward(message: Message) -> tuple[bool, str]:
    """
    Deteksi apakah pesan adalah forward dan dari mana asalnya.
    Kompatibel dengan Pyrogram Message object.
    Mengembalikan (is_forwarded: bool, source_name: str).
    """
    if message.forward_date:
        source = ""
        if message.forward_from_chat:
            source = message.forward_from_chat.title or str(message.forward_from_chat.id)
        elif message.forward_from:
            source = message.forward_from.username or message.forward_from.first_name
        elif message.forward_sender_name:
            source = message.forward_sender_name
        return True, source
    return False, ""


async def handle_group_message(client: Client, message: Message):
    """
    Menangani pesan dari grup admin (topik).
    Support: teks murni, foto, video, dokumen, dan forward dari channel lain.
    Seluruh handler dibungkus try-except agar tidak pernah diam/crash tanpa laporan.
    """
    try:
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
                f"⚠️ **Debug Info**\n\n"
                f"Thread ID `{thread_id}` belum terdaftar.\n\n"
                f"**Konfigurasi saat ini:**\n"
                f"• HASIL_TRADING = `{TOPIC_HASIL_TRADING_ID}`\n"
                f"• TESTIMONI = `{TOPIC_TESTIMONI_ID}`\n"
                f"• LAINNYA = `{TOPIC_LAINNYA_ID}`\n\n"
                f"Update nilai yang sesuai di Railway → Variables.",
                parse_mode=ParseMode.MARKDOWN
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

        # Kirim sinyal typing ke grup admin (Pyrogram enums/string tidak strict)
        # Di userbot mungkin tidak bisa kirim chat_action di group
        try:
            pass # userbot rarely uses chat actions in groups
        except Exception:
            pass  

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
            file_id = message.photo.file_id
            await client.send_photo(
                chat_id=CHANNEL_ID, photo=file_id,
                caption=caption, parse_mode=ParseMode.HTML
            )
        elif has_video:
            file_id = message.video.file_id
            await client.send_video(
                chat_id=CHANNEL_ID, video=file_id,
                caption=caption, parse_mode=ParseMode.HTML
            )
        elif has_document:
            file_id = message.document.file_id
            await client.send_document(
                chat_id=CHANNEL_ID, document=file_id,
                caption=caption, parse_mode=ParseMode.HTML
            )
        else:
            await client.send_message(
                chat_id=CHANNEL_ID, text=caption, parse_mode=ParseMode.HTML
            )

        memory.update_post_history(topic_name)
        logger.info(f"[AutoPost] ✅ Terkirim ke channel | topik={topic_name} | forward={is_forwarded}")

        # ── 8. KONFIRMASI KE ADMIN ──────────────────────────────────────────────
        label = "🔄 Re-brand & post" if is_forwarded else "✅ Berhasil dipost"
        preview = caption[:220] + ("..." if len(caption) > 220 else "")
        await message.reply_text(
            f"{label} ke channel!\n\n<b>Preview:</b>\n{preview}",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        # Handler level error — selalu laporkan ke admin group
        logger.error(f"[AutoPost] ERROR tidak tertangani: {e}", exc_info=True)
        try:
            await message.reply_text(
                f"❌ <b>Error tidak terduga:</b>\n<code>{e}</code>\n\nCek logs untuk detail.",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass
