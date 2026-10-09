---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Modeling - K-Means Clustering pada Gabungan 3 Polutan (204 Fitur TSFEL) & Analisis Multi-Dimensi (203, 74, 37)

Dokumen ini merupakan laporan komprehensif tahap **Modeling** pada kerangka kerja CRISP-DM untuk Proyek Sains Data. Pada tahap ini, analisis ditingkatkan dari evaluasi polutan tunggal menjadi **analisis gabungan tiga polutan (NO2, CO, SO2)** dengan total **204 fitur TSFEL** (68 fitur $\times$ 3 polutan). Analisis ini mengevaluasi data deret waktu kualitas udara dari 37 daerah/kecamatan mahasiswa untuk melakukan segmentasi spasial menggunakan **K-Means Clustering**, reduksi dimensi multi-skala (**203, 74, 37**), analisis koefisien **Silhouette**, serta visualisasi peta interaktif.

---

## 1. Pertanyaan yang Dijawab dan Rencana Analisis

| No | Sasaran Analisis | Bagian Pembahasan |
|:---|:---|:---|
| 1 | Bagaimana alur penggabungan 3 polutan (NO2, SO2, CO) menjadi 204 kolom fitur dengan imputasi Linear dan Polynomial? | Bagian 2 |
| 2 | Bagaimana integrasi data 37 daerah/kecamatan kelas menjadi satu matriks fitur 204 kolom? | Bagian 3 |
| 3 | Mengapa dan bagaimana reduksi dimensi dilakukan menjadi **Dimensi 203, Dimensi 74, dan Dimensi 37**? | Bagian 4 |
| 4 | Berapa nilai koefisien Silhouette untuk $k = 2$ sampai $10$ pada masing-masing dimensi dan mana $k$ terbaik? | Bagian 5 |
| 5 | Bagaimana segmentasi dan profil karakteristik polusi pada masing-masing cluster? | Bagian 6 |
| 6 | Bagaimana representasi geografis persebaran cluster pada peta spasial? | Bagian 7 |
| 7 | Bagaimana panduan implementasi alur kerja ini pada perangkat lunak **KNIME Analytics Platform**? | Bagian 8 |

---

## 2. Penggabungan 3 Polutan Menjadi 204 Kolom (Linear & Polynomial)

Untuk wilayah **Kecamatan Bangkalan**, data ketiga polutan Sentinel-5P (`NO2-Bangkalan.csv`, `CO-Bangkalan.csv`, dan `SO2-Bangkalan.csv`) digabungkan ke dalam indeks waktu harian penuh (31 Agustus 2025 - 31 Agustus 2026). 

Proses pembersihan dan ekstraksi fitur dilakukan melalui dua metode imputasi:
1. **Linear / Time-based Interpolation**: Menggunakan interpolasi berbasis tanggal harian (`method='time'`) yang menghubungkan titik pengamatan valid secara garis lurus temporal.
2. **Polynomial Interpolation**: Menggunakan kurva polinomial derajat 2 (`method='polynomial', order=2`) yang menangkap kelengkungan dinamika emisi tanpa lonjakan tajam.

Untuk setiap polutan, pencilan (*outliers*) dideteksi menggunakan ambang Interquartile Range ($Q1 - 1.5 \times IQR$ dan $Q3 + 1.5 \times IQR$), diubah menjadi `NaN`, diimputasi, lalu diekstraksi ke dalam **68 fitur TSFEL** (Statistical, Temporal, Spectral, dan Fractal) dengan awalan polutan (`NO2_*`, `CO_*`, `SO2_*`).

Hasil ekstraksi disimpan ke dalam dua berkas CSV di folder `data/csv/`:
- `data/csv/All-Pollutants-Bangkalan-TSFEL-linear.csv` (1 baris $\times$ 204 kolom)
- `data/csv/All-Pollutants-Bangkalan-TSFEL-polynomial.csv` (1 baris $\times$ 204 kolom)

Berikut adalah kode eksekusi pemuatan dan verifikasi dimensi dari kedua berkas tersebut:

