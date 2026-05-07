import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID", "0"))

# AI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_BASE_URL = "https://ai.sumopod.com/v1/"
AI_MODEL = "gpt-4o"

# Konstanta
OFFICIAL_WEBSITE = os.getenv("OFFICIAL_WEBSITE", "https://xauengine.com")
LINK_MEMBERSHIP = os.getenv("LINK_MEMBERSHIP", "https://xauengine.com/membership")

CHANNEL_LINK = "https://t.me/xauengine"
CONTACT_ADMIN = "@xauengine_official"
MIN_DEPOSIT = "$100"
