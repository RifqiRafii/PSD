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
mengikuti kerangka kerja **CRISP-DM**. Cakupan tugas ini berhenti pada
tahap **Data Understanding**, termasuk statistik deskriptif dan
visualisasi time series menggunakan **KNIME**. Tahap Data Preparation,
eksplorasi lanjutan, dan analisis mendalam (deteksi outlier, dsb.)
dikerjakan sebagai bagian dari tugas terpisah.

## Susunan Bab

Berikut adalah urutan bab pada portofolio ini.

### 1. [Ekstraksi Data](./1-ekstraksi-data.ipynb)

Notebook yang menghubungkan ke server openEO Copernicus Data Space,
menarik data Sentinel-5P L2 untuk wilayah Bangkalan per polutan (dipecah
menjadi 4 bagian 3 bulanan), melakukan agregasi temporal (harian) dan
spasial (rata rata dalam polygon AOI asli Bangkalan), lalu menggabungkan
hasilnya menjadi satu tabel CSV: `data_polutan_bangkalan.csv`.

### 2. [Business Understanding](./2-business-understanding-bangkalan.md)

Pembahasan latar belakang wilayah Bangkalan, tujuan analisis, manfaat dan
pemangku kepentingan, penjelasan Indeks Kualitas Udara (AQI), penjelasan
detail tiap polutan (NO2, CO, SO2, CH4), serta ruang lingkup analisis.

### 3. [Data Understanding](./3-data-understanding-bangkalan.md)

Pembahasan sumber data, resolusi spasial Sentinel-5P, cara koneksi dan
otentikasi ke openEO, definisi Area of Interest (AOI) Kabupaten Bangkalan,
proses ekstraksi (termasuk pemecahan rentang waktu), struktur data hasil,
keterbatasan data, serta **statistik deskriptif dan visualisasi time
series yang dikerjakan di KNIME** (PostgreSQL Connector, DB Table
Selector, DB Reader, Statistics, dan Line Plot).

## Alur Kerja Singkat

```{mermaid}
flowchart LR
    A[Ekstraksi Data] --> B[Business Understanding]
    B --> C[Data Understanding]
    C --> D[Statistik & Visualisasi KNIME]
    D --> E[Tugas Berikutnya: Data Preparation dan Analisis]
```

## Cara Menjalankan

1. Install dependensi dengan perintah `pip install -r requirements.txt`.
2. Jalankan `1-ekstraksi-data.ipynb` untuk mengambil dan menyiapkan data,
   memerlukan login Copernicus Data Space Ecosystem. Proses ini memakan
   waktu cukup lama karena data diambil bertahap per 3 bulan untuk
   menghindari ketidakstabilan pada backend openEO.
3. Muat `data_polutan_bangkalan.csv` ke PostgreSQL, lalu jalankan workflow
   KNIME (PostgreSQL Connector, DB Table Selector, DB Reader, Statistics,
   Line Plot) untuk menghasilkan statistik deskriptif dan visualisasi
   time series.
4. Baca bab **Business Understanding** dan **Data Understanding** untuk
   konteks lengkap serta tempat menyisipkan hasil dari KNIME.
