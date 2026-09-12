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

AOI didefinisikan sebagai **batas administratif asli Kabupaten Bangkalan**
(bentuk polygon sesuai wilayah sebenarnya), bukan kotak bounding box.
Polygon ini diambil dari data batas administratif resmi (GADM level 2,
kode wilayah BPS/Kemendagri 3526), lalu disederhanakan agar tidak terlalu
berat saat dikirim sebagai parameter permintaan ke openEO, namun tetap
mengikuti lekukan pesisir dan bentuk asli kabupaten, tersimpan sebagai
`../data/bangkalan-boundary.geojson`.

```python
import json

with open("../data/bangkalan-boundary.geojson", encoding="utf-8") as f:
    bangkalan_geojson = json.load(f)

bangkalan_polygon = bangkalan_geojson["geometry"]  # objek Polygon GeoJSON
```

Bounding box (`west`, `south`, `east`, `north`) tetap dihitung, tetapi
hanya dipakai sebagai batas kasar pada parameter `spatial_extent` di
`load_collection`, sekadar mempersempit area unduhan data mentah. Batas
yang sesungguhnya dipakai untuk agregasi spasial pada `aggregate_spatial`
adalah polygon administratif di atas, bukan kotak ini.

```python
lons = [pt[0] for pt in bangkalan_polygon["coordinates"][0]]
lats = [pt[1] for pt in bangkalan_polygon["coordinates"][0]]
bangkalan_bbox = {
    "west": min(lons),
    "east": max(lons),
    "south": min(lats),
    "north": max(lats),
}
```

Visualisasi peta interaktif dari AOI ini, lengkap dengan titik acuan
kontekstual seperti akses Suramadu dan pesisir Klampis, dibahas pada
bagian **Eksplorasi Data**.

## 4. Proses Ekstraksi Data

Untuk setiap polutan, data dimuat, diagregasi secara temporal (harian,
mean), lalu diagregasi secara spasial (mean di dalam polygon AOI asli
Bangkalan).

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
format NetCDF (`.nc`) untuk masing masing polutan, lalu keempatnya
digabungkan menjadi satu tabel CSV agar mudah dipakai pada tahap
eksplorasi dan analisis lanjutan. Detail lengkap kode ekstraksi dan
penggabungan tersedia pada notebook `4-ekstraksi-data.ipynb`, termasuk
sel diagnostik untuk memeriksa apakah hasil ekstraksi benar benar
bernilai nol atau hanya nilai yang sangat kecil.

## 5. Struktur Data Hasil

Berbeda dari pendekatan menyimpan satu file CSV per polutan, keempat
polutan hasil ekstraksi digabungkan menjadi **satu tabel tunggal**, mirip
struktur tabel pada basis data, dengan satu baris per tanggal dan satu
kolom per polutan.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| `date` | datetime | Tanggal pengukuran (harian) |
| `NO2` | float | Nilai konsentrasi rata rata harian NO2 pada wilayah Bangkalan |
| `CO` | float | Nilai konsentrasi rata rata harian CO pada wilayah Bangkalan |
| `SO2` | float | Nilai konsentrasi rata rata harian SO2 pada wilayah Bangkalan |
| `CH4` | float | Nilai konsentrasi rata rata harian CH4 pada wilayah Bangkalan |

Contoh isi file `bangkalan_polutan.csv`:

| date | NO2 | CO | SO2 | CH4 |
|------|-----|----|----|-----|
| 2025-08-24 | 0.000123 | 0.021 | 0.0004 | 0.00019 |
| 2025-08-25 | 0.000119 | 0.020 | 0.0003 | 0.00018 |
| ... | ... | ... | ... | ... |

Hanya ada satu file CSV yang dihasilkan, yaitu `bangkalan_polutan.csv`,
tersimpan di folder `../data/csv/`. File NetCDF per polutan
(`bangkalan_NO2.nc`, `bangkalan_CO.nc`, `bangkalan_SO2.nc`,
`bangkalan_CH4.nc`) tetap disimpan di folder `../data/nc/` sebagai data
mentah untuk keperluan pelacakan (traceability) atau pemeriksaan ulang.

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

## 7. Catatan Jika Hasil Ekstraksi Bernilai 0

Jika seluruh nilai pada tabel hasil ekstraksi terlihat bernilai 0, hal ini
umumnya bukan berarti udara benar benar bersih sempurna, melainkan
menandakan salah satu dari beberapa kemungkinan berikut.

1. Nama band yang diminta tidak sesuai dengan nama band pada koleksi
   `SENTINEL_5P_L2` (bersifat case sensitive).
2. Nilai kosong (NaN) akibat tutupan awan tidak sengaja terisi 0 pada
   suatu tahap pemrosesan, alih alih dibiarkan sebagai data hilang.
3. Nilai konsentrasi memang sangat kecil (orde 1e-4 hingga 1e-6), sehingga
   terlihat seperti 0.000000 jika dicetak dengan pembulatan yang terlalu
   sedikit angka desimal.
4. Area yang diagregasi meleset dari wilayah yang dimaksud, misalnya
   sebagian besar jatuh di area laut tanpa data yang relevan.

Notebook `4-ekstraksi-data.ipynb` menyediakan sel uji coba dan diagnostik
khusus untuk memeriksa kemungkinan kemungkinan ini sebelum menjalankan
ekstraksi penuh setahun.

## 8. Kesimpulan

Data Sentinel-5P L2 yang diakses melalui openEO Copernicus Data Space
Ecosystem terbukti dapat diambil untuk wilayah dan rentang waktu yang
ditentukan, yaitu 24 Agustus 2025 sampai dengan 24 Agustus 2026, dengan
catatan penting bahwa ekstraksi harus dilakukan per polutan karena
keterbatasan backend. Area of Interest yang dipakai sudah mengikuti
bentuk administratif asli Kabupaten Bangkalan, bukan kotak bounding box,
sehingga agregasi spasial lebih mencerminkan wilayah yang sesungguhnya.
Struktur data hasil ekstraksi berupa satu tabel gabungan berkolom
`date`, `NO2`, `CO`, `SO2`, dan `CH4` sudah dirancang agar mudah dipakai
pada tahap berikutnya, mirip sebuah tabel pada basis data. Dengan
mempertimbangkan keterbatasan resolusi spasial dan kemungkinan data
kosong, serta setelah memastikan hasil ekstraksi tidak seluruhnya
bernilai 0 melalui sel diagnostik, data ini dinyatakan cukup untuk
dilanjutkan ke tahap **Eksplorasi Data**, tempat kualitas data akan
diperiksa lebih lanjut sebelum dianalisis secara mendalam.
