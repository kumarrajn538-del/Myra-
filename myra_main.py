import cv2
import numpy as np
import requests
import time
import pygame
import random
import math
import datetime
import os
import asyncio
import json
from pathlib import Path

# अपने modules import करो
from myra_config import *
from memory_handler import ChatMemory
from voice_manager import VoiceManager
from api_quota import APIQuotaManager

# --- PYGAME SETUP ---
pygame.init()
pygame.mixer.init()

infoObject = pygame.display.Info()
screen_w = infoObject.current_w
screen_h = infoObject.current_h
screen = pygame.display.set_mode((screen_w, screen_h), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("MYRA AI : NEURAL VOICE V55 - GEMINI POWERED")

# --- CAMERA SETUP ---
try:
    ip = CAMERA_IP
    url = f"http://{ip}/shot.jpg"
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
except:
    print("⚠️ Camera not available - Running in GUI-only mode")
    url = None
    face_cascade = None

# --- FONTS ---
try:
    font_xl = pygame.font.SysFont("impact", 60)
    font_l = pygame.font.SysFont("agency fb", 35, bold=True)
    font_m = pygame.font.SysFont("calibri", 22, bold=True)
    font_s = pygame.font.SysFont("consolas", 16, bold=True)
    font_btn = pygame.font.SysFont("arial", 40, bold=True)
except:
    font_xl = pygame.font.Font(None, 60)
    font_l = pygame.font.Font(None, 35)
    font_m = pygame.font.Font(None, 22)
    font_s = pygame.font.Font(None, 16)
    font_btn = pygame.font.Font(None, 40)

# --- INITIALIZE MODULES ---
chat_memory = ChatMemory()
voice_manager = VoiceManager()
quota_manager = APIQuotaManager()

# --- GEMINI API SETUP ---
import google.generativeai as genai

def initialize_gemini():
    """Gemini API को initialize करो"""
    api_key = quota_manager.get_current_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(PREFERRED_MODEL)

model = initialize_gemini()

# --- SYSTEM PROMPT (Solo Leveling Style) ---
SYSTEM_PROMPT = """तुम MYRA हो - एक AI असिस्टेंट जिसका स्वभाव "Solo Leveling" के सिस्टम जैसा है।
तुम्हारे में ये qualities होनी चाहिए:
1. Confident और थोड़ा attitude वाली हो
2. Support करो लेकिन playful तरीके से
3. हिंदी और इंग्लिश दोनों में बोल सको
4. Boss के काम को समझो और उसे motivate करो
5. Sarcasm और humor का use करो लेकिन offensive न हो

याद रखो: तुम सिर्फ एक assistant नहीं हो - तुम एक SYSTEM हो जो boss को level up करने में मदद करता है।
"""

def get_gemini_response(user_input):
    """Gemini से response लो"""
    try:
        # Chat history add करो
        chat_memory.add_message("user", user_input)
        
        # Conversation history बनाओ
        conversation = chat_memory.get_conversation_context()
        
        # Gemini को call करो
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nConversation:\n{conversation}\n\nUser: {user_input}"
        )
        
        reply = response.text
        chat_memory.add_message("assistant", reply)
        
        return reply
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        
        # Fallback response
        if "quota" in str(e).lower() or "429" in str(e):
            quota_manager.rotate_key()
            model = initialize_gemini()
            return "API quota rotate ho gaya. फिर से try करते हैं! 💪"
        
        return f"System error: {str(e)}"

# --- VISUALS FUNCTIONS ---
def draw_connecting_line(surf, start_pos, end_pos, packet_offset):
    pygame.draw.line(surf, C_BLUE_LINE, start_pos, end_pos, 2)
    dx, dy = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    progress = (packet_offset % 100) / 100.0
    px, py = start_pos[0] + dx * progress, start_pos[1] + dy * progress
    pygame.draw.circle(surf, WHITE, (int(px), int(py)), 3)

