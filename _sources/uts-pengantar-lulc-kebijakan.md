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

# UTS SIG: Data Understanding & Kebijakan LULC Jawa Timur

| Metadata Proyek | Informasi |
| :--- | :--- |
| **Mata Kuliah** | Proyek Sains Data (PSD) - Ujian Tengah Semester (UTS) |
| **Topik Analisis** | Sistem Informasi Geografis (SIG) Berbasis Analisis Spasial Penutup Lahan (*LULC*) dan Kebijakan Tata Ruang |
| **Wilayah Studi** | Provinsi Jawa Timur |
| **Nama Penulis** | Rifqi Fairurrafi |
| **NIM** | 240411100201 |
| **Kelas** | IF5A |

---

## 1. Data Understanding & Latar Belakang Wilayah

Provinsi Jawa Timur merupakan salah satu pusat gravitasi ekonomi, demografi, dan agrikultur terbesar di Indonesia. Dengan luas wilayah daratan mencapai lebih dari 47.800 km² yang mencakup 38 kabupaten/kota, dinamika pemanfaatan ruang di Jawa Timur berada dalam ketegangan konstan antara **pertumbuhan ekonomi/industrialisasi** dan **pelestarian daya dukung lingkungan serta ketahanan pangan nasional**.

```{figure} images/logo.png
---
width: 140px
align: center
---
Universitas Trunojoyo Madura - Program Studi Teknik Informatika
```

### 1.1 Tekanan Spasial Utama di Jawa Timur

1. **Aglomerasi Perkotaan & Industri Megapolitan Gerbangkertosusila:**
   Koridor metropolitan yang menghubungkan Gresik, Bangkalan, Mojokerto, Surabaya, Sidoarjo, dan Lamongan mengalami ekspansi kawasan terbangun yang luar biasa cepat. Pembangunan infrastruktur strategis nasional (Jalan Tol Trans-Jawa, pelebaran kawasan pelabuhan, sentra logistik) memicu konversi lahan terbuka dan sawah produktif menjadi kawasan industri dan permukiman kedap air (*impervious surface*).
2. **Keterancaman Lumbung Pangan Nasional (LSD / LP2B):**
   Jawa Timur berkontribusi terhadap sekitar 17–18% produksi beras nasional. Sebagian besar sentra produksi padi berada di kawasan dataran aluvial Sungai Brantas dan Bengawan Solo (Lamongan, Bojonegoro, Ngawi, Sidoarjo, Mojokerto, dan Jember). Alih fungsi lahan sawah beririgasi teknis ke non-pertanian menjadi ancaman langsung terhadap ketahanan pangan nasional.
3. **Kerentanan Ekosistem Pesisir & Degradasi Mangrove:**
   Garis pantai Jawa Timur membentang di pesisir utara (Laut Jawa), Selat Madura, dan pesisir selatan (Samudera Hindia). Hutan mangrove di kawasan Pantai Timur Surabaya (Wonorejo & Gunung Anyar), Ujungpangkah Gresik, Probolinggo, dan Teluk Pangpang Banyuwangi berfungsi krusial sebagai sabuk hijau (*green belt*), penahan abrasi pantai, pencegah intrusi air asin ke air tanah perkotaan, serta penyerap karbon biru (*blue carbon*).
4. **Kelestarian Hidrologis Danau Vulkanik & Ranu:**
   Jawa Timur memiliki formasi hidrologis danau vulkanik maar dan kaldera alami yang khas, yang secara lokal dikenal sebagai **Ranu** (misalnya Ranu Grati di Pasuruan; Ranu Klakah, Ranu Bedali, dan Ranu Pakis di Lumajang; serta Ranu Kumbolo dan Ranu Pane di lereng Gunung Semeru / Taman Nasional Bromo Tengger Semeru). Kawasan ini berfungsi sebagai cadangan air tawar vital, ekosistem akuatik tawar, dan pengendali tata air regional yang terancam oleh pencemaran limbah, sedimentasi, dan pelanggaran garis sempadan danau.

---

## 2. Tujuan Analisis Land Use and Land Cover (LULC)

