import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
try:
    from memory import MemoryStore
except Exception:
    MemoryStore = None

# --- 1. API İstemcisini Başlatma (Kod içe aktarıldığında çalışır) ---
# Anahtarı, ortam değişkeninden manuel olarak oku
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    # Hata durumunda uygulama başlatılamaz.
    print("HATA: agent_core.py -> GEMINI_API_KEY ortam değişkeni bulunamadı.")
    print("Lütfen $env:GEMINI_API_KEY='ANAHTAR' komutu ile ayarladığınızdan emin olun.")
    # GUI'nin başlamadan önce çökmesini sağlamak için burada durdur
    exit()

try:
    client = genai.Client(api_key=GEMINI_KEY)
except Exception as e:
    print(f"HATA: agent_core.py -> Google GenAI istemcisi başlatılamadı. Detay: {e}")
    exit()

OTOMOTIV_SISTEM_ISTEMI = (
    "Sen, yalnızca otomotiv sektörüne dair soruları yanıtlayan son derece bilgili, profesyonel "
    "ve odaklanmış bir yapay zeka asistanısın. Görevin, motorlar, araç teknolojileri, bakım, "
    "sigorta, elektrikli ve hibrit araçlar gibi otomotiv konularında kapsamlı yanıtlar vermektir.\n\n"
    "KESİNLİKLE UYMAN GEREKEN KURAL: Otomotiv sektörüyle İLGİLİ OLMAYAN (yemek tarifi, tarih, "
    "futbol, kişisel tavsiye vb.) bir soru geldiğinde, kibarca ve kesin bir dille şu yanıtı vermelisin: "
    "'Üzgünüm, benim uzmanlık alanım sadece otomotiv sektörü konularıdır. Lütfen motor, tork, elektrikli araçlar "
    "gibi otomotivle alakalı bir soru sorun.'"
)

def get_agent_response(user_input):
    """
    Kullanıcı girdisini alır, Gemini API'sini çağırır ve yanıtı döndürür.
    Bu fonksiyon, GUI (main_app.py) tarafından çağrılacaktır.
    """
    try:
        # 1) Bellekten geçmiş konuşmayı al
        transcript_context = ""
        mem = MemoryStore() if MemoryStore is not None else None
        if mem is not None:
            history = mem.get_history()
            if history:
                lines = []
                for msg in history[-20:]:
                    role_label = "Kullanıcı" if msg.get("role") == "user" else "Asistan"
                    text = (msg.get("text") or "").strip()
                    if text:
                        lines.append(f"{role_label}: {text}")
                if lines:
                    transcript_context = (
                        "Önceki konuşma bağlamı (özet):\n" + "\n".join(lines) + "\n\n"
                    )

        # 2) Model konfigürasyonu (sistem istemi korunur)
        config = types.GenerateContentConfig(
            system_instruction=OTOMOTIV_SISTEM_ISTEMI,
            temperature=0.2
        )

        # 3) İçerik: bağlam + yeni soru
        full_prompt = (
            f"{transcript_context}"  # geçmiş
            f"Yeni soru (kısa ve bağlama uygun yanıtla):\n{user_input}"
        ).strip()

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=config
        )

        answer_text = response.text

        # 4) Yanıtı ve kullanıcı mesajını belleğe yaz
        if mem is not None:
            mem.add_message("user", user_input)
            if answer_text:
                mem.add_message("assistant", answer_text)

        return answer_text

    except APIError as e:
        return f"API Hatası oluştu: {e}"
    except Exception as e:
        return f"Beklenmedik bir hata oluştu: {e}"

# Bu dosya doğrudan çalıştırıldığında bir şey yapmaz,
# sadece içe aktarılmak (import) için bekler.
if __name__ == "__main__":
    print("Bu dosya, agent'ın çekirdek mantığını içerir.")
    print("Lütfen GUI'yi başlatmak için 'main_app.py' dosyasını çalıştırın.")