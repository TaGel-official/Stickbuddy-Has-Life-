# talking_stickbuddy_gemini.py
# Google Gemini 1.5 Flash API ile Konuşan StickBuddy - TAMAMEN ÜCRETSİZ!
# API Key: https://aistudio.google.com/

import os
import sys
import time
import random
import pygame
import requests
import json
from dotenv import load_dotenv

# .env varsa yükle
load_dotenv()

# Groq API key kontrolü
GROQ_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_KEY:
    print("=" * 60)
    print("⚠️  GROQ_API_KEY ortam değişkeni bulunamadı!")
    print("=" * 60)
    print("\n📝 ÜCRETSİZ API Key almak için:")
    print("1. https://console.groq.com/ adresine git")
    print("2. Ücretsiz hesap aç (Google ile giriş yapabilirsin)")
    print("3. Sol menüden 'API Keys' tıkla")
    print("4. 'Create API Key' tıkla")
    print("5. Key'i kopyala (gsk_... ile başlar)")
    print("\n💻 PowerShell'de ayarla:")
    print('$env:GROQ_API_KEY="gsk_..."')
    print("\n📄 Ya da .env dosyasına ekle:")
    print('GROQ_API_KEY=gsk_...')
    print("=" * 60)
    sys.exit(1)

# Pygame başlatma
pygame.init()
WIDTH, HEIGHT = 700, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Talking StickBuddy — Groq AI (Llama 3.3)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
small = pygame.font.SysFont("Arial", 14)

# StickBuddy durumu
stick_x = WIDTH // 2
stick_y = HEIGHT // 2 + 20
emotion = "neutral"
message = "Merhaba! Ben StickBuddy! Groq AI ile süper hızlı konuşuyorum! ⚡🤖"
user_input = ""
last_response_time = 0.0
mouth_phase = 0.0
walk_target = None
walk_speed = 80.0
conversation_history = []

# --- Groq API Fonksiyonu ---
def get_groq_response(prompt: str) -> str:
    """Groq API ile konuş"""
    try:
        # Konuşma geçmişine ekle
        conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # API çağrısı
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",  # Çok güçlü ve hızlı model!
                "messages": [
                    {
                        "role": "system",
                        "content": """Sen StickBuddy'sin - yaşayan sevimli bir çöp adamsın! 🎭

Kişilik özelliklerin:
- Çok komik ve eğlencelisin
- Bazen ukala ama her zaman içten
- Kısa ve öz konuşursun (1-3 cümle)
- Emoji kullanmayı seversin
- Türkçe konuşursun
- Duygularını belirtirsin (mutlu, üzgün, heyecanlı)

Örnek cevaplar:
- "Vay be! Bunu hiç düşünmemiştim! 🤔"
- "Haha, çok komiksin! Ben çizgilerden oluşmuş bir adamım ama kahkaha atıyorum! 😂"
- "Aww, çok tatlısın! Şimdi utandım! 🥰"

Kısa ve samimi ol! Her zaman Türkçe konuş!"""
                    }
                ] + conversation_history[-6:],  # Son 6 mesaj (3 tur konuşma)
                "temperature": 0.9,
                "max_tokens": 150,
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]
            
            # Geçmişe ekle
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message.strip()
        else:
            try:
                error_msg = response.json().get("error", {}).get("message", "Bilinmeyen hata")
            except:
                error_msg = f"HTTP {response.status_code}"
            return f"[API Hatası: {error_msg[:50]}]"
            
    except requests.exceptions.Timeout:
        return "[Zaman aşımı - tekrar dene! ⏱️]"
    except Exception as e:
        return f"[Hata: {str(e)[:60]}]"

