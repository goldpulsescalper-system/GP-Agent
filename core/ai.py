import logging
from openai import AsyncOpenAI
import asyncio
import html
import re
from config.settings import OPENAI_API_KEY, AI_BASE_URL, AI_MODEL

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=AI_BASE_URL,
)

def format_for_telegram_html(text: str) -> str:
    """Escape HTML characters and convert markdown bold to HTML."""
    safe_text = html.escape(text)
    # Ubah **teks** menjadi <b>teks</b>
    safe_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_text)
    # Tambahkan support untuk __teks__ menjadi italic jika diinginkan (opsional)
    safe_text = re.sub(r'__(.*?)__', r'<i>\1</i>', safe_text)
    
    # Kembalikan tag HTML yang valid jika AI merespons langsung dengan HTML
    valid_tags = ['b', '/b', 'i', '/i', 'strong', '/strong', 'u', '/u']
    for tag in valid_tags:
        safe_text = safe_text.replace(f"&lt;{tag}&gt;", f"<{tag}>")
    
    return safe_text

async def generate_response(messages: list, temperature: float = 0.7, max_tokens: int = 1500) -> str:
    """Wrapper untuk call OpenAI dengan retry logic dan formatting khusus Telegram."""
    retries = 3
    delay = 2
    for attempt in range(retries):
        try:
            response = await client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()
            return format_for_telegram_html(content)
        except Exception as e:
            logger.error(f"OpenAI API Error (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                return "Sori banget, sistem gue lagi error dikit nih. Coba lagi bentar ya."
