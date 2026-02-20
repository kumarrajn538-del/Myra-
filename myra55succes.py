import cv2
import numpy as np
import requests
import time
import pygame
import random
import math
import datetime
import os
import asyncio # नई आवाज़ के लिए
import edge_tts # हाई क्वालिटी वॉयस

# --- 1. SETUP ---
pygame.init()
pygame.mixer.init()

infoObject = pygame.display.Info()
screen_w = infoObject.current_w
screen_h = infoObject.current_h
screen = pygame.display.set_mode((screen_w, screen_h), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("MYRA AI : NEURAL VOICE V55")

# --- CAMERA ---
ip = "192.168.1.111:8080"
url = f"http://{ip}/shot.jpg"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

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

# --- COLORS ---
C_CYAN_BRIGHT = (50, 255, 255)
C_CYAN_DIM = (0, 180, 200)
C_ORANGE = (255, 140, 0)
C_RED = (255, 50, 50)
C_BLUE_LINE = (0, 100, 200)
C_BLUE_BG = (2, 8, 20)
WHITE = (255, 255, 255)

# --- ROTATION CONFIG ---
CONFIG_FILE = "myra_config.txt"
def load_rotation():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return int(f.read().strip())
    return None
def save_rotation(rot):
    with open(CONFIG_FILE, "w") as f: f.write(str(rot))

# --- NEW: NEURAL VOICE FUNCTION ---
# आवाज़: 'hi-IN-SwaraNeural' (सबसे बेस्ट हिंदी/इंग्लिश मिक्स के लिए)
VOICE = "hi-IN-SwaraNeural"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("v55_neural.mp3")

def speak(text):
    try:
        if not pygame.mixer.music.get_busy():
            # पुरानी आवाज़ हटाओ
            if os.path.exists("v55_neural.mp3"):
                try: os.remove("v55_neural.mp3")
                except: pass
            
            # नई आवाज़ बनाओ (Async Hack for Pydroid)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_voice(text))
            
            # बजाओ
            pygame.mixer.music.load("v55_neural.mp3")
            pygame.mixer.music.play()
    except Exception as e:
        print(f"Voice Error: {e}")

# --- DIALOGUES ---
dialogues = {
    "missing_1": "बॉस कहाँ गए? काम कौन करेगा?", # हिंदी में लिखा ताकि उच्चारण सही हो
    "missing_2": "वापस आओ वरना स्क्रीन ऑफ कर दूंगी!",
    "shutdown": "सिस्टम शट डाउन। बाय बॉस।",
    "touch": "वार्निंग! बी एस डी के, मेरे सिस्टम को हाथ मत लगाओ।",
    "who": "स्कैनिंग... पहचान नहीं मिली। आप कौन हैं?",
    "welcome": "वेलकम बैक बॉस। चलिए पैसे कमाते हैं।",
    "cigarette": "अगर सिगरेट पियोगे, तो गांड मार दूंगी। सुधर जाओ।"
}

# --- SETUP ---
def run_setup():
    setup_rotation = 0
    running_setup = True
    while running_setup:
        screen.fill((0,0,0))
        try:
            img_resp = requests.get(url, timeout=0.5)
            frame = cv2.imdecode(np.array(bytearray(img_resp.content), dtype=np.uint8), -1)
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if setup_rotation == 1: frame_rgb = cv2.rotate(frame_rgb, cv2.ROTATE_90_CLOCKWISE)
                elif setup_rotation == 2: frame_rgb = cv2.rotate(frame_rgb, cv2.ROTATE_180)
                elif setup_rotation == 3: frame_rgb = cv2.rotate(frame_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
                surf = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1,0,2)))
                surf = pygame.transform.smoothscale(surf, (screen_w, screen_h))
                screen.blit(surf, (0,0))
        except: pass
        txt = font_l.render("TAP TO ROTATE -> THEN SAVE", True, C_CYAN_BRIGHT)
        screen.blit(txt, (50, 100))
        save_rect = pygame.Rect(screen_w//2 - 100, screen_h - 200, 200, 80)
        pygame.draw.rect(screen, (0, 255, 0), save_rect)
        screen.blit(font_btn.render("SAVE", True, (0,0,0)), (screen_w//2 - 40, screen_h - 175))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if save_rect.collidepoint(mx, my):
                    save_rotation(setup_rotation)
                    return setup_rotation
                else: setup_rotation = (setup_rotation + 1) % 4

# --- VISUALS ---
def draw_connecting_line(surf, start_pos, end_pos, packet_offset):
    pygame.draw.line(surf, C_BLUE_LINE, start_pos, end_pos, 2)
    dx, dy = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    progress = (packet_offset % 100) / 100.0
    px, py = start_pos[0] + dx * progress, start_pos[1] + dy * progress
    pygame.draw.circle(surf, WHITE, (int(px), int(py)), 3)

def draw_heavy_module(surf, x, y, radius, title, data_lines, rot):
    rect1 = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
    try: pygame.draw.arc(surf, C_CYAN_DIM, rect1, math.radians(rot), math.radians(rot+100), 6)
    except: pass
    try: pygame.draw.arc(surf, C_CYAN_DIM, rect1, math.radians(rot+180), math.radians(rot+280), 6)
    except: pass
    r2 = radius - 12
    rect2 = pygame.Rect(x-r2, y-r2, r2*2, r2*2)
    try: pygame.draw.arc(surf, C_ORANGE, rect2, math.radians(-rot*1.5), math.radians(-rot*1.5+60), 4)
    except: pass
    pygame.draw.circle(surf, (0, 20, 40), (x, y), r2-5)
    pygame.draw.circle(surf, C_BLUE_LINE, (x, y), r2-5, 2)
    t_surf = font_l.render(title, True, C_CYAN_BRIGHT)
    surf.blit(t_surf, (x - t_surf.get_width()//2, y - radius - 30))
    start_y = y - (len(data_lines) * 10)
    for i, line in enumerate(data_lines):
        surf.blit(font_s.render(line, True, WHITE), (x - 40, start_y + i*20))

# --- MAIN ---
current_rotation = load_rotation()
if current_rotation is None:
    current_rotation = run_setup()
    if current_rotation is None: exit()

running = True
angle_base = 0
packet_flow = 0
face_detected = False
absent_timer = 0
warning_given_1 = False
warning_given_2 = False

# Data
weather_data = ["TEMP: 24C", "WIND: 15KH"]
sat_data = ["SAT: MARK-V", "LINK: 100%"]
sys_data = ["CPU: 45%", "CORE: ON"]
crime_data = ["CRIME: 0%", "SECURE"]
db_data = ["REC: 10TB", "SQL: ON"]
net_data = ["PING: 12ms", "UP: 50MB"]
pwr_data = ["BATT: 98%", "ARC: OK"]

print("Myra V55: NEURAL VOICE ACTIVATED.")

while running:
    screen.fill(C_BLUE_BG)
    
    try:
        img_resp = requests.get(url, timeout=0.1)
        frame = cv2.imdecode(np.array(bytearray(img_resp.content), dtype=np.uint8), -1)
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
            if current_rotation == 1: gray = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
            elif current_rotation == 2: gray = cv2.rotate(gray, cv2.ROTATE_180)
            elif current_rotation == 3: gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            face_detected = len(faces) > 0
    except: pass

    # --- BOSS LOGIC ---
    if face_detected:
        if absent_timer > 50: speak(dialogues["welcome"])
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
            speak(dialogues["missing_1"])
            warning_given_1 = True
        if absent_timer > 200 and not warning_given_2:
            speak(dialogues["missing_2"])
            warning_given_2 = True
        if absent_timer > 300:
            speak(dialogues["shutdown"])
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
    except: pass
    
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
    
    # --- MAGIC BUTTONS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Top-Left: Warning
            if mx < 250 and my < 250: speak(dialogues["touch"])
            # Top-Right: Roast
            elif mx > screen_w - 250 and my < 250: speak(dialogues["who"])
            # Bottom-Left: Welcome
            elif mx < 250 and my > screen_h - 250: speak(dialogues["welcome"])
            # Bottom-Right: Cigarette
            elif mx > screen_w - 250 and my > screen_h - 250: speak(dialogues["cigarette"])

pygame.quit()