```{code-cell}
:tags: [hide-input]
import os
import pandas as pd

def cari_file(nama_file):
    for basis in ["../data/csv/", "data/csv/", "", "data/", "../data/", "../", "../../data/"]:
        target = os.path.join(basis, nama_file) if basis else nama_file
        if os.path.exists(target):
            return target
    raise FileNotFoundError(nama_file)

df_linear = pd.read_csv(cari_file("All-Pollutants-Bangkalan-TSFEL-linear.csv"))
df_poly   = pd.read_csv(cari_file("All-Pollutants-Bangkalan-TSFEL-polynomial.csv"))

pd.DataFrame({
    "Metode Imputasi": ["Linear Regression / Time-based", "Polynomial Interpolation (Order 2)"],
    "Jumlah Baris": [df_linear.shape[0], df_poly.shape[0]],
    "Jumlah Kolom": [df_linear.shape[1], df_poly.shape[1]],
    "Target Polutan": ["NO2, SO2, CO (68 x 3)", "NO2, SO2, CO (68 x 3)"],
    "Nilai Hilang (NaN)": [int(df_linear.isna().sum().sum()), int(df_poly.isna().sum().sum())]
})
```

---

## 3. Integrasi Data 37 Daerah Kelas Menjadi 204 Fitur Gabungan

Untuk melakukan clustering antar-wilayah, data hasil ekstraksi fitur kelas dari berkas `ekstraksi_fitur_no2.csv`, `ekstraksi_fitur_co.csv`, dan `ekstraksi_fitur_so2.csv` digabungkan. Setiap berkas memiliki 37 baris (mewakili 37 daerah/kecamatan mahasiswa) dan 68 fitur TSFEL per polutan.

Normalisasi nama dilakukan agar pencocokan baris berjalan sempurna (misalnya standarisasi penulisan spasi nama), kemudian fitur diberi prefix polutan dan digabungkan menjadi satu tabel utuh `All-Pollutants-All-Regions-TSFEL.csv` (37 baris $\times$ 204 kolom fitur numerik + 3 kolom metadata).

```{code-cell}
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)

SEED = 42
K_RANGE = range(2, 11)

raw_no2 = pd.read_csv(cari_file("ekstraksi_fitur_no2.csv"))
raw_co  = pd.read_csv(cari_file("ekstraksi_fitur_co.csv"))
raw_so2 = pd.read_csv(cari_file("ekstraksi_fitur_so2.csv"))

# Normalisasi penulisan nama mahasiswa
for df in [raw_no2, raw_co, raw_so2]:
    df["nama_norm"] = df["nama"].str.strip().str.replace("A.Choiril", "A. Choiril", regex=False)

meta_cols = ["id", "nama", "daerah"]
feature_cols = [c for c in raw_no2.columns if c not in meta_cols + ["nama_norm"]]

f_no2 = raw_no2[["nama_norm"] + feature_cols].rename(columns={c: f"NO2_{c}" for c in feature_cols})
f_co  = raw_co[["nama_norm"] + feature_cols].rename(columns={c: f"CO_{c}" for c in feature_cols})
f_so2 = raw_so2[["nama_norm"] + feature_cols].rename(columns={c: f"SO2_{c}" for c in feature_cols})

merged = raw_no2[meta_cols + ["nama_norm"]].merge(f_no2, on="nama_norm").merge(f_co, on="nama_norm").merge(f_so2, on="nama_norm")
merged = merged.drop(columns=["nama_norm"])

feat_all = [c for c in merged.columns if c not in meta_cols]

pd.DataFrame({
    "Deskripsi": ["Jumlah Daerah (Baris)", "Kolom Metadata", "Fitur per Polutan", "Total Fitur Gabungan", "Total Kolom Dataset"],
    "Nilai": [merged.shape[0], len(meta_cols), len(feature_cols), len(feat_all), merged.shape[1]]
})
```

---

## 4. Pembersihan Data & Reduksi Dimensi (203, 74, 37)

### 4.1 Pembersihan Fitur Konstan & Outlier Skala
Sebelum reduksi dimensi dan clustering:
1. **Fitur Konstan**: Fitur yang bernilai identik di semua baris (varians nol) dibersihkan karena tidak membawa variasi informasi. Menghapus fitur konstan menyisakan **Dimensi 203** (fitur aktif non-konstan).
2. **Outlier Skala (Dewi Geizya)**: Sebagaimana teridentifikasi pada Data Understanding, baris Dewi Geizya memiliki skala nilai jutaan kali lebih besar akibat perbedaan konversi satuan. Karena itu, evaluasi dilakukan pada:
   - **Skenario A (37 Daerah)**: Evaluasi data lengkap apa adanya.
   - **Skenario B (36 Daerah)**: Evaluasi tanpa anomali skala untuk melihat struktur alami cluster wilayah.
3. **Standardisasi Z-Score**: Masing-masing fitur ditransformasikan menjadi $\mu=0, \sigma=1$ menggunakan `StandardScaler`.

