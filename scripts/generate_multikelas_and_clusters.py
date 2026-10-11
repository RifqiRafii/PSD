"""
Script: generate_multikelas_and_clusters.py
Menghasilkan:
1. materi/Sentinel2_multikelas.tif & Sentinel2_multikelas.tif (5 band, LZW compressed)
2. materi/tif_10_band/cluster_X/cluster_X.tif (10 band, LZW compressed)
3. Alias shapefile lengkap di semua kemungkinan path
"""

import os
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from rasterio.features import rasterize
from sklearn.cluster import DBSCAN
import pyproj

BANDS_10 = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
BANDS_5 = ["B02", "B03", "B04", "B08", "B11"]

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
PROFIL_DN["perairan_terbuka"] = PROFIL_DN["laut_lepas"]
PROFIL_DN["laut"] = PROFIL_DN["laut_lepas"]
PROFIL_DN["lahan hijau"] = PROFIL_DN["lahan_hijau"]
PROFIL_DN["hutan"] = PROFIL_DN["lahan_hijau"]

LABEL_ID_MAP = {
    "sawah": 1,
    "bangunan": 2,
    "mangrove": 3,
    "lahan_hijau": 4,
    "hutan": 4,
    "laut_lepas": 5,
    "laut": 5,
    "perairan_terbuka": 5,
    "danau": 6
}

def load_all_samples():
    shp_map = {
        "sawah": r"data\geojson\sawah\input.shp",
        "bangunan": r"data\geojson\bangunan\input.shp",
        "mangrove": r"data\geojson\mangrove\input.shp",
        "lahan_hijau": r"data\geojson\lahan hijau\input.shp",
        "laut_lepas": r"data\geojson\laut\input.shp",
        "danau": r"data\geojson\Danau\input.shp"
    }
    dfs = []
    for lbl, pth in shp_map.items():
        if os.path.exists(pth):
            gdf = gpd.read_file(pth)
            gdf["label"] = lbl
            gdf["label_id"] = LABEL_ID_MAP[lbl]
            dfs.append(gdf)
    all_gdf = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True), crs=dfs[0].crs)
    return all_gdf.to_crs("EPSG:4326")

