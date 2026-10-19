import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from PIL import Image
import io
import os
import json

# ==============================================================================
# 1. KONFIGURASI HALAMAN & TEMA (CLEAN CORPORATE DESIGN)
# ==============================================================================
st.set_page_config(
    page_title="Enterprise AI & Data Hub",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk menyembunyikan header Streamlit dan menempatkan branding di dasar sidebar.
st.markdown("""
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    .stHeading h2 {color: #16466B; font-weight: 700;}
    .stHeading h3 {color: #245D80; font-weight: 600;}
    .stAlert {border-radius: 10px;}
    .metric-card {background-color: #EAF6FD; border: 1px solid #CDE7F7; padding: 10px; border-radius: 8px;}
    header[data-testid="stHeader"] {display: none;}
    section[data-testid="stSidebar"] [data-testid="stFullScreenFrame"] > div {
        width: 100%;
    }
    section[data-testid="stSidebar"] [data-testid="stImage"] {
        width: 100%;
        justify-content: center;
    }
    section[data-testid="stSidebar"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .sidebar-brand {
        position: fixed;
        left: 0;
        bottom: 0.75rem;
        width: 300px;
        max-width: 100vw;
        color: #16466B;
        font-size: 1.05rem;
        font-weight: 700;
        padding: 0.75rem 0;
        border-top: 1px solid #CDE7F7;
        background: #E8F4FB;
        text-align: center;
    }
    @media (max-width: 768px) {
        header[data-testid="stHeader"] { display: flex; }
    }
    </style>
""", unsafe_allow_html=True)

# Membuat folder arsip data lokal jika belum ada di server/komputer Anda
SAVE_DIR = "saved_files"
CHAT_FILE = "chat_history.json"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "LogoStatlabChat_transparant.png")

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

with st.sidebar:
    logo_display = st.empty()

    #with st.expander("Ganti logo", expanded=False):
     #   uploaded_logo = st.file_uploader(
      #      "Unggah logo baru",
       #     type=["png", "jpg", "jpeg", "webp"],
        #    key="brand_logo_upload",
        #)
        #if uploaded_logo is not None:
        #    try:
         #       uploaded_logo.seek(0)
          #      with Image.open(uploaded_logo) as logo:
           #         logo.load()
            #        logo_buffer = io.BytesIO()
             #       logo.convert("RGBA").save(logo_buffer, format="PNG")
              #  logo_content = logo_buffer.getvalue()

               # logo_needs_saving = not os.path.isfile(LOGO_PATH)
               # if not logo_needs_saving:
                #    with open(LOGO_PATH, "rb") as existing_logo:
                #        logo_needs_saving = existing_logo.read() != logo_content
                #if logo_needs_saving:
                #    with open(LOGO_PATH, "wb") as logo_file:
                #        logo_file.write(logo_content)
                #st.caption("Logo tersimpan di folder aplikasi sebagai `logoStatlab_chat.png`.")
            #except (OSError, ValueError) as e:
             #   st.error(f"Logo tidak dapat diproses atau disimpan: {e}")

    if os.path.isfile(LOGO_PATH):
        logo_display.image(LOGO_PATH, width=150)

