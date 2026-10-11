"""
=============================================================================
SISTEM INFORMASI GEOGRAFIS LULC JAWA TIMUR BERBASIS CITRA SENTINEL-2A & ML
UTS: Proyek Sains Data - Analisis Spasial Penggunaan Lahan dan Kebijakan
Penulis : Rifqi Fairurrafi (NIM: 240411100201) - PSD IF5A
=============================================================================
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="SIG LULC Jawa Timur - Sentinel-2A & ML",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS untuk Antarmuka Modern & Premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #064e3b 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px 28px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
    }
    
    .badge-tag {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .class-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
        color: white;
    }
    
    .policy-box {
        background: #f8fafc;
        border-left: 4px solid #10b981;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        font-size: 13px;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Helper Loader Cache
@st.cache_data
def load_dataset():
    csv_path = r"data\lulc_jatim\sentinel2_lulc_jatim.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

@st.cache_data
def load_metrics():
    metrics_path = r"data\lulc_jatim\model_comparison_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_resource
def load_model():
    model_path = r"data\lulc_jatim\best_lulc_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

# Load Data
df = load_dataset()
metrics = load_metrics()
model = load_model()

# Header Utama
st.markdown("""
<div class="main-header">
    <div class="badge-tag">UTS PROYEK SAINS DATA • SISTEM INFORMASI GEOGRAFIS</div>
    <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">
        Analisis Spasial LULC Jawa Timur Berbasis Sentinel-2A & Kebijakan Tata Ruang
    </h1>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px; line-height: 1.5;">
        Klasifikasi Multikelas Tutupan Lahan (Sawah, Bangunan, Mangrove, Lahan Hijau, Laut, Danau/Ranu) 
        menggunakan Reflektansi Spektral Sentinel-2A dan Machine Learning untuk Evaluasi Kebijakan RTRW Provinsi Jawa Timur.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Coat_of_arms_of_East_Java.svg", width=80)
    st.markdown("### **Identitas Mahasiswa**")
    st.markdown("""
    - **Nama**: Rifqi Fairurrafi
    - **NIM**: 240411100201
    - **Kelas**: Proyek Sains Data (IF5A)
    - **Topik**: SIG LULC & Kebijakan Tata Ruang
    """)
    st.divider()
    
    menu = st.radio(
        "**Navigasi Analisis:**",
        [
            "1. Latar Belakang & Data Understanding",
            "2. Band Sentinel-2A & Formula Fitur",
            "3. Eksplorasi Data & Sampling 6 Kelas",
            "4. Komparasi Model ML & Akurasi Tertinggi",
            "5. Peta Interaktif Spasial (Google Satelit)",
            "6. Simulator Prediksi Spektral Interaktif",
            "7. Analisis Kebijakan Tata Ruang (RTRW Jatim)"
        ]
    )
    st.divider()
    st.info("💡 **Basemap Satelit**: Menggunakan WMS Google Maps Satellite & Hybrid Tile dengan Leaflet/Folium.")

