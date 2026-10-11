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

# UTS SIG: Karakteristik Band Sentinel-2A & Ekstraksi Fitur Spektral

Bab ini menyajikan karakteristik radiometrik instrumen **Sentinel-2A MSI (MultiSpectral Instrument)**, perbandingan spesifikasi 13 band spektral, serta perumusan matematika seluruh fitur turunan (indeks spektral) yang diekstraksi untuk membedakan ke-6 kelas penutup lahan di Jawa Timur.

---

## 1. Karakteristik Macam-Macam Band pada Sentinel-2A

Satelit Sentinel-2A beroperasi pada orbit kutub sinkron matahari (*sun-synchronous orbit*) pada ketinggian 786 km, membawa sensor optik multispektral canggih yang merekam 13 saluran radiasi elektromagnetik mulai dari spektrum tampak (*visible*), tepi merah (*red-edge*), inframerah dekat (*NIR*), hingga inframerah gelombang pendek (*SWIR*).

```{table} Rincian Karakteristik 13 Band Spektral Citra Satelit Sentinel-2A
:name: tabel-band-sentinel2a

| Nomor Band | Nama Saluran | Panjang Gelombang Tengah ($\lambda$) | Resolusi Spasial | Lebar Pita Spektral | Kegunaan Utama & Sensitivitas Deteksi |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **B1** | Coastal Aerosol | 443 nm | 60 m | 21 nm | Estimasi aerosol atmosfer, penetrasi perairan pesisir dangkal, koreksi hamburan Rayleigh. |
| **B2** | Blue (Biru) | 490 nm | 10 m | 66 nm | Pembeda vegetasi vs tanah terbuka, penetrasi air dalam, deteksi klorofil-a tanaman. |
| **B3** | Green (Hijau) | 560 nm | 10 m | 36 nm | Puncak pantulan klorofil daun sehat, delineasi batas air dan daratan melalui indeks NDWI. |
| **B4** | Red (Merah) | 665 nm | 10 m | 31 nm | Penyerapan klorofil maksimal untuk fotosintesis; komponen wajib perhitungan indeks vegetasi NDVI. |
| **B5** | Vegetation Red Edge 1 | 705 nm | 20 m | 15 nm | Transisi tajam batas red-edge; sangat sensitif terhadap stres klorofil dan variasi kanopi mangrove. |
| **B6** | Vegetation Red Edge 2 | 740 nm | 20 m | 15 nm | Penentuan indeks luas daun (*Leaf Area Index / LAI*) dan estimasi kandungan nitrogen vegetasi. |
| **B7** | Vegetation Red Edge 3 | 783 nm | 20 m | 20 nm | Evaluasi struktur biomassa kanopi hutan lebat (*dense forest*) dan estimasi kesehatan hutan. |
| **B8** | NIR (Near Infrared Wide) | 842 nm | 10 m | 106 nm | Reflektansi maksimal struktur sel mesofil daun hijau; diserap hampir mutlak oleh molekul air murni. |
| **B8A** | Narrow NIR | 865 nm | 20 m | 21 nm | Pita inframerah dekat sempit untuk menghindari gangguan uap air atmosfer; kalibrasi biofisik. |
| **B9** | Water Vapour | 940 nm | 60 m | 20 nm | Pengukuran absorbsi uap air atmosferik untuk normalisasi radiometrik citra. |
| **B10** | SWIR - Cirrus | 1375 nm | 60 m | 30 nm | Deteksi awan tipis cirrus di lapisan troposfer atas yang tidak tampak pada saluran visual. |
| **B11** | SWIR 1 | 1610 nm | 20 m | 91 nm | Sensitivitas tinggi terhadap kelembapan daun dan tanah; memantulkan radiasi tinggi pada beton/material bangunan (NDBI). |
| **B12** | SWIR 2 | 2190 nm | 20 m | 175 nm | Diskriminasi batuan, mineral, lahan terbakar/kering, serta pemisahan area urban kedap air. |
```

---

## 2. Deskripsi Lengkap Seluruh Fitur yang Dikeluarkan Beserta Formulanya

