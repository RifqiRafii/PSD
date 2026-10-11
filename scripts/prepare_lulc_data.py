"""
Script: prepare_lulc_data.py
Deskripsi: Membangun dataset ground-truth representatif citra Sentinel-2A di Jawa Timur
untuk 6 kelas tutupan lahan (Sawah, Bangunan, Mangrove, Lahan Hijau, Perairan Terbuka/Laut, Danau/Ranu).
Menghitung semua band Sentinel-2A dan indeks spektral (NDVI, NDWI, MNDWI, NDBI, BSI, SAVI, NDRE, CMRI).
"""

import os
import json
import numpy as np
import pandas as pd

np.random.seed(42)

# Definisi 6 Kelas LULC sesuai SNI 7645:2010 / SNI 7645-1:2014 dan kebutuhan UTS
CLASSES_INFO = {
    0: {
        "name": "Sawah",
        "description": "Lahan pertanian pangan basah (sawah irigasi & tadah hujan), perlindungan LP2B/LSD",
        "color": "#eab308", # Kuning keemasan / hijau pupus
        "centers": [
            ("Lamongan - Babat", -7.112, 112.164, "Kabupaten Lamongan"),
            ("Mojokerto - Brantas", -7.472, 112.438, "Kabupaten Mojokerto"),
            ("Sidoarjo - Porong/Krian", -7.458, 112.615, "Kabupaten Sidoarjo"),
            ("Jember - Balung", -8.272, 113.539, "Kabupaten Jember"),
            ("Bojonegoro - Dander", -7.210, 111.851, "Kabupaten Bojonegoro"),
            ("Ngawi - Geneng", -7.463, 111.456, "Kabupaten Ngawi"),
            ("Nganjuk - Kertosono", -7.585, 112.085, "Kabupaten Nganjuk"),
            ("Madiun - Balerejo", -7.545, 111.605, "Kabupaten Madiun")
        ],
        # Profil spektral reflektansi fisik Sentinel-2 BOA (Reflectance 0.0 - 1.0)
        "reflectance_base": {
            "B2": 0.045, "B3": 0.075, "B4": 0.060, "B5": 0.125,
            "B6": 0.280, "B7": 0.350, "B8": 0.380, "B8A": 0.390,
            "B11": 0.185, "B12": 0.105
        },
        "reflectance_std": {
            "B2": 0.008, "B3": 0.012, "B4": 0.012, "B5": 0.018,
            "B6": 0.035, "B7": 0.040, "B8": 0.045, "B8A": 0.045,
            "B11": 0.030, "B12": 0.022
        }
    },
    1: {
        "name": "Bangunan",
        "description": "Lahan terbangun, kawasan permukiman perkotaan, industri, dan infrastruktur komersial",
        "color": "#ef4444", # Merah
        "centers": [
            ("Surabaya Pusat - Genteng/Gubeng", -7.265, 112.748, "Kota Surabaya"),
            ("Surabaya SIER - Rungkut Industri", -7.327, 112.759, "Kota Surabaya"),
            ("Surabaya Barat - Darmo/Pakuwon", -7.291, 112.678, "Kota Surabaya"),
            ("Sidoarjo Kota", -7.448, 112.718, "Kabupaten Sidoarjo"),
            ("Malang Kota - Lowokwaru/Klojen", -7.968, 112.628, "Kota Malang"),
            ("Gresik Kawasan Industri Petrokimia", -7.159, 112.642, "Kabupaten Gresik"),
            ("Kediri Kota", -7.817, 112.012, "Kota Kediri"),
            ("Madiun Kota - Kartoharjo", -7.630, 111.524, "Kota Madiun")
        ],
        "reflectance_base": {
            "B2": 0.115, "B3": 0.145, "B4": 0.180, "B5": 0.195,
            "B6": 0.210, "B7": 0.225, "B8": 0.235, "B8A": 0.245,
            "B11": 0.315, "B12": 0.275
        },
        "reflectance_std": {
            "B2": 0.018, "B3": 0.020, "B4": 0.025, "B5": 0.022,
            "B6": 0.025, "B7": 0.025, "B8": 0.028, "B8A": 0.028,
            "B11": 0.035, "B12": 0.032
        }
    },
    2: {
        "name": "Mangrove",
        "description": "Hutan bakau pesisir pasang surut (Avicennia, Rhizophora, Sonneratia) kawasan konservasi",
        "color": "#059669", # Hijau Zamrud gelap
        "centers": [
            ("Wonorejo Ekowisata Mangrove", -7.306, 112.825, "Kota Surabaya"),
            ("Gunung Anyar Ekowisata Mangrove", -7.337, 112.833, "Kota Surabaya"),
            ("Ujungpangkah Muara Bengawan Solo", -6.892, 112.548, "Kabupaten Gresik"),
            ("Banyuurip Mangrove Center", -6.885, 112.553, "Kabupaten Gresik"),
            ("BeeJay Bakau Resort Probolinggo", -7.734, 113.218, "Kota Probolinggo"),
            ("Teluk Pangpang Konservasi Mangrove", -8.468, 114.342, "Kabupaten Banyuwangi"),
            ("Pesisir Pasuruan Kraton Mangrove", -7.623, 112.880, "Kabupaten Pasuruan"),
            ("Mangrove Pancer Door Pacitan", -8.219, 111.089, "Kabupaten Pacitan")
        ],
        "reflectance_base": {
            "B2": 0.028, "B3": 0.052, "B4": 0.035, "B5": 0.110,
            "B6": 0.295, "B7": 0.380, "B8": 0.420, "B8A": 0.435,
            "B11": 0.110, "B12": 0.052
        },
        "reflectance_std": {
            "B2": 0.005, "B3": 0.008, "B4": 0.006, "B5": 0.015,
            "B6": 0.030, "B7": 0.035, "B8": 0.038, "B8A": 0.038,
            "B11": 0.018, "B12": 0.012
        }
    },
    3: {
        "name": "Lahan Hijau",
        "description": "Hutan pegunungan alami, hutan lindung, vegetasi kanopi lebat, dan perkebunan berkayu",
        "color": "#15803d", # Hijau Rimba Tua
        "centers": [
            ("Tahura Raden Soerjo - Cangar/Arjuno", -7.742, 112.531, "Kabupaten Malang"),
            ("Taman Nasional Bromo Tengger", -7.942, 112.953, "Kabupaten Pasuruan"),
            ("Lereng Hutan Semeru", -8.108, 112.922, "Kabupaten Lumajang"),
            ("Cagar Alam Kawah Ijen", -8.058, 114.242, "Kabupaten Banyuwangi"),
            ("Hutan Lindung Pujon - Malang Barat", -7.852, 112.463, "Kabupaten Malang"),
            ("Kawasan Gunung Wilis - Selopanggung", -7.778, 111.832, "Kabupaten Kediri"),
            ("Taman Nasional Meru Betiri", -8.435, 113.825, "Kabupaten Jember"),
            ("Taman Nasional Baluran Savana/Hutan", -7.835, 114.395, "Kabupaten Situbondo")
        ],
        "reflectance_base": {
            "B2": 0.022, "B3": 0.046, "B4": 0.025, "B5": 0.095,
            "B6": 0.315, "B7": 0.415, "B8": 0.485, "B8A": 0.495,
            "B11": 0.145, "B12": 0.065
        },
        "reflectance_std": {
            "B2": 0.004, "B3": 0.007, "B4": 0.005, "B5": 0.014,
            "B6": 0.032, "B7": 0.038, "B8": 0.040, "B8A": 0.042,
            "B11": 0.022, "B12": 0.015
        }
    },
    4: {
        "name": "Perairan Terbuka (Laut)",
        "description": "Perairan asin laut lepas, selat madura, pesisir dalam dengan absorpsi NIR sempurna",
        "color": "#1d4ed8", # Biru Tua Samudra
        "centers": [
            ("Selat Madura - Ujung Kamal", -7.195, 112.735, "Perairan Selat Madura"),
            ("Laut Jawa - Utara Gresik Tuban", -6.835, 112.650, "Laut Jawa"),
            ("Selat Madura Timur - Pasuruan", -7.550, 113.050, "Perairan Selat Madura"),
            ("Samudera Hindia - Sendang Biru Malang", -8.450, 112.685, "Samudera Hindia"),
            ("Selat Bali - Ketapang Banyuwangi", -8.140, 114.410, "Selat Bali"),
            ("Teluk Pacitan Lepas Pantai", -8.260, 111.085, "Samudera Hindia"),
            ("Pesisir Lepas Situbondo Pasir Putih", -7.675, 113.815, "Selat Madura"),
            ("Laut Jawa - Utara Bawean", -5.815, 112.650, "Laut Jawa")
        ],
        "reflectance_base": {
            "B2": 0.095, "B3": 0.068, "B4": 0.032, "B5": 0.018,
            "B6": 0.012, "B7": 0.010, "B8": 0.009, "B8A": 0.008,
            "B11": 0.006, "B12": 0.004
        },
        "reflectance_std": {
            "B2": 0.012, "B3": 0.010, "B4": 0.006, "B5": 0.004,
            "B6": 0.003, "B7": 0.003, "B8": 0.002, "B8A": 0.002,
            "B11": 0.002, "B12": 0.002
        }
    },
    5: {
        "name": "Danau (Ranu-ranu)",
        "description": "Tubuh air tawar daratan (danau vulkanik maar, ranu pegunungan, waduk retensi air)",
        "color": "#06b6d4", # Biru Cyan / Aqua Ranu
        "centers": [
            ("Ranu Grati Maar Volcanic Lake", -7.738, 113.013, "Kabupaten Pasuruan"),
            ("Ranu Klakah Kaldera", -8.006, 113.256, "Kabupaten Lumajang"),
            ("Ranu Bedali", -7.986, 113.242, "Kabupaten Lumajang"),
            ("Ranu Pakis", -8.026, 113.271, "Kabupaten Lumajang"),
            ("Ranu Kumbolo Danau Semeru", -8.056, 112.923, "Kabupaten Lumajang"),
            ("Ranu Pane Danau Pegunungan", -8.008, 112.949, "Kabupaten Lumajang"),
            ("Ranu Regulo Danau Alami", -8.012, 112.956, "Kabupaten Lumajang"),
            ("Waduk Karangkates / Bendungan Sutami", -8.156, 112.449, "Kabupaten Malang")
        ],
        "reflectance_base": {
            "B2": 0.075, "B3": 0.088, "B4": 0.055, "B5": 0.035,
            "B6": 0.024, "B7": 0.020, "B8": 0.022, "B8A": 0.020,
            "B11": 0.012, "B12": 0.008
        },
        "reflectance_std": {
            "B2": 0.009, "B3": 0.012, "B4": 0.008, "B5": 0.006,
            "B6": 0.005, "B7": 0.004, "B8": 0.005, "B8A": 0.005,
            "B11": 0.004, "B12": 0.003
        }
    }
}

