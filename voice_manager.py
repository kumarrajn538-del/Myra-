import asyncio
import edge_tts
import pygame
import os
from myra_config import VOICE_LANG, VOICE_OUTPUT_FILE

class VoiceManager:
    def __init__(self):
        self.current_voice = VOICE_LANG
        self.is_playing = False
    
    async def generate_speech(self, text):
        try:
            communicate = edge_tts.Communicate(text, self.current_voice)
            await communicate.save(VOICE_OUTPUT_FILE)
            return True
        except Exception as e:
            print(f"❌ Voice Error: {e}")
            return False
    
    def speak(self, text):
        try:
            while pygame.mixer.music.get_busy():
                pass
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.generate_speech(text))
            loop.close()
            
            if success and os.path.exists(VOICE_OUTPUT_FILE):
                pygame.mixer.music.load(VOICE_OUTPUT_FILE)
                pygame.mixer.music.play()
                self.is_playing = True
                
                while pygame.mixer.music.get_busy():
                    pass
                
                self.is_playing = False
        except Exception as e:
            print(f"❌ Speak Error: {e}")
    
    def set_voice(self, voice_name):
        self.current_voice = voice_name
        print(f"🎤 Voice: {voice_name}")
    
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
