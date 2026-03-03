from fastapi import FastAPI, HTTPException

from ai_service import analyze_text
from models import TextRequest

app = FastAPI(title="LMS AI Service API")


@app.post("/analyze-text")
def analyze_text_endpoint(data: TextRequest):
    """
    LMS'den gelen metni alır, seçilen sağlayıcı (Gemini/Groq) ile
    analiz eder ve yapılandırılmış sonuç döner.
    """
    try:
        # ai_service.py içindeki mantığı çağırıyoruz
        result = analyze_text(text=data.text, provider=data.provider)

        # Eğer servisten bir hata döndüyse (API key eksikliği vb.)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "status": "success",
            "provider": data.provider,
            "data": result,
        }

    except HTTPException:
        # Yukarıda fırlattığımız HTTPException'ı tekrar raise edelim
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")


@app.get("/")
def read_root():
    return {
        "message": "LMS AI Backend Çalışıyor. Dökümantasyon için /docs adresine gidin."
    }


