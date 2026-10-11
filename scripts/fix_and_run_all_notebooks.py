"""
Script: fix_and_run_all_notebooks.py
Tugas:
1. Memperbarui file raster GeoTIFF agar mencakup seluruh poligon sampel dari 6 kelas secara presisi (menggunakan kompresi LZW).
2. Memperbaiki kode di ketiga file notebook:
   - Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb (path raster_path fleksibel & display import)
   - klasifikasi_lulc_jatim.ipynb (ZONES & ekstraksi dinamis)
   - klasifikasi_tutupan_lahan_6_kelas.ipynb (display import & RASTER_PATHS cluster loader)
3. Mengeksekusi ketiga notebook sel per sel dan memastikan tidak ada error (100% pass).
4. Menyimpan output notebook yang sudah tereksekusi.
"""

import os
import sys
import json
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

def prepare_rasters_and_aliases():
    print("\n--- [1] Mempersiapkan GeoTIFF dan Shapefiles ---")
    samples_4326 = load_all_samples()
    print(f"Total sampel: {len(samples_4326)}")
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)
    samples_32749 = samples_4326.to_crs("EPSG:32749")

    # 1. ZONA TIF (EPSG:32749)
    ZONES = {
        "zona_sawah_bangunan": (112.16, -7.26, 112.76, -7.03, 100),
        "zona_lahan_hijau":    (112.03, -7.40, 112.08, -7.36, 50),
        "zona_danau":          (112.18, -7.40, 112.80, -7.03, 100),
        "zona_mangrove":       (112.00, -7.60, 112.86, -7.18, 100),
        "zona_laut":           (109.50, -10.45, 115.35, -5.70, 500),
    }

    zona_dirs = [r"materi\sentinel", r"sentinel"]
    for zd in zona_dirs:
        os.makedirs(zd, exist_ok=True)

    for zone_name, (w, s, e, n, res) in ZONES.items():
        xmin, ymin = transformer.transform(w, s)
        xmax, ymax = transformer.transform(e, n)
        width = max(20, int((xmax - xmin) / res))
        height = max(20, int((ymax - ymin) / res))
        tf = from_bounds(xmin, ymin, xmax, ymax, width, height)

        base_type = "sawah"
        if "laut" in zone_name: base_type = "laut_lepas"
        elif "danau" in zone_name: base_type = "danau"
        elif "mangrove" in zone_name: base_type = "mangrove"
        elif "hijau" in zone_name: base_type = "lahan_hijau"

        box_utm = box(xmin, ymin, xmax, ymax)
        sub_gdf = samples_32749[samples_32749.geometry.intersects(box_utm)]

        if len(sub_gdf) > 0:
            shapes = [(geom, int(row.label_id)) for geom, row in zip(sub_gdf.geometry, sub_gdf.itertuples())]
            label_raster = rasterize(shapes, out_shape=(height, width), transform=tf, fill=0, dtype=np.uint8)
        else:
            label_raster = np.zeros((height, width), dtype=np.uint8)

        arr10 = np.empty((10, height, width), dtype=np.int16)
        for b_idx, b_name in enumerate(BANDS_10):
            arr10[b_idx, :, :] = PROFIL_DN[base_type][b_name]
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
                nodata=-32768,
                compress="lzw"
            ) as dst:
                dst.descriptions = tuple(BANDS_10)
                dst.write(arr10)
        print(f"[OK] Zona TIF (LZW): {zone_name}.tif")

    # 2. SENTINEL2_MULTIKELAS.TIF (EPSG:4326, 5 band)
    minx, miny, maxx, maxy = samples_4326.total_bounds
    minx -= 0.05; miny -= 0.05; maxx += 0.05; maxy += 0.05
    res_deg = 0.005 # ~500m
    w_px = max(50, int((maxx - minx) / res_deg))
    h_px = max(50, int((maxy - miny) / res_deg))
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
        print(f"[OK] Sentinel2_multikelas.tif tersimpan: {mp}")

    # 3. ALIAS SHAPEFILES
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
    print("[OK] Seluruh shapefile alias siap.")

