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

# UTS SIG: Koleksi Data, Eksperimen Machine Learning & Evaluasi Akurasi

Bab ini menguraikan tahapan pengumpulan data sampling spasial (*data collection*), pembagian data latih dan uji (*train-test split*), komparasi multi-algoritma *Machine Learning*, hingga penentuan model dengan akurasi klasifikasi tertinggi.

---

## 1. Koleksi Data Ground-Truth Sentinel-2A di Jawa Timur

Dataset dibangun dengan mengambil sampel koordinat nyata di berbagai bentang alam representatif di Provinsi Jawa Timur. Untuk memastikan validitas statistik dan mencegah terjadinya *class imbalance bias*, diterapkan strategi **Stratified Balanced Sampling** dengan alokasi **350 titik sampel per kelas**.

```{table} Distribusi Sampel Ground-Truth Berdasarkan 6 Kelas Tutupan Lahan
:name: tabel-distribusi-sampel

| Kode Kelas | Nama Kelas | Jumlah Total Sampel | Proporsi (%) | Wilayah Lokasi Pengambilan Sampel di Jawa Timur |
| :---: | :--- | :---: | :---: | :--- |
| **0** | **Sawah** | 350 | 16.67% | Lamongan (Babat), Mojokerto, Sidoarjo, Jember (Balung), Bojonegoro, Ngawi |
| **1** | **Bangunan** | 350 | 16.67% | Surabaya Pusat, Surabaya SIER, Malang Kota, Sidoarjo Kota, Gresik Industri |
| **2** | **Mangrove** | 350 | 16.67% | Ekowisata Wonorejo Surabaya, Gunung Anyar, Ujungpangkah Gresik, Probolinggo |
| **3** | **Lahan Hijau** | 350 | 16.67% | Tahura Raden Soerjo, Lereng Bromo Tengger, Semeru, Ijen Banyuwangi, Pujon |
| **4** | **Perairan Terbuka (Laut)** | 350 | 16.67% | Selat Madura (Kamal-Surabaya), Laut Jawa (Tuban-Gresik), Samudera Hindia |
| **5** | **Danau (Ranu-ranu)** | 350 | 16.67% | Ranu Grati Pasuruan, Ranu Klakah, Ranu Kumbolo, Ranu Pane, Waduk Sutami |
| **Total** | **6 Kelas LULC** | **2.100** | **100.00%** | **Provinsi Jawa Timur** |
```

---

## 2. Pembagian Data Training dan Testing (*Data Splitting*)

Dataset dipartisi menggunakan rasio standar **80% Training Set** dan **20% Testing Set** dengan teknik *Stratified Train-Test Split* menggunakan `random_state=42`. Hal ini menjamin bahwa proporsi setiap kelas pada data latih dan data uji tetap identik.

```{table} Rincian Pembagian Data Training vs Testing
:name: tabel-split-data

| Kategori Data | Persentase | Jumlah Sampel Tiap Kelas (x6 Kelas) | Total Sampel Data |
| :--- | :---: | :---: | :---: |
| **Data Training (Latih)** | 80% | 280 sampel / kelas | **1.680 Sampel** |
| **Data Testing (Uji)** | 20% | 70 sampel / kelas | **420 Sampel** |
| **Total Data Eksperimen** | **100%** | **350 sampel / kelas** | **2.100 Sampel** |
```

* **Data Training (1.680 sampel):** Digunakan untuk melatih parameter internal model klasifikasi.
* **Data Testing (420 sampel):** Digunakan secara independen untuk menguji kemampuan generalisasi model terhadap data baru yang belum pernah dilihat sebelumnya.

---

## 3. Komparasi Multi-Model Machine Learning

Sesuai instruksi tugas: *"gunakan model lain yang menghasilkan akurasi paling tinggi"*, dilakukan pengujian komparatif terhadap **7 algoritma Machine Learning**:

1. **Random Forest Classifier (RF):** Algoritma ensemble berbasis bagging dengan 200 pohon keputusan (*decision trees*).
2. **Hist Gradient Boosting Classifier (HistGBM):** Varian boosting cepat berbasis *histogram binning* dari scikit-learn (arsitektur serupa LightGBM).
3. **Gradient Boosting Classifier (GBM):** Boosting bertahap berbasis penurunan gradien (*gradient descent*).
4. **XGBoost (Extreme Gradient Boosting):** Boosting pohon keputusan dengan regularisasi L1/L2 ketat.
5. **LightGBM:** Algoritma boosting berbasis *leaf-wise tree growth*.
6. **Support Vector Machine (SVM):** Model pemisah berbasis hyperplane dengan kernel *Radial Basis Function (RBF)* dan standarisasi fitur.
7. **K-Nearest Neighbors (KNN):** Model berbasis jarak dengan pembobotan *inverse distance* ($k=5$).

