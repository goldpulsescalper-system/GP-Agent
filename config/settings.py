import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Topic IDs
TOPIC_HASIL_TRADING_ID = int(os.getenv("TOPIC_HASIL_TRADING_ID", "0"))
TOPIC_TESTIMONI_ID = int(os.getenv("TOPIC_TESTIMONI_ID", "0"))
TOPIC_LAINNYA_ID = int(os.getenv("TOPIC_LAINNYA_ID", "0"))

# AI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_BASE_URL = "https://ai.sumopod.com/v1/"
AI_MODEL = "gpt-4o"

# Konstanta
OFFICIAL_WEBSITE = os.getenv("OFFICIAL_WEBSITE", "https://tfengine.com")
LINK_MEMBERSHIP = os.getenv("LINK_MEMBERSHIP", "https://tfengine.com/membership")
LINK_FUNDED = os.getenv("LINK_FUNDED", "https://tfengine.com/funded")
LINK_COPY_EXECUTION = os.getenv("LINK_COPY_EXECUTION", "https://tfengine.com/copy-execution")

CHANNEL_LINK = "https://t.me/tfengine_official"
CONTACT_ADMIN = "@Tfengine_admin"
MIN_DEPOSIT = "$50"
