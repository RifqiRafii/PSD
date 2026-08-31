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

# Pengantar Analisis Polutan Kabupaten Bangkalan

## Tentang Proyek

Proyek ini menganalisis **kualitas udara di Kabupaten Bangkalan, Jawa Timur**
dengan fokus pada empat polutan udara utama: **NO2, CO, SO2, dan CH4**.
Data diperoleh dari citra satelit **Sentinel-5P (TROPOMI)** melalui layanan
**openEO** pada **Copernicus Data Space Ecosystem**, mencakup rentang waktu
**24 Agustus 2025 sampai dengan 24 Agustus 2026**.

Proyek ini disusun sebagai bagian dari mata kuliah **Proyek Sains Data**,
mengikuti kerangka kerja **CRISP-DM**, mulai dari pemahaman bisnis dan data,
eksplorasi awal, ekstraksi data satelit, hingga analisis deret waktu.

## Susunan Bab

Berikut adalah urutan bab pada portofolio ini.

### 1. [Business Understanding](./1-business-understanding-bangkalan.md)

Pembahasan latar belakang wilayah Bangkalan, tujuan analisis, manfaat dan
pemangku kepentingan, penjelasan Indeks Kualitas Udara (AQI), penjelasan
detail tiap polutan (NO2, CO, SO2, CH4), serta ruang lingkup analisis.

### 2. [Data Understanding](./2-data-understanding-bangkalan.md)

Pembahasan sumber data, resolusi spasial Sentinel-5P, cara koneksi dan
otentikasi ke openEO, definisi Area of Interest (AOI) Kabupaten Bangkalan,
gambaran proses ekstraksi, struktur data hasil, serta keterbatasan data.

### 3. [Eksplorasi Data](./3-eksplorasi-data-bangkalan.md)

Peta interaktif wilayah Bangkalan, statistik deskriptif tiap polutan,
pemeriksaan missing values, deteksi outlier awal dengan Isolation Forest,
dan korelasi antar polutan.

### 4. [Ekstraksi Data](./1-ekstraksi-data.ipynb)

Notebook yang menghubungkan ke server openEO Copernicus Data Space,
menarik data Sentinel-5P L2 untuk wilayah Bangkalan per polutan, melakukan
agregasi temporal (harian) dan spasial (rata rata dalam polygon AOI), lalu
menyimpan hasilnya sebagai file NetCDF dan mengonversinya menjadi CSV.

### 5. [Analisis Bangkalan](./2-analisis-bangkalan.ipynb)

Notebook yang memuat data CSV hasil ekstraksi, menampilkan peta interaktif
area Bangkalan, menangani missing values pada data deret waktu, mendeteksi
anomali atau outlier menggunakan Isolation Forest, serta memvisualisasikan
hasilnya dalam bentuk grafik deret waktu.

## Alur Kerja Singkat

```{mermaid}
flowchart LR
    A[Business Understanding] --> B[Data Understanding]
    B --> C[Eksplorasi Data]
    C --> D[Ekstraksi Data]
    D --> E[Analisis Bangkalan]
    E --> F[Kesimpulan dan Rekomendasi]
```

## Cara Menjalankan

1. Install dependensi dengan perintah `pip install -r requirements.txt`.
2. Jalankan `1-ekstraksi-data.ipynb` untuk mengambil dan menyiapkan data,
   memerlukan login Copernicus Data Space Ecosystem.
3. Jalankan `2-analisis-bangkalan.ipynb` untuk eksplorasi lanjutan dan
   deteksi outlier.
4. Baca bab **Business Understanding**, **Data Understanding**, dan
   **Eksplorasi Data** untuk konteks lengkap sebelum menelusuri hasil
   analisis pada notebook.