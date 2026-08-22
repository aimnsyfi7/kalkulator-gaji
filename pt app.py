import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set skrin penuh & tajuk
st.set_page_config(page_title="Sistem Rekod Gaji Jam", layout="centered")

FILE_PATH = "rekod_gaji.csv"

# 1. Semak fail data CSV, jika belum ada buat fail baru
if not os.path.exists(FILE_PATH):
  df_init = pd.DataFrame(columns=["Tarikh", "Jam Kerja", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
  df_init.to_csv(FILE_PATH, index=False)

# Baca data semasa dari fail
df = pd.read_csv(FILE_PATH)

st.title("⏱️ Sistem Pengira & Rekod Gaji Jam")

# ---- BAHAGIAN 1: BORANG MASUKKAN DATA HARIAN ----
st.subheader("➕ Isi Rekod Kerja Baru")

with st.form("form_gaji", clear_on_submit=True):
  tarikh = st.date_input("Tarikh Kerja", value=datetime.now())
  jam_kerja = st.number_input("Berapa Jam Bekerja", min_value=0.0, step=0.5, value=0.0)
  rate_jam = st.number_input("Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=0.0)

simpan = st.form_submit_button("Simpan Rekod")

if simpan:
  if jam_kerja > 0 and rate_jam > 0:
  gaji_syif = jam_kerja * rate_jam
  bulan_tahun = tarikh.strftime("%B %Y")

data_baru = pd.DataFrame({
"Tarikh": [tarikh.strftime("%d/%m/%Y")],
"Jam Kerja": [jam_kerja],
"Rate/Jam (RM)": [rate_jam],
"Gaji Syif (RM)": [gaji_syif],
"Bulan_Tahun": [bulan_tahun]
})

data_baru.to_csv(FILE_PATH, mode='a', header=False, index=False)
st.success(f"Berjaya disimpan! RM {gaji_syif:.2f} dimasukkan.")
st.rerun()
else:
st.error("Sila isi jam kerja dan rate jam dengan betul.")

st.markdown("---")

# ---- BAHAGIAN 2: JADUAL REKOD & PADAM BULANAN ----
st.subheader("📑 Senarai Rekod & Rekap Bulan")

if not df.empty:
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
st.warning(f"Adakah anda pasti nak padam SEMUA rekod untuk bulan {bulan_pilihan} sahaja?")
if st.button(f"Sahkan Padam Bulan {bulan_pilihan}"):
df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
df_baki.to_csv(FILE_PATH, index=False)
st.success(f"Rekod untuk bulan {bulan_pilihan} telah dipadam!")
st.rerun()
else:
st.info("Belum ada rekod lagi. Isi borang di atas untuk mula simpan data.")
