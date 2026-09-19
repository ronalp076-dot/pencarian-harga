import streamlit as st
import pandas as pd
import os

# 1. Konfigurasi Tampilan Halaman Resmi Streamlit
st.set_page_config(
    page_title="Pencarian Harga Produk",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Sistem Pencarian Harga Produk")
st.write("Cari nama suku cadang atau barang untuk memantau detail harga pokok, HET, eceran, bengkel, dan grosir.")

# 2. Fungsi Memuat Data dari File (.xlsx atau .csv)
@st.cache_data
def load_data():
    file_csv = "data_item.csv"
    file_xlsx = "data_item.xlsx"
    
    try:
        if os.path.exists(file_xlsx):
            # Membaca file excel khusus pada sheet "data item new"
            df = pd.read_excel(file_xlsx, sheet_name="data item new")
            return df
        elif os.path.exists(file_csv):
            # Jika menggunakan file CSV
            df = pd.read_csv(file_csv)
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # Sinkronisasi nama kolom (menghilangkan spasi tak sengaja dan mengubah ke huruf kecil)
    df = df_raw.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Mapping kolom dari file Anda [Nama Item, Merek, Harga Pokok, Het, Ecer, Bengkel, Grosir]
    # Otomatis membersihkan kolom ecer jika mengandung spasi bawaan ('ecer ')
    df = df.rename(columns=lambda x: 'ecer' if 'ecer' in x else x)

    # Pastikan kolom-kolom utama yang Anda inginkan ada di dalam database
    target_columns = ['nama item', 'merek', 'harga pokok', 'het', 'ecer', 'bengkel', 'grosir']
    for col in target_columns:
        if col not in df.columns:
            df[col] = "-"

    # Filter data hanya untuk kolom yang diminta
    df_display = df[target_columns].copy()

    # 3. Kolom Input Pencarian Barang
    search_query = st.text_input("👉 Ketik Nama Item di sini (Contoh: 'As Shock', 'Oli', 'Ban'):", "").strip()

    if search_query:
        # Melakukan pencarian data yang cocok secara fleksibel
        results = df_display[df_display['nama item'].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            st.success(f"🎉 Ditemukan {len(results)} item yang cocok:")
            
            # 4. Tampilan Grid Resmi Streamlit yang Otomatis Sangat Rapi di HP Android & Laptop
            for idx, row in results.iterrows():
                # Fungsi pembantu untuk merapikan format Rupiah
                def format_idr(val):
                    try:
                        if pd.isna(val) or val == "" or val == "-":
                            return "-"
                        return f"Rp {float(val):,.0f}".replace(",", ".")
                    except:
                        return str(val)

                # Membuat kotak kontainer untuk satu produk
                with st.container(border=True):
                    st.subheader(f"📦 {row['nama item']}")
                    
                    # Membagi menjadi 3 kolom (Di HP akan otomatis menyusun ke bawah, di Laptop berjejer ke samping)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**🏷️ Merek:** {row['merek']}")
                        st.markdown(f"**💰 Harga Pokok:** {format_idr(row['harga pokok'])}")
                    with col2:
                        st.markdown(f"**⚠️ HET:** {format_idr(row['het'])}")
                        st.markdown(f"**🛒 Ecer:** {format_idr(row['ecer'])}")
                    with col3:
                        st.markdown(f"**🔧 Bengkel:** {format_idr(row['bengkel'])}")
                        st.markdown(f"**📦 Grosir:** {format_idr(row['grosir'])}")
        else:
            st.warning("Produk tidak ditemukan. Silakan periksa kembali ejaan kata kunci Anda.")
    else:
        st.info("💡 Tip: Ketik sebagian kata saja untuk memunculkan rekomendasi daftar suku cadang.")

else:
    st.warning("⚠️ File data (`data_item.xlsx` atau `data_item.csv`) tidak ditemukan di folder aplikasi Anda.")
    st.info("Pastikan Anda sudah menyimpan file database Anda dengan nama `data_item.xlsx` (sheet: 'data item new') atau `data_item.csv` di folder GitHub yang sama.")
