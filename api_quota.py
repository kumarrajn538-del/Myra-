import time
from myra_config import API_KEYS, MAX_MESSAGES_PER_KEY

class APIQuotaManager:
    def __init__(self):
        self.api_keys = API_KEYS
        self.total_keys = len(self.api_keys)
        self.current_key_index = 0
        self.message_count = 0
        self.last_rotation_time = time.time()
        self.quota_exceeded_count = 0
    
    def get_current_key(self):
        return self.api_keys[self.current_key_index]
    
    def rotate_key(self):
        if self.total_keys <= 1:
            print("⚠️ Only 1 key available")
            return
        
        self.current_key_index = (self.current_key_index + 1) % self.total_keys
        self.message_count = 0
        self.quota_exceeded_count += 1
        print(f"🔄 Rotated to Key #{self.current_key_index + 1}")
    
    def increment_message_count(self):
        self.message_count += 1
        if self.message_count >= MAX_MESSAGES_PER_KEY:
            self.rotate_key()
    
    def get_stats(self):
        return {
            "current_key": self.current_key_index + 1,
            "total_keys": self.total_keys,
            "messages_used": self.message_count,
            "quota_exceeded_count": self.quota_exceeded_count,
            "uptime": time.time() - self.last_rotation_time
        }
