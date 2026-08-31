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

# Data Understanding - Kabupaten Bangkalan

Data Understanding adalah tahap untuk mengenali sumber data, cakupan
wilayah dan waktu, cara memperoleh data, serta struktur data yang akan
dipakai pada analisis kualitas udara Kabupaten Bangkalan. Tahap
pemeriksaan kualitas data secara mendetail (missing values, outlier)
dibahas terpisah pada bagian **Eksplorasi Data**.

## 1. Sumber Data

| Item | Keterangan |
|------|------------|
| Sumber | Copernicus Data Space Ecosystem |
| Layanan | openEO |
| Server | `openeo.dataspace.copernicus.eu` |
| Produk / Koleksi | Sentinel-5P L2 (`SENTINEL_5P_L2`) |
| Instrumen | TROPOMI (TROPOspheric Monitoring Instrument) |
| Polutan | NO2, CO, SO2, CH4 |
| Periode | 24 Agustus 2025 sampai dengan 24 Agustus 2026 |
| Lokasi | Kabupaten Bangkalan, Jawa Timur |

Sentinel-5P adalah satelit milik European Space Agency (ESA) yang membawa
instrumen TROPOMI, dirancang khusus untuk memantau komposisi atmosfer
Bumi, termasuk gas rumah kaca dan polutan udara. Satelit ini memiliki
waktu kunjung ulang (revisit time) sekitar satu hari untuk cakupan
global, sehingga cocok dipakai untuk analisis deret waktu harian.

### 1.1 Resolusi Spasial per Polutan

Perlu dicatat bahwa resolusi spasial data TROPOMI berbeda untuk tiap
polutan, sehingga tingkat kedetailan spasial yang diperoleh juga berbeda.

| Polutan | Resolusi Spasial (perkiraan) |
|---------|-------------------------------|
| NO2 | sekitar 5.5 km x 3.5 km |
| SO2 | sekitar 5.5 km x 3.5 km |
| CO | sekitar 7 km x 7 km |
| CH4 | sekitar 7 km x 7 km |

Karena luas Kabupaten Bangkalan hanya sekitar 1.260 km persegi, setiap
piksel Sentinel-5P dapat mencakup area yang cukup luas relatif terhadap
ukuran kabupaten. Oleh karena itu, agregasi spasial (dijelaskan pada
bagian 3) digunakan untuk merangkum seluruh piksel yang berada di dalam
wilayah Bangkalan menjadi satu nilai representatif per hari.

## 2. Koneksi dan Otentikasi

Koneksi ke server openEO dilakukan menggunakan akun Copernicus Data Space
Ecosystem, melalui metode **device code flow**.

```python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu")
connection = connection.authenticate_oidc()
```

Saat kode di atas dijalankan, klien akan menampilkan tautan login beserta
kode singkat di layar. Setelah login berhasil dilakukan melalui browser,
koneksi akan terautentikasi secara otomatis untuk seluruh permintaan
data berikutnya.

Perlu dicatat bahwa backend Sentinel Hub untuk koleksi `SENTINEL_5P_L2`
hanya mengizinkan satu band, yaitu satu polutan, pada setiap proses
permintaan data. Oleh karena itu, proses ekstraksi harus dilakukan secara
terpisah untuk NO2, CO, SO2, dan CH4, bukan sekaligus dalam satu
permintaan.

## 3. Area of Interest (AOI) Kabupaten Bangkalan

AOI didefinisikan sebagai bounding box yang mencakup wilayah administratif
Kabupaten Bangkalan.

| Atribut | Nilai | Keterangan |
|---------|-------|------------|
| `west` | 112.671 | Longitude terkecil, batas kiri |
| `east` | 113.116 | Longitude terbesar, batas kanan |
| `south` | -7.227 | Latitude terkecil, batas bawah |
| `north` | -6.848 | Latitude terbesar, batas atas |

Parameter `spatial_extent` pada `load_collection` menggunakan bounding
box (`west`, `south`, `east`, `north`) di atas. Untuk agregasi spasial
pada `aggregate_spatial`, bounding box yang sama direpresentasikan
sebagai polygon GeoJSON yang tertutup, artinya titik pertama dan titik
terakhir pada koordinat sama.

