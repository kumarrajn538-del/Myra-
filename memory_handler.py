import json
import os
from datetime import datetime
from myra_config import CHAT_HISTORY_FILE, MAX_HISTORY_SIZE

class ChatMemory:
    def __init__(self):
        self.history = []
        self.load()
    
    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(message)
        
        if len(self.history) > MAX_HISTORY_SIZE:
            self.history = self.history[-MAX_HISTORY_SIZE:]
    
    def get_conversation_context(self):
        context = ""
        for msg in self.history[-10:]:
            role = msg["role"].upper()
            content = msg["content"]
            context += f"{role}: {content}\n"
        return context
    
    def load(self):
        try:
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                print(f"✅ Loaded {len(self.history)} messages")
        except Exception as e:
            print(f"⚠️ Could not load history: {e}")
            self.history = []
    
    def save(self):
        try:
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {len(self.history)} messages")
        except Exception as e:
            print(f"❌ Could not save: {e}")
    
    def clear(self):
        self.history = []
        self.save()
    
    def get_stats(self):
        user_msgs = len([m for m in self.history if m["role"] == "user"])
        assistant_msgs = len([m for m in self.history if m["role"] == "assistant"])
        return {
            "total_messages": len(self.history),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs
        }
