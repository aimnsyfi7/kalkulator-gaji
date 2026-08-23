import streamlit as st
import pandas as pd
import os
import datetime
import shutil
from google import genai
from PIL import Image

# 1. Konfigurasi Halaman & Dark Theme
st.set_page_config(
    page_title="GajiKu | AI Scan & Multi-Page Edition",
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

    .stButton>button, .stDownloadButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #6200EA 0%, #7C4DFF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 15px rgba(124, 77, 255, 0.4);
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 77, 255, 0.7) !important;
    }
    
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 10px !important;
        background-color: #1A1D24 !important;
        border: 1px solid #2D323E !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #12161F !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

FILE_PATH = "rekod_gaji.csv"
BACKUP_DIR = "backups"

# Cipta folder backups jika belum wujud
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Semak fail data CSV utama
if not os.path.exists(FILE_PATH):
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)

df = pd.read_csv(FILE_PATH)

# Auto-reset jika format fail lama digunakan
if not df.empty and "Jam Tolak" not in df.columns:
    df_init = pd.DataFrame(columns=["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"])
    df_init.to_csv(FILE_PATH, index=False)
    df = pd.read_csv(FILE_PATH)

# Fungsi Auto Backup
def buat_auto_backup():
    if os.path.exists(FILE_PATH):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_rekod_gaji_{timestamp}.csv")
        shutil.copy(FILE_PATH, backup_file)

# ---- SIDEBAR NAVIGATION ----
st.sidebar.title("⚡ GajiKu Navigation")
st.sidebar.caption("🌌 Pilih halaman untuk diguna")

menu_pilihan = st.sidebar.radio(
    "Menu Utama:",
    ["⏱️ Rekod Syif Baru", "📸 Scan Jadual (AI)", "✏️ Live Edit Jadual", "📊 Analitik & Ringkasan", "🤖 AI Advisor", "💾 Backup & Restore"]
)

st.sidebar.markdown("---")
# Input API Key di Sidebar
st.sidebar.subheader("🔑 Gemini API Settings")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Dapatkan API key percuma dari aistudio.google.com")

st.sidebar.markdown("---")
st.sidebar.info("💡 Data tersimpan dalam `rekod_gaji.csv` & auto-backup tersedia.")

# ==========================================
# PAGE 1: REKOD SYIF BARU
# ==========================================
if menu_pilihan == "⏱️ Rekod Syif Baru":
    st.title("⚡ Input Syif Harian")
    st.caption("Masukkan maklumat syif kerja harian korang di sini.")
    st.markdown("---")

    with st.form("form_gaji", clear_on_submit=True):
        tarikh = st.date_input("🗓️ Tarikh Kerja", value=datetime.date.today())
        
        st.write("🌆 **Waktu Mula Kerja:**")
        col_h1, col_m1, col_p1 = st.columns([1, 1, 1])
        with col_h1:
            jam_mula = st.selectbox("Jam", list(range(1, 13)), index=9, key="jm") 
        with col_m1:
            minit_mula = st.selectbox("Minit", ["00", "15", "30", "45"], index=0, key="mm")
        with col_p1:
            ampm_mula = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="pm1") 

        st.write("🌃 **Waktu Tamat Kerja:**")
        col_h2, col_m2, col_p2 = st.columns([1, 1, 1])
        with col_h2:
            jam_tamat = st.selectbox("Jam", list(range(1, 13)), index=9, key="jt") 
        with col_m2:
            minit_mula2 = st.selectbox("Minit ", ["00", "15", "30", "45"], index=0, key="mm2")
        with col_p2:
            ampm_tamat = st.selectbox("AM/PM ", ["AM", "PM"], index=1, key="pm2") 
            
        st.write("")
        col_tolak, col_rate = st.columns(2)
        with col_tolak:
            jam_tolak = st.number_input("☕ Jam Tolak / Break (Jam)", min_value=0.0, max_value=12.0, step=0.5, value=1.0)
        with col_rate:
            rate_jam = st.number_input("💎 Rate Gaji Per Jam (RM)", min_value=0.0, step=0.5, value=7.0)
        
        simpan = st.form_submit_button("⚡ SIMPAN REKOD")
        
        if simpan:
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
                buat_auto_backup()
                st.snow()
                st.success(f"✨ Saved & Auto-backed up! Total Bersih: **{jam_bersih:.2f} hrs** (RM {gaji_syif:.2f})")
                st.rerun()
            else:
                st.error("Sila pastikan jumlah jam bersih melebihi 0 dan rate jam betul.")

