import os
import json
import geopandas as gpd
import pandas as pd

KELAS = ['sawah', 'bangunan', 'mangrove', 'lahan_hijau', 'laut_lepas', 'danau']
NAMA = {'sawah': 'Sawah', 'bangunan': 'Bangunan', 'mangrove': 'Mangrove', 'lahan_hijau': 'Lahan hijau', 'laut_lepas': 'Laut lepas', 'danau': 'Danau'}
WARNA = {'sawah': '#e6c229', 'bangunan': '#d1495b', 'mangrove': '#2a9d8f', 'lahan_hijau': '#6a994e', 'laut_lepas': '#1d3557', 'danau': '#4cc9f0'}
KODE = {k: i + 1 for i, k in enumerate(KELAS)}

MATERI_DIR = 'materi' if os.path.exists('materi') else '.'
bagian = []
for k in KELAS:
    path_k = f'{MATERI_DIR}/sampel/{k}/input.shp'
    if not os.path.exists(path_k):
        path_k = f'sampel/{k}/input.shp'
    g = gpd.read_file(path_k).to_crs('EPSG:4326')
    g['label'] = k
    bagian.append(g[['label', 'geometry']])
sampel = gpd.GeoDataFrame(pd.concat(bagian, ignore_index=True), crs='EPSG:4326')

out_text = f"Jumlah sampel: {len(sampel)}\nJumlah kelas : {sampel['label'].nunique()}\n{sampel['label'].value_counts().to_string()}\n"
print(out_text)

p = 'materi/klasifikasi_lulc_jatim.ipynb'
with open(p, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for c in nb['cells']:
    if c.get('id') == 'c08':
        c['outputs'] = [{
            'name': 'stdout',
            'output_type': 'stream',
            'text': [out_text]
        }]
        c['execution_count'] = 3

with open(p, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Updated cell c08 outputs successfully!')