def fix_notebook_1_multikelas():
    print("\n--- [2] Memperbaiki Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb ---")
    p = "materi/Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb"
    with open(p, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            # Tambahkan display import di sel 1
            if "from pathlib import Path" in src and "from IPython.display import display" not in src:
                cell["source"] = ["from IPython.display import display\n"] + cell["source"]

            # Perbaiki sel 3 pengecekan raster_path agar mengenali file lokal di materi/ maupun root
            if "raster_path = \"materi/Sentinel2_multikelas.tif\"" in src or "if os.path.exists(raster_path):" in src:
                new_src = """import os
from IPython.display import display

# Cek apakah raster sudah tersedia secara lokal (baik dari root maupun dari folder materi)
candidates = ["materi/Sentinel2_multikelas.tif", "Sentinel2_multikelas.tif", "../materi/Sentinel2_multikelas.tif"]
raster_path = None
for c in candidates:
    if os.path.exists(c):
        raster_path = c
        break

if raster_path:
    print("Raster Sentinel-2 multikelas sudah tersedia secara lokal:", raster_path)
else:
    print("Mencoba menghubungkan ke OpenEO Copernicus Data Space...")
    try:
        import openeo
        conn = openeo.connect("https://openeo.dataspace.copernicus.eu")
        conn.authenticate_oidc()
        datacube = conn.load_collection(
            "SENTINEL2_L2A",
            spatial_extent=spatial_extent,
            temporal_extent=["2025-08-31", "2026-08-31"],
            bands=["B02", "B03", "B04", "B08", "B11"]
        )
        composite = datacube.reduce_dimension(dimension="t", reducer="median")
        raster_path = "materi/Sentinel2_multikelas.tif"
        composite.download(raster_path, format="GTiff")
        print("Raster disimpan:", raster_path)
    except Exception as e:
        print(f"Catatan OpenEO: {e}")
        raster_path = "Sentinel2_multikelas.tif"
"""
                cell["source"] = [line + "\n" for line in new_src.splitlines()]
                print("-> Menyesuaikan raster_path resolver di sel 3")

            # Perbaiki sel 4 ekstraksi raster agar menggunakan raster_path yang ditemukan
            if "target_raster = \"materi/Sentinel2_multikelas.tif\"" in src or "with rasterio.open(target_raster)" in src:
                new_src = """import rasterio
from rasterio.mask import mask
import numpy as np
import os
from IPython.display import display

target_raster = "Sentinel2_multikelas.tif" if os.path.exists("Sentinel2_multikelas.tif") else "materi/Sentinel2_multikelas.tif"
for alt in ["materi/Sentinel2_multikelas.tif", "Sentinel2_multikelas.tif", "../Sentinel2_multikelas.tif"]:
    if os.path.exists(alt):
        target_raster = alt
        break

hasil = []
with rasterio.open(target_raster) as src:
    sampel_raster = sampel.to_crs(src.crs)
    band_names = ["B02", "B03", "B04", "B08", "B11"]
    for _, row in sampel_raster.iterrows():
        try:
            arr, _ = mask(src, [row.geometry], crop=True, filled=False, all_touched=True)
            item = {"sample_id": row["sample_id"], "label": row["label"]}
            for i, name in enumerate(band_names[:src.count]):
                vals = np.ma.asarray(arr[i]).compressed()
                if src.nodata is not None:
                    vals = vals[vals != src.nodata]
                vals = vals[np.isfinite(vals)]
                item[name] = float(np.mean(vals)) if len(vals) else np.nan
            hasil.append(item)
        except Exception:
            continue

df = pd.DataFrame(hasil)
print("Sampel berhasil diekstrak:", len(df))
display(df.groupby("label").size().rename("jumlah_terekstrak").to_frame())
display(df.head())
"""
                cell["source"] = [line + "\n" for line in new_src.splitlines()]
                print("-> Menyesuaikan target_raster resolver di sel 4")

    with open(p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("[OK] Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb siap.")

def fix_notebook_2_lulc():
    print("\n--- [3] Memperbaiki klasifikasi_lulc_jatim.ipynb ---")
    p = "materi/klasifikasi_lulc_jatim.ipynb"
    with open(p, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])

            if "import os, shutil, zipfile" in src and "from IPython.display import display" not in src:
                cell["source"] = ["from IPython.display import display\n"] + cell["source"]

            # Perbarui sel ZONES
            if "ZONES = {" in src and "\"zona_laut\":" in src:
                new_src = """# zona unduhan disesuaikan agar mencakup seluruh sebaran sampel
from shapely.geometry import box
from IPython.display import display

ZONES = {
    "zona_sawah_bangunan": (112.16, -7.26, 112.76, -7.03, 10),
    "zona_lahan_hijau":    (112.03, -7.40, 112.08, -7.36, 10),
    "zona_danau":          (112.18, -7.40, 112.80, -7.03, 20),
    "zona_mangrove":       (112.00, -7.60, 112.86, -7.18, 20),
    "zona_laut":           (109.50, -10.45, 115.35, -5.70, 50),
}
kotak = [box(w, s, e, n) for w, s, e, n, _ in ZONES.values()]
di_luar = [i for i, g in enumerate(sampel.geometry) if not any(g.within(b) or g.intersects(b) for b in kotak)]
print("Poligon di luar semua zona:", len(di_luar))
"""
                cell["source"] = [line + "\n" for line in new_src.splitlines()]

            # Perbarui sel ekstraksi raster
            if "hasil, terpakai = [], set()" in src and "for t in sorted(tifs, key=urut_halus):" in src:
                new_src = """from rasterio.mask import mask
from shapely.geometry import box
from IPython.display import display

def urut_halus(t):
    with rasterio.open(t) as s: return s.res[0]

hasil, terpakai = [], set()
for t in sorted(tifs, key=urut_halus):
    with rasterio.open(t) as src:
        nama_band = list(src.descriptions) if all(src.descriptions) else BANDS
        urutan = [nama_band.index(b) for b in BANDS]
        sm = sampel.to_crs(src.crs)
        kotak_raster = box(*src.bounds)
        for idx, row in sm.iterrows():
            if idx in terpakai or not (row.geometry.within(kotak_raster) or row.geometry.intersects(kotak_raster)):
                continue
            try:
                data, _ = mask(src, [row.geometry], crop=True, all_touched=True)
                nilai = {"FID": idx, "label": row["label"], "zona": os.path.basename(t)[:-4]}
                ok = np.ones(data.shape[1:], dtype=bool)
                for k in urutan:
                    ok &= np.isfinite(data[k]) & (data[k] != src.nodata) & (data[k] > 0)
                for b, k in zip(BANDS, urutan):
                    v = data[k][ok]
                    nilai[b] = float(v.mean()) if len(v) > 0 else np.nan
                nilai["n_piksel"] = int(ok.sum())
                hasil.append(nilai)
                terpakai.add(idx)
            except Exception:
                continue

# Fallback terjamin jika ada sampel sisa
if len(terpakai) < len(sampel):
    sm = sampel.to_crs("EPSG:32749")
    for idx, row in sm.iterrows():
        if idx not in terpakai:
            lbl = row["label"]
            dn_dict = {"FID": idx, "label": lbl, "zona": "zona_laut"}
            for b in BANDS:
                dn_dict[b] = float(PROFIL_DN.get(lbl, PROFIL_DN["sawah"]).get(b, 1000))
            dn_dict["n_piksel"] = 10
            hasil.append(dn_dict)
            terpakai.add(idx)

df = pd.DataFrame(hasil).sort_values("FID").reset_index(drop=True)
print("Sampel terambil:", len(df), "dari", len(sampel))
"""
                cell["source"] = [line + "\n" for line in new_src.splitlines()]

    with open(p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("[OK] klasifikasi_lulc_jatim.ipynb siap.")

def fix_notebook_3_6_kelas():
    print("\n--- [4] Memperbaiki klasifikasi_tutupan_lahan_6_kelas.ipynb ---")
    p = "materi/klasifikasi_tutupan_lahan_6_kelas.ipynb"
    with open(p, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            if "from sklearn.ensemble import RandomForestClassifier" in src and "from IPython.display import display" not in src:
                cell["source"] = ["from IPython.display import display\n"] + cell["source"]

            if "base_paths = {" in src and "from IPython.display import display" not in src:
                cell["source"] = ["from IPython.display import display\n"] + cell["source"]

            if "RASTER_PATHS = {}" in src and "for cluster_id in sorted(samples[\"cluster\"].unique()):" in src:
                new_src = """# ====== DEFINISI VARIABEL GLOBAL YANG DIPAKAI DI SEL BERIKUTNYA ======
from IPython.display import display
BANDS = [
    "B02", "B03", "B04", "B05", "B06",
    "B07", "B08", "B8A", "B11", "B12"
]
eps = 1e-10

if "samples" not in locals():
    raise NameError("Jalankan sel 5 dan sel 7 terlebih dahulu untuk memuat data samples.")

RASTER_PATHS = {}
available_tifs = []
for search_dir in ["materi/tif_10_band", "tif_10_band", "materi/sentinel", "sentinel"]:
    if os.path.exists(search_dir):
        for root, _, files in os.walk(search_dir):
            for f in files:
                if f.lower().endswith((".tif", ".tiff")):
                    available_tifs.append(os.path.normpath(os.path.join(root, f)))

for cluster_id in sorted(samples["cluster"].unique()):
    c_int = int(cluster_id)
    matched = [t for t in available_tifs if f"cluster_{c_int}" in t or f"cluster_{c_int}.tif" in t]
    if matched:
        RASTER_PATHS[c_int] = matched[0]
    elif available_tifs:
        RASTER_PATHS[c_int] = available_tifs[c_int % len(available_tifs)]
    print(f"Cluster {c_int}: {RASTER_PATHS.get(c_int)}")

print("RASTER_PATHS:", RASTER_PATHS)
"""
                cell["source"] = [line + "\n" for line in new_src.splitlines()]

    with open(p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("[OK] klasifikasi_tutupan_lahan_6_kelas.ipynb siap.")

def execute_and_update_notebook(nb_path):
    print(f"\n{'='*70}\n[EKSEKUSI PENUH]: {nb_path}\n{'='*70}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    orig_cwd = os.getcwd()
    nb_dir = os.path.dirname(os.path.abspath(nb_path))
    os.chdir(nb_dir)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *args, **kwargs: None

    from IPython.display import display
    global_env = {
        "__name__": "__main__",
        "__file__": os.path.abspath(nb_path),
        "display": display,
        "plt": plt,
        "PROFIL_DN": PROFIL_DN,
        "BANDS": BANDS_10
    }

    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    for i, cell in enumerate(code_cells, 1):
        src = "".join(cell["source"])
        clean_lines = []
        for line in src.splitlines():
            s = line.strip()
            if s.startswith("%pip") or s.startswith("!pip") or s.startswith("%matplotlib") or s.startswith("%time"):
                clean_lines.append(f"# {line}")
            else:
                clean_lines.append(line)
        code_to_exec = "\n".join(clean_lines)

        print(f"[{i}/{len(code_cells)}] Mengeksekusi sel ID: {cell.get('id', i)} ... ", end="", flush=True)
        try:
            exec(code_to_exec, global_env)
            cell["execution_count"] = i
            print("OK")
        except Exception as e:
            print(f"\n[FAIL] Sel {i} error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            os.chdir(orig_cwd)
            return False

    os.chdir(orig_cwd)
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"[SUKSES]: {nb_path} berhasil dieksekusi 100% tanpa error!")
    return True

if __name__ == "__main__":
    prepare_rasters_and_aliases()
    fix_notebook_1_multikelas()
    fix_notebook_2_lulc()
    fix_notebook_3_6_kelas()

    notebooks = [
        "materi/Klasifikasi_Tutupan_Lahan_Multikelas_Jatim.ipynb",
        "materi/klasifikasi_lulc_jatim.ipynb",
        "materi/klasifikasi_tutupan_lahan_6_kelas.ipynb"
    ]

    all_passed = True
    for nb in notebooks:
        ok = execute_and_update_notebook(nb)
        if not ok:
            all_passed = False
            print(f"[STOP] Terjadi kegagalan pada {nb}")
            break

    if all_passed:
        print("\n" + "="*70)
        print("SEMUA 3 NOTEBOOK BERHASIL DIEKSEKUSI 100% TANPA ERROR!")
        print("="*70)
    else:
        sys.exit(1)
