import streamlit as st
import pandas as pd
import os
import datetime
import shutil

# 1. Konfigurasi Halaman & Dark Theme
st.set_page_config(
    page_title="GajiKu | Live Punch-In Edition",
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

# Reading & Saving CSV
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

# Session state untuk tracking waktu Punch
if "punch_mula" not in st.session_state:
    st.session_state.punch_mula = None
if "punch_mula_rehat" not in st.session_state:
    st.session_state.punch_mula_rehat = None
if "total_jam_rehat" not in st.session_state:
    st.session_state.total_jam_rehat = 0.0

# ---- SIDEBAR ----
st.sidebar.title("⚡ GajiKu Navigation")
menu_pilihan = st.sidebar.radio(
    "Menu Utama:",
    ["⏱️ Quick Punch-In / Input Syif", "✏️ Live Edit Jadual", "📊 Analitik & Ringkasan", "💾 Backup & Restore"]
)

# ==========================================
# PAGE 1: QUICK PUNCH-IN & INPUT SYIF
# ==========================================
if menu_pilihan == "⏱️ Quick Punch-In / Input Syif":
    st.title("⚡ Punch-In & Rekod Syif")
    st.markdown("---")

    # ---- SEKSYEN 1: LIVE PUNCH CLOCK ----
    st.subheader("🟢 Live Punch Clock (Kerja & Rehat)")
    rate_live = st.number_input("💎 Rate Gaji/Jam (RM)", min_value=0.0, step=0.5, value=6.5, key="rate_live")

    # FASA 1: BELUM PUNCH IN KERJA
    if st.session_state.punch_mula is None:
        if st.button("🚀 PUNCH IN KERJA", use_container_width=True):
            st.session_state.punch_mula = datetime.datetime.now()
            st.session_state.punch_mula_rehat = None
            st.session_state.total_jam_rehat = 0.0
            st.success(f"Mula Kerja: **{st.session_state.punch_mula.strftime('%I:%M:%S %p')}**")
            st.rerun()

    # FASA 2: SEDANG BEKERJA ATAU SEDANG REHAT
    else:
        mula_time = st.session_state.punch_mula
        st.info(f"STATUS: **Mula Kerja:** {mula_time.strftime('%I:%M %p')} | **Total Rehat Semasa:** {st.session_state.total_jam_rehat:.2f} jam")

        col_rehat, col_balik = st.columns(2)

        with col_rehat:
            if st.session_state.punch_mula_rehat is None:
                if st.button("☕ PUNCH OUT REHAT", use_container_width=True):
                    st.session_state.punch_mula_rehat = datetime.datetime.now()
                    st.warning(f"Mula Rehat pada: **{st.session_state.punch_mula_rehat.strftime('%I:%M:%S %p')}**")
                    st.rerun()
            else:
                mula_r = st.session_state.punch_mula_rehat
                st.warning(f"Sedang Rehat Sejak: **{mula_r.strftime('%I:%M %p')}**")
                if st.button("🟢 PUNCH IN REHAT TAMAT", use_container_width=True):
                    tamat_r = datetime.datetime.now()
                    durasi_rehat = (tamat_r - mula_r).total_seconds() / 3600.0
                    st.session_state.total_jam_rehat += durasi_rehat
                    st.session_state.punch_mula_rehat = None
                    st.success(f"Tamat Rehat! Masa rehat ditambah: **{durasi_rehat*60:.0f} minit**")
                    st.rerun()

        with col_balik:
            if st.button("🔴 PUNCH OUT KERJA & SIMPAN", use_container_width=True):
                if st.session_state.punch_mula_rehat is not None:
                    tamat_r = datetime.datetime.now()
                    durasi_rehat = (tamat_r - st.session_state.punch_mula_rehat).total_seconds() / 3600.0
                    st.session_state.total_jam_rehat += durasi_rehat
                    st.session_state.punch_mula_rehat = None

                tamat_time = datetime.datetime.now()
                tempoh_kasar = (tamat_time - mula_time).total_seconds() / 3600.0
                jam_tolak = round(st.session_state.total_jam_rehat, 2)
                jam_bersih = round(max(0.0, tempoh_kasar - jam_tolak), 2)
                gaji_syif = round(jam_bersih * rate_live, 2)

                data_baru = pd.DataFrame({
                    "Tarikh": [mula_time.strftime("%d/%m/%Y")],
                    "Mula Kerja": [mula_time.strftime("%I:%M %p")],
                    "Tamat Kerja": [tamat_time.strftime("%I:%M %p")],
                    "Jam Tolak": [jam_tolak],
                    "Jam Bersih": [jam_bersih],
                    "Rate/Jam (RM)": [rate_live],
                    "Gaji Syif (RM)": [gaji_syif],
                    "Bulan_Tahun": [mula_time.strftime("%B %Y")]
                })
                df_updated = pd.concat([df, data_baru], ignore_index=True)
                simpan_data_csv(df_updated)
                buat_auto_backup()

                st.session_state.punch_mula = None
                st.session_state.punch_mula_rehat = None
                st.session_state.total_jam_rehat = 0.0

                st.success(f"Punch Out Berjaya! Jam Bersih: **{jam_bersih:.2f} hrs** | Jam Rehat: **{jam_tolak:.2f} hrs** (RM {gaji_syif:.2f})")
                st.rerun()

    st.markdown("---")

    # ---- SEKSYEN 2: INPUT MANUAL ----
    st.subheader("📝 Input Manual (Pilih Jam)")
    with st.form("form_gaji", clear_on_submit=True):
        tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
        
        st.write("🌆 **Waktu Mula Kerja:**")
        col_h1, col_m1, col_p1 = st.columns(3)
        with col_h1: jam_mula = st.selectbox("Jam", list(range(1, 13)), index=1, key="jm") 
        with col_m1: minit_mula = st.selectbox("Minit", ["00", "15", "30", "45"], index=2, key="mm") 
        with col_p1: ampm_mula = st.selectbox("AM/PM", ["AM", "PM"], index=1, key="pm1") 

        st.write("🌃 **Waktu Tamat Kerja:**")
        col_h2, col_m2, col_p2 = st.columns(3)
        with col_h2: jam_tamat = st.selectbox("Jam ", list(range(1, 13)), index=10, key="jt") 
        with col_m2: minit_mula2 = st.selectbox("Minit ", ["00", "15", "30", "45"], index=0, key="mm2") 
        with col_p2: ampm_tamat = st.selectbox("AM/PM ", ["AM", "PM"], index=1, key="pm2") 
            
        col_tolak, col_rate = st.columns(2)
        with col_tolak: jam_tolak = st.number_input("☕ Jam Tolak (Jam)", min_value=0.0, max_value=12.0, step=0.5, value=1.0)
        with col_rate: rate_jam = st.number_input("💎 Rate Gaji/Jam (RM)", min_value=0.0, step=0.5, value=6.5)
        
        simpan = st.form_submit_button("⚡ SIMPAN REKOD MANUAL")
        
        if simpan:
            h_mula = jam_mula % 12 + (12 if ampm_mula == "PM" else 0)
            h_tamat = jam_tamat % 12 + (12 if ampm_tamat == "PM" else 0)
            
            waktu_mula = datetime.time(h_mula, int(minit_mula))
            waktu_tamat = datetime.time(h_tamat, int(minit_mula2))

            dt_mula = datetime.datetime.combine(tarikh, waktu_mula)
            dt_tamat = datetime.datetime.combine(tarikh, waktu_tamat)
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
# PAGE 2: LIVE EDIT JADUAL
# ==========================================
elif menu_pilihan == "✏️ Live Edit Jadual":
    st.title("✏️ Pengurusan & Edit Rekod")
    st.markdown("---")

    if len(df) > 0:
        senarai_bulan = df["Bulan_Tahun"].dropna().unique().tolist()
        bulan_pilihan = st.selectbox("📅 Pilih Bulan Nak Edit:", senarai_bulan)
        df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
        
        df_edited = st.data_editor(df_filtered, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 SIMPAN PERUBAHAN JADUAL"):
            for i in df_edited.index:
                try:
                    dt_mula = datetime.datetime.strptime(df_edited.at[i, "Mula Kerja"], "%I:%M %p")
                    dt_tamat = datetime.datetime.strptime(df_edited.at[i, "Tamat Kerja"], "%I:%M %p")
                    if dt_tamat <= dt_mula: dt_tamat += datetime.timedelta(days=1)
                    
                    jam_tolak = float(df_edited.at[i, "Jam Tolak"])
                    rate_jam = float(df_edited.at[i, "Rate/Jam (RM)"])
                    jam_b = ((dt_tamat - dt_mula).total_seconds() / 3600.0) - jam_tolak
                    
                    df_edited.at[i, "Jam Bersih"] = round(jam_b, 2)
                    df_edited.at[i, "Gaji Syif (RM)"] = round(jam_b * rate_jam, 2)
                except: pass
                    
            df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
            df_final = pd.concat([df_baki, df_edited], ignore_index=True)
            simpan_data_csv(df_final)
            buat_auto_backup()
            st.success("Perubahan berjaya disimpan!")
            st.rerun()
    else:
        st.info("Belum ada data rekod.")

# ==========================================
# PAGE 3: ANALITIK & RINGKASAN
# ==========================================
elif menu_pilihan == "📊 Analitik & Ringkasan":
    st.title("📊 Analitik Gaji Bulanan")
    st.markdown("---")

    if len(df) > 0:
        senarai_bulan = df["Bulan_Tahun"].dropna().unique().tolist()
        bulan_pilihan = st.selectbox("📅 Pilih Bulan:", senarai_bulan)
        df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
        
        col1, col2 = st.columns(2)
        with col1: st.metric(f"💰 Total Gaji ({bulan_pilihan})", f"RM {df_filtered['Gaji Syif (RM)'].sum():.2f}")
        with col2: st.metric(f"⏳ Total Jam Bersih ({bulan_pilihan})", f"{df_filtered['Jam Bersih'].sum():.1f} hrs")
        
        st.bar_chart(df_filtered.set_index("Tarikh")["Gaji Syif (RM)"])
        st.dataframe(df_filtered.drop(columns=["Bulan_Tahun"]), use_container_width=True)
    else:
        st.info("Belum ada data analitik.")

# ==========================================
# PAGE 4: BACKUP & RESTORE
# ==========================================
elif menu_pilihan == "💾 Backup & Restore":
    st.title("💾 Pusat Backup & Restore Data")
    st.markdown("---")
    
    if len(df) > 0:
        st.download_button("📥 DOWNLOAD CSV BACKUP", data=df.to_csv(index=False).encode('utf-8'), file_name="rekod_gaji_backup.csv", mime="text/csv")
        
    uploaded_file = st.file_uploader("Upload CSV Backup:", type=["csv"])
    if uploaded_file is not None:
        if st.button("🔄 SAHKAN RESTORE DATA"):
            df_up = pd.read_csv(uploaded_file)
            simpan_data_csv(df_up)
            st.success("Data berjaya dipulihkan!")
            st.rerun()