Dalam model klasifikasi ini, data masukan (*input feature space*) terdiri dari **18 Fitur**, yang terbagi atas:
1. **10 Band Spektral Reflektansi BOA:** $B_2, B_3, B_4, B_5, B_6, B_7, B_8, B_{8A}, B_{11}, B_{12}$.
2. **8 Indeks Spektral Turunan:** Indeks biofisik dan geomorfik yang diformulasikan secara khusus untuk memisahkan 6 kelas target.

Berikut adalah uraian teoritis dan formula matematis masing-masing indeks:

### 2.1 Normalized Difference Vegetation Index (NDVI)
NDVI adalah indeks vegetasi standar yang memanfaatkan perbedaan kontras antara penyerapan radiasi pada spektrum merah (*Red*) oleh pigmen klorofil dan pemantulan tinggi pada spektrum inframerah dekat (*NIR*) oleh jaringan daun berpori (*spongy mesophyll*).

$$\text{NDVI} = \frac{B_8 - B_4}{B_8 + B_4}$$

* **Rentang Nilai:** $-1.0$ hingga $+1.0$
* **Perilaku Spektral:**
  - Hutan Lahan Hijau: Sangat tinggi ($0.75 - 0.90$)
  - Sawah (fase vegetatif): Sedang hingga tinggi ($0.45 - 0.75$)
  - Mangrove: Tinggi ($0.65 - 0.88$)
  - Bangunan: Rendah hingga mendekati nol ($0.05 - 0.20$)
  - Tubuh Air (Laut & Danau): Negatif ($< 0$)

### 2.2 Normalized Difference Water Index (NDWI - McFeeters)
Dikembangkan oleh McFeeters (1996) untuk mendelineasi tubuh air terbuka dan meningkatkan kontras antara air dengan fitur daratan. Indeks ini memanfaatkan reflektansi tinggi spektrum hijau (*Green*) dan penyerapan total pada inframerah dekat (*NIR*).

$$\text{NDWI} = \frac{B_3 - B_8}{B_3 + B_8}$$

* **Perilaku Spektral:**
  - Perairan Terbuka (Laut): Sangat tinggi ($> +0.35$)
  - Danau Alami (Ranu): Tinggi ($+0.20 - +0.45$)
  - Vegetasi dan Lahan Hijau: Negatif kuat ($< -0.40$)

### 2.3 Modified Normalized Difference Water Index (MNDWI - Xu)
Xu (2006) memodifikasi NDWI dengan mengganti pita NIR menggunakan pita Shortwave Infrared ($B_{11}$ / SWIR1). Penggantian ini secara efektif menekan sinyal bising dari kawasan terbangun dan tanah kering, yang sering kali menghasilkan nilai positif palsu pada NDWI standar.

$$\text{MNDWI} = \frac{B_3 - B_{11}}{B_3 + B_{11}}$$

* **Perilaku Spektral:**
  - Sangat efektif membedakan Danau (Ranu) dan Perairan Laut dari area bangunan permukiman dan persawahan yang baru diairi.

### 2.4 Normalized Difference Built-up Index (NDBI - Zha)
Zha et al. (2003) merumuskan NDBI untuk memetakan kawasan perkotaan dan lahan terbangun (*built-up land*). Permukaan buatan manusia (aspal, genteng, beton semen) memiliki sifat memantulkan radiasi SWIR1 ($B_{11}$) jauh lebih tinggi dibandingkan dengan radiasi NIR ($B_8$).

$$\text{NDBI} = \frac{B_{11} - B_8}{B_{11} + B_8}$$

* **Perilaku Spektral:**
  - Bangunan / Urban: Bernilai positif ($+0.12$ hingga $+0.40$)
  - Lahan Hijau, Hutan, Mangrove, dan Air: Bernilai negatif ($-0.15$ hingga $-0.60$)

### 2.5 Bare Soil Index (BSI - Rikimaru)
BSI mengombinasikan saluran Blue, Red, NIR, dan SWIR1 untuk mendeteksi tanah terbuka tanpa tutupan vegetasi, lahan sawah saat periode bera/pengolahan tanah (*plowing*), serta bukaan lahan konstruksi.

$$\text{BSI} = \frac{(B_{11} + B_4) - (B_8 + B_2)}{(B_{11} + B_4) + (B_8 + B_2)}$$

