import json
import os
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "signals.json")

def ensure_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as f:
            json.dump({}, f)

def get_signal_message_id(ticket: str, channel_type: str) -> int:
    ensure_db()
    with open(DB_PATH, 'r') as f:
        try:
            data = json.load(f)
            ticket_data = data.get(str(ticket), {})
            if isinstance(ticket_data, dict):
                return ticket_data.get(channel_type)
            # Legacy support
            if channel_type == "free" and isinstance(ticket_data, int):
                return ticket_data
            return None
        except Exception as e:
            logger.error(f"Error reading DB: {e}")
            return None

def save_signal_message_id(ticket: str, channel_type: str, message_id: int):
    ensure_db()
    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
        
        if str(ticket) not in data or not isinstance(data[str(ticket)], dict):
            # If old format or missing, convert to dict
            old_val = data.get(str(ticket))
            data[str(ticket)] = {}
            if isinstance(old_val, int):
                data[str(ticket)]["free"] = old_val
                
        data[str(ticket)][channel_type] = message_id
        
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to DB: {e}")

def get_free_signal_date() -> str:
    ensure_db()
    with open(DB_PATH, 'r') as f:
        try:
            data = json.load(f)
            return data.get("free_signal_date", "")
        except Exception:
            return ""

def set_free_signal_date(date_str: str):
    ensure_db()
    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
        data["free_signal_date"] = date_str
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to DB: {e}")
