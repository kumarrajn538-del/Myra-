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
        
        print(f"📊 APIQuotaManager initialized with {self.total_keys} keys")
    
    def get_current_key(self):
        """Current API key return करो"""
        return self.api_keys[self.current_key_index]
    
    def rotate_key(self):
        """अगली key पर switch करो"""
        if self.total_keys <= 1:
            print("⚠️ Only one API key available")
            return
        
        self.current_key_index = (self.current_key_index + 1) % self.total_keys
        self.message_count = 0
        self.quota_exceeded_count += 1
        
        print(f"🔄 Rotated to Key #{self.current_key_index + 1}")
        print(f"   (Total rotations: {self.quota_exceeded_count})")
    
    def increment_message_count(self):
        """Message count बढ़ाओ"""
        self.message_count += 1
        
        if self.message_count >= MAX_MESSAGES_PER_KEY:
            print(f"⚠️ Message limit reached ({self.message_count}/{MAX_MESSAGES_PER_KEY})")
            self.rotate_key()
    
    def get_stats(self):
        """Quota statistics"""
        return {
            "current_key": self.current_key_index + 1,
            "total_keys": self.total_keys,
            "messages_used": self.message_count,
            "quota_exceeded_count": self.quota_exceeded_count,
            "uptime_seconds": time.time() - self.last_rotation_time
        }
