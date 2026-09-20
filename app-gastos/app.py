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

def cargar_usuarios():
    return cargar_datos("usuarios")

def cargar_finanzas():
    return cargar_datos("finanzas")

# --- SISTEMA DE LOGIN Y CONTROL DE USUARIOS ---
st.sidebar.title("🔐 Control de Accesos")

df_usuarios = cargar_usuarios()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.es_admin = False

if not st.session_state.autenticado:
    st.subheader("Iniciar Sesión")
    usuario_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if not df_usuarios.empty and "usuario" in df_usuarios.columns and "password" in df_usuarios.columns:
            user_row = df_usuarios[(df_usuarios["usuario"] == usuario_input) & (df_usuarios["password"] == password_input)]
            if not user_row.empty:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario_input
                st.session_state.es_admin = (usuario_input.lower() == "admin") 
                st.success(f"¡Bienvenido/a {usuario_input}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        else:
            st.warning("La pestaña 'usuarios' está vacía o mal configurada en Google Sheets.")
    st.stop()

# Barra lateral para el usuario conectado
st.sidebar.write(f"Conectado como: **{st.session_state.usuario_actual}**")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.rerun()

# --- APLICACIÓN PRINCIPAL DE GASTOS ---
st.title("💰 Control de Gastos AS")

# Cargar los datos de finanzas
df_finanzas = cargar_finanzas()

# Filtrar según el usuario (si es admin ve todo, si es usuario común ve solo lo suyo)
if not st.session_state.es_admin and not df_finanzas.empty and "usuario" in df_finanzas.columns:
    df_finanzas = df_finanzas[df_finanzas["usuario"] == st.session_state.usuario_actual]

st.subheader("Tus Registros")
st.dataframe(df_finanzas)

# Formulario rápido para agregar un gasto (Ejemplo básico adaptado a tus columnas)
st.subheader("Agregar Nuevo Gasto")
with st.form("form_gasto"):
    # Ajustá estos campos según las columnas reales que tenga tu pestaña 'finanzas'
    monto = st.number_input("Monto", min_value=0.0, format="%.2f")
    categoria = st.text_input("Categoría")
    descripcion = st.text_input("Descripción")
    
    submitted = st.form_submit_button("Guardar Gasto")
    if submitted:
        # Armamos la fila respetando el orden de columnas de tu Google Sheet
        nueva_fila = [st.session_state.usuario_actual, monto, categoria, descripcion]
        guardar_fila("finanzas", nueva_fila)
        st.success("¡Gasto guardado con éxito!")
        st.rerun()