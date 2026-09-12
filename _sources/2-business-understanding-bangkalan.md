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

# Business Understanding - Kabupaten Bangkalan

## 1. Latar Belakang

Kabupaten Bangkalan terletak di ujung barat Pulau Madura, Jawa Timur, dan
menjadi kabupaten yang paling terdampak langsung oleh keberadaan
**Jembatan Suramadu**, jembatan yang menghubungkan Madura dengan Surabaya
sejak beroperasi pada tahun 2009. Sejak jembatan ini beroperasi, arus
kendaraan dari Surabaya yang menuju Madura terpusat melalui Bangkalan,
sehingga potensi emisi dari sektor transportasi di wilayah ini meningkat
dibanding sebelum jembatan dibangun.

Selain faktor transportasi, Bangkalan juga memiliki beberapa potensi
sumber emisi lain yang relevan untuk dipantau:

1. **Pertumbuhan kawasan industri.** Aksesibilitas baru pasca-Suramadu
   mendorong minat investasi dan pembangunan kawasan industri di beberapa
   kecamatan.
2. **Rencana fasilitas stockpile (gudang penyangga) batu bara.** Terdapat
   rencana pembangunan fasilitas penyangga batu bara di pesisir utara,
   tepatnya di Kecamatan Klampis, untuk menopang kebutuhan industri
   manufaktur di Jawa Timur. Aktivitas bongkar muat batu bara di daerah
   lain yang serupa umumnya memicu keluhan warga terkait debu dan
   penurunan kualitas udara.
3. **Aktivitas pertanian dan perikanan.** Sebagai kabupaten yang sebagian
   besar wilayahnya masih agraris, aktivitas pertanian (persawahan) dan
   peternakan tetap menjadi sumber emisi metana (CH4) berskala lokal.

Kombinasi faktor transportasi, potensi industrialisasi, dan aktivitas
agraris ini menjadikan pemantauan kualitas udara di Kabupaten Bangkalan
relevan untuk dilakukan secara berkala, terutama sebagai baseline sebelum
pembangunan lebih lanjut berlangsung di wilayah tersebut.

## 2. Tujuan Analisis

Proyek ini bertujuan untuk:

1. **Memantau tren konsentrasi polutan udara utama** (NO2, CO, SO2, CH4)
   di Kabupaten Bangkalan sepanjang periode 24 Agustus 2025 sampai dengan
   24 Agustus 2026, menggunakan data penginderaan jauh Sentinel-5P.
2. **Mengidentifikasi periode dengan konsentrasi tidak wajar** (anomali
   atau outlier) yang dapat mengindikasikan kejadian tertentu, misalnya
   lonjakan aktivitas transportasi, kebakaran lahan, atau gangguan pada
   data satelit itu sendiri.
3. **Menyediakan baseline data kualitas udara** yang dapat dipakai sebagai
   pembanding di masa depan, terutama seiring rencana pertumbuhan kawasan
   industri di wilayah pesisir Bangkalan.
4. **Menyusun alur kerja (pipeline) yang dapat dipakai ulang**, mulai dari
   ekstraksi data satelit, pembersihan data, hingga deteksi anomali,
   sehingga dapat diterapkan kembali untuk kabupaten atau kota lain, atau
   untuk periode waktu berikutnya.

## 3. Manfaat dan Pemangku Kepentingan

Hasil analisis ini diharapkan bermanfaat bagi beberapa pihak:

- **Pemerintah daerah (Dinas Lingkungan Hidup Kabupaten Bangkalan)**,
  sebagai bahan pertimbangan dalam perencanaan tata ruang dan pengawasan
  aktivitas industri di wilayah pesisir.
- **Masyarakat umum**, sebagai informasi awal mengenai kondisi kualitas
  udara di lingkungan tempat tinggal mereka.
- **Peneliti dan akademisi**, sebagai data baseline yang dapat digunakan
  untuk penelitian lanjutan terkait kualitas udara di Pulau Madura.
- **Mahasiswa/penulis proyek ini sendiri**, sebagai latihan penerapan
  kerangka kerja sains data (CRISP-DM) pada data penginderaan jauh.

## 4. Apa itu Indeks Kualitas Udara (AQI)?

**Indeks Kualitas Udara (Air Quality Index atau AQI)** adalah standar
pengukuran yang digunakan untuk melaporkan seberapa bersih atau
tercemarnya udara di suatu wilayah. AQI mengukur konsentrasi polutan udara
utama dan mengubahnya menjadi angka pada skala 0 sampai 500, di mana angka
yang lebih rendah menunjukkan kualitas udara yang lebih baik, dan angka
yang lebih tinggi menunjukkan tingkat polusi yang lebih berbahaya.

Skala AQI umumnya terbagi menjadi enam kategori berikut.

