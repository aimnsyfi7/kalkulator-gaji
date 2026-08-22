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

# Custom CSS untuk Dark Aesthetic (Cyberpunk / Modern Dark Glass)
st.markdown("""
    <style>
    /* Latar Belakang Gelap */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Tajuk & Subtitle */
    h1 {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: -1px;
    }
    
    /* Metrics Box Gelap Glow */
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
        color: #00E676 !important; /* Neon Green */
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #A0A0A0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Style Butang Utamakan Neon Gradient */
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
    
    /* Input Fields Design */
    div[data-baseweb="input"] {
        border-radius: 10px !important;
        background-color: #1A1D24 !important;
        border: 1px solid #2D323E !important;
    }
    
    /* Horizontal Divider Line */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

FILE_PATH = "rekod_gaji.csv"

# Semak fail data CSV
if not os.path.exists(FILE_PATH):
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Kerja", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)

df = pd.read_csv(FILE_PATH)

# Auto-reset jika format fail lama digunakan
if not df.empty and "Mula Kerja" not in df.columns:
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Kerja", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)
    df = pd.read_csv(FILE_PATH)

# ---- HEADER SECTION ----
st.title("⚡ GajiKu Dark ")
st.caption("🌌 Sistem pemantauan jam kerja & gaji bulanan bergaya futuristik.")

st.markdown("---")

# ---- BAHAGIAN 1: INPUT SHIFT HARIAN ----
st.subheader("⏱️ Record Shift Harian")

with st.form("form_gaji", clear_on_submit=True):
    tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
    
    col_waktu1, col_waktu2 = st.columns(2)
    with col_waktu1:
        waktu_mula = st.time_input("🌆 Pukul Berapa Mula", value=datetime.time(9, 0))
    with col_waktu2:
        waktu_tamat = st.time_input("🌃 Pukul Berapa Tamat", value=datetime.time(17, 0))
        
    rate_jam = st.number_input("💎 Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=7.0)
    
    simpan = st.form_submit_button("⚡ SIMPAN REKOD")
    
    if simpan:
        dt_mula = datetime.datetime.combine(datetime.date.today(), waktu_mula)
        dt_tamat = datetime.datetime.combine(datetime.date.today(), waktu_tamat)
        
        if dt_tamat <= dt_mula:
            dt_tamat = dt_tamat + datetime.timedelta(days=1)
            
        durasi = dt_tamat - dt_mula
        jam_kerja = durasi.total_seconds() / 3600.0
        
        if jam_kerja > 0 and rate_jam > 0:
            gaji_syif = jam_kerja * rate_jam
            bulan_tahun = tarikh.strftime("%B %Y")
            
            data_baru = pd.DataFrame({
                "Tarikh": [tarikh.strftime("%d/%m/%Y")],
                "Mula Kerja": [waktu_mula.strftime("%I:%M %p")],
                "Tamat Kerja": [waktu_tamat.strftime("%I:%M %p")],
                "Jam Kerja": [round(jam_kerja, 2)],
                "Rate/Jam (RM)": [rate_jam],
                "Gaji Syif (RM)": [round(gaji_syif, 2)],
                "Bulan_Tahun": [bulan_tahun]
            })
            
            data_baru.to_csv(FILE_PATH, mode='a', header=False, index=False)
            st.snow() # Kesan salji bertema gelap/sejuk bila berjaya simpan
            st.success(f"✨ Rekod disimpan! Total: **{jam_kerja:.2f} Jam** = **RM {gaji_syif:.2f}**")
            st.rerun()
        else:
            st.error("Sila pastikan waktu kerja dan rate jam betul.")

st.markdown("---")

# ---- BAHAGIAN 2: REKAP BULANAN ----
st.subheader("📊 Analytics & Data")

if len(df) > 0:
    senarai_bulan = df["Bulan_Tahun"].unique().tolist()
    bulan_pilihan = st.selectbox("📅 Pilih Bulan:", senarai_bulan)
    
    df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
    
    total_gaji_bulan = df_filtered["Gaji Syif (RM)"].sum()
    total_jam_bulan = df_filtered["Jam Kerja"].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"💰 Total Gaji ({bulan_pilihan})", f"RM {total_gaji_bulan:.2f}")
    with col2:
        st.metric(f"⏳ Total Jam ({bulan_pilihan})", f"{total_jam_bulan:.1f} hrs")
    
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
