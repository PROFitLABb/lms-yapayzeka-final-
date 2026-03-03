import os
import time

import streamlit as st
from dotenv import load_dotenv

from ai_service import analyze_text
from database import get_history, init_db, save_analysis
from models import TextRequest


# .env dosyasını yüklemeyi dene (Lokaldeysen çalışır)
load_dotenv()


def get_api_key(key_name: str) -> str | None:
    """
    Önce .env dosyasını kontrol eder, bulamazsa
    Streamlit Secrets (Bulut) sistemine bakar.
    """
    # Önce sistem ortam değişkenlerine bak (.env burayı doldurur)
    api_key = os.getenv(key_name)

    # Eğer orada yoksa (Deploy ortamındaysak) Streamlit Secrets'a bak
    if not api_key and key_name in st.secrets:
        api_key = st.secrets[key_name]

    return api_key


if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0


def check_rate_limit(interval_seconds: int = 10) -> bool:
    """
    Kullanıcının isteklerini basitçe sınırlamak için zaman kontrolü.
    Varsayılan olarak 10 saniyede bir istek yapılmasına izin verir.
    """
    current_time = time.time()
    if current_time - st.session_state.last_request_time < interval_seconds:
        return False
    st.session_state.last_request_time = current_time
    return True


# 1. Başlangıç Ayarları
st.set_page_config(page_title="AI Destekli LMS", page_icon="🎓")

# Uygulama açıldığında veritabanı tablolarını oluştur (Eğer yoksa)
init_db()

st.title("🎓 AI Destekli LMS Analiz Paneli")
st.markdown(
    """
Bu sistem, öğrenci geri bildirimlerini **Doğal Dil İşleme (NLP)** kullanarak analiz eder.
Eğitmenlere ders kalitesini artırmak için yapay zeka tabanlı içgörüler sunar.
"""
)
st.markdown("---")

# 2. Yan Menü (Sekme Mantığı)
menu = st.sidebar.selectbox("Menü", ["Analiz Yap", "Geçmiş Analizler"])

if menu == "Analiz Yap":
    st.subheader("📝 Yeni Analiz")

    # Kullanıcı Girdileri
    user_name = st.text_input("Kullanıcı Adınız", value="Öğrenci")
    feedback_text = st.text_area("Analiz edilecek geri bildirimi girin:", height=150)
    provider = st.selectbox("AI Modeli", ["gemini", "groq"])

    if st.button("AI Analizini Başlat"):
        if feedback_text:
            with st.spinner("Yapay zeka analiz ediyor..."):
                try:
                    # Basit rate limit kontrolü
                    if not check_rate_limit():
                        st.warning("Lütfen yeni bir istek göndermeden önce birkaç saniye bekleyin.")
                    else:
                        # A. Veri Doğrulama (Models kullanımı)
                        request_data = TextRequest(
                            text=feedback_text, provider=provider
                        )

                        # B. AI Servis Çağrısı
                        response = analyze_text(
                            request_data.text, request_data.provider
                        )

                    if "error" in response:
                        st.error(response["error"])
                    else:
                        # C. Sonuçları Ekranda Göster
                        st.success("Analiz Tamamlandı!")
                        st.subheader("📊 AI Analiz Sonucu")
                        st.info(response["analysis"])
                        st.caption(f"Kaynak: {response['source']}")

                        # D. Veritabanına Kaydet (Database kullanımı)
                        save_analysis(
                            user_name=user_name,
                            text=feedback_text,
                            result=response["analysis"],
                            provider=response["source"],
                        )
                        st.toast("Veritabanına kaydedildi!")

                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
        else:
            st.warning("Lütfen bir metin girin.")

elif menu == "Geçmiş Analizler":
    st.subheader("📜 Analiz Geçmişi")
    history = get_history()

    if not history:
        st.write("Henüz bir analiz kaydı bulunamadı.")
    else:
        for row in history:
            with st.expander(f"📌 {row['user_name']} - {row['created_at']}"):
                st.write(f"**Orijinal Metin:** {row['original_text']}")
                st.write(f"**AI Analizi:** {row['ai_result']}")
                st.caption(f"Model: {row['provider']}")

st.markdown("---")
st.caption("LMS AI Final Project v1.0")

 