# ==========================================
# PAGE 2: SCAN JADUAL KERJA (AI OCR)
# ==========================================
elif menu_pilihan == "📸 Scan Jadual (AI)":
    st.title("📸 AI Scan Jadual Syif")
    st.caption("Muat naik gambar jadual syif kerja kau, AI akan baca & rekodkan secara automatik.")
    st.markdown("---")

    if not api_key:
        st.warning("⚠️ Sila masukkan **Gemini API Key** korang dekat bahagian sidebar sebelah kiri dulu.")
    else:
        uploaded_img = st.file_uploader("Upload gambar jadual syif (PNG/JPG):", type=["png", "jpg", "jpeg"])
        
        default_rate = st.number_input("💎 Set Rate Gaji Per Jam (RM):", min_value=0.0, step=0.5, value=7.0)
        default_break = st.number_input("☕ Set Jam Tolak / Break Default (Jam):", min_value=0.0, step=0.5, value=1.0)
        
        if uploaded_img is not None:
            img = Image.open(uploaded_img)
            st.image(img, caption="Gambar Jadual Di-upload", use_container_width=True)
            
            if st.button("✨ BACA JADUAL & EAKSTRAK SYIF"):
                with st.spinner("AI sedang membaca maklumat jadual kerja dalam gambar..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt_ocr = """
                        Ekstrak jadual syif kerja daripada gambar ini. 
                        Sila kembalikan jawapan HANYA dalam format CSV (tanpa sebarang penjelasan atau markdown codeblock), dengan header berikut:
                        Tarikh,Mula Kerja,Tamat Kerja
                        
                        Aturan format:
                        - Tarikh: DD/MM/YYYY (jika tiada tahun, andaikan tahun semasa 2026)
                        - Mula Kerja: HH:MM AM/PM (contoh: 09:00 AM)
                        - Tamat Kerja: HH:MM AM/PM (contoh: 06:00 PM)
                        
                        Contoh jawapan yang betul:
                        Tarikh,Mula Kerja,Tamat Kerja
                        23/08/2026,09:00 AM,06:00 PM
                        24/08/2026,10:00 AM,07:00 PM
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[img, prompt_ocr]
                        )
                        
                        st.subheader("📝 Data Dikesan AI:")
                        raw_csv = response.text.strip().replace("```csv", "").replace("```", "").strip()
                        
                        # Process Extracted CSV
                        from io import StringIO
                        df_extracted = pd.read_csv(StringIO(raw_csv))
                        
                        # Add calculated columns
                        jam_bersih_list = []
                        gaji_syif_list = []
                        bulan_tahun_list = []
                        jam_tolak_list = []
                        rate_list = []

                        for index, row in df_extracted.iterrows():
                            dt_mula = datetime.datetime.strptime(row["Mula Kerja"], "%I:%M %p")
                            dt_tamat = datetime.datetime.strptime(row["Tamat Kerja"], "%I:%M %p")
                            dt_tarikh = datetime.datetime.strptime(row["Tarikh"], "%d/%m/%Y")
                            
                            if dt_tamat <= dt_mula:
                                dt_tamat += datetime.timedelta(days=1)
                                
                            durasi = dt_tamat - dt_mula
                            jam_kasar = durasi.total_seconds() / 3600.0
                            jam_bersih = round(max(0, jam_kasar - default_break), 2)
                            gaji_syif = round(jam_bersih * default_rate, 2)
                            
                            jam_bersih_list.append(jam_bersih)
                            gaji_syif_list.append(gaji_syif)
                            bulan_tahun_list.append(dt_tarikh.strftime("%B %Y"))
                            jam_tolak_list.append(default_break)
                            rate_list.append(default_rate)

                        df_extracted["Jam Tolak"] = jam_tolak_list
                        df_extracted["Jam Bersih"] = jam_bersih_list
                        df_extracted["Rate/Jam (RM)"] = rate_list
                        df_extracted["Gaji Syif (RM)"] = gaji_syif_list
                        df_extracted["Bulan_Tahun"] = bulan_tahun_list

                        # Reorder columns
                        df_extracted = df_extracted[["Tarikh", "Mula Kerja", "Tamat Kerja", "Jam Tolak", "Jam Bersih", "Rate/Jam (RM)", "Gaji Syif (RM)", "Bulan_Tahun"]]
                        
                        st.dataframe(df_extracted, use_container_width=True)
                        
                        # Save Option
                        if st.button("💾 MASUKKAN SEMUA SYIF INI KE DATABASE"):
                            df_final = pd.concat([df, df_extracted], ignore_index=True)
                            df_final.to_csv(FILE_PATH, index=False)
                            buat_auto_backup()
                            st.success("Semua syif daripada jadual berjaya dimasukkan!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Gagal membaca imej/jadual: {e}. Sila pastikan gambar jelas.")

