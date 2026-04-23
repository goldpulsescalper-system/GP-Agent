import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ADMIN_GROUP_ID, CHANNEL_ID, TOPIC_HASIL_TRADING_ID, TOPIC_TESTIMONI_ID, TOPIC_LAINNYA_ID
from config.prompts import get_caption_prompt
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan dari grup admin (Monitoring Topik)."""
    message = update.message
    
    # Validasi bahwa pesan berasal dari admin group
    if message.chat.id != ADMIN_GROUP_ID:
        return
    
    # Harus ada foto/media
    if not message.photo and not message.video and not message.document:
        return

    thread_id = message.message_thread_id
    
    topic_name = None
    if thread_id == TOPIC_HASIL_TRADING_ID:
        topic_name = "hasil_trading"
    elif thread_id == TOPIC_TESTIMONI_ID:
        topic_name = "testimoni"
    elif thread_id == TOPIC_LAINNYA_ID:
        topic_name = "lainnya"
    else:
        # Jika ada di thread lain atau default thread, skip
        return

    # Filter Anti-Spam / Rate-Limiting (Maks 1 post per 2 jam)
    if not memory.can_post_to_channel():
        logger.info(f"Skip post dari topik {topic_name}: masih dalam cooldown 2 jam.")
        # Bisa juga kirim pesan peringatan ke admin group
        # await message.reply_text("Sabar boss, cooldown 2 jam belum kelar.")
        return

    # Anti-monoton (Optional: skip jika topik sama berturut-turut)
    # if memory.last_topic_posted == topic_name:
    #     logger.info(f"Skip post: Topik '{topic_name}' sudah diposting sebelumnya.")
    #     return

    logger.info(f"Menerima media dari topik {topic_name}. Generating caption...")

    # Tampilkan status typing di grup admin (opsional)
    await context.bot.send_chat_action(chat_id=ADMIN_GROUP_ID, action='typing', message_thread_id=thread_id)

    prompt = get_caption_prompt(topic_name)
    messages = [{"role": "system", "content": prompt}]
    
    # Gunakan temperature yang lebih tinggi agar lebih kreatif
    caption = await generate_response(messages, temperature=0.8)

    if "Sori banget" in caption:
        await message.reply_text("Waduh, AI lagi error dikit. Gagal generate caption.")
        return

    # Post ke Channel
    try:
        # Kirim foto menggunakan file_id
        if message.photo:
            file_id = message.photo[-1].file_id
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=caption)
        elif message.video:
            file_id = message.video.file_id
            await context.bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=caption)
        elif message.document:
            file_id = message.document.file_id
            await context.bot.send_document(chat_id=CHANNEL_ID, document=file_id, caption=caption)
            
        logger.info(f"Berhasil meneruskan post dari {topic_name} ke channel.")
        
        # Update memory setelah post sukses
        memory.update_post_history(topic_name)
        
        # Konfirmasi ke admin
        await message.reply_text("✅ Berhasil di-post ke channel dengan caption AI.")

    except Exception as e:
        logger.error(f"Gagal mem-posting ke channel: {e}")
        await message.reply_text("❌ Gagal kirim ke channel, coba cek log.")