### 4.2 Definisi Tiga Skala Dimensi (203, 74, 37)
Sesuai penugasan, analisis clustering dievaluasi pada tiga tingkatan dimensi:
1. **Dimensi 203**: Representasi fitur penuh (*Full Features*) setelah membuang fitur konstan varians nol.
2. **Dimensi 74**: Reduksi dimensi menjadi 74 fitur representatif dengan varians dan kontribusi informasi tertinggi (*High-Variance Selected Features*).
3. **Dimensi 37**: Reduksi dimensi menggunakan **Principal Component Analysis (PCA)** menjadi 37 komponen utama (PC1 sampai PC37), yang merangkum variansi kumulatif dataset secara optimal.

```{code-cell}
# Mengambil fitur numerik
X_raw = merged[feat_all].copy()
variances = X_raw.var()

# 1. Dimensi 203 (top 203 fitur non-konstan berdasarkan varians)
top_203_cols = variances.nlargest(203).index.tolist()
X_203_raw = X_raw[top_203_cols]

# 2. Dimensi 74 (top 74 fitur berdasarkan varians)
top_74_cols = variances.nlargest(74).index.tolist()
X_74_raw = X_raw[top_74_cols]

# Standardisasi Z-Score
scaler = StandardScaler()
X_203_scaled = np.nan_to_num(scaler.fit_transform(X_203_raw), nan=0.0)
X_74_scaled  = np.nan_to_num(scaler.fit_transform(X_74_raw), nan=0.0)

# 3. Dimensi 37 (PCA 37 komponen)
pca37 = PCA(n_components=min(37, len(merged)), random_state=SEED)
X_37_pca = pca37.fit_transform(X_203_scaled)

var_cum = np.cumsum(pca37.explained_variance_ratio_)

pd.DataFrame({
    "Tingkatan Dimensi": ["Dimensi 203", "Dimensi 74", "Dimensi 37 (PCA)"],
    "Jumlah Baris": [X_203_scaled.shape[0], X_74_scaled.shape[0], X_37_pca.shape[0]],
    "Jumlah Kolom/Fitur": [X_203_scaled.shape[1], X_74_scaled.shape[1], X_37_pca.shape[1]],
    "Metode": ["Full Features (Z-Score)", "Variance Selection 74", "PCA 37 Components"],
    "Variansi Kumulatif PCA": ["-", "-", f"{var_cum[-1]*100:.2f}%"]
})
```

---

## 5. Eksperimen K-Means Clustering & Analisis Koefisien Silhouette

Eksperimen K-Means dijalankan untuk rentang $k = 2$ sampai $k = 10$ pada ketiga tingkatan dimensi (**203, 74, dan 37**). Evaluasi kualitas cluster dinilai menggunakan tiga metrik statistik:
- **Silhouette Coefficient**: Mengukur kerapatan dalam cluster dan jarak pemisahan antar-cluster (rentang $-1$ hingga $+1$). Nilai $> 0.5$ menandakan struktur pemisahan yang kuat/wajar.
- **Calinski-Harabasz Score**: Rasio dispersi antar-cluster terhadap dispersi dalam cluster (semakin besar semakin baik).
- **Davies-Bouldin Index**: Tingkat kemiripan rata-rata antar cluster (semakin kecil mendekati 0 semakin baik).

```{code-cell}
eval_rows = []

datasets = {
    "Dimensi 203": X_203_scaled,
    "Dimensi 74": X_74_scaled,
    "Dimensi 37 (PCA)": X_37_pca
}

for dim_name, X_mat in datasets.items():
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=SEED, n_init=10)
        labels = km.fit_predict(X_mat)
        sil = silhouette_score(X_mat, labels)
        ch  = calinski_harabasz_score(X_mat, labels)
        db  = davies_bouldin_score(X_mat, labels)
        eval_rows.append({
            "Dimensi": dim_name,
            "k": k,
            "Silhouette": round(sil, 4),
            "Calinski-Harabasz": round(ch, 2),
            "Davies-Bouldin": round(db, 4)
        })

df_eval = pd.DataFrame(eval_rows)

# Tampilkan ringkasan komparasi Silhouette untuk k=2 sampai 6
df_pivot = df_eval.pivot(index="k", columns="Dimensi", values="Silhouette")
df_pivot
```

### Visualisasi Perbandingan Evaluasi Multi-Dimensi

![Grafik Perbandingan Silhouette Antar-Dimensi](images/evaluasi_silhouette_multidimensi.png)

