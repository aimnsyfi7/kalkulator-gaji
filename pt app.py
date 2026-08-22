import streamlit as st
import pandas as pd
import os
import datetime

# 1. Konfigurasi Halaman & Tema Ceria
st.set_page_config(
    page_title="GajiKu | Pengira Gaji Jam",
    page_icon="💰",
    layout="centered"
)

# Custom Styling (CSS) untuk bagi rupa mesra & ceria
st.markdown("""
    <style>
    /* Mengubah latar belakang dan gaya kad */
    .stApp {
        background-color: #FAF9F6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #FF5722 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #4A4A4A !important;
    }
    /* Style untuk butang utama */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #FF7043 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #E64A19 !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
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

# ---- TAJUK UTAMA ----
st.title("✨ GajiKu Tracker ✨")
st.caption("Pantau waktu kerja dan kira gaji harian kau dengan mudah & cepat!")

st.markdown("---")

# ---- BAHAGIAN 1: BORANG INPUT HARIAN ----
st.subheader("📝 Record Shift Hari Ni")

with st.form("form_gaji", clear_on_submit=True):
    tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
    
    col_waktu1, col_waktu2 = st.columns(2)
    with col_waktu1:
        waktu_mula = st.time_input("⏰ Pukul Berapa Mula", value=datetime.time(9, 0))
    with col_waktu2:
        waktu_tamat = st.time_input("⌛ Pukul Berapa Tamat", value=datetime.time(17, 0))
        
    rate_jam = st.number_input("💵 Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=7.0)
    
    simpan = st.form_submit_button("🚀 Simpan Rekod")
    
    if simpan:
        # Kira waktu kerja automatik
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
            st.balloons() # Kesan selebrasi belon bila berjaya simpan!
            st.success(f"Mantap! Total kerja **{jam_kerja:.2f} jam** = **RM {gaji_syif:.2f}**")
            st.rerun()
        else:
            st.error("Sila pastikan waktu kerja dan rate jam betul.")

st.markdown("---")

# ---- BAHAGIAN 2: SENARAI REKOD & REKAP BULANAN ----
st.subheader("📊 Ringkasan & Sejarah Gaji")

if len(df) > 0:
    senarai_bulan = df["Bulan_Tahun"].unique().tolist()
    bulan_pilihan = st.selectbox("📅 Pilih Bulan:", senarai_bulan)
    
    df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
    
    total_gaji_bulan = df_filtered["Gaji Syif (RM)"].sum()
    total_jam_bulan = df_filtered["Jam Kerja"].sum()
    
    # Kad Ringkasan Terkumpul
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"💰 Total Gaji ({bulan_pilihan})", f"RM {total_gaji_bulan:.2f}")
    with col2:
        st.metric(f"⏳ Total Jam ({bulan_pilihan})", f"{total_jam_bulan:.1f} Jam")
    
    st.write("")
    st.dataframe(df_filtered.drop(columns=["Bulan_Tahun"]), use_container_width=True)
    
    # Option Padam Bulan
    st.markdown("---")
    with st.expander(f"🗑️ Padam Data Bulan {bulan_pilihan}"):
        st.warning(f"Adakah kau pasti nak padam SEMUA rekod untuk bulan **{bulan_pilihan}** sahaja?")
        if st.button(f"Sahkan Padam {bulan_pilihan}"):
            df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
            df_baki.to_csv(FILE_PATH, index=False)
            st.success(f"Rekod bulan {bulan_pilihan} telah dipadam!")
            st.rerun()
else:
    st.info("Belum ada rekod lagi. Masukkan shift kerja kau kat atas tu untuk mula simpan!")
