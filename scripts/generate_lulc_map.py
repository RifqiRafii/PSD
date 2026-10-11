"""
Script: generate_lulc_map.py
Deskripsi: Menghasilkan peta interaktif Folium / Leaflet dengan WMS Google Maps Satelit & Hybrid,
dilengkapi visualisasi sebaran 6 kelas tutupan lahan Sentinel-2A di Jawa Timur,
layer control, popup spektral komprehensif, legend interaktif, serta zona kebijakan tata ruang.
"""

import os
import json
import pandas as pd
import folium
from folium import plugins
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl

def create_lulc_interactive_map():
    csv_path = r"data\lulc_jatim\sentinel2_lulc_jatim.csv"
    out_html = r"data\lulc_jatim\peta_lulc_jawa_timur.html"
    materi_html = r"materi\peta_lulc_jawa_timur.html"
    
    df = pd.read_csv(csv_path)
    
    # Titik tengah Jawa Timur (antara Mojokerto - Pasuruan - Malang)
    center_lat, center_lon = -7.65, 112.75
    
    # Inisialisasi Folium Map tanpa default tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles=None,
        control_scale=True
    )
    
    # 1. Base Layer WMS / Tile Satelit Google Maps & Pilihan Lainnya
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='🛰️ Google Maps Satellite',
        max_zoom=20,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='🗺️ Google Maps Hybrid (Satelit + Label)',
        max_zoom=20,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Roadmap',
        name='🛣️ Google Maps Terrain / Road',
        max_zoom=20,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='🌐 OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='🌙 CartoDB Dark Matter',
        overlay=False,
        control=True
    ).add_to(m)

    # Definisi Warna & Metadata Kelas
    class_meta = {
        0: {
            "name": "Sawah",
            "color": "#eab308",
            "border": "#ca8a04",
            "icon": "leaf",
            "policy": "Zona LP2B / Lahan Sawah Dilindungi (LSD) - Larangan Alih Fungsi Lahan (UU No. 41/2009)"
        },
        1: {
            "name": "Bangunan",
            "color": "#ef4444",
            "border": "#b91c1c",
            "icon": "building",
            "policy": "Zona Budidaya Terbangun / Perkotaan & Industri - Pengendalian KDB & Penyediaan RTH 30% (Permen ATR/BPN 14/2021)"
        },
        2: {
            "name": "Mangrove",
            "color": "#059669",
            "border": "#047857",
            "icon": "tree",
            "policy": "Kawasan Lindung Sempadan Pantai & Ekosistem Pesisir - Restorasi & Konservasi Sabuk Hijau (Perpres 73/2012)"
        },
        3: {
            "name": "Lahan Hijau",
            "color": "#15803d",
            "border": "#166534",
            "icon": "tint",
            "policy": "Kawasan Lindung Resapan Air & Hutan Konservasi / TNBTS / Tahura - Penyangga Tata Air Regional"
        },
        4: {
            "name": "Perairan Terbuka (Laut)",
            "color": "#1d4ed8",
            "border": "#1e40af",
            "icon": "tint",
            "policy": "Kawasan Alur Pelayaran & Ruang Laut Pesisir - Zonasi RZWP-3-K Jawa Timur"
        },
        5: {
            "name": "Danau (Ranu-ranu)",
            "color": "#06b6d4",
            "border": "#0e7490",
            "icon": "water",
            "policy": "Kawasan Sempadan Danau Alami (Ranu) - Perlindungan Minimum 50m dari Titik Pasang Tertinggi (Permen PUPR 28/2015)"
        }
    }
    
    # Layer Group untuk masing-masing kelas
    layer_groups = {}
    for code, info in class_meta.items():
        layer_groups[code] = folium.FeatureGroup(name=f"📍 {info['name']} ({info['color']})", show=True)

    # Tambahkan titik-titik sampel dengan CircleMarker estetik
    for _, row in df.iterrows():
        code = int(row["class_code"])
        info = class_meta[code]
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 280px; font-size: 12px; line-height: 1.4;">
            <div style="background-color: {info['color']}; color: white; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; margin-bottom: 8px;">
                {info['name'].upper()} - {row['sample_id']}
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 8px;">
                <tr><td style="color: #666;"><b>Lokasi:</b></td><td>{row['location_name']}</td></tr>
                <tr><td style="color: #666;"><b>Kab/Kota:</b></td><td>{row['kabupaten_kota']}</td></tr>
                <tr><td style="color: #666;"><b>Koordinat:</b></td><td>{row['latitude']:.5f}, {row['longitude']:.5f}</td></tr>
            </table>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; margin-bottom: 8px;">
                <b>Indeks Spektral Sentinel-2A:</b><br>
                • <b>NDVI:</b> {row['NDVI']:.4f} &nbsp;|&nbsp; • <b>NDWI:</b> {row['NDWI']:.4f}<br>
                • <b>MNDWI:</b> {row['MNDWI']:.4f} &nbsp;|&nbsp; • <b>NDBI:</b> {row['NDBI']:.4f}<br>
                • <b>BSI:</b> {row['BSI']:.4f} &nbsp;|&nbsp; • <b>CMRI:</b> {row['CMRI']:.4f}
            </div>
            <div style="border-left: 3px solid {info['color']}; padding-left: 6px; font-size: 11px; color: #334155;">
                <b>Arahan Kebijakan:</b><br>{info['policy']}
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            color=info["border"],
            weight=1.5,
            fill=True,
            fill_color=info["color"],
            fill_opacity=0.85,
            tooltip=f"{info['name']} - {row['location_name']}",
            popup=folium.Popup(popup_html, max_width=320)
        ).add_to(layer_groups[code])

    for code in class_meta.keys():
        layer_groups[code].add_to(m)

    # Tambahkan Poligon Contoh Kawasan Konservasi & Kebijakan Khusus
    # 1. Ranu Grati Pasuruan (Sempadan Danau)
    folium.Polygon(
        locations=[
            [-7.732, 113.007], [-7.732, 113.020],
            [-7.744, 113.020], [-7.744, 113.007]
        ],
        color="#06b6d4",
        weight=2,
        fill=True,
        fill_color="#06b6d4",
        fill_opacity=0.2,
        tooltip="Sempadan Perlindungan Hidrologis Ranu Grati Pasuruan",
        popup="<b>Kawasan Konservasi Sumber Air Ranu Grati</b><br>Danau maar vulkanik dengan zona sempadan terlindungi 50 meter."
    ).add_to(m)

    # 2. Mangrove Wonorejo Surabaya (Zona Lindung Sabuk Hijau Pesisir)
    folium.Polygon(
        locations=[
            [-7.300, 112.818], [-7.300, 112.835],
            [-7.315, 112.835], [-7.315, 112.818]
        ],
        color="#059669",
        weight=2,
        fill=True,
        fill_color="#059669",
        fill_opacity=0.2,
        tooltip="Kawasan Konservasi Hutan Mangrove Wonorejo Surabaya",
        popup="<b>Ekowisata & Sabuk Hijau Mangrove Wonorejo</b><br>Penahan abrasi pesisir Selat Madura dan habitat burung migran."
    ).add_to(m)

    # 3. Ranu Kumbolo - TNBTS (Kawasan Taman Nasional Semeru)
    folium.Polygon(
        locations=[
            [-8.050, 112.915], [-8.050, 112.930],
            [-8.062, 112.930], [-8.062, 112.915]
        ],
        color="#15803d",
        weight=2,
        fill=True,
        fill_color="#15803d",
        fill_opacity=0.2,
        tooltip="Zona Inti & Danau Ranu Kumbolo - TNBTS",
        popup="<b>Zona Inti Ekosistem Danau Dataran Tinggi Ranu Kumbolo</b><br>Kawasan konservasi ketat Taman Nasional Bromo Tengger Semeru."
    ).add_to(m)

    # Plugins Tambahan
    Fullscreen(position='topleft').add_to(m)
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    # Tambahkan Custom Legend Box di Peta Leaflet
    legend_html = """
    {% macro html(this, kwargs) %}
    <div id="legend-box" style="
        position: fixed; 
        bottom: 25px; 
        right: 25px; 
        width: 250px; 
        background-color: rgba(255, 255, 255, 0.95); 
        box-shadow: 0 4px 15px rgba(0,0,0,0.25); 
        border-radius: 8px; 
        padding: 12px 14px; 
        font-family: Arial, sans-serif; 
        font-size: 12px; 
        z-index: 9999;
        border: 1px solid #cbd5e1;
    ">
        <h4 style="margin: 0 0 8px 0; font-size: 13px; font-weight: bold; color: #1e293b; border-bottom: 2px solid #3b82f6; padding-bottom: 4px;">
            Legenda Tutupan Lahan Jawa Timur
        </h4>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="background: #eab308; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #ca8a04;"></span>
            <span style="color: #334155; font-weight: 500;">Sawah (Padi / LP2B)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="background: #ef4444; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #b91c1c;"></span>
            <span style="color: #334155; font-weight: 500;">Bangunan (Urban / Industri)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="background: #059669; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #047857;"></span>
            <span style="color: #334155; font-weight: 500;">Mangrove (Hutan Bakau)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="background: #15803d; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #166534;"></span>
            <span style="color: #334155; font-weight: 500;">Lahan Hijau (Hutan Rimba)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="background: #1d4ed8; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #1e40af;"></span>
            <span style="color: #334155; font-weight: 500;">Perairan Terbuka (Laut)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <span style="background: #06b6d4; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 8px; border: 1px solid #0e7490;"></span>
            <span style="color: #334155; font-weight: 500;">Danau (Ranu-ranu Jatim)</span>
        </div>
        <div style="font-size: 10px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 5px;">
            Satelit: Sentinel-2A MSI (ESA) | Basemap: Google Satelit WMS
        </div>
    </div>
    {% endmacro %}
    """
    macro = folium.MacroElement()
    macro._template = folium.plugins.marker_cluster.Template(legend_html)
    m.get_root().add_child(macro)

    # Simpan ke data dan materi
    m.save(out_html)
    m.save(materi_html)
    print(f"Peta interaktif Leaflet Google Satelit berhasil dibuat:")
    print(f"- {out_html}")
    print(f"- {materi_html}")

if __name__ == "__main__":
    create_lulc_interactive_map()