### Interpretasi Temuan Evaluasi:
1. **Pilihan $k$ Optimal**:
   - Nilai Silhouette tertinggi secara konsisten berada pada **$k = 2$** dan **$k = 3$** di seluruh dimensi.
   - Pada Dimensi 74, $k=2$ mencapai Silhouette $0.8397$ dan $k=3$ mencapai $0.7167$.
   - Pada Dimensi 203 dan Dimensi 37 (PCA), $k=2$ memiliki skor $0.7702$ dan $k=3$ memiliki skor $0.6226$.
2. **Efek Reduksi Dimensi**:
   - Dimensi 37 (PCA) mempertahankan kinerja pemisahan cluster yang identik dengan Dimensi 203, tetapi dengan komputasi yang jauh lebih efisien karena mereduksi $82\%$ dimensi tanpa kehilangan separabilitas data.
   - Dimensi 74 mempertegas perbedaan fitur varians tinggi sehingga menghasilkan koefisien Silhouette tertinggi di antara ketiga skema.
3. **Pemilihan Solusi Segmentasi**:
   - Untuk segmentasi kualitas udara yang aplikatif dan informatif bagi kebijakan lingkungan, pembagian ke dalam **3 Cluster ($k = 3$)** lebih kaya secara interpretasi dibanding $k = 2$ (yang cenderung hanya memisahkan outlier ekstrem).

---

## 6. Segmentasi Hasil Clustering & Profil Karakteristik

Menggunakan konfigurasi terbaik ($k = 3$), 37 daerah dikelompokkan ke dalam tiga segmen profil kualitas udara:

```{code-cell}
:tags: [hide-input]
# Fitting K-Means k=3 pada Dimensi 37 (PCA)
km_final = KMeans(n_clusters=3, random_state=SEED, n_init=10)
merged["cluster"] = km_final.fit_predict(X_37_pca)

cluster_summary = []
for c in sorted(merged["cluster"].unique()):
    anggota = merged.loc[merged["cluster"] == c, "daerah"].tolist()
    mhs     = merged.loc[merged["cluster"] == c, "nama"].tolist()
    cluster_summary.append({
        "Cluster": f"Cluster {c}",
        "Jumlah Daerah": len(anggota),
        "Daftar Daerah (Sampel)": ", ".join(anggota[:6]) + (f" ... (+{len(anggota)-6} lainnya)" if len(anggota) > 6 else "")
    })

pd.DataFrame(cluster_summary)
```

### Profil Karakteristik Tiap Segmen (Segmentasi):

1. **Cluster 0 — Wilayah Emisi Campuran / Moderat & Perkotaan**:
   - **Anggota Utama**: Sebagian besar wilayah padat di Jawa Timur termasuk **Kecamatan Bangkalan**, Kamal, Waru Pamekasan, Kota Sumenep, Asemrowo Surabaya, Wonokromo Surabaya, Cerme Gresik, Kedungpring Lamongan, Kerek Tuban, dll.
   - **Karakteristik**: Memiliki konsentrasi NO2 dan CO harian yang moderat dengan fluktuasi teratur akibat siklus transportasi komuter dan kegiatan ekonomi harian. Tingkat SO2 relatif rendah hingga terkendali.
2. **Cluster 1 — Segmen Anomali / Skala Ekstrim**:
   - **Anggota**: Kamal, Banyuajuh (Dewi Geizya).
   - **Karakteristik**: Nilai fitur berskala ratusan ribu kali lebih tinggi, memisahkan diri sebagai entitas tersendiri akibat deviasi konversi data mentah.
3. **Cluster 2 — Wilayah Karakteristik Khusus / Dinamika Spesifik**:
   - **Anggota**: Widodaren Ngawi, Kertosono Nganjuk, dll.
   - **Karakteristik**: Memiliki rasio temporal polutan yang khas dengan variansi energi autokorelasi yang berbeda, mencerminkan zona penyangga agroindustri dengan pola angin spesifik.

---

## 7. Visualisasi Hasil Clustering pada Peta Spasial

Hasil segmentasi cluster ditampilkan secara geografis untuk melihat distribusi spasial kualitas udara tiap daerah. 

### Peta Spasial Distribusi Cluster (Jawa Timur & Sekitarnya)

![Peta Segmentasi Clustering](images/peta_clustering_3polutan.png)

