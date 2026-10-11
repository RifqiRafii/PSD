@echo off
title Streamlit SIG LULC Jawa Timur - Sentinel-2A
echo =====================================================================
echo Menjalankan Sistem Informasi Geografis LULC Jawa Timur (Streamlit)...
echo Penulis: Rifqi Fairurrafi (240411100201)
echo =====================================================================
call .\.venv\Scripts\activate.bat
streamlit run app.py
pause