```{table} Hasil Komparasi Performa 7 Model Klasifikasi LULC Jawa Timur
:name: tabel-komparasi-model

| Peringkat | Algoritma Model | Overall Accuracy (OA) | Cohen's Kappa ($\kappa$) | Macro F1-Score | Macro Precision | Macro Recall | Status Evaluasi |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 **1** | **Hist Gradient Boosting** | **99.29%** | **0.9914** | **0.9928** | **0.9930** | **0.9929** | ⭐ **Model Terbaik** |
| 🥈 **2** | **Support Vector Machine (RBF)** | **99.29%** | **0.9914** | **0.9929** | **0.9931** | **0.9929** | Sangat Tinggi |
| 🥉 **3** | **Random Forest Classifier** | **99.05%** | **0.9886** | **0.9905** | **0.9906** | **0.9905** | Sangat Andal & Robust |
| 4 | **XGBoost Classifier** | **99.05%** | **0.9886** | **0.9905** | **0.9906** | **0.9905** | Sangat Tinggi |
| 5 | **LightGBM Classifier** | **99.05%** | **0.9886** | **0.9905** | **0.9907** | **0.9905** | Sangat Cepat |
| 6 | **Gradient Boosting (GBM)** | **98.81%** | **0.9857** | **0.9881** | **0.9883** | **0.9881** | Tinggi |
| 7 | **K-Nearest Neighbors (KNN)** | **98.57%** | **0.9829** | **0.9857** | **0.9861** | **0.9857** | Baseline Cukup Baik |
```

> **Temuan Eksperimen:**
> Model **Hist Gradient Boosting** dan **Support Vector Machine (RBF)** mencatatkan akurasi tertinggi sebesar **99.29%** dengan nilai **Cohen's Kappa 0.9914** (kategori *Almost Perfect Agreement*). Random Forest dan XGBoost juga menunjukkan performa luar biasa dengan akurasi **99.05%**. Hist Gradient Boosting dipilih sebagai model produksi karena keunggulannya dalam waktu inferensi cepat dan ketahanan terhadap multikolinearitas antar band spektral.

---

## 4. Confusion Matrix Model Terbaik

Confusion matrix menunjukkan distribusi prediksi model terbaik (Hist Gradient Boosting) pada data uji independen (420 sampel testing):

```{table} Confusion Matrix Hasil Klasifikasi Data Testing (420 Sampel)
:name: tabel-confusion-matrix

| Kelas Sebenarnya \ Prediksi | Sawah | Bangunan | Mangrove | Lahan Hijau | Laut | Danau (Ranu) | Total Uji | Recall (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sawah** | **69** | 0 | 1 | 0 | 0 | 0 | 70 | **98.57%** |
| **Bangunan** | 0 | **70** | 0 | 0 | 0 | 0 | 70 | **100.00%** |
| **Mangrove** | 1 | 0 | **69** | 0 | 0 | 0 | 70 | **98.57%** |
| **Lahan Hijau** | 0 | 0 | 1 | **69** | 0 | 0 | 70 | **98.57%** |
| **Perairan Laut** | 0 | 0 | 0 | 0 | **70** | 0 | 70 | **100.00%** |
| **Danau (Ranu)** | 0 | 0 | 0 | 0 | 0 | **70** | 70 | **100.00%** |
| **Total Prediksi** | 70 | 70 | 71 | 69 | 70 | 70 | 420 | - |
| **Precision (%)** | **98.57%** | **100.00%** | **97.18%** | **100.00%** | **100.00%** | **100.00%** | - | **OA: 99.29%** |
```

---

## 5. Analisis Tingkat Pengaruh Fitur (*Feature Importance*)

Melalui evaluasi bobot kepentingan fitur (*Gini Importance*) pada ensemble Random Forest, teridentifikasi fitur-fitur yang paling menentukan keberhasilan klasifikasi penutup lahan:

```{table} Peringkat 10 Fitur Paling Berpengaruh dalam Klasifikasi
:name: tabel-feature-importance

| Peringkat | Nama Fitur | Bobot Kepentingan Relatif | Peran Utama dalam Pembedaan Kelas |
| :---: | :---: | :---: | :--- |
| 1 | **CMRI** | **13.75%** | Memisahkan hutan mangrove dari hutan darat dan sawah. |
| 2 | **B8 (NIR)** | **12.40%** | Membedakan seluruh kelas vegetasi dari tubuh air (laut dan danau). |
| 3 | **NDBI** | **11.20%** | Membedakan kawasan terbangun (beton/atap) dari lahan terbuka dan vegetasi. |
| 4 | **B11 (SWIR1)** | **10.15%** | Mengukur kelembapan kanopi dan mendeteksi bahan bangunan buatan. |
| 5 | **NDVI** | **9.80%** | Mengukur kerapatan biomassa hijau antara sawah, mangrove, dan hutan lebat. |
| 6 | **MNDWI** | **8.90%** | Memisahkan air danau tawar dan laut dari pantulan bising permukiman. |
| 7 | **B3 (Green)** | **7.50%** | Membedakan perairan laut jernih dari danau vulkanik (Ranu) yang mengandung fitoplankton. |
| 8 | **SAVI** | **6.90%** | Mengoreksi pantulan tanah pada lahan persawahan yang jarang atau baru ditanami. |
| 9 | **BSI** | **6.40%** | Mendeteksi tanah kering, lahan olahan sawah bera, dan singkapan batuan. |
| 10 | **NDRE** | **5.20%** | Mengukur klorofil kanopi lebat tanpa mengalami saturasi radiometrik. |
```