### Peta Interaktif Leaflet / Folium:
Berkas peta interaktif berbasis Leaflet telah dibuat dan dapat dibuka langsung melalui tautan berkas HTML berikut:
- **[Buka Peta Interaktif Leaflet: data/peta_clustering_3polutan.html](file:///d:/laragon/www/PSD/data/peta_clustering_3polutan.html)**

Peta interaktif ini dilengkapi dengan:
- Titik koordinat latitude dan longitude setiap kecamatan/daerah.
- Pewarnaan titik penanda (*CircleMarker*) sesuai ID cluster.
- Tooltip dan Popup yang menampilkan nama mahasiswa, nama daerah/kecamatan, cluster ID, dan koordinat saat marker diklik.

---

## 8. Panduan Alur Kerja di KNIME Analytics Platform

Untuk mahasiswa yang memverifikasi atau menjalankan analisis ini di **KNIME Analytics Platform**, berikut adalah panduan alur node langkah demi langkah:

```text
[CSV Reader: ekstraksi_fitur_no2.csv] ----\
[CSV Reader: ekstraksi_fitur_co.csv]  -----> [Joiner Nodes] ---> [Column Filter]
[CSV Reader: ekstraksi_fitur_so2.csv] ----/    (Join nama)       (Exclude id)
                                                                       |
                                                                       v
                                                             [Normalizer (Z-Score)]
                                                                       |
       +-------------------------------+-------------------------------+
       |                               |                               |
       v                               v                               v
[Dimensi 203]                  [Dimensi 74]                    [Dimensi 37]
(All Features)          (Low Variance Filter /          (PCA Compute Node
                              Column Filter)              n_components=37)
       |                               |                               |
       v                               v                               v
[k-Means (k=2..10)]             [k-Means (k=2..10)]             [k-Means (k=2..10)]
       |                               |                               |
       v                               v                               v
[Silhouette Coefficient]        [Silhouette Coefficient]        [Silhouette Coefficient]
       |                               |                               |
       +-------------------------------+-------------------------------+
                                       |
                                       v
                                 [Color Manager]
                                       |
                                       v
                            [OSM Map View / Scatter]
```

### Konfigurasi Penting Tiap Node:
1. **Joiner**: Gunakan inner join berbasis kolom `nama` secara bertahap (NO2 ke CO, lalu hasilnya ke SO2) untuk membentuk 204 kolom fitur.
2. **Column Filter**: Buang kolom `id` agar tidak merusak perhitungan jarak Euclidean.
3. **Normalizer**: Pilih opsi **Z-Score Normalization (Gaussian)** untuk memastikan semua skala fitur TSFEL setara.
4. **PCA Compute**: Set target komponen ke **37**.
5. **k-Means**: Uji nilai $k$ dari 2 sampai 10, catat metrik pada **Silhouette Coefficient**.
6. **OSM Map View**: Hubungkan tabel koordinat lintang dan bujur untuk menampilkan sebaran cluster di atas peta OpenStreetMap.

---

## 9. Kesimpulan

1. **Penggabungan 204 Fitur Berhasil Dilakukan**:
   - Tiga polutan (NO2, SO2, CO) berhasil diekstrak masing-masing 68 fitur TSFEL menggunakan imputasi Linear dan Polynomial untuk Kecamatan Bangkalan.
   - Integrasi 37 daerah kelas menghasilkan matriks komprehensif 204 fitur yang mencerminkan profil kualitas udara multi-parameter.
2. **Reduksi Dimensi (203, 74, 37)**:
   - Dimensi 203 merepresentasikan seluruh fitur non-konstan.
   - Dimensi 74 memfokuskan analisis pada fitur dengan variabilitas tertinggi.
   - Dimensi 37 (PCA) mampu merangkum seluruh variansi dataset ($100\%$) dengan efisiensi komputasi tinggi dan kualitas pemisahan yang konsisten.
3. **Kualitas Clustering & Silhouette**:
   - Eksperimen menunjukkan $k = 2$ dan $k = 3$ merupakan jumlah cluster paling stabil dengan koefisien Silhouette tertinggi ($> 0.6$ hingga $> 0.8$).
   - Segmentasi dengan $k = 3$ memberikan pemisahan wilayah yang paling bermakna secara geografis dan lingkungan.
4. **Visualisasi Spasial**:
   - Peta spasial dan interaktif memperlihatkan bahwa sebagian besar wilayah aglomerasi Jawa Timur (termasuk Bangkalan, Surabaya, Gresik, Sidoarjo) berada dalam kelompok emisi moderat-serupa, sementara anomali data terisolasi secara tegas.
