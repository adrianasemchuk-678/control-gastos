import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Control de Gastos", page_icon="💰", layout="wide")

# --- ARCHIVOS DE DATOS ---
USERS_FILE = "users.json"
GASTOS_FILE = "gastos.json"

def cargar_json(filepath, default):
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=4)
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def guardar_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Cargar datos
usuarios = cargar_json(USERS_FILE, {"admin": "5861"})
gastos_data = cargar_json(GASTOS_FILE, [])

# --- AUTENTICACIÓN Y SESIÓN ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("🔑 Control de Gastos - Iniciar Sesión")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", type="primary"):
            if user_input in usuarios and usuarios[user_input] == pass_input:
                st.session_state["usuario_actual"] = user_input
                st.success(f"¡Bienvenido/a {user_input}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

# --- NAVEGACIÓN Y CERRAR SESIÓN ---
es_admin = (st.session_state["usuario_actual"] == "admin")

st.sidebar.title(f"👤 {st.session_state['usuario_actual'].capitalize()}")
if es_admin:
    st.sidebar.caption("👑 Administrador")

opciones = ["Cargar Gastos", "Reportes y Resumen"]
if es_admin:
    opciones.append("Gestión de Usuarios")

opcion = st.sidebar.radio("Navegación", opciones)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["usuario_actual"] = None
    st.rerun()

# MAPA DE EMOJIS AUTOMÁTICOS
EMOJIS_KEYWORDS = {
    "maquillaje": "💄", "cosmetico": "💄", "skincare": "🧴", "crema": "🧴",
    "comida": "🍔", "almuerzo": "🍲", "cena": "🍕", "super": "🛒", "supermercado": "🛒",
    "nafta": "⛽", "combustible": "⛽", "auto": "🚗", "remis": "🚖", "uber": "🚖",
    "gimnasio": "🏋️‍♀️", "gym": "🏋️‍♀️", "padel": "🎾", "deporte": "⚽",
    "ropa": "👗", "zapatillas": "👟", "zapato": "👠",
    "farmacia": "💊", "remedio": "💊", "medico": "🩺",
    "regalo": "🎁", "veterinaria": "🐾", "perro": "🐶", "gato": "🐱"
}

def obtener_emoji_descripcion(texto):
    texto_clean = texto.lower()
    for kw, emoji in EMOJIS_KEYWORDS.items():
        if kw in texto_clean:
            return f"{emoji} {texto.capitalize()}"
    return f"📌 {texto.capitalize()}"

# --- SECCIÓN 1: CARGAR GASTOS ---
if opcion == "Cargar Gastos":
    st.header("📝 Cargar Gastos Diarios")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha = st.date_input("Fecha del gasto", datetime.now(), format="DD/MM/YYYY")
    with col_f2:
        monto = st.number_input("Monto del gasto ($)", min_value=0.0, step=100.0, format="%.2f")
        if monto > 0:
            monto_formateado = f"$ {monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.caption(f"Monto ingresado: **{monto_formateado}**")

    categorias = ["Alimentación", "Transporte", "Salud / Estética", "Deporte / Gimnasio", "Servicios", "Otros"]
    categoria = st.selectbox("Categoría", categorias)

    descripcion_final = categoria
    if categoria == "Otros":
        desc_custom = st.text_input("Escribe el detalle del gasto (ej. Maquillaje, Regalo, etc.)")
        if desc_custom:
            descripcion_final = obtener_emoji_descripcion(desc_custom)
            st.info(f"Categoría guardada como: **{descripcion_final}**")

    if st.button("Guardar Gasto", type="primary"):
        if monto <= 0:
            st.warning("El monto debe ser mayor a 0.")
        else:
            nuevo_gasto = {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "fecha_display": fecha.strftime("%d/%m/%Y"),
                "monto": monto,
                "categoria": descripcion_final,
                "usuario": st.session_state["usuario_actual"]
            }
            gastos_data.append(nuevo_gasto)
            guardar_json(GASTOS_FILE, gastos_data)
            st.success("¡Gasto guardado correctamente!")

# --- SECCIÓN 2: REPORTES Y RESUMEN ---
elif opcion == "Reportes y Resumen":
    st.header("📊 Reporte de Gastos Mensuales")

    # Filtrar según permisos
    if es_admin:
        usuarios_lista = ["Todos"] + list(set(g["usuario"] for g in gastos_data)) if gastos_data else ["Todos"]
        filtro_usr = st.selectbox("Filtrar por usuario:", usuarios_lista)
        if filtro_usr != "Todos":
            gastos_filtrados = [g for g in gastos_data if g["usuario"] == filtro_usr]
        else:
            gastos_filtrados = list(gastos_data)
    else:
        gastos_filtrados = [g for g in gastos_data if g["usuario"] == st.session_state["usuario_actual"]]

    if not gastos_filtrados:
        st.info("No hay gastos registrados todavía.")
    else:
        df = pd.DataFrame(gastos_filtrados)
        total_gastado = df["monto"].sum()
        total_formateado = f"$ {total_gastado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # VISTAZO RÁPIDO / PANTALLAZO
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gastado", total_formateado)
        col2.metric("Cantidad de Registros", len(df))
        if not df.empty:
            cat_top = df.groupby("categoria")["monto"].sum().idxmax()
            col3.metric("Categoría principal", cat_top)

        st.subheader("📋 Resumen Detallado")
        
        df_display = df.copy()
        df_display["Monto Formateado"] = df_display["monto"].apply(lambda x: f"$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        cols_mostrar = ["fecha_display", "categoria", "Monto Formateado"]
        headers_mostrar = ["Fecha (DD/MM/YYYY)", "Categoría / Detalle", "Monto"]
        if es_admin:
            cols_mostrar.append("usuario")
            headers_mostrar.append("Usuario")

        df_tabla = df_display[cols_mostrar]
        df_tabla.columns = headers_mostrar
        st.dataframe(df_tabla, use_container_width=True)

        # Gráfico simple
        st.subheader("📈 Resumen por Categorías")
        cat_chart = df.groupby("categoria")["monto"].sum()
        st.bar_chart(cat_chart)

# --- SECCIÓN 3: GESTIÓN DE USUARIOS (SOLO ADMIN) ---
elif opcion == "Gestión de Usuarios" and es_admin:
    st.header("👥 Administración de Usuarios")

    st.subheader("Crear un nuevo usuario")
    nuevo_user = st.text_input("Nombre de usuario (ej. maria)")
    nueva_pass = st.text_input("Contraseña asignada", type="password")

    if st.button("Crear Usuario", type="primary"):
        if not nuevo_user or not nueva_pass:
            st.warning("Completa el usuario y la contraseña.")
        elif nuevo_user in usuarios:
            st.error("Ese usuario ya existe.")
        else:
            usuarios[nuevo_user] = nueva_pass
            guardar_json(USERS_FILE, usuarios)
            st.success(f"Usuario '{nuevo_user}' creado exitosamente.")

    st.divider()
    st.subheader("Usuarios existentes")
    for u in usuarios.keys():
        st.write(f"- **{u}** {'(Administrador)' if u == 'admin' else ''}")