Analisis klasifikasi tutupan dan penggunaan lahan (*Land Use and Land Cover Classification*) dalam proyek ini bertujuan untuk:

1. **Delineasi Spasial Multi-Kelas Berbasis Spektral Objektif:**
   Mengidentifikasi dan memetakan 6 kelas tutupan lahan representatif di Jawa Timur secara akurat dengan memanfaatkan data reflektansi fisik *Bottom-of-Atmosphere* (BOA) dari citra satelit **Sentinel-2A MSI (MultiSpectral Instrument)**.
2. **Diskriminasi Spektral Tingkat Lanjut:**
   Mengembangkan kombinasi fitur band spektral dan indeks vegetasi/air/bangunan (NDVI, NDWI, MNDWI, NDBI, BSI, SAVI, NDRE, CMRI) untuk memecahkan kelemahan klasifikasi tradisional yang sering mencampuradukkan sawah basah dengan perairan tawar, atau mangrove dengan hutan lebat daratan.
3. **Eksperimen Pemodelan Machine Learning Multikelas:**
   Membandingkan kinerja berbagai algoritma klasifikasi mutakhir (*Random Forest, Hist Gradient Boosting, Gradient Boosting, Support Vector Machine, K-Nearest Neighbors, XGBoost, LightGBM*) guna menemukan model dengan akurasi (*Overall Accuracy*) dan *Cohen's Kappa* tertinggi (>99%).
4. **Visualisasi Kartografis Interaktif WMS Satelit:**
   Menyajikan hasil klasifikasi dan titik sampel ground truth ke dalam peta geospasial interaktif berbasis web (Leaflet/Folium) yang menggunakan *Web Map Service* (WMS) Google Maps Satellite dan Hybrid Tiles.
5. **Penyusunan Arahan Kebijakan Tata Ruang Berbasis Spasial:**
   Menghubungkan hasil analisis LULC dengan instrumen hukum tata ruang di Indonesia (UU Tata Ruang, UU Perlindungan LP2B, Perpres Sabuk Hijau Mangrove, dan Permen PUPR Sempadan Danau) untuk mendukung pengambilan kebijakan berbasis data (*data-driven policy*).

---

## 3. Acuan Klasifikasi Lahan di Indonesia (Bukan Sekadar Sawah vs Non-Sawah)

Banyak kajian klasifikasi lahan sederhana hanya membagi tutupan menjadi biner (misalnya sawah vs non-sawah). Pendekatan tersebut tidak mencukupi untuk kebutuhan tata ruang wilayah yang kompleks. Dalam proyek ini, skema klasifikasi tutupan lahan mengacu pada standar nasional resmi yang berlaku di Republik Indonesia:

### 3.1 Standar Nasional Indonesia (SNI 7645:2010 & SNI 7645-1:2014)
SNI 7645 yang diterbitkan oleh **Badan Standardisasi Nasional (BSN)** bekerjasama dengan **Badan Informasi Geospasial (BIG)** merupakan rujukan resmi nasional untuk *Klasifikasi Penutup Lahan*. Standar ini mengadaptasi metodologi internasional *Land Cover Classification System (LCCS)* dari FAO/UNEP.

Berdasarkan SNI 7645, hierarki penutup lahan dibagi menjadi dua kategori utama:
1. **Daerah Bervegetasi (*Vegetated Area*):**
   - Hutan Lahan Kering (Primer dan Sekunder)
   - Hutan Mangrove (Bakau pesisir)
   - Hutan Rawa
   - Pertanian Lahan Basah (Sawah Irigasi, Sawah Tadah Hujan, Sawah Pasang Surut)
   - Pertanian Lahan Kering (Tegalan/Ladang)
   - Perkebunan (Kelapa sawit, karet, kopi, tebu)
2. **Daerah Tak Bervegetasi (*Non-Vegetated Area*):**
   - Lahan Terbangun (Permukiman, Kawasan Industri, Infrastruktur Transportasi)
   - Lahan Terbuka / Tanah Kosong (*Bare Land*)
   - Tubuh Air Daratan (*Inland Water Body*: Danau alami/Ranu, Situ, Rawa tawar, Waduk/Bendungan)
   - Tubuh Air Laut (*Marine Water*: Muara sungai, estuari, teluk, laut lepas)

