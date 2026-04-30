import json
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "signals.json")

def ensure_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as f:
            json.dump({}, f)

def get_signal_message_id(ticket: str) -> int:
    ensure_db()
    with open(DB_PATH, 'r') as f:
        try:
            data = json.load(f)
            return data.get(str(ticket))
        except Exception as e:
            logger.error(f"Error reading DB: {e}")
            return None

def save_signal_message_id(ticket: str, message_id: int):
    ensure_db()
    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
        data[str(ticket)] = message_id
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to DB: {e}")