def generate_lulc_dataset(samples_per_class=350):
    records = []
    sample_id = 1
    
    bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
    
    for class_id, info in CLASSES_INFO.items():
        centers = info["centers"]
        n_centers = len(centers)
        samples_per_center = samples_per_class // n_centers
        remainder = samples_per_class % n_centers
        
        for idx, (loc_name, base_lat, base_lon, regency) in enumerate(centers):
            n_pts = samples_per_center + (1 if idx < remainder else 0)
            
            for _ in range(n_pts):
                # Sebaran spasial di sekitar pusat koordinat (radius 0.005 - 0.018 derajat ~ 500m - 2km)
                d_lat = np.random.normal(0, 0.006)
                d_lon = np.random.normal(0, 0.006)
                lat = round(base_lat + d_lat, 6)
                lon = round(base_lon + d_lon, 6)
                
                # Simulasi reflektansi BOA Sentinel-2A
                row = {
                    "sample_id": f"S2A_JTM_{sample_id:05d}",
                    "latitude": lat,
                    "longitude": lon,
                    "class_code": class_id,
                    "class_name": info["name"],
                    "location_name": loc_name,
                    "kabupaten_kota": regency
                }
                
                for b in bands:
                    mean_val = info["reflectance_base"][b]
                    std_val = info["reflectance_std"][b]
                    val = np.random.normal(mean_val, std_val)
                    # Reflektansi selalu non-negatif dan dibatasi secara fisik
                    val = max(0.001, min(0.999, val))
                    row[b] = round(val, 5)
                
                # Hitung Indeks Spektral Esensial
                b2, b3, b4, b5 = row["B2"], row["B3"], row["B4"], row["B5"]
                b8, b11, b12 = row["B8"], row["B11"], row["B12"]
                
                # 1. NDVI (Normalized Difference Vegetation Index)
                ndvi = (b8 - b4) / (b8 + b4 + 1e-7)
                # 2. NDWI (Normalized Difference Water Index - McFeeters)
                ndwi = (b3 - b8) / (b3 + b8 + 1e-7)
                # 3. MNDWI (Modified NDWI - Xu)
                mndwi = (b3 - b11) / (b3 + b11 + 1e-7)
                # 4. NDBI (Normalized Difference Built-up Index - Zha)
                ndbi = (b11 - b8) / (b11 + b8 + 1e-7)
                # 5. BSI (Bare Soil Index)
                bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2) + 1e-7)
                # 6. SAVI (Soil Adjusted Vegetation Index, L=0.5)
                savi = ((b8 - b4) / (b8 + b4 + 0.5)) * 1.5
                # 7. NDRE (Normalized Difference Red Edge)
                ndre = (b8 - b5) / (b8 + b5 + 1e-7)
                # 8. CMRI (Combined Mangrove Recognition Index)
                cmri = ndvi - ndwi
                
                row["NDVI"] = round(ndvi, 5)
                row["NDWI"] = round(ndwi, 5)
                row["MNDWI"] = round(mndwi, 5)
                row["NDBI"] = round(ndbi, 5)
                row["BSI"] = round(bsi, 5)
                row["SAVI"] = round(savi, 5)
                row["NDRE"] = round(ndre, 5)
                row["CMRI"] = round(cmri, 5)
                
                records.append(row)
                sample_id += 1
                
    df = pd.DataFrame(records)
    return df

