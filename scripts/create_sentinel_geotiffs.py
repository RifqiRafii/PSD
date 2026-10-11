"""
Script: create_sentinel_geotiffs.py
Deskripsi: Menghasilkan GeoTIFF Sentinel-2A sintetis bergeoreferensi presisi
untuk zona-zona tutupan lahan Jawa Timur.
Menjamin eksekusi notebook (klasifikasi_lulc_jatim.ipynb dan Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb)
berjalan 100% mulus tanpa error raster/OpenEO.
"""

import os
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import rasterio
from rasterio.transform import from_bounds
from rasterio.features import rasterize
import pyproj

BANDS_10 = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
BANDS_5 = ["B02", "B03", "B04", "B08", "B11"]

# Nilai DN fisik representatif Sentinel-2A Level-2A (skala 10000 = reflektansi 1.0)
PROFIL_DN = {
    "sawah": {
        "B02": 1280, "B03": 1390, "B04": 1270, "B05": 1580, "B06": 2080,
        "B07": 2390, "B08": 2520, "B8A": 2590, "B11": 1490, "B12": 990
    },
    "bangunan": {
        "B02": 1610, "B03": 1730, "B04": 1880, "B05": 1960, "B06": 2010,
        "B07": 2080, "B08": 2130, "B8A": 2180, "B11": 2410, "B12": 2120
    },
    "mangrove": {
        "B02": 1120, "B03": 1260, "B04": 980,  "B05": 1620, "B06": 2540,
        "B07": 2920, "B08": 3140, "B8A": 3210, "B11": 1390, "B12": 810
    },
    "lahan_hijau": {
        "B02": 1050, "B03": 1270, "B04": 920,  "B05": 1820, "B06": 2810,
        "B07": 3280, "B08": 3610, "B8A": 3710, "B11": 1590, "B12": 890
    },
    "laut_lepas": {
        "B02": 1650, "B03": 1020, "B04": 410,  "B05": 310,  "B06": 230,
        "B07": 190,  "B08": 170,  "B8A": 170,  "B11": 130,  "B12": 95
    },
    "danau": {
        "B02": 1410, "B03": 1310, "B04": 1020, "B05": 880,  "B06": 820,
        "B07": 790,  "B08": 770,  "B8A": 760,  "B11": 720,  "B12": 450
    }
}

# Alias nama kelas
PROFIL_DN["perairan_terbuka"] = PROFIL_DN["laut_lepas"]
PROFIL_DN["lahan hijau"] = PROFIL_DN["lahan_hijau"]

ZONES = {
    "zona_sawah_bangunan": (112.165, -7.245, 112.215, -7.185, 10),
    "zona_lahan_hijau":    (112.035, -7.395, 112.075, -7.365, 10),
    "zona_danau":          (112.185, -7.405, 112.755, -7.025, 20),
    "zona_mangrove":       (111.995, -7.595, 112.895, -6.815, 20),
    "zona_laut":           (112.825, -7.675, 113.465, -7.245, 20),
}

def load_all_sample_polygons():
    shp_mapping = {
        "sawah": r"data\geojson\sawah\input.shp",
        "bangunan": r"data\geojson\bangunan\input.shp",
        "mangrove": r"data\geojson\mangrove\input.shp",
        "lahan_hijau": r"data\geojson\lahan hijau\input.shp",
        "laut_lepas": r"data\geojson\laut\input.shp",
        "danau": r"data\geojson\Danau\input.shp"
    }
    dfs = []
    for lbl, pth in shp_mapping.items():
        if os.path.exists(pth):
            gdf = gpd.read_file(pth)
            gdf["label"] = lbl
            dfs.append(gdf)
    if dfs:
        all_gdf = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True), crs=dfs[0].crs)
        return all_gdf.to_crs("EPSG:4326")
    return None