* **Perilaku Spektral:**
  - Bernilai tinggi pada tanah terbuka dan persawahan kering yang belum ditanami padi.

### 2.6 Soil-Adjusted Vegetation Index (SAVI - Huete)
Huete (1988) memperkenalkan faktor koreksi latar belakang tanah ($L$) untuk meminimalkan gangguan kecerahan tanah pada area dengan kanopi tanaman yang belum rapat. Dalam analisis ini digunakan nilai standar $L = 0.5$.

$$\text{SAVI} = \frac{B_8 - B_4}{B_8 + B_4 + 0.5} \times (1 + 0.5)$$

* **Perilaku Spektral:**
  - Mengoreksi estimasi klorofil pada petak sawah saat fase tanam awal atau sawah tergenang, sehingga tidak salah diklasifikasikan sebagai tubuh air murni.

### 2.7 Normalized Difference Red Edge (NDRE - Barnes)
NDRE menggantikan pita Red ($B_4$) dengan pita pita Red Edge 1 ($B_5$). Saluran red-edge mampu menembus lapisan kanopi lebih dalam tanpa mengalami kejenuhan radiasi (*signal saturation*), menjadikannya ideal untuk mengukur biomassa kanopi lebat.

$$\text{NDRE} = \frac{B_8 - B_5}{B_8 + B_5}$$

* **Perilaku Spektral:**
  - Sangat berguna dalam membedakan Hutan Rimba Pegunungan (Tahura/Bromo) yang memiliki nilai NDRE sangat tinggi dari tutupan sawah musiman.

### 2.8 Combined Mangrove Recognition Index (CMRI)
CMRI dirumuskan dari selisih antara indeks vegetasi (NDVI) dan indeks kebasahan air (NDWI). Hutan mangrove memiliki keunikan biologis: kanopinya hijau lebat (NDVI tinggi), namun substrat akarnya terendam air payau pasang surut berlumpur (NDWI sedikit terpengaruh).

$$\text{CMRI} = \text{NDVI} - \text{NDWI}$$

* **Perilaku Spektral:**
  - Mangrove: Nilai CMRI positif tinggi dan stabil ($+0.40$ hingga $+0.75$)
  - Memisahkan mangrove secara sempurna dari sawah, hutan darat, dan air laut murni.

---

## 3. Matriks Karakteristik Pembeda Antar-Kelas

```{table} Matriks Profil Respon Spektral 6 Kelas Tutupan Lahan Jawa Timur
:name: tabel-profil-spektral

| Kelas Tutupan Lahan | NDVI | NDWI | MNDWI | NDBI | BSI | CMRI | Ciri Reflektansi Band Kunci |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Sawah** | $0.50 - 0.75$ | Negatif | Negatif | Negatif | Sedang | $0.6 - 0.9$ | B8 moderat, B11 sedang, fluktuatif mengikuti siklus tanam padi. |
| **Bangunan** | $0.05 - 0.20$ | Sangat Negatif | Sangat Negatif | **Positif** | **Tinggi** | $0.2 - 0.4$ | B11 dan B12 sangat tinggi; memantulkan spektrum pendek. |
| **Mangrove** | **Tinggi** ($0.7 - 0.88$) | Negatif moderat | Rendah | Negatif | Rendah | **Khas Tinggi** | B8 tinggi, B11 & B12 rendah karena kelembapan substrat lumpur. |
| **Lahan Hijau** | **Sangat Tinggi** ($> 0.80$) | Sangat Negatif | Sangat Negatif | Sangat Negatif | Sangat Rendah | **Tinggi** | B8 sangat tinggi ($> 0.45$), B5-B7 red edge curam. |
| **Perairan Laut** | Negatif kuat ($< -0.2$) | **Sangat Tinggi** ($> 0.4$) | **Sangat Tinggi** | Negatif kuat | Negatif | Negatif | B8 dan B11 mendekati 0; penyerapan sempurna. |
| **Danau (Ranu)** | Negatif ringan ($ -0.1$) | **Tinggi** ($0.2 - 0.45$) | **Tinggi** | Negatif kuat | Negatif | Negatif | B3 (Green) sedikit lebih tinggi dari laut karena fitoplankton alami. |
```