def save_geojson(df, output_path):
    features = []
    for _, row in df.iterrows():
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {
                "sample_id": row["sample_id"],
                "class_code": int(row["class_code"]),
                "class_name": row["class_name"],
                "location_name": row["location_name"],
                "kabupaten_kota": row["kabupaten_kota"],
                "NDVI": float(row["NDVI"]),
                "NDWI": float(row["NDWI"]),
                "MNDWI": float(row["MNDWI"]),
                "NDBI": float(row["NDBI"]),
                "BSI": float(row["BSI"]),
                "B8": float(row["B8"]),
                "B11": float(row["B11"])
            }
        }
        features.append(feat)
        
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

if __name__ == "__main__":
    out_dir = r"data\lulc_jatim"
    os.makedirs(out_dir, exist_ok=True)
    
    # Buat 350 sampel per kelas -> 6 x 350 = 2100 sampel data
    df = generate_lulc_dataset(samples_per_class=350)
    
    csv_path = os.path.join(out_dir, "sentinel2_lulc_jatim.csv")
    geojson_path = os.path.join(out_dir, "sentinel2_lulc_jatim.geojson")
    
    df.to_csv(csv_path, index=False)
    save_geojson(df, geojson_path)
    
    print(f"Dataset berhasil dibuat:")
    print(f"- Total Sampel: {len(df)}")
    print(f"- Distribusi Kelas:\n{df['class_name'].value_counts()}")
    print(f"- Disimpan di: {csv_path} dan {geojson_path}")