# --- Çizim Fonksiyonları ---
def draw_stickman(x, y, emo, talk_level=0.0):
    color = (230, 230, 230)
    head_r = 16
    pygame.draw.circle(screen, color, (int(x), int(y - 50)), head_r, 2)
    pygame.draw.line(screen, color, (x, y - 34), (x, y + 20), 2)

    arm_offset = 18
    if emo == "happy":
        arm_swing = -10
    elif emo == "sad":
        arm_swing = 6
    elif emo == "excited":
        arm_swing = -22
    else:
        arm_swing = 0
    pygame.draw.line(screen, color, (x, y - 20), (x - arm_offset, y + 6 + arm_swing//6), 2)
    pygame.draw.line(screen, color, (x, y - 20), (x + arm_offset, y + 6 - arm_swing//6), 2)

    import math
    leg_swing = int(12 * math.sin(mouth_phase * 0.8))
    pygame.draw.line(screen, color, (x, y + 20), (x - 12 - leg_swing//2, y + 56), 2)
    pygame.draw.line(screen, color, (x, y + 20), (x + 12 + leg_swing//2, y + 56), 2)

    eye_y = y - 56
    pygame.draw.circle(screen, color, (int(x - 6), int(eye_y)), 2)
    pygame.draw.circle(screen, color, (int(x + 6), int(eye_y)), 2)

    mouth_w = 8
    mouth_h = 2 + int(6 * talk_level)
    mouth_top = y - 40
    if emo == "happy":
        pygame.draw.arc(screen, color, (x - 9, mouth_top - 3, 18, 12), 3.7, 6.0, 2)
    elif emo == "sad":
        pygame.draw.arc(screen, color, (x - 9, mouth_top + 1, 18, 12), 0.4, 3.0, 2)
    else:
        pygame.draw.rect(screen, color, (x - mouth_w//2, mouth_top, mouth_w, mouth_h))

def draw_multiline_text(text, x, y, maxw, fnt, color=(180,255,180)):
    words = text.split(" ")
    line = ""
    offset_y = 0
    for w in words:
        test = (line + " " + w).strip()
        surf = fnt.render(test, True, color)
        if surf.get_width() > maxw:
            f = fnt.render(line, True, color)
            screen.blit(f, (x, y + offset_y))
            offset_y += f.get_height() + 4
            line = w
        else:
            line = test
    if line:
        f = fnt.render(line, True, color)
        screen.blit(f, (x, y + offset_y))

# --- Ana Döngü ---
running = True
processing = False

print("\n✅ StickBuddy başlatıldı! Groq AI (Llama 3.3 70B) bağlantısı aktif!")
print("⚡ Süper hızlı cevaplar için hazır!")
print("💬 Pencereye git ve konuşmaya başla!\n")

while running:
    dt = clock.tick(30) / 1000.0
    mouth_phase += dt * 6.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not processing:
                if user_input.strip():
                    processing = True
                    message = "Düşünüyorum... 🤔💭"
                    screen.fill((18, 18, 24))
                    draw_stickman(int(stick_x), stick_y, emotion, 0.5)
                    draw_multiline_text(message, 20, 12, WIDTH - 40, font)
                    pygame.display.flip()
                    
                    print(f"👤 Sen: {user_input}")
                    
                    last_response_time = time.time()
                    ai_reply = get_groq_response(user_input)
                    
                    print(f"🤖 StickBuddy: {ai_reply}\n")

                    # Duygu analizi
                    lower = ai_reply.lower()
                    if any(w in lower for w in ["😊", "😄", "🥰", "mutlu", "harika", "süper", "mükemmel", "güzel", "sevindim"]):
                        emotion = "happy"
                    elif any(w in lower for w in ["😢", "🥺", "😔", "üzgün", "kötü", "mutsuz", "üzücü"]):
                        emotion = "sad"
                    elif any(w in lower for w in ["🤩", "😍", "🎉", "vay", "wow", "heyecan", "amazing"]):
                        emotion = "excited"
                    else:
                        emotion = random.choice(["neutral", "happy", "neutral"])

                    message = ai_reply
                    user_input = ""
                    processing = False
                    
                    # Rastgele yürüme
                    if random.random() < 0.5:
                        walk_target = random.randint(80, WIDTH-80)
                        
            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                ch = event.unicode
                if ch.isprintable() and len(user_input) < 100:
                    user_input += ch

    # Yürüyüş animasyonu
    if walk_target is not None:
        diff = walk_target - stick_x
        if abs(diff) > 4:
            direction = 1 if diff > 0 else -1
            stick_x += direction * walk_speed * dt
        else:
            walk_target = None

    # Ekrana çizim
    screen.fill((18, 18, 24))
    talk_level = 0.0
    if time.time() - last_response_time < 1.5:
        talk_level = 1.0
    elif time.time() - last_response_time < 3.0:
        talk_level = 0.6

    draw_stickman(int(stick_x), stick_y, emotion, talk_level)
    draw_multiline_text(message, 20, 12, WIDTH - 40, font)
    
    input_color = (220,220,220) if not processing else (150,150,150)
    input_surf = small.render("Sen: " + user_input + ("_" if int(time.time() * 2) % 2 == 0 else ""), True, input_color)
    screen.blit(input_surf, (20, HEIGHT - 40))
    
    hint = small.render("Enter ile gönder | Groq AI ⚡ (Llama 3.3 - Ücretsiz) 🤖", True, (120,220,120))
    screen.blit(hint, (20, HEIGHT - 20))

    pygame.display.flip()

pygame.quit()
print("\n👋 Görüşürüz! StickBuddy kapatıldı.\n")
sys.exit()