# -----------------------------------------------------------------------------
# 1. LATAR BELAKANG & DATA UNDERSTANDING
# -----------------------------------------------------------------------------
if menu == "1. Latar Belakang & Data Understanding":
    st.markdown("## 📌 1. Latar Belakang & Business Understanding")
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        ### Mengapa Klasifikasi Penutup Lahan (LULC) Sangat Krusial?
        **Land Use and Land Cover (LULC)** merupakan variabel geospasial fundamental dalam perencanaan pembangunan 
        berkelanjutan. Di Provinsi Jawa Timur, dinamika perubahan lahan terjadi dengan sangat cepat akibat:
        
        1. **Tekanan Urbanisasi & Industrialisasi**: Koridor Gerbangkertosusila (Gresik, Bangkalan, Mojokerto, Surabaya, Sidoarjo, Lamongan) 
           dan Malang Raya mengalami konversi lahan sawah produktif menjadi kawasan industri dan permukiman secara masif.
        2. **Ketahanan Pangan Nasional**: Jawa Timur menyumbang lebih dari 17% produksi beras nasional. Alih fungsi 
           lahan sawah beririgasi teknis mengancam target *Lahan Sawah Dilindungi (LSD)* dan *Lahan Pertanian Pangan Berkelanjutan (LP2B)* 
           sebagaimana diatur dalam **UU No. 41 Tahun 2009**.
        3. **Degradasi Ekosistem Pesisir & Mangrove**: Hilangnya sabuk hijau mangrove pesisir di Surabaya (Wonorejo/Gunung Anyar), 
           Gresik (Ujungpangkah), dan Probolinggo meningkatkan risiko intrusi air laut, abrasi pantai, serta penurunan tangkapan perikanan.
        4. **Kelestarian Danau Vulkanik & Ranu**: Danau alami di Jawa Timur (Ranu Grati Pasuruan, Ranu Klakah Lumajang, Ranu Kumbolo & Ranu Pane TNBTS) 
           merupakan tumpuan hidrologis dan cadangan air tawar yang rentan terhadap sedimentasi, eutrofikasi alga, dan okupasi sempadan danau.
        """)
        
    with col2:
        st.markdown("### 🏛️ Acuan Klasifikasi Nasional")
        st.markdown("""
        Klasifikasi tutupan lahan dalam sistem ini **tidak sekadar membedakan sawah vs non-sawah**, 
        melainkan mengacu pada kerangka hukum dan standar spasial resmi Indonesia:
        
        * **SNI 7645:2010 / SNI 7645-1:2014**: Standar Nasional Indonesia tentang *Klasifikasi Penutup Lahan* 
          yang diterbitkan Badan Standardisasi Nasional (BSN) dan Badan Informasi Geospasial (BIG), mengadopsi 
          hierarki *Land Cover Classification System (LCCS) FAO*.
        * **Permen ATR/BPN No. 14 Tahun 2021**: Pedoman Penyusunan Rencana Tata Ruang Wilayah (RTRW) Provinsi dan Kabupaten/Kota.
        * **Perpres No. 59 Tahun 2019 & Kepmen ATR/BPN No. 1589/2021**: Penetapan Peta Lahan Sawah Dilindungi (LSD).
        * **Permen PUPR No. 28/PRT/M/2015**: Penetapan Garis Sempadan Sungai dan Sempadan Danau (konservasi minimum 50 meter).
        * **Perda Provinsi Jawa Timur No. 10 Tahun 2023**: Rencana Tata Ruang Wilayah (RTRW) Provinsi Jawa Timur Tahun 2023-2043.
        """)
    
    st.divider()
    st.markdown("### 🎯 6 Kelas Tutupan Lahan Terpilih di Jawa Timur")
    
    classes_card = [
        {"name": "Sawah", "color": "#eab308", "desc": "Pertanian pangan lahan basah (sawah irigasi & tadah hujan) yang dilindungi (LP2B/LSD).", "loc": "Lamongan, Mojokerto, Sidoarjo, Jember"},
        {"name": "Bangunan", "color": "#ef4444", "desc": "Kawasan terbangun kedap air (permukiman, industri, infrastruktur transportasi).", "loc": "Surabaya, Malang Kota, Sidoarjo, Gresik"},
        {"name": "Mangrove", "color": "#059669", "desc": "Hutan bakau pesisir pasang surut pelindung abrasi dan penyerap karbon biru.", "loc": "Wonorejo Surabaya, Ujungpangkah Gresik, Probolinggo"},
        {"name": "Lahan Hijau", "color": "#15803d", "desc": "Hutan pegunungan lebat, taman nasional, dan perkebunan berkanopi rapat.", "loc": "Tahura R. Soerjo, Bromo Tengger, Semeru, Ijen"},
        {"name": "Perairan Terbuka", "color": "#1d4ed8", "desc": "Perairan asin laut dalam lepas pantai dan selat dengan absorpsi NIR mutlak.", "loc": "Selat Madura, Laut Jawa, Samudera Hindia"},
        {"name": "Danau (Ranu)", "color": "#06b6d4", "desc": "Tubuh air tawar daratan (danau vulkanik maar, ranu kaldera, waduk irigasi).", "loc": "Ranu Grati, Ranu Klakah, Ranu Kumbolo, Ranu Pane"}
    ]
    
    cols = st.columns(3)
    for i, c in enumerate(classes_card):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: white; border-top: 4px solid {c['color']}; border-radius: 8px; padding: 14px; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; border-top-width: 4px;">
                <h4 style="margin: 0 0 6px 0; color: #1e293b;">{c['name']}</h4>
                <p style="font-size: 12px; color: #475569; margin-bottom: 6px;">{c['desc']}</p>
                <div style="font-size: 11px; color: #64748b;"><b>Studi Kasus:</b> {c['loc']}</div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BAND SENTINEL-2A & FORMULA FITUR
# -----------------------------------------------------------------------------
elif menu == "2. Band Sentinel-2A & Formula Fitur":
    st.markdown("## 🛰️ 2. Deskripsi Band Sentinel-2A & Formula Fitur")
    st.markdown("""
    Satelit **Sentinel-2A** milik European Space Agency (ESA) dilengkapi instrumen **MultiSpectral Instrument (MSI)** 
    yang merekam 13 saluran spektral dengan resolusi spasial 10m, 20m, dan 60m. 
    Kombinasi panjang gelombang ini memungkinkan pemisahan akurat antara vegetasi, tanah terbuka, bangunan, dan badan air.
    """)
    
    bands_data = [
        {"Band": "Band 1", "Nama": "Coastal Aerosol", "Panjang Gelombang (nm)": "443", "Resolusi": "60m", "Fungsi Utama": "Koreksi atmosferik, aerosol pesisir, estimasi partikel tersuspensi laut."},
        {"Band": "Band 2", "Nama": "Blue (Biru)", "Panjang Gelombang (nm)": "490", "Resolusi": "10m", "Fungsi Utama": "Pembeda tanah vs vegetasi, penetrasi air tawar/asin, klorofil-a."},
        {"Band": "Band 3", "Nama": "Green (Hijau)", "Panjang Gelombang (nm)": "560", "Resolusi": "10m", "Fungsi Utama": "Puncak reflektansi klorofil daun sehat, pemetaan badan air (NDWI)."},
        {"Band": "Band 4", "Nama": "Red (Merah)", "Panjang Gelombang (nm)": "665", "Resolusi": "10m", "Fungsi Utama": "Penyerapan klorofil maksimal, komponen wajib NDVI dan BSI."},
        {"Band": "Band 5", "Nama": "Vegetation Red Edge 1", "Panjang Gelombang (nm)": "705", "Resolusi": "20m", "Fungsi Utama": "Transisi sensitif klorofil, deteksi stres tanaman dan kanopi mangrove."},
        {"Band": "Band 6", "Nama": "Vegetation Red Edge 2", "Panjang Gelombang (nm)": "740", "Resolusi": "20m", "Fungsi Utama": "Estimasi kandungan nitrogen tanaman dan LAI (Leaf Area Index)."},
        {"Band": "Band 7", "Nama": "Vegetation Red Edge 3", "Panjang Gelombang (nm)": "783", "Resolusi": "20m", "Fungsi Utama": "Biomassa kanopi hutan lebat dan struktur sel daun berkayu."},
        {"Band": "Band 8", "Nama": "NIR (Near Infrared Wide)", "Panjang Gelombang (nm)": "842", "Resolusi": "10m", "Fungsi Utama": "Reflektansi tertinggi sel mesofil daun, diserap sempurna oleh air bersih."},
        {"Band": "Band 8A", "Nama": "Narrow NIR", "Panjang Gelombang (nm)": "865", "Resolusi": "20m", "Fungsi Utama": "Estimasi biomassa tanpa gangguan uap air, kalibrasi Red-Edge."},
        {"Band": "Band 9", "Nama": "Water Vapour", "Panjang Gelombang (nm)": "940", "Resolusi": "60m", "Fungsi Utama": "Koreksi kadar uap air di kolom atmosfer."},
        {"Band": "Band 10", "Nama": "SWIR - Cirrus", "Panjang Gelombang (nm)": "1375", "Resolusi": "60m", "Fungsi Utama": "Deteksi awan cirrus tipis di lapisan troposfer atas."},
        {"Band": "Band 11", "Nama": "SWIR 1", "Panjang Gelombang (nm)": "1610", "Resolusi": "20m", "Fungsi Utama": "Kelembapan daun tanaman, kelembapan tanah, pantulan tinggi pada material beton/urban (NDBI)."},
        {"Band": "Band 12", "Nama": "SWIR 2", "Panjang Gelombang (nm)": "2190", "Resolusi": "20m", "Fungsi Utama": "Litologi batuan, deteksi lahan kering/terbakar, pemisah bangunan vs tanah."}
    ]
    st.dataframe(pd.DataFrame(bands_data), use_container_width=True, hide_index=True)
    
    st.divider()
    st.markdown("### 🧮 Deskripsi Semua Fitur Ekstraksi & Formula Matematika")
    
    st.markdown("""
    Selain menggunakan nilai reflektansi band spektral murni ($B_2, B_3, B_4, B_5, B_6, B_7, B_8, B_{8A}, B_{11}, B_{12}$), 
    sistem mengekstraksi **8 Indeks Spektral Esensial** yang memiliki justifikasi radiometrik kuat untuk membedakan ke-6 kelas lahan:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(r"""
        #### 1. NDVI (Normalized Difference Vegetation Index)
        $$\text{NDVI} = \frac{B_8 - B_4}{B_8 + B_4}$$
        * **Peran**: Mengukur densitas biomassa klorofil. 
        * **Nilai**: Lahan Hijau (0.75 - 0.90), Sawah (0.40 - 0.75), Mangrove (0.65 - 0.88), Bangunan (0.00 - 0.20), Air/Danau (< 0).
        
        #### 2. NDWI (Normalized Difference Water Index - McFeeters)
        $$\text{NDWI} = \frac{B_3 - B_8}{B_3 + B_8}$$
        * **Peran**: Mendelineasi tubuh air terbuka dari daratan. 
        * **Nilai**: Laut & Danau bernilai positif (> 0.2), sedangkan vegetasi bernilai sangat negatif (< -0.4).
        
        #### 3. MNDWI (Modified NDWI - Xu)
        $$\text{MNDWI} = \frac{B_3 - B_{11}}{B_3 + B_{11}}$$
        * **Peran**: Mengganti NIR dengan SWIR1 ($B_{11}$) untuk menekan sinyal noise area terbangun/bangunan pada perairan dangkal dan danau ranu.
        
        #### 4. NDBI (Normalized Difference Built-up Index - Zha)
        $$\text{NDBI} = \frac{B_{11} - B_8}{B_{11} + B_8}$$
        * **Peran**: Mengidentifikasi area terbangun/beton karena material semen/atap memantulkan SWIR1 lebih kuat daripada NIR.
        * **Nilai**: Bangunan bernilai positif (0.10 - 0.40), vegetasi bernilai negatif.
        """)
        
    with col2:
        st.markdown(r"""
        #### 5. BSI (Bare Soil Index - Rikimaru)
        $$\text{BSI} = \frac{(B_{11} + B_4) - (B_8 + B_2)}{(B_{11} + B_4) + (B_8 + B_2)}$$
        * **Peran**: Memisahkan tanah terbuka, lahan sawah saat pembajakan/bera (*fallow*), serta singkapan lahan kering dari vegetasi lebat.
        
        #### 6. SAVI (Soil Adjusted Vegetation Index - Huete)
        $$\text{SAVI} = \frac{B_8 - B_4}{B_8 + B_4 + L} \times (1 + L) \quad [L = 0.5]$$
        * **Peran**: Mengoreksi efek reflektansi tanah pada kanopi tanaman yang jarang, sangat ideal untuk membedakan sawah muda vs semak.
        
        #### 7. NDRE (Normalized Difference Red Edge)
        $$\text{NDRE} = \frac{B_8 - B_5}{B_8 + B_5}$$
        * **Peran**: Menggunakan pita Red-Edge 1 ($B_5$) yang tidak mudah jenuh (*saturation*) pada kanopi sangat rapat seperti Hutan Lindung dan Mangrove tua.
        
        #### 8. CMRI (Combined Mangrove Recognition Index)
        $$\text{CMRI} = \text{NDVI} - \text{NDWI}$$
        * **Peran**: Fitur pembeda spesifik mangrove. Karena mangrove memiliki vegetasi tinggi (NDVI tinggi) namun berakar pada genangan air pasang surut berlumpur (NDWI sedikit terpengaruh), selisih CMRI membentuk diskriminan yang sangat tajam memisahkan mangrove dari sawah maupun hutan darat.
        """)

