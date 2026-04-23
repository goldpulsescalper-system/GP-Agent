import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.prompts import PRIVATE_MESSAGE_SYSTEM_PROMPT
from core.ai import generate_response
from core.memory import memory

logger = logging.getLogger(__name__)

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan DM dari user."""
    user = update.message.from_user
    user_id = user.id
    text = update.message.text

    if not text:
        return

    # Logging untuk debug
    logger.info(f"Received DM from {user.first_name} ({user_id}): {text}")

    # Tambahkan pesan user ke memory
    memory.add_message(user_id, "user", text)

    # Siapkan messages untuk OpenAI
    messages = [{"role": "system", "content": PRIVATE_MESSAGE_SYSTEM_PROMPT}]
    messages.extend(memory.get_messages(user_id))

    # Tampilkan status typing
    await context.bot.send_chat_action(chat_id=user_id, action='typing')

    # Generate balasan
    response = await generate_response(messages, temperature=0.7)

    # Tambahkan balasan bot ke memory
    memory.add_message(user_id, "assistant", response)

    # Kirim balasan
    await update.message.reply_text(response)
