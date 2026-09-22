import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configurar la conexión con Google Sheets usando gspread y st.secrets
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Cargamos credenciales desde los secrets de Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

# Función para obtener datos de una hoja específica (ej. "usuarios" o "gastos")
def cargar_datos_sheet(nombre_hoja):
    client = conectar_gsheets()
    # Reemplaza 'db_gastos' con el nombre exacto de tu planilla en Google Drive
    sheet = client.open("db_gastos").worksheet(nombre_hoja)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Función para guardar/agregar datos a la hoja
def guardar_datos_sheet(nombre_hoja, df):
    client = conectar_gsheets()
    sheet = client.open("db_gastos").worksheet(nombre_hoja)
    # Limpiamos y reescribimos o añadimos según tu lógica
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Ejemplo de uso dentro de tu app:
st.title("Control de Gastos con Google Sheets 🚀")

# Cargar usuarios o finanzas directamente de la nube
try:
    df_finance = cargar_datos_sheet("finance_data")
    st.write("Datos financieros cargados desde Google Sheets:")
    st.dataframe(df_finance)
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")