### 3.2 Regulasi dan Kebijakan Tata Ruang Terkait di Indonesia
* **Peraturan Menteri ATR/BPN No. 14 Tahun 2021:** Pedoman Penyusunan Rencana Tata Ruang Wilayah (RTRW) Provinsi dan Kabupaten/Kota, yang membagi ruang wilayah ke dalam **Kawasan Lindung** (resapan air, sempadan danau, kawasan lindung pesisir) dan **Kawasan Budidaya** (kawasan pertanian pangan, peruntukan industri, perumahan).
* **Undang-Undang No. 41 Tahun 2009 & Kepmen ATR/BPN No. 1589/2021:** Perlindungan Lahan Pertanian Pangan Berkelanjutan (LP2B) dan penetapan peta spasial Lahan Sawah Dilindungi (LSD) untuk mencegah konversi lahan persawahan irigasi teknis di Jawa Timur.
* **Peraturan Presiden No. 73 Tahun 2012:** Strategi Nasional Pengelolaan Ekosistem Mangrove untuk mempertahankan keberadaan sabuk hijau pesisir.
* **Peraturan Menteri PUPR No. 28/PRT/M/2015:** Penetapan Garis Sempadan Sungai dan Sempadan Danau, yang mewajibkan batas perlindungan fisik minimum **50 meter** dari tepi titik pasang tertinggi danau/ranu alami.
* **Peraturan Daerah Provinsi Jawa Timur No. 10 Tahun 2023:** Rencana Tata Ruang Wilayah (RTRW) Provinsi Jawa Timur Tahun 2023–2043.

---

## 4. Definisi 6 Kelas Tutupan Lahan Terpilih di Jawa Timur

Berdasarkan standar nasional di atas, sistem ini mendefinisikan 6 kelas tutupan lahan spasial di Jawa Timur:

| Kode | Nama Kelas | Definisi Spasial & Tipologi SNI | Sebaran Lokasi Representatif di Jawa Timur | Warna Standar |
| :---: | :--- | :--- | :--- | :---: |
| **0** | **Sawah** | Lahan pertanian pangan basah (sawah irigasi teknis/setengah teknis/tadah hujan) yang masuk zonasi LP2B/LSD. | Lamongan, Mojokerto, Sidoarjo, Jember, Bojonegoro, Ngawi | `#eab308` (Kuning Emas) |
| **1** | **Bangunan** | Area terbangun kedap air (*impervious*), mencakup permukiman perkotaan, pergudangan, pabrik industri, jalan raya. | Kota Surabaya, Kota Malang, Sidoarjo Kota, Gresik Industri | `#ef4444` (Merah Urban) |
| **2** | **Mangrove** | Komunitas vegetasi hutan bakau (*Avicennia, Rhizophora, Sonneratia*) di zona pasang surut pesisir dan muara sungai. | Wonorejo Surabaya, Ujungpangkah Gresik, Probolinggo, Banyuwangi | `#059669` (Hijau Zamrud Gelap) |
| **3** | **Lahan Hijau** | Hutan pegunungan lebat (*dense mountain forest*), hutan lindung, cagar alam, dan perkebunan berkanopi rapat. | Tahura Raden Soerjo, TN Bromo Tengger Semeru, Ijen, Meru Betiri | `#15803d` (Hijau Rimba Tua) |
| **4** | **Perairan Terbuka (Laut)** | Tubuh perairan asin laut lepas, selat, dan perairan dalam yang menyerap radiasi inframerah dekat secara sempurna. | Selat Madura, Laut Jawa (Utara Gresik-Tuban), Samudera Hindia | `#1d4ed8` (Biru Samudra) |
| **5** | **Danau (Ranu-ranu)** | Tubuh air tawar daratan yang mencakup danau vulkanik maar alami (Ranu) dan waduk retensi air di pedalaman Jatim. | Ranu Grati Pasuruan, Ranu Klakah Lumajang, Ranu Kumbolo/Pane TNBTS | `#06b6d4` (Cyan / Aqua Danau) |
