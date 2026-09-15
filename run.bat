@echo off
title Control de Gastos Mensuales & Alcancia de Ahorro
cd /d "%~dp0"
echo Iniciando aplicacion Streamlit...
python -m streamlit run app.py
pause