# ==========================================
# PAGE 3: LIVE EDIT JADUAL
# ==========================================
elif menu_pilihan == "✏️ Live Edit Jadual":
    st.title("✏️ Pengurusan & Edit Rekod")
    st.caption("Ubah data secara terus dalam jadual interaktif di bawah.")
    st.markdown("---")

    if len(df) > 0:
        senarai_bulan = df["Bulan_Tahun"].unique().tolist()
        bulan_pilihan = st.selectbox("📅 Pilih Bulan Nak Edit:", senarai_bulan)
        
        df_filtered = df[df["Bulan_Tahun"] == bulan_pilihan].copy()
        
        st.write("")
        st.caption("💡 **Petunjuk:** Tekan petak jadual untuk ubah data. Tekan butang di bawah lepas dah siap ubah.")
        
        df_edited = st.data_editor(
            df_filtered,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_gaji"
        )
        
        if st.button("💾 SIMPAN PERUBAHAN JADUAL"):
            for i in df_edited.index:
                try:
                    dt_mula = datetime.datetime.strptime(df_edited.at[i, "Mula Kerja"], "%I:%M %p")
                    dt_tamat = datetime.datetime.strptime(df_edited.at[i, "Tamat Kerja"], "%I:%M %p")
                    
                    if dt_tamat <= dt_mula:
                        dt_tamat = dt_tamat + datetime.timedelta(days=1)
                        
                    durasi = dt_tamat - dt_mula
                    jam_kasar = durasi.total_seconds() / 3600.0
                    
                    jam_tolak = float(df_edited.at[i, "Jam Tolak"])
                    rate_jam = float(df_edited.at[i, "Rate/Jam (RM)"])
                    
                    jam_bersih = jam_kasar - jam_tolak
                    gaji_syif = jam_bersih * rate_jam
                    
                    df_edited.at[i, "Jam Bersih"] = round(jam_bersih, 2)
                    df_edited.at[i, "Gaji Syif (RM)"] = round(gaji_syif, 2)
                except:
                    pass
                    
            df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
            df_final = pd.concat([df_baki, df_edited], ignore_index=True)
            
            df_final.to_csv(FILE_PATH, index=False)
            buat_auto_backup()
            st.success("Perubahan berjaya disimpan & auto-backup dihasilkan!")
            st.rerun()

        st.markdown("---")
        with st.expander(f"🗑️ Padam Semua Rekod Bulan {bulan_pilihan}"):
            st.warning(f"Adakah anda pasti nak padam SEMUA rekod untuk bulan **{bulan_pilihan}**?")
            if st.button(f"Sahkan Padam {bulan_pilihan}"):
                buat_auto_backup()
                df_baki = df[df["Bulan_Tahun"] != bulan_pilihan]
                df_baki.to_csv(FILE_PATH, index=False)
                st.success(f"Rekod bulan {bulan_pilihan} telah dipadam!")
                st.rerun()
    else:
        st.info("Belum ada data rekod. Sila masukkan rekod baru di menu ⏱️ Rekod Syif Baru.")