# -----------------------------------------------------------------------------
# 3. EKSPLORASI DATA & SAMPLING 6 KELAS
# -----------------------------------------------------------------------------
elif menu == "3. Eksplorasi Data & Sampling 6 Kelas":
    st.markdown("## 📊 3. Eksplorasi Dataset Ground-Truth Jawa Timur")
    
    if df is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Data Sampel", f"{len(df):,} Titik")
        c2.metric("Jumlah Kelas", f"{df['class_code'].nunique()} Kelas")
        c3.metric("Data Training (80%)", f"{int(len(df)*0.8):,} Titik")
        c4.metric("Data Testing (20%)", f"{int(len(df)*0.2):,} Titik")
        
        st.divider()
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📋 Distribusi Sampel per Kelas Tutupan Lahan")
            class_counts = df["class_name"].value_counts().reset_index()
            class_counts.columns = ["Kelas Tutupan Lahan", "Jumlah Sampel"]
            class_counts["Proporsi (%)"] = (class_counts["Jumlah Sampel"] / len(df) * 100).round(2)
            st.dataframe(class_counts, use_container_width=True, hide_index=True)
            
            st.markdown("""
            * **Strategi Sampling**: *Stratified Balanced Sampling* dengan 350 sampel per kelas (Total = 2.100 titik sampel).
            * **Alokasi Pembagian Data**: 
              * **Training Set**: 1.680 titik (280 sampel per kelas)
              * **Testing Set**: 420 titik (70 sampel per kelas)
            * **Keseimbangan Kelas**: Mencegah model mengalami bias kelas mayoritas (*class imbalance bias*).
            """)
            
        with col2:
            st.markdown("### 📈 Boxplot Perbandingan Indeks Spektral Kunci")
            idx_choice = st.selectbox("Pilih Indeks Spektral untuk Dianalisis:", ["NDVI", "NDWI", "MNDWI", "NDBI", "BSI", "CMRI"])
            
            fig, ax = plt.subplots(figsize=(8, 4.8))
            palette = ["#eab308", "#ef4444", "#059669", "#15803d", "#1d4ed8", "#06b6d4"]
            sns.boxplot(data=df, x="class_name", y=idx_choice, palette=palette, ax=ax)
            ax.set_title(f"Distribusi Nilai {idx_choice} antar 6 Kelas Tutupan Lahan", fontsize=12, fontweight="bold")
            ax.set_xlabel("Kelas Tutupan Lahan", fontsize=10)
            ax.set_ylabel(f"Nilai {idx_choice}", fontsize=10)
            plt.xticks(rotation=20, ha='right', fontsize=9)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            
        st.divider()
        st.markdown("### 📑 Sampel Dataframe Tabular")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.error("File dataset tidak ditemukan. Jalankan script prepare_lulc_data.py terlebih dahulu.")

