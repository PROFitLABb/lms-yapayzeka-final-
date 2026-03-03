import os
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from groq import Groq
except ImportError:
    Groq = None

# .env dosyasını oku (Dosya ana dizinde olduğu için basit yol kullanıyoruz)
load_dotenv()

# --- Mühendislik Kuralı: System Prompt ---
SYSTEM_PROMPT = """
Sen bir eğitim platformunda çalışan profesyonel bir yapay zeka asistanısın.
Görevin, öğrenci geri bildirimlerini derinlemesine analiz etmek.
Lütfen yanıtını şu yapıda ver:
1. Kısa Özet: (Metnin ana fikri)
2. Duygu Durumu: (Pozitif, Negatif veya Nötr)
3. Eğitmen İçin Öneri: (Eğitim kalitesini artıracak aksiyon adımı)
"""


def analyze_text(text, provider="gemini"):
    """
    Ana servis fonksiyonu. İstediğin sağlayıcıyı (Gemini veya Groq) seçebilirsin.
    """
    if not text:
        return {"error": "Analiz edilecek metin boş olamaz."}

    if provider == "gemini":
        return _analyze_with_gemini(text)
    elif provider == "groq":
        return _analyze_with_groq(text)
    else:
        return {"error": "Geçersiz sağlayıcı seçimi."}


# --- Google Gemini Motoru ---
def _analyze_with_gemini(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Gemini API Key bulunamadı!", "api_configured": False}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # System Prompt ve Kullanıcı Metni birleştiriliyor
        full_prompt = f"{SYSTEM_PROMPT}\\n\\nAnaliz edilecek öğrenci metni: {text}"
        response = model.generate_content(full_prompt)

        return {
            "source": "Google Gemini",
            "analysis": response.text,
            "api_configured": True,
        }
    except Exception as e:
        return {"error": f"Gemini Hatası: {str(e)}", "api_configured": False}


# --- Groq Cloud Motoru ---
def _analyze_with_groq(text):
    if Groq is None:
        return {"error": "Groq paketi yüklü değil.", "api_configured": False}

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "Groq API Key bulunamadı!", "api_configured": False}

    try:
        client = Groq(api_key=api_key)
        full_prompt = f"{SYSTEM_PROMPT}\\n\\nAnaliz edilecek öğrenci metni: {text}"

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": full_prompt}],
        )
        return {
            "source": "Groq (Llama 3)",
            "analysis": completion.choices[0].message.content,
            "api_configured": True,
        }
    except Exception as e:
        return {"error": f"Groq Hatası: {str(e)}", "api_configured": False}

 