```python
bangkalan_polygon = {
    "type": "Polygon",
    "coordinates": [[
        [112.671, -7.227],   # kiri bawah, barat daya
        [113.116, -7.227],   # kanan bawah, tenggara
        [113.116, -6.848],   # kanan atas, timur laut
        [112.671, -6.848],   # kiri atas, barat laut
        [112.671, -7.227],   # kembali ke titik awal
    ]],
}
```

Visualisasi peta interaktif dari AOI ini, lengkap dengan titik acuan
kontekstual seperti akses Suramadu dan pesisir Klampis, dibahas pada
bagian **Eksplorasi Data**.

## 4. Proses Ekstraksi Data

Untuk setiap polutan, data dimuat, diagregasi secara temporal (harian,
mean), lalu diagregasi secara spasial (mean di dalam polygon AOI).

```python
s5 = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent=bangkalan_bbox,
    bands=["NO2"],  # ganti sesuai polutan: NO2, CO, SO2, atau CH4
)
s5 = s5.aggregate_temporal_period(reducer="mean", period="day")
s5 = s5.aggregate_spatial(reducer="mean", geometries=bangkalan_polygon)

job = s5.execute_batch(
    title="NO2 Bangkalan",
    outputfile="../data/nc/bangkalan_NO2.nc",
)
```

Proses ini dijalankan sebagai batch job di server openEO, dan dapat
dipantau melalui openEO Web Editor. Setelah selesai, hasil diunduh dalam
format NetCDF (`.nc`), lalu dikonversi menjadi CSV agar mudah dipakai
pada tahap eksplorasi dan analisis lanjutan. Detail lengkap kode
ekstraksi dan konversi tersedia pada notebook `1-ekstraksi-data.ipynb`.

## 5. Struktur Data Hasil

Setiap file CSV hasil ekstraksi memiliki struktur (skema) yang sama:
kolom tanggal, dan kolom nilai konsentrasi polutan.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| `date` | datetime | Tanggal pengukuran (harian) |
| `NO2` / `CO` / `SO2` / `CH4` | float | Nilai konsentrasi rata rata harian pada wilayah Bangkalan |

Contoh isi file `bangkalan_NO2.csv`:

| date | NO2 |
|------|-----|
| 2025-08-24 | 0.000123 |
| 2025-08-25 | 0.000119 |
| ... | ... |

Terdapat empat file CSV yang dihasilkan, masing masing untuk satu
polutan: `bangkalan_NO2.csv`, `bangkalan_CO.csv`, `bangkalan_SO2.csv`, dan
`bangkalan_CH4.csv`, seluruhnya tersimpan di folder `../data/csv/`.

## 6. Keterbatasan Data

Beberapa keterbatasan yang perlu disadari sejak tahap ini:

1. **Resolusi spasial relatif kasar** dibanding luas Kabupaten Bangkalan,
   sehingga nilai yang diperoleh merupakan rata rata area yang cukup
   luas, bukan potret polusi pada titik tertentu.
2. **Kemungkinan data kosong pada hari tertentu**, terutama akibat
   tutupan awan yang menghalangi pengukuran instrumen berbasis optik.
3. **Nilai dapat berupa estimasi kolom atmosfer**, bukan konsentrasi
   permukaan tanah secara langsung, sehingga interpretasinya perlu
   berhati hati saat dikaitkan dengan dampak kesehatan langsung pada
   manusia di permukaan.

## 7. Kesimpulan

Data Sentinel-5P L2 yang diakses melalui openEO Copernicus Data Space
Ecosystem terbukti dapat diambil untuk wilayah dan rentang waktu yang
ditentukan, yaitu 24 Agustus 2025 sampai dengan 24 Agustus 2026, dengan
catatan penting bahwa ekstraksi harus dilakukan per polutan karena
keterbatasan backend. Area of Interest yang didefinisikan dalam bentuk
bounding box dan polygon sudah jelas cakupannya, dan struktur data hasil
ekstraksi berupa CSV harian per polutan sudah dirancang agar mudah dipakai
pada tahap berikutnya. Dengan mempertimbangkan keterbatasan resolusi
spasial dan kemungkinan data kosong, data ini dinyatakan cukup untuk
dilanjutkan ke tahap **Eksplorasi Data**, tempat kualitas data akan
diperiksa lebih lanjut sebelum dianalisis secara mendalam.
