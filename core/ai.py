import logging
from openai import AsyncOpenAI
import asyncio
from config.settings import OPENAI_API_KEY, AI_BASE_URL, AI_MODEL

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=AI_BASE_URL,
)

async def generate_response(messages: list, temperature: float = 0.7, max_tokens: int = 1500) -> str:
    """Wrapper untuk call OpenAI dengan retry logic."""
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
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API Error (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                return "Sori banget, sistem gue lagi error dikit nih. Coba lagi bentar ya."
