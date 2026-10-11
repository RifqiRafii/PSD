"""Streamlit - Sistem Informasi LULC Jawa Timur. Jalankan: streamlit run app.py"""
import json, os
import pandas as pd, streamlit as st, folium
from streamlit_folium import st_folium

ART = "web/artifacts"
st.set_page_config(page_title="LULC Jawa Timur", layout="wide")
content = json.load(open("web/content.json", encoding="utf-8"))
have = os.path.exists(f"{ART}/metrics.json")
M = json.load(open(f"{ART}/metrics.json")) if have else None
T = json.load(open(f"{ART}/tiles.json")) if have else []

st.title(content["judul"])
tab_map, tab_data, tab_band, tab_model, tab_proc = st.tabs(
    ["Peta hasil", "Data understanding", "Band & fitur", "Model & akurasi", "Proses"])

with tab_map:
    if not have:
        st.warning("Artefak belum ada. Jalankan 02_pipeline.py lebih dulu.")
    else:
        c1, c2 = st.columns([3, 1])
        with c2:
            zones = st.multiselect("Zona hasil klasifikasi", [t["name"] for t in T], [t["name"] for t in T])
            op = st.slider("Opasitas", 0.1, 1.0, 0.8)
            show_s = st.checkbox("Tampilkan poligon sampel", False)
            st.markdown("**Legenda**")
            for k, v in M["classes"].items():
                st.markdown(f"<span style='background:{v};padding:2px 10px;border-radius:3px'>&nbsp;</span> {k}", unsafe_allow_html=True)
            st.caption("Luas per kelas (ha)")
            sel = [t for t in T if t["name"] in zones]
            if sel: st.dataframe(pd.DataFrame({t["name"]: t["area_ha"] for t in sel}), use_container_width=True)
        with c1:
            m = folium.Map(location=[-7.3, 112.5], zoom_start=9, tiles=None)
            folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google Satellite",
                             name="Google Satellite", max_zoom=20).add_to(m)
            folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
            for t in sel:
                folium.raster_layers.ImageOverlay(f"{ART}/{t['name']}_kelas.png", bounds=t["bounds"],
                                                  opacity=op, name=t["name"]).add_to(m)
            if sel:
                m.fit_bounds([[min(t["bounds"][0][0] for t in sel), min(t["bounds"][0][1] for t in sel)],
                              [max(t["bounds"][1][0] for t in sel), max(t["bounds"][1][1] for t in sel)]])
            if show_s:
                folium.GeoJson(f"{ART}/samples.geojson", name="Sampel",
                    style_function=lambda f: dict(color=f["properties"]["warna"], weight=2, fillOpacity=0),
                    tooltip=folium.GeoJsonTooltip(["kelas"])).add_to(m)
            folium.LayerControl().add_to(m)
            st_folium(m, height=620, use_container_width=True, returned_objects=[])

with tab_data:
    st.subheader("Tujuan analisis land use & land cover")
    for x in content["tujuan"]: st.markdown(f"- {x}")
    st.subheader("Pengumpulan data")
    for x in content["koleksi"]: st.markdown(f"- {x}")
    st.subheader("Acuan klasifikasi lahan Indonesia")
    st.write(content["acuan"]["sumber"])
    st.table(pd.DataFrame(content["acuan"]["struktur"], columns=["Kelompok", "Contoh kelas"]))
    st.markdown("**Pemetaan ke 6 kelas penelitian**")
    st.table(pd.DataFrame(content["acuan"]["pemetaan"], columns=["Kelas penelitian", "Padanan pada acuan"]))
    if have:
        st.subheader("Jumlah kelas dan data training/testing")
        st.write(f"Jumlah kelas: **{len(M['classes'])}**. Split stratifikasi {int((1-M['test_size'])*100)}% training / {int(M['test_size']*100)}% testing; "
                 "satu sampel = rata-rata nilai band di dalam satu poligon.")
        df = pd.DataFrame(M["counts"]).T; df.loc["Total"] = df.sum()
        st.dataframe(df.astype(int), use_container_width=True)

with tab_band:
    st.subheader("Band Sentinel-2A (MSI)")
    st.dataframe(pd.DataFrame(content["band"]), use_container_width=True, hide_index=True)
    st.subheader("Fitur turunan (indeks) dan rumusnya")
    st.dataframe(pd.DataFrame(content["indeks"]), use_container_width=True, hide_index=True)
    for x in content["catatan"]: st.caption(x)
    if have:
        st.subheader("Kepentingan fitur (permutation importance, model terbaik)")
        st.bar_chart(pd.DataFrame(M["importance"], columns=["fitur", "penurunan akurasi"]).set_index("fitur"))

with tab_model:
    if have:
        df = pd.DataFrame(M["models"]).sort_values("test_accuracy", ascending=False)
        st.success(f"Model terbaik: {M['best_model']}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.subheader("Confusion matrix (data uji)")
        cm = pd.DataFrame(M["confusion"]["matrix"], index=M["confusion"]["labels"], columns=M["confusion"]["labels"])
        st.dataframe(cm, use_container_width=True)
        st.subheader("Precision / recall / F1 per kelas")
        rep = pd.DataFrame(M["report"]).T
        st.dataframe(rep, use_container_width=True)

with tab_proc:
    st.markdown("""
1. **Ambil citra**: komposit median Sentinel-2 L2A 10 band dari OpenEO Copernicus menjadi GeoTIFF per zona.
2. **Ekstraksi**: rata-rata nilai band di dalam tiap poligon sampel.
3. **Fitur**: 10 band ditambah 11 indeks (NDVI, EVI, SAVI, NDWI, MNDWI, NDBI, NDMI, NDRE, BSI, CMRI, MVI).
4. **Split**: 80% training dan 20% testing, stratifikasi per kelas.
5. **Model**: Random Forest, Extra Trees, HistGradientBoosting, SVM, k-NN, MLP, Logistic Regression, XGBoost, LightGBM; dibandingkan dengan CV 5-fold dan data uji.
6. **Klasifikasi**: model dengan akurasi uji tertinggi dipakai memprediksi seluruh GeoTIFF.
7. **Visualisasi**: hasil menjadi GeoTIFF kelas dan PNG overlay, ditampilkan di Leaflet/folium di atas Google Satellite.
""")
