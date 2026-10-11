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

# UTS SIG: Visualisasi Spasial Google Satelit WMS, Deployment Streamlit & Kebijakan Tata Ruang

Bab ini mendokumentasikan implementasi kartografi digital interaktif menggunakan **Leaflet & Folium** dengan integrasi **Tile/WMS Satelit Google Maps**, arsitektur penyebaran sistem ke aplikasi web interaktif **Streamlit**, serta formulasi arahan kebijakan tata ruang wilayah di Jawa Timur.

---

## 1. Peta Interaktif Klasifikasi LULC Berbasis WMS Satelit Google Maps

Sesuai ketentuan penugasan: *"menampilkan hasil klasifikasi menggunakan : wms satelit google maps menggunakan leaflet atau folium"*, sistem ini menghasilkan peta web interaktif komprehensif.

Peta dilengkapi dengan kemampuan:
1. **Multi-Basemap Layer WMS:**
   * **Google Maps Satellite WMS:** `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}` (Citra satelit resolusi tinggi asli dari Google).
   * **Google Maps Hybrid WMS:** `https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}` (Citra satelit dengan overlay label jalan dan toponimi wilayah).
   * **Google Maps Roadmap:** Peta jalan konvensional.
   * **OpenStreetMap & CartoDB:** Peta jalan dan kanvas gelap untuk analisis visual kontras.
2. **Layer Control Interaktif:** Pengguna dapat mencentang atau menyembunyikan lapisan kelas spesifik (*Sawah, Bangunan, Mangrove, Lahan Hijau, Laut, Danau/Ranu*).
3. **Popup Radiometrik Spasial:** Klik pada setiap titik sampel menampilkan dialog interaktif berisi koordinat, nama kabupaten/kota, nilai spektral (NDVI, NDWI, MNDWI, NDBI, BSI, CMRI), dan landasan hukum perlindungan zonasi.
4. **Delineasi Poligon Kawasan Konservasi & Sempadan:**
   * Poligon Sempadan Perlindungan Hidrologis Ranu Grati Pasuruan (Zona 50m).
   * Poligon Kawasan Konservasi Sabuk Hijau Mangrove Wonorejo Surabaya.
   * Poligon Zona Inti Ekosistem Danau Dataran Tinggi Ranu Kumbolo TNBTS.

### Tampilan Peta Interaktif Terintegrasi

Peta interaktif HTML yang telah dibuat dapat diakses langsung pada lembar web statis ini:

```{raw} html
<div style="border: 2px solid #cbd5e1; border-radius: 10px; overflow: hidden; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <iframe src="peta_lulc_jawa_timur.html" width="100%" height="600px" style="border: none;"></iframe>
</div>
```

> **Catatan Penggunaan Peta:**
> Anda dapat memperbesar (*zoom-in*), memperkecil (*zoom-out*), menggeser (*pan*), menggunakan tombol *Fullscreen* di pojok kiri atas, serta mengganti basemap ke Google Satellite atau Google Hybrid melalui menu lapisan di pojok kanan atas.

---

## 2. Deployment Sistem Informasi Geografis ke Streamlit

Aplikasi Sistem Informasi Geografis interaktif telah selesai dibangun menggunakan kerangka kerja **Streamlit** dan disimpan pada file `streamlit_app.py` serta entry point `app.py`.

### 2.1 Fitur Unggulan Aplikasi Streamlit
1. **Dashboard Eksekutif Modern:** Antarmuka responsif dengan tipografi modern, indikator metrik kartu, dan desain bertema spasial profesional.
2. **Eksplorasi Data Tabular & Visual:** Grafik distribusi kelas, boxplot perbandingan indeks spektral interaktif, dan penampil tabel dataset.
3. **Dashboard Evaluasi Model:** Menampilkan tabel performa 7 model Machine Learning, heatmap confusion matrix interaktif, serta diagram batang kepentingan fitur (*feature importance*).
4. **Peta Satelit Google Terintegrasi:** Embed langsung visualisasi spasial peta Folium dengan seluruh lapisan layer control.
5. **Simulator Prediksi Spektral Real-Time:** 
   * Menyediakan formulir masukan numerik untuk 10 band Sentinel-2A.
   * Tersedia template preset lokasi Jawa Timur (*Wonorejo Surabaya, Ranu Grati Pasuruan, Sawah Lamongan, Pusat Kota Surabaya, Bromo/Tahura, Selat Madura*).
   * Menghitung seluruh indeks spektral secara otomatis dan memprediksi kelas tutupan lahan beserta tingkat keyakinan probabilitas model.
   * Menampilkan rekomendasi kebijakan tata ruang otomatis berdasarkan hasil prediksi.

### 2.2 Cara Menjalankan Aplikasi Streamlit Secara Mandiri

Untuk menjalankan aplikasi ini di komputer lokal, buka terminal PowerShell dan jalankan perintah berikut:

```powershell
# 1. Pindah ke direktori proyek
cd d:\laragon\www\PSD

# 2. Jalankan aplikasi Streamlit menggunakan virtual environment
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Atau cukup **klik ganda (double-click)** pada berkas:
`run_streamlit.bat`

Aplikasi akan otomatis terbuka pada peramban web di alamat: `http://localhost:8501`.

---

## 3. Analisis Kebijakan Tata Ruang & Implikasi Spasial di Jawa Timur

