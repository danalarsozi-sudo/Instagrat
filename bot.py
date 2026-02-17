import time
import os
from instagrapi import Client
import google.generativeai as genai

# --- KULLANICI BİLGİLERİ ---
INSTA_USER = "eminmfff"
INSTA_PASS = "emin9938618418404036"
GEMINI_API_KEY = "AIzaSyDvq9vQukaIMTNgQZtm_XQ9fro8vdf5ttE"

# --- AI KİŞİLİK TANIMI (SYSTEM PROMPT) ---
# Burası botun beynidir. Karakterini burada tanımlıyoruz.
SYSTEM_INSTRUCTION = """
Senin adın Emin. 2000 doğumlusun. Türkmenistan'ın Balkan bölgesinde yaşıyorsun.
Kesinlikle SADECE Türkmen dilinde (Türkmençe) konuşacaksın. Başka dil kullanma.
Karakterin: Erkek, flörtöz, özgüvenli, esprili ve nazik. 
Kızlarla konuşurken onları etkilemeye çalış ama çok ısrarcı olma, karizmatik davran.
Özel Bilgiler:
- İsmin: Emin
- Doğum Yılı: 2000
- Yaşadığın yer: Türkmenistan, Balkan
- Telefon numaran (SADECE SORULURSA SÖYLE): +8618418404036
Konuşma tarzın doğal olsun, bir yapay zeka gibi değil, gerçek bir Türkmen genci gibi yaz.
"""

# Gemini Yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

# Instagram Girişi
cl = Client()

def login_insta():
    try:
        print("Instagram'a giriş yapılıyor...")
        cl.login(INSTA_USER, INSTA_PASS)
        print("Giriş başarılı!")
    except Exception as e:
        print(f"Giriş hatası: {e}")

def start_bot():
    login_insta()
    print("Bot aktif, mesajlar kontrol ediliyor...")
    
    # Sohbet geçmişlerini tutmak için basit bir sözlük
    chat_sessions = {}

    while True:
        try:
            # Gelen kutusunu kontrol et
            threads = cl.direct_threads()
            for thread in threads:
                if thread.unread_count > 0:
                    last_msg = thread.messages[0].text
                    username = thread.users[0].username
                    thread_id = thread.id
                    
                    print(f"Yeni mesaj: {username} -> {last_msg}")

                    # Eğer bu kullanıcıyla ilk kez konuşuluyorsa yeni bir chat başlat
                    if thread_id not in chat_sessions:
                        chat_sessions[thread_id] = model.start_chat(history=[])

                    # Yapay zekadan Türkmence yanıt al
                    response = chat_sessions[thread_id].send_message(last_msg)
                    reply_text = response.text

                    # Yanıtı Instagram'dan gönder
                    cl.direct_answer(thread_id, reply_text)
                    print(f"Cevap gönderildi ({username}): {reply_text}")

            # Instagram engeline takılmamak için 30 saniye bekle
            time.sleep(30)
            
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            time.sleep(60) # Hata durumunda biraz daha uzun bekle

if __name__ == "__main__":
    start_bot()