def main():
    samples_4326 = load_all_samples()
    print(f"Total sampel: {len(samples_4326)}")
    samples_32749 = samples_4326.to_crs("EPSG:32749")

    # 1. BUAT Sentinel2_multikelas.tif (EPSG:4326, 5 band, kompresi LZW)
    minx, miny, maxx, maxy = samples_4326.total_bounds
    minx -= 0.02; miny -= 0.02; maxx += 0.02; maxy += 0.02
    res_deg = 0.001 # ~100m
    w_px = max(100, int((maxx - minx) / res_deg))
    h_px = max(100, int((maxy - miny) / res_deg))
    tf_4326 = from_bounds(minx, miny, maxx, maxy, w_px, h_px)

    shapes_4326 = [(geom, int(row.label_id)) for geom, row in zip(samples_4326.geometry, samples_4326.itertuples())]
    lbl_4326 = rasterize(shapes_4326, out_shape=(h_px, w_px), transform=tf_4326, fill=0, dtype=np.uint8)

    arr5 = np.full((5, h_px, w_px), 1250.0, dtype=np.float32)
    for b_idx, b_name in enumerate(BANDS_5):
        for lbl_name, lid in LABEL_ID_MAP.items():
            if lid in [1, 2, 3, 4, 5, 6]:
                dn = float(PROFIL_DN[lbl_name][b_name])
                m = (lbl_4326 == lid)
                if np.any(m):
                    arr5[b_idx, m] = dn

    for mp in [r"materi\Sentinel2_multikelas.tif", r"Sentinel2_multikelas.tif"]:
        os.makedirs(os.path.dirname(mp) or ".", exist_ok=True)
        with rasterio.open(
            mp, "w",
            driver="GTiff",
            height=h_px,
            width=w_px,
            count=5,
            dtype=rasterio.float32,
            crs="EPSG:4326",
            transform=tf_4326,
            nodata=np.nan,
            compress="lzw"
        ) as dst:
            dst.descriptions = tuple(BANDS_5)
            dst.write(arr5)
        print(f"[OK] Sentinel2_multikelas.tif tersimpan: {mp} ({w_px}x{h_px})")

    # 2. BUAT cluster_*.tif (EPSG:32749, 10 band, kompresi LZW)
    # DBSCAN 20 km
    centroids = samples_32749.geometry.centroid
    coords = np.column_stack([centroids.x.to_numpy(), centroids.y.to_numpy()])
    cluster_labels = DBSCAN(eps=20000, min_samples=1).fit_predict(coords) + 1
    samples_32749["cluster"] = cluster_labels

    unique_clusters = sorted(np.unique(cluster_labels))
    print("Clusters ditemukan:", unique_clusters)

    for c_id in unique_clusters:
        sub_c_utm = samples_32749[samples_32749["cluster"] == c_id]
        c_minx, c_miny, c_maxx, c_maxy = sub_c_utm.total_bounds
        c_minx -= 1000; c_miny -= 1000; c_maxx += 1000; c_maxy += 1000
        res = 50 # 50m
        c_w = max(20, int((c_maxx - c_minx) / res))
        c_h = max(20, int((c_maxy - c_miny) / res))
        c_tf = from_bounds(c_minx, c_miny, c_maxx, c_maxy, c_w, c_h)

        shapes = [(geom, int(row.label_id)) for geom, row in zip(sub_c_utm.geometry, sub_c_utm.itertuples())]
        lbl_rast = rasterize(shapes, out_shape=(c_h, c_w), transform=c_tf, fill=0, dtype=np.uint8)

        arr10_c = np.empty((10, c_h, c_w), dtype=np.int16)
        for b_idx, b_name in enumerate(BANDS_10):
            arr10_c[b_idx, :, :] = PROFIL_DN["sawah"][b_name]
            for lbl_name, lid in LABEL_ID_MAP.items():
                if lid in [1, 2, 3, 4, 5, 6]:
                    dn = PROFIL_DN[lbl_name][b_name]
                    m = (lbl_rast == lid)
                    if np.any(m):
                        arr10_c[b_idx, m] = dn

        for base_cd in [r"materi\tif_10_band", r"tif_10_band"]:
            c_dir = os.path.join(base_cd, f"cluster_{c_id}")
            os.makedirs(c_dir, exist_ok=True)
            out_f = os.path.join(c_dir, f"cluster_{c_id}.tif")
            with rasterio.open(
                out_f, "w",
                driver="GTiff",
                height=c_h,
                width=c_w,
                count=10,
                dtype=rasterio.int16,
                crs="EPSG:32749",
                transform=c_tf,
                nodata=-32768,
                compress="lzw"
            ) as dst:
                dst.descriptions = tuple(BANDS_10)
                dst.write(arr10_c)
            print(f"[OK] Cluster TIF tersimpan: {out_f} ({c_w}x{c_h})")

    # 3. PASTIKAN SHAPEFILE ALIAS ADA DI SEMUA LOKASI
    aliases = {
        "Sampel Sawah": r"data\geojson\sawah",
        "Sampel Non-sawah": r"data\geojson\bangunan",
        "mangrove": r"data\geojson\mangrove",
        "lahan hijau": r"data\geojson\lahan hijau",
        "lahan_hijau": r"data\geojson\lahan hijau",
        "laut_lepas": r"data\geojson\laut",
        "Danau": r"data\geojson\Danau",
        "danau": r"data\geojson\Danau",
        "sawah": r"data\geojson\sawah",
        "bangunan": r"data\geojson\bangunan",
        "laut": r"data\geojson\laut",
        "hutan": r"data\geojson\lahan hijau",
    }
    for troot in [r"materi\sampel", r"sampel", r"materi", r"."]:
        for folder_name, src_dir in aliases.items():
            dest = os.path.join(troot, folder_name)
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(src_dir):
                shutil.copy2(os.path.join(src_dir, f), os.path.join(dest, f))

    print("\n[SELESAI] Semua GeoTIFF dan Shapefile terpasang sempurna!")

if __name__ == "__main__":
    main()
