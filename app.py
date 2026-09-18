import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Control de Gastos & Alcancía", page_icon="🌸", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { background-color: #FFB6C1; color: black; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- ARCHIVOS DE DATOS PERMANENTES ---
USERS_FILE = "users.json"
DATA_FILE = "finance_data.json"

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

usuarios = cargar_json(USERS_FILE, {"admin": "5861"})
db_data = cargar_json(DATA_FILE, {})

# --- LOGIN Y SESIÓN ---
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

usr_actual = st.session_state["usuario_actual"]
es_admin = (usr_actual == "admin")

# Estructura de datos por usuario
if usr_actual not in db_data:
    db_data[usr_actual] = {"ingreso_inicial": 0.0, "pagos_fijos": [], "gastos_diarios": []}

usr_data = db_data[usr_actual]

# NAVEGACIÓN
st.sidebar.title(f"👤 {usr_actual.capitalize()}")
if es_admin:
    st.sidebar.caption("👑 Administrador")

opciones = ["💰 Mi Presupuesto & Panel", "📌 Pagos Fijos", "🛒 Gastos Diarios", "📊 Reportes & Resumen"]
if es_admin:
    opciones.append("👥 Gestión de Usuarios")

opcion = st.sidebar.radio("Menú Principal", opciones)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["usuario_actual"] = None
    st.rerun()

# HELPER DE EMOJIS AUTOMÁTICOS
EMOJIS_KEYWORDS = {
    "maquillaje": "💄", "skincare": "🧴", "crema": "🧴", "cosmetico": "💄",
    "comida": "🍔", "almuerzo": "🍲", "cena": "🍕", "super": "🛒", "supermercado": "🛒",
    "nafta": "⛽", "auto": "🚗", "remis": "🚖", "uber": "🚖",
    "gimnasio": "🏋️‍♀️", "gym": "🏋️‍♀️", "padel": "🎾",
    "ropa": "👗", "zapatillas": "👟", "farmacia": "💊", "regalo": "🎁"
}

def obtener_emoji(texto):
    txt_lower = texto.lower()
    for kw, emoji in EMOJIS_KEYWORDS.items():
        if kw in txt_lower:
            return f"{emoji} {texto.capitalize()}"
    return f"📦 {texto.capitalize()}"

def fmt_moneda(monto):
    return f"$ {monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- SECCIÓN 1: PANEL Y PRESUPUESTO INICIAL ---
if opcion == "💰 Mi Presupuesto & Panel":
    st.header("💵 Ingreso Mensual y Saldo Disponible")
    
    nuevo_ingreso = st.number_input("Ingreso / Sueldo del Mes ($):", min_value=0.0, value=float(usr_data.get("ingreso_inicial", 0.0)), step=10000.0)
    if nuevo_ingreso != usr_data.get("ingreso_inicial"):
        usr_data["ingreso_inicial"] = nuevo_ingreso
        guardar_json(DATA_FILE, db_data)
        st.success("Sueldo / Ingreso actualizado.")

    total_fijos_pagados = sum(pf["monto"] for pf in usr_data["pagos_fijos"] if pf["pagado"])
    total_gastos_diarios = sum(g["monto"] for g in usr_data["gastos_diarios"])
    total_gastado = total_fijos_pagados + total_gastos_diarios
    saldo_disponible = usr_data["ingreso_inicial"] - total_gastado

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Ingreso Inicial", fmt_moneda(usr_data["ingreso_inicial"]))
    c2.metric("💸 Gastos Totales (Pagados)", fmt_moneda(total_gastado))
    c3.metric("🟢 Saldo Disponible", fmt_moneda(saldo_disponible))

