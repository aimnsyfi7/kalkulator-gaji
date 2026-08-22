import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Sistem Rekod Gaji Jam", layout="centered")

FILE_PATH = "rekod_gaji.csv"

# 1. Semak fail data CSV, jika belum ada atau lajur tak sepadan, buat baru
if not os.path.exists(FILE_PATH):
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Kerja", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)

# Baca data
df = pd.read_csv(FILE_PATH)

# Jika fail CSV lama tak ada lajur Mula Kerja, reset automatik supaya tak crash
if not df.empty and "Mula Kerja" not in df.columns:
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Kerja", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)
    df = pd.read_csv(FILE_PATH)

st.title("⏱️ Sistem Pengira & Rekod Gaji Jam")

# ---- BAHAGIAN 1: BORANG INPUT HARIAN ----
st.subheader("➕ Isi Rekod Kerja Baru")

with st.form("form_gaji", clear_on_submit=True):
    tarikh = st.date_input("Tarikh Kerja", value=datetime.date.today())
    
    col_waktu1, col_waktu2 = st.columns(2)
    with col_waktu1:
        waktu_mula = st.time_input("Pukul Berapa Mula", value=datetime.time(9, 0))
    with col_waktu2:
        waktu_tamat = st.time_input("Pukul Berapa Tamat", value=datetime.time(17, 0))
        
    rate_jam = st.number_input("Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=7.0)
    
    simpan = st.form_submit_button("Simpan Rekod")
    
    if simpan:
        # Kirakan beza masa (jumlah jam kerja) secara automatik
        dt_mula = datetime.datetime.combine(datetime.date.today(), waktu_mula)
        dt_tamat = datetime.datetime.combine(datetime.date.today(), waktu_tamat)
        
        # Jika kerja melepasi tengah malam (contoh: 10 PM hingga 6 AM)
        if dt_tamat <= dt_mula:
            dt_tamat = dt_tamat + datetime.timedelta(days=1)
            
        durasi = dt_tamat - dt_mula
        jam_kerja = durasi.total_seconds() / 3600.0  # Tukar ke unit jam
        
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
            st.success(f"Berjaya disimpan! Total kerja {jam_kerja:.2f} jam = RM {gaji_syif:.2f}")
            st.rerun()
        else:
            st.error("Sila pastikan waktu kerja dan rate jam betul.")

st.markdown("---")

# ---- BAHAGIAN 2: SENARAI REKOD & REKAP BULANAN ----
st.subheader("📑 Senarai Rekod & Rekap Bulan")

if len(df) > 0:
    senarai_bulan = df["Bulan_Tahun"].unique().tolist()
    bulan_pilihan = st.selectbox("📅 Pilih Bulan Untuk Dilihat / Dipadam:", senarai_bulan)
    
    df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
    
    total_gaji_bulan = df_filtered["Gaji Syif (RM)"].sum()
    total_jam_bulan = df_filtered["Jam Kerja"].sum()
    
    col1, col2 = st.columns(2)
    col1.metric(f"TOTAL GAJI ({bulan_pilihan})", f"RM {total_gaji_bulan:.2f}")
    col2.metric(f"TOTAL JAM ({bulan_pilihan})", f"{total_jam_bulan:.1f} Jam")
    
    st.write("")
    st.dataframe(df_filtered.drop(columns=["Bulan_Tahun"]), use_container_width=True)
    
    st.markdown("---")
    with st.expander(f"🗑️ Padam Data Bulan {bulan_pilihan}"):
        st.warning(f"Adakah anda pasti nak padam SEMUA rekod untuk bulan **{bulan_pilihan}** sahaja?")
        if st.button(f"Sahkan Padam Bulan {bulan_pilihan}"):
            df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
            df_baki.to_csv(FILE_PATH, index=False)
            st.success(f"Rekod untuk bulan {bulan_pilihan} telah dipadam!")
            st.rerun()
else:
    st.info("Belum ada rekod lagi. Isi borang di atas untuk mula simpan data.")
