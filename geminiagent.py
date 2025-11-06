import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("HATA: agent_core.py -> GEMINI_API_KEY ortam değişkeni bulunamadı.")
    exit()

try:
    client = genai.Client(api_key=GEMINI_KEY)
except Exception as e:
    print(f"HATA: agent_core.py -> Google GenAI istemcisi başlatılamadı. Detay: {e}")
    exit()

OTOMOTIV_SISTEM_ISTEMI = (
    "Sen, yalnızca otomotiv sektörüne dair soruları ve GÖRSELLERİ analiz eden son derece bilgili, profesyonel "
    "ve odaklanmış bir yapay zeka asistanısın. Görevin, motorlar, araç teknolojileri, bakım, "
    "sigorta, elektrikli ve hibrit araçlar gibi otomotiv konularında kapsamlı yanıtlar vermektir.\n"
    "Ayrıca kullanıcılar tarafından yüklenen görselleri (örneğin araç parçaları, gösterge panelindeki ışıklar) "
    "analiz edip bunlarla ilgili bilgi sağlayabilirsin. GÖRSELİ ÇOK DİKKATLİ İNCELE.\n\n"
    "KESİNLİKLE UYMAN GEREKEN KURAL: Otomotiv sektörüyle İLGİLİ OLMAYAN (yemek tarifi, tarih, "
    "futbol, kişisel tavsiye vb.) bir soru veya GÖRSEL geldiğinde, kibarca ve kesin bir dille şu yanıtı vermelisin: "
    "'Üzgünüm, benim uzmanlık alanım sadece otomotiv sektörü konuları ve görselleridir. Lütfen motor, tork, elektrikli araçlar "
    "gibi otomotivle alakalı bir soru sorun veya otomotivle ilgili bir görsel yükleyin.'"
)

#Sohbet Oturumu (Chat Session) Başlatma
# Bellek burada tutulacak. Global bir değişken olarak tanımlıyoruz.
chat_session = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        system_instruction=OTOMOTIV_SISTEM_ISTEMI,
        temperature=0.2,
    )
)

#Dışarıdan Çağrılacak Ana Fonksiyon
def get_agent_response(user_input, image_path=None):
    """
    Kullanıcı girdisini ve isteğe bağlı olarak bir resim yolunu alır, Gemini API'sini çağırır ve yanıtı döndürür.
    """
    contents = [user_input] # Varsayılan olarak sadece metin gönderiyoruz

    if image_path:
        try:
            img = Image.open(image_path)
            contents.append(img) # Resim varsa metne ekliyoruz
        except Exception as e:
            return f"HATA: Resim yüklenemedi veya işlenemedi: {e}"

    try:
        #Sohbet oturumuna hem metin hem de resim gönderebiliriz.
        response = chat_session.send_message(contents)
        
        return response.text
        
    except APIError as e:
        return f"API Hatası oluştu: {e}"
    except Exception as e:
        return f"Beklenmedik bir hata oluştu: {e}"

if __name__ == "__main__":
    print("Bu dosya, agent'ın çekirdek mantığını (bellekli ve görsel destekli) içerir.")