# --- SECCIÓN 2: PAGOS FIJOS ---
elif opcion == "📌 Pagos Fijos":
    st.header("📌 Gestión de Pagos Fijos Recurrentes")
    
    with st.form("form_fijo", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        concepto = col_f1.text_input("Concepto (ej. Alquiler, Luz, Internet)")
        monto = col_f2.number_input("Monto ($)", min_value=0.0, step=1000.0)
        vencimiento = col_f3.text_input("Vencimiento (ej. Del 1 al 10)")
        btn_fijo = st.form_submit_button("Agregar Pago Fijo")

        if btn_fijo and concepto and monto > 0:
            concepto_emoji = obtener_emoji(concepto)
            usr_data["pagos_fijos"].append({
                "concepto": concepto_emoji,
                "monto": monto,
                "vencimiento": vencimiento if vencimiento else "Sin fecha",
                "pagado": False
            })
            guardar_json(DATA_FILE, db_data)
            st.success("Pago fijo agregado.")
            st.rerun()

    if usr_data["pagos_fijos"]:
        st.subheader("📋 Lista de Compromisos Fijos")
        for idx, pf in enumerate(usr_data["pagos_fijos"]):
            col_a, col_b, col_c, col_d, col_e = st.columns([2, 1, 1, 1, 1])
            col_a.write(f"**{pf['concepto']}**")
            col_b.write(fmt_moneda(pf["monto"]))
            col_c.write(f"🗓️ {pf['vencimiento']}")
            
            label_estado = "✅ Pagado" if pf["pagado"] else "💳 Marcar Pagado"
            if col_d.button(label_estado, key=f"pay_{idx}"):
                usr_data["pagos_fijos"][idx]["pagado"] = not usr_data["pagos_fijos"][idx]["pagado"]
                guardar_json(DATA_FILE, db_data)
                st.rerun()

            if col_e.button("🗑️ Eliminar", key=f"del_pf_{idx}"):
                usr_data["pagos_fijos"].pop(idx)
                guardar_json(DATA_FILE, db_data)
                st.rerun()

# --- SECCIÓN 3: GASTOS DIARIOS ---
elif opcion == "🛒 Gastos Diarios":
    st.header("🛒 Cargar Gastos Diarios")
    
    with st.form("form_diarios", clear_on_submit=True):
        col_g1, col_g2 = st.columns(2)
        fecha = col_g1.date_input("Fecha", datetime.now(), format="DD/MM/YYYY")
        monto = col_g2.number_input("Monto ($)", min_value=0.0, step=500.0)
        
        cat_select = st.selectbox("Categoría", ["Supermercado", "Servicios", "Transporte", "Salud / Estética", "Otros"])
        detalle = st.text_input("Detalle corto (ej. Maquillaje, Cena, Regalo)")
        
        if st.form_submit_button("Registrar Gasto"):
            if monto > 0:
                texto_base = detalle if detalle else cat_select
                cat_con_emoji = obtener_emoji(texto_base)
                
                usr_data["gastos_diarios"].append({
                    "fecha": fecha.strftime("%d/%m/%Y"),
                    "categoria": cat_con_emoji,
                    "monto": monto
                })
                guardar_json(DATA_FILE, db_data)
                st.success("Gasto registrado correctamente.")
                st.rerun()

    if usr_data["gastos_diarios"]:
        st.subheader("📋 Historial de Gastos Diarios")
        df_g = pd.DataFrame(usr_data["gastos_diarios"])
        df_g["Monto Formateado"] = df_g["monto"].apply(fmt_moneda)
        st.dataframe(df_g[["fecha", "categoria", "Monto Formateado"]], use_container_width=True)

# --- SECCIÓN 4: REPORTES Y RESUMEN ---
elif opcion == "📊 Reportes & Resumen":
    st.header("📊 Vistas y Reportes Financieros")
    
    target_user = usr_actual
    if es_admin:
        lista_usr = ["Todos"] + list(db_data.keys())
        sel = st.selectbox("Ver información de:", lista_usr)
        if sel != "Todos":
            target_user = sel

    if es_admin and sel == "Todos":
        gastos_totales_lista = []
        for u, udata in db_data.items():
            for g in udata.get("gastos_diarios", []):
                gastos_totales_lista.append({**g, "usuario": u})
            for pf in udata.get("pagos_fijos", []):
                if pf["pagado"]:
                    gastos_totales_lista.append({"fecha": "Pago Fijo", "categoria": pf["concepto"], "monto": pf["monto"], "usuario": u})
    else:
        udata = db_data.get(target_user, {})
        gastos_totales_lista = list(udata.get("gastos_diarios", []))
        for pf in udata.get("pagos_fijos", []):
            if pf["pagado"]:
                gastos_totales_lista.append({"fecha": "Pago Fijo", "categoria": pf["concepto"], "monto": pf["monto"]})

    if gastos_totales_lista:
        df_rep = pd.DataFrame(gastos_totales_lista)
        st.metric("Total Acumulado Gastado", fmt_moneda(df_rep["monto"].sum()))
        
        st.subheader("📌 Desglose en Pantalla")
        df_rep["Monto"] = df_rep["monto"].apply(fmt_moneda)
        st.dataframe(df_rep.drop(columns=["monto"]), use_container_width=True)
        
        st.subheader("📈 Gastos por Categoría")
        cat_chart = df_rep.groupby("categoria")["monto"].sum()
        st.bar_chart(cat_chart)
    else:
        st.info("No hay información suficiente para generar reportes.")

# --- SECCIÓN 5: GESTIÓN DE USUARIOS (ADMIN) ---
elif opcion == "👥 Gestión de Usuarios" and es_admin:
    st.header("👥 Crear y Modificar Usuarios")
    
    nu = st.text_input("Nuevo Usuario")
    np = st.text_input("Contraseña", type="password")
    if st.button("Crear Usuario"):
        if nu and np:
            usuarios[nu] = np
            guardar_json(USERS_FILE, usuarios)
            st.success(f"Usuario {nu} creado exitosamente.")
            st.rerun()
        else:
            st.warning("Completa usuario y contraseña.")