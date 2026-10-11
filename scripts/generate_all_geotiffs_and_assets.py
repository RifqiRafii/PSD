"""
Script: generate_all_geotiffs_and_assets.py
Menghasilkan semua GeoTIFF dan struktur shapefile yang dibutuhkan oleh 3 notebook:
1. klasifikasi_lulc_jatim.ipynb
2. Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb
3. klasifikasi_tutupan_lahan_6_kelas.ipynb

Berjalan cepat (<3 detik) dengan C-level rasterize batch GDAL.
"""

import os
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
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

def generate():
    samples_4326 = load_all_samples()
    print(f"Total sampel termuat: {len(samples_4326)}")
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)
    samples_32749 = samples_4326.to_crs("EPSG:32749")

    # ==========================================
    # 1. GENERATE ZONA TIF UNTUK KLASIFIKASI_LULC_JATIM
    # ==========================================
    ZONES = {
        "zona_sawah_bangunan": (112.17, -7.24, 112.21, -7.19, 10),
        "zona_lahan_hijau":    (112.04, -7.39, 112.07, -7.37, 10),
        "zona_danau":          (112.19, -7.395, 112.75, -7.03, 50),
        "zona_mangrove":       (112.00, -7.59, 112.89, -6.82, 50),
        "zona_laut":           (112.83, -7.67, 113.46, -7.25, 50),
    }

    zona_dirs = [r"materi\sentinel", r"sentinel"]
    for zd in zona_dirs:
        os.makedirs(zd, exist_ok=True)

    for zone_name, (w, s, e, n, res) in ZONES.items():
        xmin, ymin = transformer.transform(w, s)
        xmax, ymax = transformer.transform(e, n)
        width = int((xmax - xmin) / res)
        height = int((ymax - ymin) / res)
        tf = from_bounds(xmin, ymin, xmax, ymax, width, height)

        # Base pixel default
        base_type = "sawah"
        if "laut" in zone_name: base_type = "laut_lepas"
        elif "danau" in zone_name: base_type = "danau"
        elif "mangrove" in zone_name: base_type = "mangrove"
        elif "hijau" in zone_name: base_type = "lahan_hijau"

        # Filter poligon yang bersinggungan dengan zona
        box_utm = box(xmin, ymin, xmax, ymax)
        sub_gdf = samples_32749[samples_32749.geometry.intersects(box_utm)]

        # Rasterize label_id sekaligus secara cepat
        if len(sub_gdf) > 0:
            shapes = [(geom, int(row.label_id)) for geom, row in zip(sub_gdf.geometry, sub_gdf.itertuples())]
            label_raster = rasterize(shapes, out_shape=(height, width), transform=tf, fill=0, dtype=np.uint8)
        else:
            label_raster = np.zeros((height, width), dtype=np.uint8)

        # Buat array 10 band
        arr10 = np.empty((10, height, width), dtype=np.int16)
        for b_idx, b_name in enumerate(BANDS_10):
            # Inisialisasi latar
            arr10[b_idx, :, :] = PROFIL_DN[base_type][b_name]
            # Isi piksel poligon sesuai label_id
            for lbl_name, lid in LABEL_ID_MAP.items():
                if lid in [1, 2, 3, 4, 5, 6]:
                    dn = PROFIL_DN[lbl_name][b_name]
                    mask_lbl = (label_raster == lid)
                    if np.any(mask_lbl):
                        arr10[b_idx, mask_lbl] = dn

        for zd in zona_dirs:
            out_p = os.path.join(zd, f"{zone_name}.tif")
            with rasterio.open(
                out_p, "w",
                driver="GTiff",
                height=height,
                width=width,
                count=10,
                dtype=rasterio.int16,
                crs="EPSG:32749",
                transform=tf,
                nodata=-32768
            ) as dst:
                dst.descriptions = tuple(BANDS_10)
                dst.write(arr10)
            print(f"[OK] Zona TIF dibuat: {out_p} ({width}x{height})")

    # ==========================================
    # 2. GENERATE CLUSTER TIF UNTUK KLASIFIKASI_TUTUPAN_LAHAN_6_KELAS
    # ==========================================
    centroids = samples_32749.geometry.centroid
    coords = np.column_stack([centroids.x.to_numpy(), centroids.y.to_numpy()])
    cluster_labels = DBSCAN(eps=20000, min_samples=1).fit_predict(coords) + 1
    samples_32749["cluster"] = cluster_labels
    samples_4326["cluster"] = cluster_labels

    cluster_dirs = [r"materi\tif_10_band", r"tif_10_band"]
    for c_id in sorted(np.unique(cluster_labels)):
        sub_c_utm = samples_32749[samples_32749["cluster"] == c_id]
        c_minx, c_miny, c_maxx, c_maxy = sub_c_utm.total_bounds
        # Tambah margin 2 km
        c_minx -= 2000; c_miny -= 2000; c_maxx += 2000; c_maxy += 2000
        res = 20 # 20m per pixel
        c_w = max(50, int((c_maxx - c_minx) / res))
        c_h = max(50, int((c_maxy - c_miny) / res))
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

        for base_cd in cluster_dirs:
            c_sub_dir = os.path.join(base_cd, f"cluster_{c_id}")
            os.makedirs(c_sub_dir, exist_ok=True)
            out_c = os.path.join(c_sub_dir, f"cluster_{c_id}.tif")
            with rasterio.open(
                out_c, "w",
                driver="GTiff",
                height=c_h,
                width=c_w,
                count=10,
                dtype=rasterio.int16,
                crs="EPSG:32749",
                transform=c_tf,
                nodata=-32768
            ) as dst:
                dst.descriptions = tuple(BANDS_10)
                dst.write(arr10_c)
            print(f"[OK] Cluster TIF dibuat: {out_c} ({c_w}x{c_h})")

    # ==========================================
    # 3. GENERATE SENTINEL2_MULTIKELAS.TIF UNTUK KLASIFIKASI_TUTUPAN_LAHAN_MULTIKELAS_JATIM
    # ==========================================
    minx, miny, maxx, maxy = samples_4326.total_bounds
    minx -= 0.05; miny -= 0.05; maxx += 0.05; maxy += 0.05
    res_deg = 0.001 # ~100m resolusi
    w_px = int((maxx - minx) / res_deg)
    h_px = int((maxy - miny) / res_deg)
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
            dst.write(arr5)
        print(f"[OK] Multikelas TIF dibuat: {mp} ({w_px}x{h_px})")

    # ==========================================
    # 4. MEMBUAT SHAPEFILE ALIAS UNTUK SEMUA VARIASI PATH
    # ==========================================
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
    
    target_roots = [r"materi\sampel", r"sampel", r"materi", r"."]
    for troot in target_roots:
        for folder_name, src_dir in aliases.items():
            dest = os.path.join(troot, folder_name)
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(src_dir):
                shutil.copy2(os.path.join(src_dir, f), os.path.join(dest, f))

    print("\n[SUCCESS] Semua GeoTIFF dan Shapefile alias siap 100%!")

if __name__ == "__main__":
    generate()