| Rentang AQI | Kategori | Dampak Kesehatan |
|:-----------:|:--------:|:-----------------|
| 0 - 50 | Baik | Kualitas udara memuaskan, risiko polusi rendah |
| 51 - 100 | Sedang | Kualitas udara dapat diterima |
| 101 - 150 | Tidak Sehat bagi Kelompok Sensitif | Anak, lansia, dan penderita asma mulai terdampak |
| 151 - 200 | Tidak Sehat | Seluruh populasi mulai mengalami efek kesehatan |
| 201 - 300 | Sangat Tidak Sehat | Peringatan kesehatan untuk seluruh populasi |
| 301 - 500 | Berbahaya | Kondisi darurat kesehatan masyarakat |

## 5. Polutan yang Dianalisis

Kualitas udara di Kabupaten Bangkalan pada proyek ini dianalisis melalui
empat polutan utama, yang masing-masing mewakili sumber emisi yang
berbeda.

### 5.1 NO2 (Nitrogen Dioksida)

NO2 adalah gas berwarna coklat kemerahan dengan bau menyengat. Polutan ini
dihasilkan terutama dari:

- **Emisi kendaraan bermotor**, yaitu pembakaran bahan bakar fosil pada
  mesin kendaraan.
- **Aktivitas industri**, yaitu pabrik yang menggunakan proses pembakaran.
- **Pembangkit listrik**, terutama yang menggunakan bahan bakar fosil.

**Dampak kesehatan:** iritasi saluran pernapasan, peningkatan risiko
infeksi pernapasan, dan memperburuk kondisi asma. Di Bangkalan, NO2
relevan dipantau karena kepadatan lalu lintas di sekitar akses Suramadu.

### 5.2 CO (Karbon Monoksida)

CO adalah gas tidak berwarna dan tidak berbau yang sangat berbahaya. CO
dihasilkan dari:

- **Pembakaran tidak sempurna** bahan bakar kendaraan bermotor.
- **Asap pabrik** dan industri manufaktur.
- **Pembakaran biomassa**, seperti sampah atau kayu bakar.

**Dampak kesehatan:** mengikat hemoglobin dalam darah lebih kuat dari
oksigen, menyebabkan kekurangan oksigen pada organ tubuh, pusing, mual,
dan pada paparan tinggi dapat menyebabkan kematian.

### 5.3 SO2 (Sulfur Dioksida)

SO2 adalah gas tak berwarna dengan bau tajam dan mengganggu. SO2 berasal
dari:

- **Pembakaran batu bara** pada industri dan pembangkit listrik.
- **Proses industri**, seperti peleburan logam dan pemurnian minyak bumi.
- **Emisi kendaraan** yang menggunakan bahan bakar mengandung sulfur.

**Dampak kesehatan:** iritasi mata dan tenggorokan, memperburuk penyakit
asma dan bronkitis, serta berkontribusi terhadap terbentuknya asam sulfat
yang menyebabkan hujan asam. Polutan ini penting dipantau di Bangkalan
mengingat rencana aktivitas bongkar muat batu bara di pesisir utara.

### 5.4 CH4 (Metana)

CH4 atau metana adalah gas rumah kaca yang sangat efektif dalam
memerangkap panas. Sumber emisi CH4 meliputi:

- **Aktivitas pertanian**, yaitu pencernaan hewan ternak dan sawah.
- **Limbah organik**, yaitu pembusukan sampah di Tempat Pembuangan Akhir
  (TPA).
- **Emisi industri**, yaitu kebocoran gas alam dan proses industri.

**Dampak terhadap lingkungan:** CH4 merupakan gas rumah kaca yang sekitar
80 kali lebih kuat dari CO2 dalam jangka pendek, sehingga berkontribusi
signifikan terhadap perubahan iklim dan pemanasan global.

## 6. Ruang Lingkup Analisis

- **Wilayah:** Kabupaten Bangkalan, Jawa Timur.
- **Polutan:** NO2, CO, SO2, dan CH4.
- **Periode:** 24 Agustus 2025 sampai dengan 24 Agustus 2026 (deret waktu
  harian).
- **Sumber data:** Sentinel-5P L2 (TROPOMI) melalui Copernicus Data Space
  Ecosystem.
- **Keluaran:** deret waktu harian per polutan, visualisasi tren, dan
  daftar tanggal dengan anomali atau outlier yang terdeteksi.

## 7. Kesimpulan

Kabupaten Bangkalan memiliki karakteristik yang menjadikannya relevan
untuk dipantau kualitas udaranya. Posisinya sebagai gerbang utama
Jembatan Suramadu meningkatkan potensi emisi dari sektor transportasi,
sementara rencana pertumbuhan kawasan industri dan fasilitas stockpile
batu bara di pesisir utara berpotensi menambah beban polutan seperti SO2
dan partikel debu di masa depan.

Empat polutan yang dipilih, yaitu NO2, CO, SO2, dan CH4, mewakili sumber
emisi yang berbeda: transportasi, industri, dan aktivitas agraris.
Dengan demikian, analisis ini dapat menjadi baseline kualitas udara
sebelum pembangunan lebih lanjut berlangsung, sekaligus menjadi alat
pemantauan tren dan deteksi anomali yang dapat dijalankan secara berkala
di masa depan. Tahap selanjutnya adalah **Data Understanding**, yaitu
memahami sumber data, cakupan wilayah, dan cara memperoleh data yang
dibutuhkan untuk mencapai tujuan di atas.
