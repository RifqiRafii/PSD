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
**24 Agustus 2025 – 24 Agustus 2026**.

Proyek ini disusun sebagai bagian dari mata kuliah **Proyek Sains Data**,
mengikuti kerangka kerja **CRISP-DM**, mulai dari pemahaman bisnis dan data,
ekstraksi data satelit, hingga eksplorasi dan analisis deret waktu.

## Susunan Bab

Berikut adalah urutan bab pada portofolio ini:

### 1. [Business & Data Understanding Bangkalan](./1-business-data-understanding-bangkalan.md)

Pembahasan latar belakang, tujuan analisis, penjelasan tiap polutan, sumber
data, area of interest (AOI), peta interaktif wilayah Bangkalan, serta
identifikasi awal kualitas data (missing values & outlier).

### 2. [Ekstraksi Data](./1-ekstraksi-data.ipynb)

Notebook yang menghubungkan ke server openEO Copernicus Data Space,
menarik data Sentinel-5P L2 untuk wilayah Bangkalan per polutan, melakukan
agregasi temporal (harian) dan spasial (rata-rata dalam polygon AOI), lalu
menyimpan hasilnya sebagai file NetCDF dan mengonversinya menjadi CSV.

### 3. [Analisis Bangkalan](./2-analisis-bangkalan.ipynb)

Notebook yang memuat data CSV hasil ekstraksi, menampilkan peta interaktif
area Bangkalan, menangani *missing values* pada data deret waktu,
mendeteksi anomali/outlier menggunakan **Isolation Forest**, serta
memvisualisasikan hasilnya dalam bentuk grafik deret waktu.

## Alur Kerja Singkat

```{mermaid}
flowchart LR
    A[Business & Data Understanding] --> B[Ekstraksi Data]
    B --> C[Analisis Bangkalan]
    C --> D[Kesimpulan & Rekomendasi]
```

## Cara Menjalankan

1. Install dependensi: `pip install -r requirements.txt`.
2. Jalankan `1-ekstraksi-data.ipynb` untuk mengambil dan menyiapkan data
   (memerlukan login Copernicus Data Space Ecosystem).
3. Jalankan `2-analisis-bangkalan.ipynb` untuk eksplorasi dan deteksi
   outlier.
4. Baca bab **Business & Data Understanding** untuk konteks lengkap
   sebelum menelusuri hasil analisis.