# ==========================================
# PAGE 4: ANALITIK & RINGKASAN
# ==========================================
elif menu_pilihan == "📊 Analitik & Ringkasan":
    st.title("📊 Analitik Gaji Bulanan")
    st.caption("Pantau jumlah pendapatan dan trend jam kerja korang.")
    st.markdown("---")

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
        st.subheader("📈 Trend Pendapatan Harian")
        st.bar_chart(df_filtered.set_index("Tarikh")["Gaji Syif (RM)"])

        st.write("")
        st.subheader("📋 Senarai Rekod Penuh")
        st.dataframe(df_filtered.drop(columns=["Bulan_Tahun"]), use_container_width=True)
    else:
        st.info("Belum ada data untuk ditayangkan analitik.")

# ==========================================
# PAGE 5: AI ADVISOR
# ==========================================
elif menu_pilihan == "🤖 AI Advisor":
    st.title("🤖 AI Personal Gaji Advisor")
    st.caption("Tanya soalan atau minta AI analisa rekod gaji & jam kerja korang.")
    st.markdown("---")

    if not api_key:
        st.warning("⚠️ Sila masukkan **Gemini API Key** korang dekat bahagian sidebar sebelah kiri dulu.")
    elif len(df) == 0:
        st.info("Belum ada data rekod gaji. Masukkan data syif dulu untuk AI analisa.")
    else:
        client = genai.Client(api_key=api_key)

        data_summary = df.to_string(index=False)
        system_prompt = f"""
        Kaji data rekod gaji berikut dan jawab soalan pengguna secara santai, mesra, dan berpandukan fakta data.
        Bercakap dalam Bahasa Melayu santai.
        
        DATA REKOD GAJI PERIBADI USER:
        {data_summary}
        """

        if st.button("✨ Minta AI Analisa Gaji & Corak Kerja Saya"):
            with st.spinner("AI sedang membaca rekod gaji kau..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"{system_prompt}\n\nSila berikan ringkasan trend gaji, purata jam kerja, dan 2-3 cadangan berasaskan data di atas."
                    )
                    st.markdown("### 📝 Analisis AI:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Ralat sambungan AI: {e}")

        st.markdown("---")
        st.subheader("💬 Sembang Interaktif dengan AI")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Tanya apa-apa pasal gaji atau syif kerja korang..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        full_query = f"{system_prompt}\n\nSoalan User: {prompt}"
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=full_query
                        )
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Ralat AI: {e}")

# ==========================================
# PAGE 6: BACKUP & RESTORE
# ==========================================
elif menu_pilihan == "💾 Backup & Restore":
    st.title("💾 Pusat Backup & Restore Data")
    st.caption("Muat turun salinan data atau pulihkan data lama sekiranya berlaku kerosakan.")
    st.markdown("---")
    
    col_down, col_up = st.columns(2)
    
    with col_down:
        st.subheader("📥 Download Backup")
        st.write("Simpan salinan `rekod_gaji.csv` terus ke telefon/laptop korang.")
        if len(df) > 0:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD CSV BACKUP",
                data=csv_data,
                file_name=f"rekod_gaji_backup_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        else:
            st.info("Tiada data untuk di-download.")
            
    with col_up:
        st.subheader("📤 Restore / Upload Data")
        st.write("Muat naik fail CSV backup lama untuk dipulihkan.")
        uploaded_file = st.file_uploader("Pilih fail CSV Backup:", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file)
                if st.button("🔄 SAHKAN RESTORE DATA"):
                    buat_auto_backup()
                    df_uploaded.to_csv(FILE_PATH, index=False)
                    st.success("Data berjaya dipulihkan sepenuhnya!")
                    st.rerun()
            except Exception as e:
                st.error("Fail tidak sah atau korup. Pastikan ia format CSV yang betul.")
                
    st.markdown("---")
    
    st.subheader("📂 Senarai Auto-Backup Lokal")
    senarai_backup = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.csv')]
    senarai_backup.sort(reverse=True)
    
    if senarai_backup:
        pilih_backup = st.selectbox("Pilih fail salinan auto-backup terdahulu:", senarai_backup)
        if st.button("⏪ Pulihkan Fail Auto-Backup Ini"):
            target_path = os.path.join(BACKUP_DIR, pilih_backup)
            shutil.copy(target_path, FILE_PATH)
            st.success(f"Berjaya pulihkan data dari {pilih_backup}!")
            st.rerun()
    else:
        st.info("Belum ada salinan auto-backup dalam folder `backups/`.")
