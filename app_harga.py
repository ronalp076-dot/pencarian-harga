import streamlit as st
import pandas as pd
import os

# 1. Konfigurasi Tampilan Halaman (Responsif untuk HP & Laptop)
st.set_page_config(
    page_title="Pencarian Harga Produk",
    page_icon="🔍",
    layout="wide",
)

# Kustomisasi CSS agar kartu harga terlihat profesional dan rapi saat dibuka di HP Android
st.markdown("""
    <style>
    .reportview-container .main .block-container { max-width: 1000px; }
    .price-card {
        background-color: #f8f9fa;
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #28a745;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-title { color: #1c3d5a; font-size: 1.15rem; font-weight: bold; margin-bottom: 10px; }
    .price-grid { display: flex; flex-wrap: wrap; gap: 15px; }
    .price-item { flex: 1; min-width: 130px; background: white; padding: 8px 12px; border-radius: 6px; border: 1px solid #e9ecef; }
    .price-label { font-size: 0.8rem; color: #6c757d; text-transform: uppercase; font-weight: bold; }
    .price-value { font-size: 1rem; color: #212529; font-weight: 600; margin-top: 2px; }
    </style>
""", unsafe_allowed_color_html=True)

st.title("🔍 Sistem Pencarian Harga Produk")
st.write("Cari nama suku cadang atau barang untuk memantau detail harga pokok, HET, eceran, bengkel, dan grosir.")

# 2. Fungsi Memuat Data dari File
@st.cache_data
def load_data():
    # Menemukan file data baik dalam format .csv maupun .xlsx di dalam folder
    file_csv = "data_item.csv"
    file_xlsx = "data_item.xlsx"
    
    try:
        if os.path.exists(file_xlsx):
            # Membaca file excel khusus pada sheet "data item new" sesuai permintaan Anda
            df = pd.read_excel(file_xlsx, sheet_name="data item new")
            return df
        elif os.path.exists(file_csv):
            # Jika di-deploy sebagai CSV, baca file CSV
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
    # Kami mendeteksi kolom ecer Anda memiliki spasi bawaan ('ecer '), kode ini otomatis membersihkannya
    df = df.rename(columns=lambda x: 'ecer' if 'ecer' in x else x)

    # Pastikan kolom-kolom utama yang Anda inginkan ada di dalam dataframe
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
            st.success(f"Ditemukan {len(results)} item yang cocok:")
            
            # 4. Tampilan Hasil Pencarian Berbentuk Kartu Ringkas (Sangat Nyaman di Layar HP)
            for idx, row in results.iterrows():
                # Fungsi pembantu untuk merapikan format Rupiah (.0f menghilangkan desimal/koma yang berantakan)
                def format_idr(val):
                    try:
                        if pd.isna(val) or val == "" or val == "-":
                            return "-"
                        return f"Rp {float(val):,.0f}".replace(",", ".")
                    except:
                        return str(val)

                # Render komponen antarmuka kartu harga
                st.markdown(f"""
                <div class="price-card">
                    <div class="price-title">📦 {row['nama item']}</div>
                    <div class="price-grid">
                        <div class="price-item"><div class="price-label">🏷️ Merek</div><div class="price-value">{row['merek']}</div></div>
                        <div class="price-item"><div class="price-label">💰 Harga Pokok</div><div class="price-value">{format_idr(row['harga pokok'])}</div></div>
                        <div class="price-item"><div class="price-label">⚠️ HET</div><div class="price-value">{format_idr(row['het'])}</div></div>
                        <div class="price-item"><div class="price-label">🛒 Ecer</div><div class="price-value">{format_idr(row['ecer'])}</div></div>
                        <div class="price-item"><div class="price-label">🔧 Bengkel</div><div class="price-value">{format_idr(row['bengkel'])}</div></div>
                        <div class="price-item"><div class="price-label">📦 Grosir</div><div class="price-value">{format_idr(row['grosir'])}</div></div>
                    </div>
                </div>
                """, unsafe_allowed_html=True)
        else:
            st.warning("Produk tidak ditemukan. Silakan periksa kembali ejaan kata kunci Anda.")
    else:
        st.info("💡 Tip: Ketik sebagian kata saja untuk memunculkan rekomendasi daftar suku cadang.")

else:
    st.warning("⚠️ File data (`data_item.xlsx` atau `data_item.csv`) tidak ditemukan di folder aplikasi Anda.")
    st.info("Pastikan Anda sudah menyimpan file Excel Anda dengan nama `data_item.xlsx` (dan pastikan sheet-nya bernama 'data item new') atau file CSV dengan nama `data_item.csv` di dalam folder yang sama.")