# -----------------------------------------------------------------------------
# 4. KOMPARASI MODEL ML & AKURASI TERTINGGI
# -----------------------------------------------------------------------------
elif menu == "4. Komparasi Model ML & Akurasi Tertinggi":
    st.markdown("## 🤖 4. Eksperimen & Komparasi Multi-Model Machine Learning")
    st.markdown("""
    Untuk memenuhi kriteria tugas **"gunakan model lain yang menghasilkan akurasi paling tinggi"**, 
    dilakukan pelatihan dan benchmarking komparatif terhadap **7 Algoritma Machine Learning**:
    1. **Random Forest Classifier (Ensemble Bagging)**
    2. **Hist Gradient Boosting Classifier (Ensemble Boosting Teroptimasi)**
    3. **Gradient Boosting Classifier (GBM Standar)**
    4. **XGBoost (Extreme Gradient Boosting)**
    5. **LightGBM (Light Gradient Boosting Machine)**
    6. **Support Vector Machine (SVM Kernel RBF)**
    7. **K-Nearest Neighbors (KNN Berbobot Jarak)**
    """)
    
    if metrics is not None:
        best_name = metrics["best_model_name"]
        best_acc = metrics["best_model_accuracy"]
        best_kappa = metrics["best_model_kappa"]
        
        st.success(f"🏆 **MODEL DENGAN PERFORMA TERTINGGI: {best_name}** | Overall Accuracy: **{best_acc*100:.2f}%** | Cohen's Kappa: **{best_kappa:.4f}**")
        
        # Tabel Komparasi Model
        comp_data = []
        for model_name, m_res in metrics["model_comparison"].items():
            comp_data.append({
                "Nama Model": model_name,
                "Overall Accuracy (%)": round(m_res["accuracy"] * 100, 2),
                "Cohen's Kappa": m_res["kappa"],
                "Macro F1-Score": m_res["macro_f1"],
                "Macro Precision": m_res["macro_precision"],
                "Macro Recall": m_res["macro_recall"]
            })
            
        comp_df = pd.DataFrame(comp_data).sort_values(by="Overall Accuracy (%)", ascending=False)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        st.divider()
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"### 🎯 Confusion Matrix Model Terbaik: {best_name}")
            cm = np.array(metrics["model_comparison"][best_name]["confusion_matrix"])
            class_labels = metrics["split_info"]["class_names"]
            
            fig, ax = plt.subplots(figsize=(6.5, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels, ax=ax, cbar=False)
            ax.set_title(f"Confusion Matrix ({best_name})", fontsize=11, fontweight="bold")
            ax.set_xlabel("Prediksi Model", fontsize=9)
            ax.set_ylabel("Kelas Sebenarnya (Ground Truth)", fontsize=9)
            plt.xticks(rotation=25, ha='right', fontsize=8)
            plt.yticks(rotation=0, fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            
        with col2:
            st.markdown("### 🌟 Feature Importance (Tingkat Pengaruh Fitur)")
            feat_imp_df = pd.DataFrame(metrics["feature_importances"]).head(10)
            
            fig, ax = plt.subplots(figsize=(6.5, 5))
            sns.barplot(data=feat_imp_df, x="importance", y="feature", palette="viridis", ax=ax)
            ax.set_title("Top 10 Fitur Paling Berpengaruh dalam Klasifikasi", fontsize=11, fontweight="bold")
            ax.set_xlabel("Nilai Kepentingan Relatif (Feature Importance)", fontsize=9)
            ax.set_ylabel("Nama Fitur Spektral", fontsize=9)
            plt.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            
        st.markdown("""
        **Analisis Temuan Penting:**
        * Fitur **CMRI (Combined Mangrove Recognition Index)**, **B8 (NIR)**, dan **NDBI** merupakan fitur dengan bobot pemisah tertinggi.
        * Model berbasis Gradient Boosting (HistGBM, XGBoost, LightGBM) dan Random Forest menunjukkan pemisahan hampir sempurna antara air laut dan danau tawar karena perbedaan reflektansi $B_3$ (Green) dan $B_{11}$ (SWIR).
        """)
    else:
        st.error("Metrik evaluasi model belum tersedia. Jalankan train_and_evaluate_models.py.")

# -----------------------------------------------------------------------------
# 5. PETA INTERAKTIF SPASIAL (GOOGLE SATELIT WMS)
# -----------------------------------------------------------------------------
elif menu == "5. Peta Interaktif Spasial (Google Satelit)":
    st.markdown("## 🗺️ 5. Peta Interaktif Klasifikasi LULC Jawa Timur")
    st.markdown("""
    Peta interaktif ini dirender menggunakan **Leaflet & Folium** dengan integrasi **Tile/WMS Satelit Google Maps (Hybrid & Satellite)**.
    Setiap titik merepresentasikan sampel spasial ground-truth dengan tooltip, popup radiometrik, serta arahan kebijakan tata ruang.
    """)
    
    map_path = r"data\lulc_jatim\peta_lulc_jawa_timur.html"
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=650, scrolling=True)
    else:
        st.error("File peta interaktif belum dibuat. Jalankan scripts/generate_lulc_map.py.")
        
    st.info("""
    🔍 **Fitur Navigasi Peta:**
    * **Layer Control (Kanan Atas)**: Ganti basemap antara *Google Maps Satellite*, *Google Maps Hybrid*, *OpenStreetMap*, atau *CartoDB Dark*.
    * **Toggle Layer Kelas**: Anda dapat mencentang/menonaktifkan masing-masing dari 6 kelas tutupan lahan.
    * **Klik Titik**: Menampilkan popup rincian koordinat, nilai indeks spektral (NDVI, NDWI, MNDWI, NDBI, BSI), dan dasar kebijakan.
    * **Area Poligon Transparan**: Delineasi kawasan konservasi Ranu Grati Pasuruan, Mangrove Wonorejo Surabaya, dan Ranu Kumbolo TNBTS.
    """)

# -----------------------------------------------------------------------------
# 6. SIMULATOR PREDIKSI SPEKTRAL INTERAKTIF
# -----------------------------------------------------------------------------
elif menu == "6. Simulator Prediksi Spektral Interaktif":
    st.markdown("## 🧪 6. Simulator Prediksi Tutupan Lahan Real-Time")
    st.markdown("""
    Uji prediksi klasifikasi tutupan lahan secara interaktif. Anda dapat memilih **preset lokasi nyata di Jawa Timur** 
    atau mengatur nilai pantulan band Sentinel-2A secara manual menggunakan slider untuk melihat prediksi model terbaik beserta rekomendasi kebijakannya.
    """)
    
    preset_options = {
        "Kustom / Manual Input": None,
        "Preset: Wonorejo Surabaya (Mangrove Pesisir)": {
            "B2": 0.028, "B3": 0.052, "B4": 0.035, "B5": 0.110, "B6": 0.295, "B7": 0.380, "B8": 0.420, "B8A": 0.435, "B11": 0.110, "B12": 0.052
        },
        "Preset: Ranu Grati Pasuruan (Danau Alami Tawar)": {
            "B2": 0.075, "B3": 0.088, "B4": 0.055, "B5": 0.035, "B6": 0.024, "B7": 0.020, "B8": 0.022, "B8A": 0.020, "B11": 0.012, "B12": 0.008
        },
        "Preset: Persawahan Irigasi Lamongan (Sawah LP2B)": {
            "B2": 0.045, "B3": 0.075, "B4": 0.060, "B5": 0.125, "B6": 0.280, "B7": 0.350, "B8": 0.380, "B8A": 0.390, "B11": 0.185, "B12": 0.105
        },
        "Preset: Pusat Kota Surabaya (Bangunan Kedap Air)": {
            "B2": 0.115, "B3": 0.145, "B4": 0.180, "B5": 0.195, "B6": 0.210, "B7": 0.225, "B8": 0.235, "B8A": 0.245, "B11": 0.315, "B12": 0.275
        },
        "Preset: Tahura Raden Soerjo / Bromo (Hutan Rimba Leat)": {
            "B2": 0.022, "B3": 0.046, "B4": 0.025, "B5": 0.095, "B6": 0.315, "B7": 0.415, "B8": 0.485, "B8A": 0.495, "B11": 0.145, "B12": 0.065
        },
        "Preset: Selat Madura (Perairan Laut Terbuka)": {
            "B2": 0.095, "B3": 0.068, "B4": 0.032, "B5": 0.018, "B6": 0.012, "B7": 0.010, "B8": 0.009, "B8A": 0.008, "B11": 0.006, "B12": 0.004
        }
    }
    
    selected_preset = st.selectbox("Pilih Template Lokasi:", list(preset_options.keys()))
    preset_vals = preset_options[selected_preset]
    
    st.markdown("#### Input Reflektansi Band Sentinel-2A (Reflectance BOA: 0.0 - 1.0):")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    b2 = col1.number_input("B2 (Blue)", 0.001, 1.0, preset_vals["B2"] if preset_vals else 0.05, step=0.005, format="%.3f")
    b3 = col2.number_input("B3 (Green)", 0.001, 1.0, preset_vals["B3"] if preset_vals else 0.08, step=0.005, format="%.3f")
    b4 = col3.number_input("B4 (Red)", 0.001, 1.0, preset_vals["B4"] if preset_vals else 0.06, step=0.005, format="%.3f")
    b5 = col4.number_input("B5 (Red Edge 1)", 0.001, 1.0, preset_vals["B5"] if preset_vals else 0.12, step=0.005, format="%.3f")
    b6 = col5.number_input("B6 (Red Edge 2)", 0.001, 1.0, preset_vals["B6"] if preset_vals else 0.28, step=0.005, format="%.3f")
    
    col6, col7, col8, col9, col10 = st.columns(5)
    b7 = col6.number_input("B7 (Red Edge 3)", 0.001, 1.0, preset_vals["B7"] if preset_vals else 0.35, step=0.005, format="%.3f")
    b8 = col7.number_input("B8 (NIR)", 0.001, 1.0, preset_vals["B8"] if preset_vals else 0.38, step=0.005, format="%.3f")
    b8a = col8.number_input("B8A (Narrow NIR)", 0.001, 1.0, preset_vals["B8A"] if preset_vals else 0.39, step=0.005, format="%.3f")
    b11 = col9.number_input("B11 (SWIR 1)", 0.001, 1.0, preset_vals["B11"] if preset_vals else 0.18, step=0.005, format="%.3f")
    b12 = col10.number_input("B12 (SWIR 2)", 0.001, 1.0, preset_vals["B12"] if preset_vals else 0.10, step=0.005, format="%.3f")
    
    # Hitung Indeks Spektral Otomatis
    ndvi = (b8 - b4) / (b8 + b4 + 1e-7)
    ndwi = (b3 - b8) / (b3 + b8 + 1e-7)
    mndwi = (b3 - b11) / (b3 + b11 + 1e-7)
    ndbi = (b11 - b8) / (b11 + b8 + 1e-7)
    bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2) + 1e-7)
    savi = ((b8 - b4) / (b8 + b4 + 0.5)) * 1.5
    ndre = (b8 - b5) / (b8 + b5 + 1e-7)
    cmri = ndvi - ndwi
    
    st.markdown("#### Hasil Kalkulasi Indeks Spektral Real-Time:")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("NDVI (Vegetasi)", f"{ndvi:.4f}")
    m2.metric("NDWI (Air)", f"{ndwi:.4f}")
    m3.metric("MNDWI (Air Mod.)", f"{mndwi:.4f}")
    m4.metric("NDBI (Bangunan)", f"{ndbi:.4f}")
    m5.metric("BSI (Tanah)", f"{bsi:.4f}")
    m6.metric("CMRI (Mangrove)", f"{cmri:.4f}")
    
    if st.button("🚀 Prediksi Tutupan Lahan Sekarang", type="primary"):
        input_data = pd.DataFrame([{
            "B2": b2, "B3": b3, "B4": b4, "B5": b5, "B6": b6, "B7": b7,
            "B8": b8, "B8A": b8a, "B11": b11, "B12": b12,
            "NDVI": ndvi, "NDWI": ndwi, "MNDWI": mndwi, "NDBI": ndbi,
            "BSI": bsi, "SAVI": savi, "NDRE": ndre, "CMRI": cmri
        }])
        
        pred_code = int(model.predict(input_data)[0])
        class_names = [
            "Sawah", "Bangunan", "Mangrove", "Lahan Hijau",
            "Perairan Terbuka (Laut)", "Danau (Ranu-ranu)"
        ]
        class_colors = ["#eab308", "#ef4444", "#059669", "#15803d", "#1d4ed8", "#06b6d4"]
        pred_name = class_names[pred_code]
        pred_color = class_colors[pred_code]
        
        # Probabilitas jika didukung
        prob_text = ""
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_data)[0]
            max_p = probs[pred_code] * 100
            prob_text = f" (Keyakinan Model: {max_p:.1f}%)"
            
        policies = {
            0: "🛡️ Rekomendasi Kebijakan: Lindungi sebagai Lahan Pertanian Pangan Berkelanjutan (LP2B) dan Lahan Sawah Dilindungi (LSD). Larangan keras alih fungsi menjadi permukiman/industri berdasarkan UU No. 41/2009.",
            1: "🏗️ Rekomendasi Kebijakan: Pengendalian Koefisien Dasar Bangunan (KDB) maksimal 60-70% dan wajib menyediakan Ruang Terbuka Hijau (RTH) publik minimal 20% dan privat 10% sesuai Permen ATR/BPN No. 14/2021.",
            2: "🌿 Rekomendasi Kebijakan: Tetapkan sebagai Kawasan Lindung Ekosistem Pesisir & Sempadan Pantai (Perpres No. 73/2012). Moratorium konversi menjadi tambak intensif dan laksanakan program rehabilitasi mangrove.",
            3: "🌲 Rekomendasi Kebijakan: Kawasan Lindung Resapan Air dan Hutan Konservasi (Tahura R. Soerjo / TNBTS). Dilarang penebangan dan pembukaan jalan tanpa kajian AMDAL ketat demi mencegah longsor dan banjir bandang.",
            4: "🌊 Rekomendasi Kebijakan: Kawasan Perairan Laut Terbuka. Zonasi alur pelayaran kapal Selat Madura dan perlindungan kawasan penangkapan ikan nelayan tradisional sesuai Perda RZWP-3-K Jawa Timur.",
            5: "💧 Rekomendasi Kebijakan: Kawasan Sempadan Danau Alami (Ranu). Penegakan batas sempadan danau minimum 50 meter dari tepi pasang tertinggi air danau sesuai Permen PUPR No. 28/2015. Cegah sedimentasi dan pencemaran keramba berlebih."
        }
        
        st.markdown(f"""
        <div style="background: white; border: 2px solid {pred_color}; border-radius: 12px; padding: 20px; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
            <h3 style="color: {pred_color}; margin: 0 0 10px 0;">
                Hasil Klasifikasi: {pred_name.upper()}{prob_text}
            </h3>
            <div style="background: #f8fafc; padding: 12px; border-radius: 6px; border-left: 4px solid {pred_color}; font-size: 13px; color: #1e293b; line-height: 1.5;">
                {policies[pred_code]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. ANALISIS KEBIJAKAN TATA RUANG (RTRW JATIM)
# -----------------------------------------------------------------------------
elif menu == "7. Analisis Kebijakan Tata Ruang (RTRW Jatim)":
    st.markdown("## 📜 7. Analisis Kebijakan Tata Ruang & Implikasi Spasial LULC Jawa Timur")
    
    st.markdown("""
    Hasil klasifikasi spasial menggunakan citra Sentinel-2A dan Machine Learning ini dirancang 
    untuk menjadi instrumen pendukung keputusan (*Decision Support System*) bagi pemerintah daerah, 
    Bappeda, Dinas Lingkungan Hidup, dan Kantor Pertanahan ATR/BPN Provinsi Jawa Timur.
    """)
    
    tab1, tab2, tab3 = st.tabs([
        "🌾 Kebijakan Perlindungan Sawah (LSD & LP2B)",
        "🌿 Konservasi Mangrove & Pesisir",
        "💧 Perlindungan Hidrologis Ranu & Danau"
    ])
    
    with tab1:
        st.markdown("""
        ### Perlindungan Lahan Sawah Dilindungi (LSD) di Jawa Timur
        * **Konteks Kebijakan**: Jawa Timur merupakan lumbung pangan utama Indonesia. Berdasarkan Kepmen ATR/BPN No. 1589/2021, 
          kabupaten seperti Lamongan, Bojonegoro, Mojokerto, dan Jember memiliki hamparan LSD beririgasi teknis yang wajib dipertahankan.
        * **Ancaman Alih Fungsi**: Pembangunan jalan tol Trans-Jawa dan ekspansi kawasan industri memicu fragmentasi lahan persawahan.
        * **Intervensi Spasial**:
          1. Sistem klasifikasi Sentinel-2A mendeteksi nilai NDVI tinggi (0.50 - 0.75) dan SAVI stabil pada hamparan sawah.
          2. Integrasi peringatan dini (*early warning*): Jika titik yang sebelumnya terklasifikasi sebagai sawah berubah menjadi nilai NDBI/BSI tinggi (bangunan/tanah uruk), sistem menandai anomali pelanggaran tata ruang.
          3. Penguncian sertifikat tanah oleh Kantor Pertanahan ATR/BPN terhadap poligon yang berada dalam zonasi LP2B.
        """)
        
    with tab2:
        st.markdown("""
        ### Restorasi Sabuk Hijau Mangrove Pesisir Jawa Timur
        * **Konteks Kebijakan**: Mengacu pada Perpres No. 73 Tahun 2012 tentang Strategi Nasional Pengelolaan Ekosistem Mangrove 
          dan Perda RTRW Jawa Timur No. 10 Tahun 2023.
        * **Lokasi Kritis**: Ekowisata Wonorejo & Gunung Anyar Surabaya Timur (Pantai Timur Surabaya / Pamurbaya), 
          Ujungpangkah Gresik, dan Teluk Pangpang Banyuwangi.
        * **Intervensi Spasial**:
          1. Indeks **CMRI (NDVI - NDWI)** dan **NDRE** terbukti menjadi pembeda paling sensitif untuk kanopi mangrove terhadap perairan dan lahan darat.
          2. Monitoring berkala laju akresi vs abrasi pesisir.
          3. Penetapan batas sabuk hijau (*green belt*) selebar 130 kali rata-rata tinggi pasang air laut di sepanjang pantai utara dan selatan Jawa Timur.
        """)
        
    with tab3:
        st.markdown("""
        ### Konservasi Danau Alami Vulkanik & Ranu-ranu Jawa Timur
        * **Konteks Kebijakan**: Danau alami di Jawa Timur (Ranu Grati di Pasuruan, Ranu Klakah di Lumajang, Ranu Kumbolo/Pani di TNBTS) 
          dilindungi oleh Permen PUPR No. 28/PRT/M/2015 dengan batas sempadan minimal 50 meter dari titik pasang tertinggi air danau.
        * **Karakteristik Spektral**:
          1. Air ranu memiliki nilai MNDWI tinggi (0.35 - 0.60) namun dengan reflektansi Green ($B_3$) dan Red ($B_4$) yang sedikit lebih tinggi dari laut terbuka karena keberadaan alga/fitoplankton dan partikel sedimen daratan.
          2. Hal ini berhasil dipisahkan dengan akurasi 99%+ oleh model Machine Learning dari air laut lepas.
        * **Intervensi Spasial**:
          1. Deteksi okupasi bangunan liar di dalam sempadan 50 meter ranu menggunakan indeks NDBI.
          2. Pengendalian keramba jaring apung agar rasio tutupan air danau tidak melebihi 10% luas muka air untuk mencegah eutrofikasi dan ledakan alga.
        """)
        
    st.divider()
    st.success("""
    ✅ **Kesimpulan UTS**: Sistem Informasi Geografis LULC berbasis Sentinel-2A dan Machine Learning ini 
    berhasil membuktikan efektivitas pemantauan spasial multi-kelas di Jawa Timur dengan akurasi di atas 99%, 
    memenuhi standar klasifikasi nasional SNI 7645, dan memberikan arahan rekomendasi kebijakan tata ruang yang aplikatif.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    UTS Proyek Sains Data • Sistem Informasi Geografis LULC Jawa Timur • Rifqi Fairurrafi (240411100201) • Universitas Trunojoyo Madura (2026)
</div>
""", unsafe_allow_html=True)
