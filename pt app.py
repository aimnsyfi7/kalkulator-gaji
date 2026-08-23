import streamlit as st
import pandas as pd
import os
import datetime
import shutil
import google.generativeai as genai
from PIL import Image
from io import StringIO

# 1. Konfigurasi Halaman & Dark Theme
st.set_page_config(
    page_title="GajiKu | AI Scan Edition",
    page_icon="🌙",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    h1 { background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900 !important; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 16px; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: 800 !important; color: #00E676 !important; }
    .stButton>button, .stDownloadButton>button { border-radius: 12px !important; background: linear-gradient(135deg, #6200EA 0%, #7C4DFF 100%) !important; color: #FFFFFF !important; font-weight: 700 !important; border: none !important; }
    section[data-testid="stSidebar"] { background-color: #12161F !important; }
    </style>
""", unsafe_allow_html=True)

FILE_PATH = "rekod_gaji.csv"
BACKUP_DIR = "backups"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Auto Cleaning & Reading CSV (Laju dengan Caching)
@st.cache_data
def muat_data():
    if os.path.exists(FILE_PATH):
        df_temp = pd.read_csv(FILE_PATH)
        if not df_temp.empty:
            df_temp = df_temp.dropna(how="all")
            if "Bulan_Tahun" in df_temp.columns:
                df_temp = df_temp[df_temp["Bulan_Tahun"].notna()]
                df_temp = df_temp[df_temp["Bulan_Tahun"].astype(str).str.strip().str.lower() != "nan"]
            return df_temp
    return pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])

def simpan_data_csv(df_input):
    df_input.to_csv(FILE_PATH, index=False)
    st.cache_data.clear()

def buat_auto_backup():
    if os.path.exists(FILE_PATH):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(FILE_PATH, os.path.join(BACKUP_DIR, f"backup_rekod_gaji_{timestamp}.csv"))

df = muat_data()

# ---- SIDEBAR ----
st.sidebar.title("⚡ GajiKu Navigation")
menu_pilihan = st.sidebar.radio(
    "Menu Utama:",
    ["⏱️ Rekod Syif Baru", "📸 Scan Jadual (AI)", "✏️ Live Edit Jadual", "📊 Analitik & Ringkasan", "🤖 AI Advisor", "💾 Backup & Restore"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Gemini API Settings")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Dapatkan API key percuma dari aistudio.google.com")

# ==========================================
# PAGE 1: REKOD SYIF BARU
# ==========================================
if menu_pilihan == "⏱️ Rekod Syif Baru":
    st.title("⚡ Input Syif Harian")
    st.markdown("---")

    with st.form("form_gaji", clear_on_submit=True):
        tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
        
        st.write("🌆 **Waktu Mula Kerja:**")
        col_h1, col_m1, col_p1 = st.columns(3)
        with col_h1: jam_mula = st.selectbox("Jam", list(range(1, 13)), index=9, key="jm") 
        with col_m1: minit_mula = st.selectbox("Minit", ["00", "15", "30", "45"], index=0, key="mm")
        with col_p1: ampm_mula = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="pm1") 

        st.write("🌃 **Waktu Tamat Kerja:**")
        col_h2, col_m2, col_p2 = st.columns(3)
        with col_h2: jam_tamat = st.selectbox("Jam ", list(range(1, 13)), index=9, key="jt") 
        with col_m2: minit_mula2 = st.selectbox("Minit ", ["00", "15", "30", "45"], index=0, key="mm2")
        with col_p2: ampm_tamat = st.selectbox("AM/PM ", ["AM", "PM"], index=1, key="pm2") 
            
        col_tolak, col_rate = st.columns(2)
        with col_tolak: jam_tolak = st.number_input("☕ Jam Tolak (Jam)", min_value=0.0, max_value=12.0, step=0.5, value=1.0)
        with col_rate: rate_jam = st.number_input("💎 Rate Gaji/Jam (RM)", min_value=0.0, step=0.5, value=7.0)
        
        simpan = st.form_submit_button("⚡ SIMPAN REKOD")
        
        if simpan:
            h_mula = jam_mula % 12 + (12 if ampm_mula == "PM" else 0)
            h_tamat = jam_tamat % 12 + (12 if ampm_tamat == "PM" else 0)
            
            waktu_mula = datetime.time(h_mula, int(minit_mula))
            waktu_tamat = datetime.time(h_tamat, int(minit_mula2))

            dt_mula = datetime.datetime.combine(datetime.date.today(), waktu_mula)
            dt_tamat = datetime.datetime.combine(datetime.date.today(), waktu_tamat)
            if dt_tamat <= dt_mula: dt_tamat += datetime.timedelta(days=1)
                
            jam_bersih = (dt_tamat - dt_mula).total_seconds() / 3600.0 - jam_tolak
            
            if jam_bersih > 0 and rate_jam > 0:
                gaji_syif = jam_bersih * rate_jam
                data_baru = pd.DataFrame({
                    "Tarikh": [tarikh.strftime("%d/%m/%Y")],
                    "Mula Kerja": [waktu_mula.strftime("%I:%M %p")],
                    "Tamat Kerja": [waktu_tamat.strftime("%I:%M %p")],
                    "Jam Tolak": [jam_tolak],
                    "Jam Bersih": [round(jam_bersih, 2)],
                    "Rate/Jam (RM)": [rate_jam],
                    "Gaji Syif (RM)": [round(gaji_syif, 2)],
                    "Bulan_Tahun": [tarikh.strftime("%B %Y")]
                })
                df_updated = pd.concat([df, data_baru], ignore_index=True)
                simpan_data_csv(df_updated)
                buat_auto_backup()
                st.success(f"Saved! Total: **{jam_bersih:.2f} hrs** (RM {gaji_syif:.2f})")
                st.rerun()

# ==========================================
# PAGE 2: SCAN JADUAL KERJA (AI OCR)
# ==========================================
elif menu_pilihan == "📸 Scan Jadual (AI)":
    st.title("📸 AI Scan Jadual Syif")
    st.markdown("---")

    if not api_key:
        st.warning("⚠️ Masukkan **Gemini API Key** di sidebar dulu.")
    else:
        uploaded_img = st.file_uploader("Upload gambar jadual (PNG/JPG):", type=["png", "jpg", "jpeg"])
        default_rate = st.number_input("💎 Rate Gaji Per Jam (RM):", min_value=0.0, step=0.5, value=7.0)
        default_break = st.number_input("☕ Jam Tolak Default (Jam):", min_value=0.0, step=0.5, value=1.0)
        
        if uploaded_img is not None:
            img = Image.open(uploaded_img)
            st.image(img, caption="Gambar Jadual", use_container_width=True)
            
            if st.button("✨ BACA JADUAL & EKSTRAK SYIF"):
                with st.spinner("AI sedang membaca jadual..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash-latest')
                        
                        prompt_ocr = """
                        Ekstrak jadual syif kerja daripada gambar ini. 
                        Kembalikan HANYA format CSV (tanpa penjelasan/markdown codeblock) dengan header:
                        Tarikh,Mula Kerja,Tamat Kerja
                        
                        Format wajib:
                        - Tarikh: DD/MM/YYYY (jika tiada tahun, guna tahun 2026)
                        - Mula Kerja: HH:MM AM/PM
                        - Tamat Kerja: HH:MM AM/PM
                        """
                        
                        response = model.generate_content([prompt_ocr, img])
                        raw_csv = response.text.strip().replace("```csv", "").replace("
