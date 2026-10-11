"""
Entrypoint untuk menjalankan aplikasi Streamlit LULC Jawa Timur.
Jalankan di terminal:
    streamlit run app.py
"""
import runpy

if __name__ == "__main__":
    runpy.run_path("streamlit_app.py", run_name="__main__")