Hasil klasifikasi tutupan lahan berbasis satelit Sentinel-2A ini bukan sekadar luaran teknis algoritma, melainkan instrumen ilmiah untuk evaluasi pelaksanaan **Rencana Tata Ruang Wilayah (RTRW) Provinsi Jawa Timur (Perda No. 10 Tahun 2023)**:

### 3.1 Kebijakan Pengendalian Alih Fungsi Lahan Sawah Dilindungi (LSD / LP2B)
* **Kondisi Eksisting:** Sawah irigasi teknis di sepanjang koridor Sungai Brantas dan Bengawan Solo (Lamongan, Mojokerto, Sidoarjo) memiliki kerentanan alih fungsi yang sangat tinggi menjadi kawasan industri pergudangan dan perumahan.
* **Instrumen Kebijakan:** UU No. 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan dan Kepmen ATR/BPN No. 1589/2021 tentang Penetapan Peta Lahan Sawah Dilindungi.
* **Rekomendasi Spasial:**
  1. Integrasi peta klasifikasi LULC bulanan menggunakan indeks **NDVI ($>0.50$)** dan **SAVI** dengan peta LSD ATR/BPN.
  2. Apabila terdeteksi kenaikan nilai **NDBI (positif)** dan **BSI (tanah uruk)** pada poligon LSD, sistem otomatis menerbitkan *Surat Peringatan Dini Pelanggaran Tata Ruang*.
  3. Moratorium penerbitan izin Persetujuan Kesesuaian Kegiatan Pemanfaatan Ruang (PKKPR) untuk kegiatan non-pertanian pada zona LP2B.

### 3.2 Kebijakan Restorasi Sabuk Hijau Mangrove Pesisir Jawa Timur
* **Kondisi Eksisting:** Kawasan pesisir Pantai Timur Surabaya (Pamurbaya) dan Ujungpangkah Gresik menghadapi tekanan konversi lahan menjadi tambak udang intensif dan permukiman pesisir liar.
* **Instrumen Kebijakan:** Perpres No. 73 Tahun 2012 tentang Strategi Nasional Pengelolaan Ekosistem Mangrove dan Perda RZWP-3-K Jawa Timur.
* **Rekomendasi Spasial:**
  1. Indeks **CMRI ($\text{NDVI} - \text{NDWI}$)** terbukti menjadi pembeda paling akurat bagi tutupan mangrove ($+0.40 \text{ s/d } +0.75$).
  2. Pemerintah Daerah wajib menetapkan garis sempadan pantai sekurang-kurangnya 100 meter dari titik pasang tertinggi air laut dan mempertahankan sabuk hijau mangrove selebar $130 \times \text{rata-rata pasang surut}$.
  3. Mengalokasikan dana bagi hasil atau skema perdagangan karbon (*carbon credit*) untuk memberdayakan kelompok tani hutan mangrove Wonorejo dan Ujungpangkah.

### 3.3 Kebijakan Perlindungan Sempadan Danau Vulkanik & Ranu Alami
* **Kondisi Eksisting:** Danau alami di Jawa Timur (Ranu Grati, Ranu Klakah, Ranu Kumbolo) mengalami ancaman okupasi bangunan semipermanen di sempadan danau serta penurunan kualitas air akibat keramba jaring apung (KJA) berlebih.
* **Instrumen Kebijakan:** Permen PUPR No. 28/PRT/M/2015 tentang Garis Sempadan Sungai dan Sempadan Danau.
* **Rekomendasi Spasial:**
  1. Delineasi zona sempadan danau selebar **minimum 50 meter** dari tepi titik pasang tertinggi danau/ranu alami.
  2. Model Machine Learning membuktikan bahwa perairan danau tawar memiliki profil reflektansi spektral yang berbeda dari laut terbuka (fitur MNDWI dan B3 Green).
  3. Penertiban bangunan yang memiliki nilai NDBI positif di dalam radius sempadan 50 meter danau.
  4. Pembatasan luasan keramba jaring apung maksimal 10% dari luas total permukaan air danau guna mencegah fenomena eutrofikasi dan kematian massal ikan.

---

## 4. Kesimpulan Akhir

Melalui integrasi data penginderaan jauh satelit **Sentinel-2A MSI**, rekayasa **18 fitur spektral**, evaluasi **7 algoritma Machine Learning**, visualisasi kartografi **Google Satellite WMS Leaflet**, deployment **Streamlit**, serta integrasi dokumentasi web statis **Jupyter Book**, proyek Ujian Tengah Semester (UTS) ini telah berhasil menyelesaikan seluruh target capaian:

1. Memberikan *Data Understanding* mendalam mengenai dinamika LULC di Jawa Timur serta acuan standar klasifikasi nasional resmi (SNI 7645 / BIG).
2. Menguraikan karakteristik 13 saluran band Sentinel-2A dan perumusan matematis lengkap indeks spektral (NDVI, NDWI, MNDWI, NDBI, BSI, SAVI, NDRE, CMRI).
3. Melakukan eksperimen dengan 2.100 titik sampel spasial pada 6 kelas tutupan lahan dengan pemisahan 80% data latih (1.680 sampel) dan 20% data uji (420 sampel).
4. Membuktikan bahwa algoritma **Hist Gradient Boosting** dan **Random Forest** menghasilkan akurasi tertinggi di atas **99%** dengan Cohen's Kappa **0.9914**.
5. Menyajikan visualisasi peta interaktif dengan layer WMS satelit Google Maps serta menyediakan antarmuka web interaktif berbasis Streamlit dan web statis portofolio.