def create_geotiffs():
    samples_4326 = load_all_sample_polygons()
    if samples_4326 is None:
        print("Error: Shapefile tidak ditemukan di data/geojson!")
        return
        
    print(f"Total poligon sampel terload: {len(samples_4326)}")
    
    # 1. Buat GeoTIFF untuk masing-masing zona (EPSG:32749, 10 Band)
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)
    samples_32749 = samples_4326.to_crs("EPSG:32749")
    
    out_dirs = [r"materi\sentinel", r"sentinel"]
    for od in out_dirs:
        os.makedirs(od, exist_ok=True)
        
    for zone_name, (w_deg, s_deg, e_deg, n_deg, res_m) in ZONES.items():
        # Konversi bounds ke UTM 49S
        xmin_utm, ymin_utm = transformer.transform(w_deg, s_deg)
        xmax_utm, ymax_utm = transformer.transform(e_deg, n_deg)
        
        # Grid dimensi
        width = max(10, int((xmax_utm - xmin_utm) / res_m))
        height = max(10, int((ymax_utm - ymin_utm) / res_m))
        transform = from_bounds(xmin_utm, ymin_utm, xmax_utm, ymax_utm, width, height)
        
        # Filter sampel di zona ini
        box_utm = box(xmin_utm, ymin_utm, xmax_utm, ymax_utm)
        sub_samples = samples_32749[samples_32749.geometry.intersects(box_utm)]
        
        # Buat array 10 band
        # Inisialisasi latar belakang default (misal tanah kering/campuran)
        data = np.full((10, height, width), -32768, dtype=np.int16)
        
        # Default base pixel
        base_zone_type = "sawah"
        if "laut" in zone_name: base_zone_type = "laut_lepas"
        elif "danau" in zone_name: base_zone_type = "danau"
        elif "mangrove" in zone_name: base_zone_type = "mangrove"
        elif "hijau" in zone_name: base_zone_type = "lahan_hijau"
        
        for b_idx, b_name in enumerate(BANDS_10):
            data[b_idx, :, :] = PROFIL_DN[base_zone_type][b_name]
            
        # Rasterize setiap poligon sampel dengan nilai spektralnya
        for _, row in sub_samples.iterrows():
            lbl = row["label"]
            geom = row.geometry
            for b_idx, b_name in enumerate(BANDS_10):
                target_dn = PROFIL_DN.get(lbl, PROFIL_DN["sawah"])[b_name]
                # Variasi alami kecil +/- 2%
                noise = int(np.random.normal(0, target_dn * 0.02))
                dn_val = max(50, target_dn + noise)
                mask_arr = rasterize([(geom, dn_val)], out_shape=(height, width), transform=transform, fill=0, dtype=np.int16)
                data[b_idx, mask_arr > 0] = mask_arr[mask_arr > 0]
                
        # Simpan GeoTIFF zona ke materi/sentinel/ dan sentinel/
        for od in out_dirs:
            out_file = os.path.join(od, f"{zone_name}.tif")
            with rasterio.open(
                out_file, "w",
                driver="GTiff",
                height=height,
                width=width,
                count=10,
                dtype=rasterio.int16,
                crs="EPSG:32749",
                transform=transform,
                nodata=-32768
            ) as dst:
                dst.descriptions = tuple(BANDS_10)
                dst.write(data)
            print(f"-> Berhasil dibuat: {out_file} ({width}x{height}, 10 band)")
            
    # 2. Buat Sentinel2_multikelas.tif (EPSG:4326, 5 Band) untuk Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb
    minx, miny, maxx, maxy = samples_4326.total_bounds
    # Tambahkan margin
    minx -= 0.02; miny -= 0.02; maxx += 0.02; maxy += 0.02
    
    # Resolusi ~ 0.0005 derajat (~50 meter)
    res_deg = 0.0008
    w_px = int((maxx - minx) / res_deg)
    h_px = int((maxy - miny) / res_deg)
    tf_4326 = from_bounds(minx, miny, maxx, maxy, w_px, h_px)
    
    data_5b = np.full((5, h_px, w_px), 1200, dtype=np.float32)
    
    for _, row in samples_4326.iterrows():
        lbl = row["label"]
        geom = row.geometry
        for b_idx, b_name in enumerate(BANDS_5):
            val = float(PROFIL_DN.get(lbl, PROFIL_DN["sawah"])[b_name])
            mask_arr = rasterize([(geom, val)], out_shape=(h_px, w_px), transform=tf_4326, fill=0, dtype=np.float32)
            data_5b[b_idx, mask_arr > 0] = mask_arr[mask_arr > 0]
            
    multi_paths = [r"materi\Sentinel2_multikelas.tif", r"Sentinel2_multikelas.tif"]
    for mp in multi_paths:
        with rasterio.open(
            mp, "w",
            driver="GTiff",
            height=h_px,
            width=w_px,
            count=5,
            dtype=rasterio.float32,
            crs="EPSG:4326",
            transform=tf_4326,
            nodata=np.nan
        ) as dst:
            dst.descriptions = tuple(BANDS_5)
            dst.write(data_5b)
        print(f"-> Berhasil dibuat: {mp} ({w_px}x{h_px}, 5 band)")

if __name__ == "__main__":
    create_geotiffs()
