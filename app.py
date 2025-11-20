import streamlit as st
import pandas as pd
import io 
# --- PERBAIKAN IMPORT ---
from pyNmonAnalyzer.nmonparser import NMONParser
# ------------------------

st.set_page_config(layout="wide")

st.title('NMON Data Visualizer dengan Streamlit')
st.markdown('---')

# --- Fungsi Parsing NMON (BARU) ---
@st.cache_data
def load_and_parse_nmon(uploaded_file_obj):
    """Mengambil objek file NMON dari Streamlit, mem-parsingnya, dan mengembalikan DataFrames."""
    try:
        # Mengkonversi objek BytesIO Streamlit ke string yang bisa dibaca oleh NMONParser
        nmon_data_string = io.StringIO(uploaded_file_obj.getvalue().decode("utf-8"))
        
        # Inisialisasi dan parsing
        parser = NMONParser(nmon_data_string) # <--- PERBAIKAN PEMANGGILAN KELAS (NMONParser, bukan nmonParser.NMONParser)
        parsed_data = parser.parse()
        
        # Mengembalikan dictionary of DataFrames (misalnya, 'CPU_ALL', 'MEM', 'DISKREAD')
        return parsed_data
    except Exception as e:
        st.error(f"Gagal memproses file NMON: {e}")
        return None
# -----------------------------------

st.header('Unggah File NMON/CSV')
uploaded_file = st.file_uploader("Unggah file NMON (.nmon) atau CSV (.csv)", type=["nmon", "csv"])

if uploaded_file is not None:
    
    # Variabel untuk menampung DataFrames
    data_frames = {} 
    
    try:
        if uploaded_file.name.endswith('.csv'):
            # Membaca data CSV dengan header inferensi
            df_main = pd.read_csv(uploaded_file)
            data_frames['Main Data'] = df_main # Simpan sebagai satu DataFrame
            st.success("File CSV berhasil dimuat!")
        
        elif uploaded_file.name.endswith('.nmon'):
            st.info("Memproses file NMON... Harap tunggu.")
            
            # Panggil fungsi parsing
            parsed_results = load_and_parse_nmon(uploaded_file)
            
            if parsed_results is not None:
                data_frames = parsed_results # Simpan hasil parsing (dictionary of DFs)
                st.success(f"File NMON berhasil diproses! Ditemukan {len(data_frames)} metrik.")
            else:
                st.stop() # Hentikan jika parsing gagal dan sudah ada error message
        
        
        # --- LANJUTKAN DENGAN PEMILIHAN DATA ---
        
        # Mendapatkan semua nama metrik (keys dari dictionary)
        metric_names = list(data_frames.keys())
        
        if not metric_names:
            st.error("Tidak ada data yang valid ditemukan untuk dianalisis.")
            st.stop()

        # 1. Pilih Metrik Utama (CPU, MEM, DISK, dll.) di sidebar
        st.sidebar.header("1. Pilih Metrik Utama")
        selected_metric_key = st.sidebar.selectbox(
            'Pilih Kategori Metrik (Contoh: CPU_ALL, DISKREAD, MEM)',
            metric_names
        )

        # Ambil DataFrame yang dipilih
        df_selected = data_frames.get(selected_metric_key)
        
        if df_selected is not None:
            
            # 2. Pilih Kolom Data di sidebar
            st.sidebar.header("2. Pilih Kolom Data")
            available_columns = df_selected.columns.tolist()
            
            # Hapus kolom waktu atau index untuk visualisasi data
            time_cols = [col for col in available_columns if 'TIME' in col or 'Index' in col]
            data_cols = [col for col in available_columns if col not in time_cols]
            
            metric_selection = st.sidebar.multiselect(
                f'Pilih Kolom Data dari {selected_metric_key}',
                data_cols,
                default=data_cols[:3]
            )

            # --- Tampilkan Visualisasi ---
            if metric_selection:
                st.subheader(f"Visualisasi: {selected_metric_key} - {', '.join(metric_selection)}")
                
                # Buat DataFrame untuk charting (pastikan time index/kolom juga dimasukkan jika ada)
                cols_to_chart = time_cols + metric_selection
                chart_data = df_selected[cols_to_chart]
                
                # Gunakan st.line_chart atau library lain
                st.line_chart(chart_data, x=time_cols[0] if time_cols else None) 
                
                st.subheader(f"Data Mentah: {selected_metric_key}")
                st.dataframe(df_selected)

            else:
                st.info("Silakan pilih metrik data dari panel samping.")

    except Exception as e:
        st.error(f"Terjadi kesalahan fatal saat memproses file: {e}")
