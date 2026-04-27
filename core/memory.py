from datetime import datetime

class Memory:
    def __init__(self):
        # Menyimpan history chat DM per user: {user_id: [ {"role": "user", "content": "..."}, ... ]}
        self.user_chats = {}
        # Tracking topik terakhir yang diposting (untuk logging, bukan untuk block)
        self.last_channel_post_time = None
        self.last_topic_posted = None

    def add_message(self, user_id: int, role: str, content: str, max_history: int = 10):
        if user_id not in self.user_chats:
            self.user_chats[user_id] = []
        self.user_chats[user_id].append({"role": role, "content": content})
        if len(self.user_chats[user_id]) > max_history:
            self.user_chats[user_id].pop(0)

    def get_messages(self, user_id: int) -> list:
        return self.user_chats.get(user_id, [])

    def can_post_to_channel(self) -> bool:
        """Selalu True — tidak ada rate limit. Bot langsung proses setiap konten."""
        return True

    def update_post_history(self, topic: str):
        self.last_channel_post_time = datetime.now()
        self.last_topic_posted = topic

# Global instance
memory = Memory()
