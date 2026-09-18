import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Función para conectar a Google Sheets usando los secretos de Streamlit
@st.cache_resource
def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Esto leerá las credenciales desde la configuración de Streamlit Cloud
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Abre la planilla usando el link que me pasaste
    sheet_url = "https://docs.google.com/spreadsheets/d/1vHTsp8RlJRzgMdPL2bYHIT0skQ_orYyYubCjbPVyHq4/edit?usp=sharing"
    return client.open_by_url(sheet_url)

# Conectamos a la base de datos
db = conectar_db()

# Para leer la pestaña de usuarios
def cargar_usuarios():
    ws = db.worksheet("usuarios")
    data = ws.get_all_records()
    return pd.DataFrame(data)

# Para leer la pestaña de finanzas/gastos
def cargar_finanzas():
    ws = db.worksheet("finanzas")
    data = ws.get_all_records()
    return pd.DataFrame(data)