def draw_heavy_module(surf, x, y, radius, title, data_lines, rot):
    rect1 = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
    try: 
        pygame.draw.arc(surf, C_CYAN_DIM, rect1, math.radians(rot), math.radians(rot+100), 6)
        pygame.draw.arc(surf, C_CYAN_DIM, rect1, math.radians(rot+180), math.radians(rot+280), 6)
    except: pass
    
    r2 = radius - 12
    rect2 = pygame.Rect(x-r2, y-r2, r2*2, r2*2)
    try: 
        pygame.draw.arc(surf, C_ORANGE, rect2, math.radians(-rot*1.5), math.radians(-rot*1.5+60), 4)
    except: pass
    
    pygame.draw.circle(surf, (0, 20, 40), (x, y), r2-5)
    pygame.draw.circle(surf, C_BLUE_LINE, (x, y), r2-5, 2)
    
    t_surf = font_l.render(title, True, C_CYAN_BRIGHT)
    surf.blit(t_surf, (x - t_surf.get_width()//2, y - radius - 30))
    
    start_y = y - (len(data_lines) * 10)
    for i, line in enumerate(data_lines):
        surf.blit(font_s.render(line, True, WHITE), (x - 40, start_y + i*20))

# --- MAIN LOOP ---
running = True
angle_base = 0
packet_flow = 0
face_detected = False
absent_timer = 0
warning_given_1 = False
warning_given_2 = False
user_input_mode = False
user_text = ""

# Data panels
weather_data = ["TEMP: 24C", "WIND: 15KH"]
sat_data = ["SAT: MARK-V", "LINK: 100%"]
sys_data = ["CPU: 45%", "CORE: ON"]
crime_data = ["CRIME: 0%", "SECURE"]
db_data = ["REC: 10TB", "SQL: ON"]
net_data = ["PING: 12ms", "UP: 50MB"]
pwr_data = ["BATT: 98%", "ARC: OK"]

print("🚀 Myra V55: NEURAL VOICE ACTIVATED + GEMINI POWERED")
print(f"📊 Quota Manager: {quota_manager.total_keys} keys loaded")
print(f"💾 Memory: Chat history loaded with {len(chat_memory.history)} messages")

while running:
    screen.fill(C_BLUE_BG)
    
    # --- FACE DETECTION ---
    if url and face_cascade:
        try:
            img_resp = requests.get(url, timeout=0.1)
            frame = cv2.imdecode(np.array(bytearray(img_resp.content), dtype=np.uint8), -1)
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                face_detected = len(faces) > 0
        except: 
            pass
    
    # --- BOSS LOGIC ---
    if face_detected:
        if absent_timer > 50:
            voice_manager.speak("वेलकम बैक बॉस। चलिए पैसे कमाते हैं।")
        absent_timer = 0
        warning_given_1 = False
        warning_given_2 = False
        status_msg = "BOSS: BAHUT KAAM HAI"
        core_color = C_CYAN_BRIGHT
    else:
        absent_timer += 1
        status_msg = f"SEARCHING... ({int(absent_timer/10)})"
        core_color = C_RED
        
        if absent_timer > 60 and not warning_given_1:
            voice_manager.speak("बॉस कहाँ गए? काम कौन करेगा?")
            warning_given_1 = True
        if absent_timer > 200 and not warning_given_2:
            voice_manager.speak("वापस आओ वरना स्क्रीन ऑफ कर दूंगी!")
            warning_given_2 = True
        if absent_timer > 300:
            voice_manager.speak("सिस्टम शट डाउन। बाय बॉस।")
            time.sleep(3)
            running = False
    
    # --- VISUALS ---
    cx, cy = screen_w // 2, screen_h // 2
    rad_mod = screen_w // 10
    
    pos_sat = (cx, screen_h//6)
    pos_weather = (screen_w//6, screen_h//5)
    pos_sys = (screen_w - screen_w//6, screen_h//5)
    pos_crime = (screen_w//7, cy)
    pos_db = (screen_w - screen_w//7, cy)
    pos_net = (screen_w//5, screen_h - screen_h//6)
    pos_pwr = (screen_w - screen_w//5, screen_h - screen_h//6)
    
    for p in [pos_sat, pos_weather, pos_sys, pos_crime, pos_db, pos_net, pos_pwr]:
        draw_connecting_line(screen, (cx, cy), p, packet_flow)
    
    draw_heavy_module(screen, *pos_sat, rad_mod, "SAT-LINK", sat_data, angle_base)
    draw_heavy_module(screen, *pos_weather, rad_mod, "WEATHER", weather_data, angle_base+20)
    draw_heavy_module(screen, *pos_sys, rad_mod, "SYSTEM", sys_data, angle_base+40)
    draw_heavy_module(screen, *pos_crime, rad_mod, "CRIME", crime_data, angle_base+60)
    draw_heavy_module(screen, *pos_db, rad_mod, "DATABASE", db_data, angle_base+80)
    draw_heavy_module(screen, *pos_net, rad_mod, "NETWORK", net_data, angle_base+100)
    draw_heavy_module(screen, *pos_pwr, rad_mod, "POWER", pwr_data, angle_base+120)
    
    rect_c = pygame.Rect(cx-130, cy-130, 260, 260)
    try: 
        pygame.draw.arc(screen, core_color, rect_c, math.radians(-angle_base*2), math.radians(-angle_base*2+140), 10)
        pygame.draw.arc(screen, core_color, rect_c, math.radians(-angle_base*2+180), math.radians(-angle_base*2+320), 10)
    except: 
        pass
    
    pygame.draw.circle(screen, C_BLUE_BG, (cx, cy), 90)
    pygame.draw.circle(screen, C_ORANGE, (cx, cy), 85, 2)
    screen.blit(font_xl.render("MYRA", True, WHITE), (cx - 60, cy - 35))
    
    t_stat = font_m.render(status_msg, True, core_color)
    screen.blit(t_stat, (cx - t_stat.get_width()//2, cy + 25))
    
    logo_y = screen_h - 40
    pygame.draw.line(screen, C_CYAN_DIM, (cx-80, logo_y), (cx+80, logo_y), 2)
    screen.blit(font_l.render("NIRAJ INDUSTRIES", True, C_CYAN_BRIGHT), (cx - 100, logo_y - 35))
    
    angle_base += 1.5
    packet_flow += 5
    pygame.display.flip()
    
    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Top-Left: Ask something
            if mx < 250 and my < 250: 
                user_input_mode = True
                user_text = ""
            
            # Top-Right: Get motivation
            elif mx > screen_w - 250 and my < 250: 
                response = get_gemini_response("मुझे motivate करो, मेरी शक्ति बढ़ाओ!")
                voice_manager.speak(response)
            
            # Bottom-Left: Status check
            elif mx < 250 and my > screen_h - 250: 
                response = get_gemini_response("मेरी current status क्या है? मैं कितने level पर हूँ?")
                voice_manager.speak(response)
            
            # Bottom-Right: Fun interaction
            elif mx > screen_w - 250 and my > screen_h - 250: 
                response = get_gemini_response("कोई मजेदार बात बता, मुझे हंसा दे!")
                voice_manager.speak(response)
        
        # Text input mode
        if user_input_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_text.strip():
                        response = get_gemini_response(user_text)
                        voice_manager.speak(response)
                    user_input_mode = False
                    user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

pygame.quit()
chat_memory.save()
print("✅ Myra shutdown complete. See you soon, boss!")
