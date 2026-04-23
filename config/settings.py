import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
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
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK", "https://broker.link/affiliate")
CHANNEL_LINK = "https://t.me/goldpulsescalper"
CONTACT_ADMIN = "@GP_Scalper"
MIN_DEPOSIT = "$50"