# Fungsi Pendukung Penyimpanan Lokal
def load_chat_history():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_history(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# ==============================================================================
# 2. INTEGRASI API GOOGLE GEN AI (STANDARD PRODUKSI STABIL)
# ==============================================================================
# Sesuai standard SDK terbaru, kita paksa routing ke API v1 stabil
gemini_api_key_st = st.secrets["GEMINI_API_KEY"]

API_KEY = os.environ.get("GEMINI_API_KEY", gemini_api_key_st)
client = genai.Client(
    api_key=API_KEY,
    http_options={'api_version': 'v1'}
)
MODEL_NAME = 'gemini-3.8-flash'

# ==============================================================================
# 3. SIDEBAR NAVIGATION (PREMIUM OPTION MENU)
# ==============================================================================
with st.sidebar:
    selected_menu = option_menu(
        menu_title="Menu Utama",
        options=["Chatbot Asisten", "Analisis & Statistik", "Pemindaian Gambar"],
        icons=["chat-left-text-fill", "bar-chart-line-fill", "camera-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px!", "background-color": "#EAF6FD"},
            "icon": {"color": "#5281A0", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#D8EDF9"},
            "nav-link-selected": {"background-color": "#3198CF"},
        }
    )
    
    # Fitur hapus riwayat chat langsung dari panel samping
    if selected_menu == "Chatbot Asisten":
        st.write("")
        if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
            if os.path.exists(CHAT_FILE):
                os.remove(CHAT_FILE)
            st.session_state.messages = []
            st.rerun()
    st.markdown("<div class='sidebar-brand'>💼 Corporate AI</div>", unsafe_allow_html=True)

# ==============================================================================
# 4. MONITOR DAN KONTEN HALAMAN UTAMA
# ==============================================================================

# ------------------------------------------------------------------------------
# HALAMAN 1: CHATBOT ASISTEN (DENGAN PENYIMPANAN DATA JSON LOKAL)
# ------------------------------------------------------------------------------
if selected_menu == "Chatbot Asisten":
    st.markdown("## 💬 Asisten Virtual Perusahaan")
    st.write("Gunakan chatbot ini untuk melakukan ekstraksi draf dokumen bisnis atau menjawab prosedur internal.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ketik instruksi atau pertanyaan bisnis di sini..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_chat_history(st.session_state.messages)
        except Exception as e:
            st.error(f"Gagal memproses permintaan: {e}")

# ------------------------------------------------------------------------------
# HALAMAN 2: ANALISIS DATA & STATISTIK (DENGAN REKOMENDASI AI & AUTO-STATISTICIAN)
# ------------------------------------------------------------------------------
elif selected_menu == "Analisis & Statistik":
    st.markdown("## 📊 Hub Intelijen Data & Uji Statistik Lengkap")
    st.write("Unggah laporan operasional (CSV) Anda untuk melakukan pengujian hipotesis saintifik secara otomatis.")
    
    col1, col2 = st.columns([2, 3]) # Proporsi layar: Kolom data kiri lebih ramping, hasil kanan lebih lebar
    
    with col1:
        st.markdown("### 📂 Input Dataset")
        uploaded_file = st.file_uploader("Seret file CSV ke sini", type=["csv"], key="csv_data")
        
        if uploaded_file is not None:
            # Otomatis save file asli ke direktori lokal server
            file_path = os.path.join(SAVE_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.caption(f"💾 File diarsipkan aman secara lokal di: `{file_path}`")
            
            df = pd.read_csv(file_path)
            st.markdown("**Pratinjau Data (10 Baris Pertama):**")
            st.dataframe(df, use_container_width=True, height=180)
            
            # Klasifikasi otomatis tipe data untuk pemetaan statistik
            kolom_numerik = df.select_dtypes(include=['number']).columns.tolist()
            kolom_kategori = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            st.markdown("---")
            st.markdown("##### 💡 Rekomendasi Analisis AI (Smart Suggestion)")
            
            # AI membaca susunan kolom untuk memberikan saran pengujian terbaik
            skema_tabel = f"Kolom Angka/Numerik: {kolom_numerik}\nKolom Teks/Kategori: {kolom_kategori}"
            with st.spinner("AI sedang membaca struktur data Anda..."):
                prompt_rekomendasi = f"""
                Kamu adalah sistem Data Analyst Otomatis. Tolong baca skema dataset ini:
                {skema_tabel}
                
                Berdasarkan kolom yang tersedia, berikan 1 rekomendasi uji statistik terbaik yang paling cocok dilakukan (Misal: Uji ANOVA, Chi-Square, atau Korelasi).
                Tuliskan rekomendasi Anda secara singkat dan padat dalam maksimal 3 kalimat di dalam kotak informasi.
                """
                try:
                    rekomendasi_ai = client.models.generate_content(model=MODEL_NAME, contents=prompt_rekomendasi)
                    st.info(rekomendasi_ai.text)
                except Exception as e:
                    st.caption("Gagal memuat rekomendasi otomatis.")
            
            st.markdown("---")
            query_data = st.text_input("Instruksi Analisis Tambahan (Opsional)", "Berikan tren utama.")

    with col2:
        st.markdown("### ⚙️ Dasbor Kontrol Statistik & Output")
        
        if uploaded_file is not None:
            # Menu pilihan analisis (Dari pembacaan umum hingga modul otomatis penuh)
            jenis_uji = st.selectbox(
                "Pilih Metode Analisis:", 
                [
                    "-- Ringkasan Umum & Baca Data --", 
                    "Uji Korelasi Pearson (Hubungan Angka)", 
                    "Uji Chi-Square Independensi (Hubungan Kategori)",
                    "🧠 AI Auto-Statistician (Semua Jenis Uji Statistik)"
                ]
            )
            st.write("---")
            
            # KONDISI A: ANALISIS UMUM
            if jenis_uji == "-- Ringkasan Umum & Baca Data --":
                if st.button("Jalankan Pemrosesan Laporan", use_container_width=True):
                    with st.spinner("AI menganalisis data..."):
                        data_summary = df.head(15).to_string()
                        full_prompt = f"Analisis data berikut secara komprehensif:\n{data_summary}\n\nInstruksi: {query_data}"
                        try:
                            response = client.models.generate_content(model=MODEL_NAME, contents=full_prompt)
                            st.markdown("##### 📄 Kesimpulan Eksekutif AI:")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Gagal memanggil AI: {e}")
                        
                        if len(kolom_numerik) >= 1:
                            fig, ax = plt.subplots(figsize=(6, 3))
                            df[kolom_numerik].plot(kind='line', ax=ax, color='#0284c7', linewidth=2)
                            plt.title("Visualisasi Tren Otomatis", fontsize=9, fontweight='bold')
                            st.pyplot(fig)

            # KONDISI B: UJI KORELASI MANUAL
            elif jenis_uji == "Uji Korelasi Pearson (Hubungan Angka)":
                if len(kolom_numerik) >= 2:
                    st.markdown("##### 🎯 Pengaturan Uji Korelasi")
                    c_kol1, c_kol2 = st.columns(2)
                    with c_kol1:
                        var1 = st.selectbox("Variabel Pertama (X):", kolom_numerik, key="v1")
                    with c_kol2:
                        var2 = st.selectbox("Variabel Kedua (Y):", kolom_numerik, key="v2")

                    if st.button("Hitung Signifikansi Korelasi", use_container_width=True):
                        df_clean = df[[var1, var2]].dropna()
                        koefisien_korelasi, p_value = stats.pearsonr(df_clean[var1], df_clean[var2])
                        m_kol1, m_kol2 = st.columns(2)
                        with m_kol1:
                            st.metric(label="Koefisien Korelasi (R)", value=f"{koefisien_korelasi:.4f}")
                        with m_kol2:
                            st.metric(label="p-Value (Signifikansi)", value=f"{p_value:.4f}")
                        with st.spinner("AI sedang menyusun interpretasi bisnis..."):
                            prompt_analisis = f"Interpretasikan hasil uji korelasi Pearson ini untuk direksi: Variabel {var1} vs {var2}, R={koefisien_korelasi:.4f}, p={p_value:.4f}. Jelaskan apakah hubungan kuat/lemah, dan signifikan (p < 0.05)."
                            response = client.models.generate_content(model=MODEL_NAME, contents=prompt_analisis)
                            st.success("##### 🧠 Interpretasi Bisnis AI:")
                            st.write(response.text)
                        fig, ax = plt.subplots(figsize=(6, 3))
                        sns.regplot(data=df_clean, x=var1, y=var2, ax=ax, color='#0284c7')
                        st.pyplot(fig)
                else:
                    st.warning("Data tidak memiliki cukup kolom angka untuk melakukan uji korelasi.")

            # KONDISI C: UJI CHI-SQUARE MANUAL
            elif jenis_uji == "Uji Chi-Square Independensi (Hubungan Kategori)":
                if len(kolom_kategori) >= 2:
                    st.markdown("##### 🎯 Pengaturan Uji Chi-Square")
                    ck_kol1, ck_kol2 = st.columns(2)
                    with ck_kol1:
                        cat1 = st.selectbox("Kategori Pertama:", kolom_kategori, key="c1")
                    with ck_kol2:
                        cat2 = st.selectbox("Kategori Kedua:", kolom_kategori, key="c2")

                    if st.button("Hitung Signifikansi Chi-Square", use_container_width=True):
                        tabel_kontingensi = pd.crosstab(df[cat1], df[cat2])
                        st.markdown("Tabel Crosstab Data:")
                        st.dataframe(tabel_kontingensi, use_container_width=True)
                        chi2, p, dof, expected = stats.chi2_contingency(tabel_kontingensi)
                        m_kol1, m_kol2 = st.columns(2)
                        with m_kol1:
                            st.metric(label="Nilai Chi-Square Hitung", value=f"{chi2:.4f}")
                        with m_kol2:
                            st.metric(label="p-Value", value=f"{p:.4f}")
                        with st.spinner("AI sedang menganalisis tingkat hubungan..."):
                            prompt_chi = f"Interpretasikan hasil uji Chi-Square ini untuk presentasi klien: Hubungan antara {cat1} dan {cat2}, Chi2={chi2:.4f}, p-value={p:.4f}. Berikan penjelasan apakah kedua faktor ini saling berpengaruh atau independen berdasarkan batas alpha 0.05."
                            response = client.models.generate_content(model=MODEL_NAME, contents=prompt_chi)
                            st.success("##### 🧠 Analisis Kategori AI:")
                            st.write(response.text)
                else:
                    st.warning("Data tidak memiliki cukup kolom teks/kategori untuk melakukan uji Chi-Square.")

            # KONDISI D: MODUL UTAMA - AI AUTO-STATISTICIAN
            elif jenis_uji == "🧠 AI Auto-Statistician (Semua Jenis Uji Statistik)":
                st.markdown("##### 🧠 Sistem Konsultan & Ahli Statistik Otomatis")
                st.write("Tuliskan metode statistik bebas yang Anda inginkan (Contoh: ANOVA, t-Test, Shapiro-Wilk, atau Regresi Linear).")
                instruksi_stats = st.text_area(
                    "Ketik Perintah Analisis Statistik:",
                    placeholder="Contoh: Lakukan uji normalitas Shapiro-Wilk pada kolom angka, lalu lakukan uji ANOVA untuk melihat pengaruh kolom kategori terhadap kolom angka tersebut."
                )
                if st.button("Jalankan Perhitungan AI Auto-Statistician", use_container_width=True):
                    with st.spinner("AI sedang memproses komputasi data dan merumuskan laporan sains data..."):
                        data_konteks = df.head(25).to_string()
                        prompt_auto_stats = f"""
                        Kamu adalah sistem kecerdasan buatan Auto-Statistician Enterprise. Tugasmu adalah mengeksekusi uji statistik sesuai permintaan pengguna.
                        Struktur dan Sampel Data Perusahaan:
                        {data_konteks}
                        Instruksi Pengujian Statistik dari Pengguna: {instruksi_stats}
                        Sajikan laporan formal hasil uji statistik dengan format terstruktur sebagai berikut:
                        1. Nama Uji Statistik yang Dipilih beserta argumentasi logis mengapa metode tersebut paling tepat untuk data ini.
                        2. Nilai Hasil Uji Matematis (Cantumkan nilai statistik uji, p-value, dan derajat kebebasan jika ada secara presisi).
                        3. Keputusan Hipotesis (Jelaskan secara tegas pakah H0 ditolak atau gagal ditolak berdasarkan batas signifikansi alpha 0.05).
                        4. Rekomendasi Bisnis/Operasional (Terjemahkan arti p-value tersebut menjadi keputusan strategis bagi direksi manajemen perusahaan target).
                        """
                        try:
                            response = client.models.generate_content(model=MODEL_NAME, contents=prompt_auto_stats)
                            st.success("##### 📋 Laporan Hasil Uji Statistik Formal Enterprise:")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Gagal menjalankan modul Auto-Statistician: {e}")
        else:
            st.info("Silakan seret file laporan CSV ke panel kiri untuk memuat dashboard kontrol statistik.")

# ------------------------------------------------------------------------------
# HALAMAN 3: PEMINDAIAN GAMBAR (MULTIMODAL VISION)
# ------------------------------------------------------------------------------
elif selected_menu == "Pemindaian Gambar":
    st.markdown("## 📸 Sistem Inspeksi Gambar & Visi Kamera")
    st.write("Kirimkan foto dokumentasi operasional, bukti kuitansi, atau foto logistik untuk dianalisis oleh sistem visi AI.")
    uploaded_image = st.file_uploader("Pilih gambar (PNG/JPG)", type=["png", "jpg", "jpeg"], key="image_data")
    if uploaded_image is not None:
        col_img, col_analysis = st.columns(2)
        with col_img:
            image = Image.open(uploaded_image)
            st.image(image, caption='Dokumentasi Berhasil Dimuat', use_container_width=True)
            instruction = st.text_input("Instruksi Gambar", "Jelaskan isi foto ini dengan detail untuk kebutuhan laporan bisnis.")
        with col_analysis:
            if st.button("Mulai Deteksi Objek Gambar", use_container_width=True):
                with st.spinner("Mengekstraksi informasi gambar..."):
                    try:
                        response = client.models.generate_content(model=MODEL_NAME, contents=[image, instruction])
                        st.success("#### Hasil Analisis Visi Perusahaan:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Gagal membaca gambar: {e}")