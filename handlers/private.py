import logging
import asyncio
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from config.prompts import PRIVATE_MESSAGE_SYSTEM_PROMPT
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)

async def handle_private_message(client: Client, message: Message):
    """Menangani pesan DM dari user."""
    user = message.from_user
    if not user:
        return
        
    user_id = user.id
    text = message.text

    if not text:
        return

    # Logging untuk debug
    logger.info(f"Received DM from {user.first_name} ({user_id}): {text}")

    # Tambahkan pesan user ke memory
    memory.add_message(user_id, "user", text)

    # Siapkan messages untuk OpenAI
    messages = [{"role": "system", "content": PRIVATE_MESSAGE_SYSTEM_PROMPT}]
    messages.extend(memory.get_messages(user_id))

    # Tampilkan status typing agar seperti manusia
    try:
        await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        # Delay simulasi membaca & mengetik (AI API jg butuh waktu, jadi totalnya sekitar 3-5 detik)
        await asyncio.sleep(2)
    except Exception as e:
        logger.warning(f"Gagal mengirim chat action typing: {e}")

    # Generate balasan
    response = await generate_response(messages, temperature=0.7)

    # Tambahkan balasan bot ke memory
    memory.add_message(user_id, "assistant", response)

    # Kirim balasan
    await message.reply_text(response)
