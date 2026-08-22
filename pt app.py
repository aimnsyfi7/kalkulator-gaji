import streamlit as st
import pandas as pd
import os
import datetime

# 1. Konfigurasi Halaman & Dark Theme
st.set_page_config(
    page_title="GajiKu | Dark Aesthetic Edition",
    page_icon="🌙",
    layout="centered"
)

# Custom CSS untuk Dark Aesthetic
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    h1 {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: -1px;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #00E676 !important;
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #A0A0A0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #6200EA 0%, #7C4DFF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 15px rgba(124, 77, 255, 0.4);
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 77, 255, 0.7) !important;
    }
    
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 10px !important;
        background-color: #1A1D24 !important;
        border: 1px solid #2D323E !important;
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

FILE_PATH = "rekod_gaji.csv"

# Semak fail data CSV
if not os.path.exists(FILE_PATH):
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)

df = pd.read_csv(FILE_PATH)

# Auto-reset jika format fail lama digunakan (elak crash)
if not df.empty and "Jam Tolak" not in df.columns:
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)
    df = pd.read_csv(FILE_PATH)

# ---- HEADER SECTION ----
st.title("⚡ GajiKu Dark Mode")
st.caption("🌌 Pemantauan waktu kerja, potongan masa rehat & gaji harian.")

st.markdown("---")

# ---- BAHAGIAN 1: INPUT SHIFT HARIAN ----
st.subheader("⏱️ Record Shift Harian")

with st.form("form_gaji", clear_on_submit=True):
    tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
    
    # --- SELECTION MASA MULA (AM / PM) ---
    st.write("🌆 **Waktu Mula Kerja:**")
    col_h1, col_m1, col_p1 = st.columns([1, 1, 1])
    with col_h1:
        jam_mula = st.selectbox("Jam", list(range(1, 13)), index=9, key="jm") # Default 10
    with col_m1:
        minit_mula = st.selectbox("Minit", ["00", "15", "30", "45"], index=0, key="mm")
    with col_p1:
        ampm_mula = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="pm1") # Default AM

    # --- SELECTION MASA TAMAT (AM / PM) ---
    st.write("🌃 **Waktu Tamat Kerja:**")
    col_h2, col_m2, col_p2 = st.columns([1, 1, 1])
    with col_h2:
        jam_tamat = st.selectbox("Jam", list(range(1, 13)), index=9, key="jt") # Default 10
    with col_m2:
        minit_mula2 = st.selectbox("Minit ", ["00", "15", "30", "45"], index=0, key="mm2")
    with col_p2:
        ampm_tamat = st.selectbox("AM/PM ", ["AM", "PM"], index=1, key="pm2") # Default PM
        
    st.write("")
    col_tolak, col_rate = st.columns(2)
    with col_tolak:
        jam_tolak = st.number_input("☕ Jam Tolak / Break (Jam)", min_value=0.0, max_value=12.0, step=0.5, value=1.0)
    with col_rate:
        rate_jam = st.number_input("💎 Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=7.0)
    
    simpan = st.form_submit_button("⚡ SIMPAN REKOD")
    
    if simpan:
        # Convert 12-hour format ke 24-hour time object
        h_mula = jam_mula % 12 + (12 if ampm_mula == "PM" else 0)
        h_tamat = jam_tamat % 12 + (12 if ampm_tamat == "PM" else 0)
        
        waktu_mula = datetime.time(h_mula, int(minit_mula))
        waktu_tamat = datetime.time(h_tamat, int(minit_mula2))

        dt_mula = datetime.datetime.combine(datetime.date.today(), waktu_mula)
        dt_tamat = datetime.datetime.combine(datetime.date.today(), waktu_tamat)
        
        if dt_tamat <= dt_mula:
            dt_tamat = dt_tamat + datetime.timedelta(days=1)
            
        durasi = dt_tamat - dt_mula
        jam_kasar = durasi.total_seconds() / 3600.0
        
        # Tolak jam rehat / jam potong
        jam_bersih = jam_kasar - jam_tolak
        
        if jam_bersih > 0 and rate_jam > 0:
            gaji_syif = jam_bersih * rate_jam
            bulan_tahun = tarikh.strftime("%B %Y")
            
            data_baru = pd.DataFrame({
                "Tarikh": [tarikh.strftime("%d/%m/%Y")],
                "Mula Kerja": [waktu_mula.strftime("%I:%M %p")],
                "Tamat Kerja": [waktu_tamat.strftime("%I:%M %p")],
                "Jam Tolak": [jam_tolak],
                "Jam Bersih": [round(jam_bersih, 2)],
                "Rate/Jam (RM)": [rate_jam],
                "Gaji Syif (RM)": [round(gaji_syif, 2)],
                "Bulan_Tahun": [bulan_tahun]
            })
            
            data_baru.to_csv(FILE_PATH, mode='a', header=False, index=False)
            st.snow()
            st.success(f"✨ Saved! Total Kasar: **{jam_kasar:.2f} hrs** | Tolak Break: **{jam_tolak} hrs** | Jam Bersih: **{jam_bersih:.2f} hrs** (RM {gaji_syif:.2f})")
            st.rerun()
        else:
            st.error("Sila pastikan jumlah jam bersih melebihi 0 dan rate jam betul.")

st.markdown("---")

# ---- BAHAGIAN 2: REKAP BULANAN ----
st.subheader("📊 Analytics & Data")

if len(df) > 0:
    senarai_bulan = df["Bulan_Tahun"].unique().tolist()
    bulan_pilihan = st.selectbox("📅 Pilih Bulan:", senarai_bulan)
    
    df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
    
    total_gaji_bulan = df_filtered["Gaji Syif (RM)"].sum()
    total_jam_bulan = df_filtered["Jam Bersih"].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"💰 Total Gaji ({bulan_pilihan})", f"RM {total_gaji_bulan:.2f}")
    with col2:
        st.metric(f"⏳ Total Jam Bersih ({bulan_pilihan})", f"{total_jam_bulan:.1f} hrs")
    
    st.write("")
    st.dataframe(df_filtered.drop(columns=["Bulan_Tahun"]), use_container_width=True)
    
    # Padam Bulan
    st.markdown("---")
    with st.expander(f"🗑️ Padam Data Bulan {bulan_pilihan}"):
        st.warning(f"Adakah anda pasti nak padam SEMUA rekod untuk bulan **{bulan_pilihan}**?")
        if st.button(f"Sahkan Padam {bulan_pilihan}"):
            df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
            df_baki.to_csv(FILE_PATH, index=False)
            st.success(f"Rekod bulan {bulan_pilihan} telah dipadam!")
            st.rerun()
else:
    st.info("Belum ada data. Masukkan waktu kerja korang kat atas untuk simpan rekod baru!")
