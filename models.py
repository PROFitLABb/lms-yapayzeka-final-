from typing import Optional

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    """
    Kullanıcıdan gelen analiz isteğini temsil eden model.
    """

    text: str = Field(..., min_length=5, description="Analiz edilecek öğrenci metni")
    provider: str = Field(
        default="gemini",
        description="Kullanılacak AI sağlayıcısı (gemini veya groq)",
    )


class AnalysisResult(BaseModel):
    """
    AI servisinden dönen ve veritabanına kaydedilecek sonuç modeli.
    """

    source: str
    analysis: str
    status: bool = True
    error_message: Optional[str] = None

