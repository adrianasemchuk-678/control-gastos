import streamlit as st
import requests
import pandas as pd

# Tu URL del puente de Google Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwkfC-KJ6QEhSeIMD784VT4fYjcNRzkIcYTpMM2pZIuiE3qmcX_43D3SHYT4xTBt3Xe/exec"

def cargar_datos(sheet_name):
    payload = {"action": "read", "sheet": sheet_name}
    response = requests.post(WEB_APP_URL, json=payload)
    rows = response.json()
    if len(rows) > 1:
        return pd.DataFrame(rows[1:], columns=rows[0])
    return pd.DataFrame()

def guardar_fila(sheet_name, fila_datos):
    payload = {"action": "append", "sheet": sheet_name, "row": fila_datos}
    response = requests.post(WEB_APP_URL, json=payload)
    return response.json()

# Funciones listas para usar en tu app
def cargar_usuarios():
    return cargar_datos("usuarios")

def cargar_finanzas():
    return cargar_datos("finanzas")