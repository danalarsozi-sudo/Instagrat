import time
import os
import random
from instagrapi import Client
import google.generativeai as genai

# --- KULLANICI BİLGİLERİ ---
INSTA_USER = "eminmfff"
INSTA_PASS = "emin9938618418404036"
GEMINI_API_KEY = "AIzaSyDvq9vQukaIMTNgQZtm_XQ9fro8vdf5ttE"

# --- AI KİŞİLİK TANIMI (SYSTEM PROMPT) ---
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

# Instagram Giriş ve Oturum Yönetimi
cl = Client()
SESSION_PATH = "session.json"

def login_insta():
    try:
        # Eğer daha önce kaydedilmiş bir oturum varsa onu yükle
        if os.path.exists(SESSION_PATH):
            print("Eski oturum dosyası bulundu, yükleniyor...")
            cl.load_settings(SESSION_PATH)
        
        # Giriş yapmadan önce rastgele bekle (İnsan taklidi)
        delay = random.randint(5, 15)
        print(f"Güvenlik için {delay} saniye bekleniyor...")
        time.sleep(delay)
        
        print(f"Instagram'a giriş deneniyor: {INSTA_USER}")
        cl.login(INSTA_USER, INSTA_PASS)
        
        # Giriş başarılıysa oturumu kaydet
        cl.dump_settings(SESSION_PATH)
        print("Giriş başarılı ve oturum kaydedildi!")
        
    except Exception as e:
        print(f"Giriş hatası oluştu: {e}")
        # Hata durumunda oturum dosyasını temizle
        if os.path.exists(SESSION_PATH):
            os.remove(SESSION_PATH)

def start_bot():
    login_insta()
    print("Emin aktif, mesajlar kontrol ediliyor...")
    
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
                    
                    print(f"Yeni mesaj alındı: {username} -> {last_msg}")

                    if thread_id not in chat_sessions:
                        chat_sessions[thread_id] = model.start_chat(history=[])

                    # Yapay zekadan Türkmence yanıt al
                    response = chat_sessions[thread_id].send_message(last_msg)
                    reply_text = response.text

                    # Yanıtı gönder
                    cl.direct_answer(thread_id, reply_text)
                    print(f"Yanıt gönderildi ({username}): {reply_text}")

            # Instagram'ın radarına girmemek için uzun bekleme süresi
            time.sleep(40)
            
        except Exception as e:
            print(f"Hata oluştu: {e}")
            # Eğer oturum düşerse tekrar giriş yapmayı dene
            if "login_required" in str(e).lower():
                print("Oturum düşmüş, tekrar giriş yapılıyor...")
                login_insta()
            time.sleep(60)

if __name__ == "__main__":
    start_bot()
