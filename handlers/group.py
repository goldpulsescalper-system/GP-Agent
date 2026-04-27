import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ADMIN_GROUP_ID, CHANNEL_ID, TOPIC_HASIL_TRADING_ID, TOPIC_TESTIMONI_ID, TOPIC_LAINNYA_ID
from config.prompts import get_caption_prompt, get_rebrand_prompt
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan dari grup admin — support foto, video, dokumen, dan teks murni."""
    message = update.message
    if not message:
        return

    # Validasi dari admin group saja
    if message.chat.id != ADMIN_GROUP_ID:
        return

    thread_id = message.message_thread_id

    # DEBUG: log selalu thread_id yang diterima dari admin group
    logger.info(
        f"[DEBUG] Pesan masuk dari admin group | chat_id={message.chat.id} | "
        f"thread_id={thread_id} | "
        f"TOPIC_HASIL_TRADING_ID={TOPIC_HASIL_TRADING_ID} | "
        f"TOPIC_TESTIMONI_ID={TOPIC_TESTIMONI_ID} | "
        f"TOPIC_LAINNYA_ID={TOPIC_LAINNYA_ID}"
    )

    # Tentukan topik berdasarkan thread
    topic_name = None
    if thread_id == TOPIC_HASIL_TRADING_ID:
        topic_name = "hasil_trading"
    elif thread_id == TOPIC_TESTIMONI_ID:
        topic_name = "testimoni"
    elif thread_id == TOPIC_LAINNYA_ID:
        topic_name = "lainnya"
    else:
        # Thread tidak dikenali — kirim notif debug ke admin agar tau ID-nya
        logger.warning(f"[AutoPost] Thread ID tidak dikenali: {thread_id}. Pesan diabaikan.")
        await message.reply_text(
            f"⚠️ <b>Debug Info</b>\n\n"
            f"Thread ID ini <b>tidak terdaftar</b> di konfigurasi bot.\n\n"
            f"<b>Thread ID sekarang:</b> <code>{thread_id}</code>\n\n"
            f"Salin angka di atas dan update <code>TOPIC_LAINNYA_ID</code> (atau topik yang sesuai) "
            f"di Railway → Variables.",
            parse_mode='HTML'
        )
        return

    # Tentukan tipe konten
    has_photo    = bool(message.photo)
    has_video    = bool(message.video)
    has_document = bool(message.document)
    has_text     = bool(message.text or message.caption)
    has_media    = has_photo or has_video or has_document

    # Skip jika benar-benar kosong (misal: sticker, voice note, dll)
    if not has_media and not has_text:
        return

    # Ambil teks referensi (caption/teks yang ada di pesan)
    admin_text = (message.caption or message.text or "").strip()

    # ── DETEKSI FORWARD ────────────────────────────────────────────────────────
    # Pesan forward dari channel/grup lain → wajib re-brand + ganti CTA
    is_forwarded = bool(
        message.forward_origin or          # API baru (PTB v20+)
        message.forward_from_chat or       # forward dari channel/grup
        message.forward_from or            # forward dari user/bot
        message.forward_sender_name        # forward dari akun privat
    )

    # Nama sumber forward (untuk log)
    forward_source = ""
    if message.forward_from_chat:
        forward_source = message.forward_from_chat.title or str(message.forward_from_chat.id)
    elif message.forward_from:
        forward_source = message.forward_from.username or message.forward_from.first_name
    elif message.forward_sender_name:
        forward_source = message.forward_sender_name

    logger.info(
        f"[AutoPost] Topik: {topic_name} | Media: {has_media} | "
        f"Forwarded: {is_forwarded} (dari: {forward_source or '-'}) | Teks: {bool(admin_text)}"
    )

    # Tampilkan status typing ke grup admin
    await context.bot.send_chat_action(
        chat_id=ADMIN_GROUP_ID,
        action='typing',
        message_thread_id=thread_id
    )

    # ── BANGUN PROMPT ──────────────────────────────────────────────────────────
    if is_forwarded and admin_text:
        # Konten forward → re-brand total + ganti CTA
        prompt = get_rebrand_prompt(topic_name, original_text=admin_text, source=forward_source)
    elif is_forwarded and not admin_text:
        # Forward tapi tidak ada teks (misal: foto saja tanpa caption dari channel lain)
        # Treat seperti biasa, generate caption fresh
        prompt = get_caption_prompt(topic_name)
    elif admin_text:
        # Bukan forward tapi ada teks admin → jadikan konteks
        base_prompt = get_caption_prompt(topic_name)
        prompt = (
            f"{base_prompt}\n\n"
            f"Admin sudah menyiapkan materi/konteks berikut — gunakan sebagai acuan:\n"
            f"\"{admin_text}\""
        )
    else:
        # Tidak ada teks sama sekali → generate fresh
        prompt = get_caption_prompt(topic_name)

    messages = [{"role": "system", "content": prompt}]
    caption = await generate_response(messages, temperature=0.85)

    if "Sori banget" in caption:
        await message.reply_text("❌ AI lagi ada gangguan, gagal generate caption. Coba kirim ulang.")
        return

    # ── POST KE CHANNEL ────────────────────────────────────────────────────────
    try:
        if has_photo:
            file_id = message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=file_id,
                caption=caption,
                parse_mode='HTML'
            )
        elif has_video:
            file_id = message.video.file_id
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=file_id,
                caption=caption,
                parse_mode='HTML'
            )
        elif has_document:
            file_id = message.document.file_id
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=file_id,
                caption=caption,
                parse_mode='HTML'
            )
        else:
            # Teks murni → kirim sebagai pesan teks ke channel
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode='HTML'
            )

        logger.info(f"[AutoPost] ✅ Berhasil dikirim ke channel dari topik '{topic_name}' (forward={is_forwarded}).")
        memory.update_post_history(topic_name)

        # Konfirmasi ke admin — label beda untuk forward vs normal
        label = "🔄 Re-brand & post" if is_forwarded else "✅ Berhasil dipost"
        preview = caption[:200] + ("..." if len(caption) > 200 else "")
        await message.reply_text(
            f"{label} ke channel!\n\n<b>Preview caption:</b>\n{preview}",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"[AutoPost] Gagal kirim ke channel: {e}")
        await message.reply_text(f"❌ Gagal kirim ke channel.\n<code>{e}</code>", parse_mode='HTML')
