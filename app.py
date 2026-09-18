import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Control de Gastos AS", page_icon="🌸", layout="wide")

# --- ESTILOS VISUALES & MARCA PERSONAL (AS) ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { background-color: #FFB6C1; color: black; border-radius: 10px; font-weight: bold; }
    
    /* ENCABEZADO DE MARCA ADRIANA SEMCHUK */
    .brand-header {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FFB6C1;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .brand-logo {
        background-color: #FFB6C1;
        color: white;
        font-size: 38px;
        font-weight: 900;
        width: 75px;
        height: 75px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.15);
        font-family: 'Helvetica Neue', sans-serif;
    }
    .brand-title {
        color: #333333;
        font-size: 26px;
        font-weight: bold;
        margin: 0;
    }
    .brand-subtitle {
        color: #666666;
        font-size: 14px;
        margin-top: 2px;
        font-style: italic;
    }
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
    # Insignia en pantalla de inicio de sesión
    st.markdown("""
        <div class="brand-header">
            <div class="brand-logo">AS</div>
            <div>
                <div class="brand-title">Control de Gastos & Alcancía</div>
                <div class="brand-subtitle">Diseñado y Creado por <b>Adriana Semchuk</b> 🌸</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
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

# Estructura inicial de datos por usuario
if usr_actual not in db_data:
    db_data[usr_actual] = {
        "ingreso_inicial": 0.0,
        "alcancia": 0.0,
        "meta_alcancia": 0.0,
        "nombre_meta": "Ahorro General",
        "usar_presupuestos": False,
        "presupuestos_cat": {},
        "pagos_fijos": [],
        "gastos_diarios": []
    }

usr_data = db_data[usr_actual]
usr_data.setdefault("alcancia", 0.0)
usr_data.setdefault("meta_alcancia", 0.0)
usr_data.setdefault("nombre_meta", "Ahorro General")
usr_data.setdefault("usar_presupuestos", False)
usr_data.setdefault("presupuestos_cat", {})

# HELPER DE FECHAS Y FORMATOS
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
hoy = datetime.now()
nombre_mes_actual = f"{MESES[hoy.month - 1]} {hoy.year}"

# CÁPSULA Y MARCA DE ADRIANA SEMCHUK EN PANEL PRINCIPAL
st.markdown(f"""
    <div class="brand-header">
        <div class="brand-logo">AS</div>
        <div style="flex-grow: 1;">
            <div class="brand-title">Control de Gastos & Alcancía</div>
            <div class="brand-subtitle">Aplicación creada por <b>Adriana Semchuk</b> 🌸 | Mes en curso: <b>{nombre_mes_actual}</b> ({hoy.strftime('%d/%m/%Y')})</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# NAVEGACIÓN
st.sidebar.title(f"👤 {usr_actual.capitalize()}")
if es_admin:
    st.sidebar.caption("👑 Administradora")

opciones = ["💰 Mi Presupuesto & Panel", "📌 Pagos Fijos", "🛒 Gastos Diarios", "⚙️ Mis Preferencias", "📊 Reportes & Exportaciones"]
if es_admin:
    opciones.append("👥 Gestión de Usuarios")

opcion = st.sidebar.radio("Menú Principal", opciones)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["usuario_actual"] = None
    st.rerun()

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
    
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        nuevo_ingreso = st.number_input("Ingreso / Sueldo del Mes ($):", min_value=0.0, value=float(usr_data.get("ingreso_inicial", 0.0)), step=10000.0)
        if nuevo_ingreso != usr_data.get("ingreso_inicial"):
            usr_data["ingreso_inicial"] = nuevo_ingreso
            guardar_json(DATA_FILE, db_data)
            st.success("Sueldo / Ingreso actualizado.")

    with col_i2:
        alcancia_val = st.number_input("🐷 Alcancía de Ahorros ($):", min_value=0.0, value=float(usr_data.get("alcancia", 0.0)), step=5000.0)
        if alcancia_val != usr_data.get("alcancia"):
            usr_data["alcancia"] = alcancia_val
            guardar_json(DATA_FILE, db_data)
            st.success("Alcancía actualizada.")

    total_fijos_pagados = sum(pf["monto"] for pf in usr_data["pagos_fijos"] if pf["pagado"])
    total_gastos_diarios = sum(g["monto"] for g in usr_data["gastos_diarios"])
    total_gastado = total_fijos_pagados + total_gastos_diarios
    saldo_disponible = usr_data["ingreso_inicial"] - total_gastado

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Ingreso Inicial", fmt_moneda(usr_data["ingreso_inicial"]))
    c2.metric("💸 Gastos Totales", fmt_moneda(total_gastado))
    c3.metric("🟢 Saldo Disponible", fmt_moneda(saldo_disponible))
    c4.metric("🐷 Alcancía Acumulada", fmt_moneda(usr_data["alcancia"]))

    if usr_data["meta_alcancia"] > 0:
        st.subheader(f"🎯 Meta: {usr_data['nombre_meta']}")
        progreso = min(usr_data["alcancia"] / usr_data["meta_alcancia"], 1.0)
        st.progress(progreso, text=f"Llevas un {progreso*100:.1f}% alcanzado ({fmt_moneda(usr_data['alcancia'])} de {fmt_moneda(usr_data['meta_alcancia'])})")

    if usr_data["usar_presupuestos"] and usr_data["gastos_diarios"]:
        df_tmp = pd.DataFrame(usr_data["gastos_diarios"])
        gastado_cat = df_tmp.groupby("categoria")["monto"].sum()
        for cat, limite in usr_data["presupuestos_cat"].items():
            if limite > 0:
                gastado = gastado_cat.get(cat, 0.0)
                if gastado >= limite:
                    st.error(f"⚠️ **Superaste el límite en {cat}**: Gastaste {fmt_moneda(gastado)} (Límite: {fmt_moneda(limite)})")
                elif gastado >= limite * 0.8:
                    st.warning(f"⚡ **Cerca del límite en {cat}**: Gastaste {fmt_moneda(gastado)} de {fmt_moneda(limite)}")

    st.divider()
    st.subheader("🔄 Cierre y Reinicio de Mes")
    col_reset1, col_reset2 = st.columns(2)
    if col_reset1.button("🧹 Pasar Sobrante a Alcancía y Reiniciar Gastos"):
        if saldo_disponible > 0:
            usr_data["alcancia"] += saldo_disponible
        usr_data["gastos_diarios"] = []
        for pf in usr_data["pagos_fijos"]:
            pf["pagado"] = False
        guardar_json(DATA_FILE, db_data)
        st.success("¡Mes cerrado! Sobrante guardado en la alcancía y registros limpios.")
        st.rerun()

    if col_reset2.button("🗑️ Borrar Gastos Diarios sin alterar Alcancía"):
        usr_data["gastos_diarios"] = []
        guardar_json(DATA_FILE, db_data)
        st.success("Gastos diarios reiniciados.")
        st.rerun()

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
    st.header("🛒 Cargar y Modificar Gastos Diarios")
    
    with st.form("form_diarios", clear_on_submit=True):
        col_g1, col_g2 = st.columns(2)
        fecha = col_g1.date_input("Fecha", datetime.now(), format="DD/MM/YYYY")
        monto = col_g2.number_input("Monto ($)", min_value=0.0, step=500.0)
        
        cat_select = st.selectbox("Categoría", ["Supermercado", "Servicios", "Transporte", "Salud / Estética", "Otros"])
        detalle = st.text_input("Detalle corto (ej. Maquillaje, Regalo)")
        
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
        st.subheader("📋 Historial de Gastos (Editar o Borrar)")
        for idx, g in enumerate(usr_data["gastos_diarios"]):
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            col1.write(g["fecha"])
            col2.write(g["categoria"])
            col3.write(fmt_moneda(g["monto"]))
            if col4.button("🗑️ Eliminar", key=f"del_g_{idx}"):
                usr_data["gastos_diarios"].pop(idx)
                guardar_json(DATA_FILE, db_data)
                st.rerun()

# --- SECCIÓN 4: PREFERENCIAS ---
elif opcion == "⚙️ Mis Preferencias":
    st.header("⚙️ Opciones de Personalización")
    st.caption("Ajusta la aplicación según la modalidad que te sea más cómoda.")

    st.subheader("🎯 Meta para la Alcancía")
    nom_m = st.text_input("Objetivo de Ahorro (ej. Viaje, Cambio de Auto)", value=usr_data["nombre_meta"])
    val_m = st.number_input("Monto Meta ($):", min_value=0.0, value=float(usr_data["meta_alcancia"]), step=10000.0)
    if st.button("Guardar Meta"):
        usr_data["nombre_meta"] = nom_m
        usr_data["meta_alcancia"] = val_m
        guardar_json(DATA_FILE, db_data)
        st.success("Meta actualizada.")

    st.divider()
    st.subheader("📊 Presupuesto Máximo por Categoría (Opcional)")
    usar_p = st.toggle("Activar límites mensuales por categoría", value=usr_data["usar_presupuestos"])
    usr_data["usar_presupuestos"] = usar_p

    if usar_p:
        st.info("Ingresa los límites máximos que no deseas superar este mes.")
        cats_def = ["🛒 Supermercado", "💡 Servicios", "🚌 Transporte", "💊 Salud / Estética", "📦 Otros"]
        for c in cats_def:
            val_actual = float(usr_data["presupuestos_cat"].get(c, 0.0))
            nuevo_limite = st.number_input(f"Límite para {c} ($):", min_value=0.0, value=val_actual, step=5000.0, key=f"pref_{c}")
            usr_data["presupuestos_cat"][c] = nuevo_limite

    if st.button("Guardar Preferencias"):
        guardar_json(DATA_FILE, db_data)
        st.success("Preferencias guardadas correctamente.")

# --- SECCIÓN 5: REPORTES Y EXPORTACIONES ---
elif opcion == "📊 Reportes & Exportaciones":
    st.header(f"📊 Reportes Financieros — {nombre_mes_actual}")
    
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
        df_rep_display = df_rep.copy()
        df_rep_display["Monto"] = df_rep_display["monto"].apply(fmt_moneda)
        st.dataframe(df_rep_display.drop(columns=["monto"]), use_container_width=True)
        
        fig, ax = plt.subplots(figsize=(6, 3))
        cat_chart = df_rep.groupby("categoria")["monto"].sum()
        cat_chart.plot(kind="pie", autopct="%1.1f%%", ax=ax, colors=['#FFB6C1', '#87CEFA', '#98FB98', '#DDA0DD', '#F0E68C', '#FFD700'])
        ax.set_ylabel("")
        ax.set_title(f"Distribución por Categorías ({nombre_mes_actual})")
        st.pyplot(fig)

        st.divider()
        st.subheader("📥 DESCARGAR REPORTES")

        def generar_pdf_1p():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#333333"))
            
            elements.append(Paragraph(f"🌸 Reporte de Gastos AS — {nombre_mes_actual}", title_style))
            elements.append(Paragraph("Diseñado por Adriana Semchuk", styles['Normal']))
            elements.append(Spacer(1, 8))
            
            data_res = [
                ["Usuario", target_user.capitalize()],
                ["Total Gastado", fmt_moneda(df_rep["monto"].sum())]
            ]
            t_res = Table(data_res, colWidths=[150, 250])
            t_res.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF0F5")),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.white)
            ]))
            elements.append(t_res)
            elements.append(Spacer(1, 10))

            img_buf = BytesIO()
            fig.savefig(img_buf, format='png', bbox_inches='tight')
            img_buf.seek(0)
            elements.append(Image(img_buf, width=280, height=130))
            elements.append(Spacer(1, 10))

            data_tab = [["Fecha", "Categoría / Detalle", "Monto"]]
            for _, item in df_rep.iterrows():
                data_tab.append([item["fecha"], item["categoria"], fmt_moneda(item["monto"])])
                
            t_det = Table(data_tab[:15], colWidths=[90, 230, 110])
            t_det.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFB6C1")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
            ]))
            elements.append(t_det)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer

        col_d1, col_d2 = st.columns(2)
        
        pdf_data = generar_pdf_1p()
        col_d1.download_button(
            label="📄 Descargar PDF (1 Hoja)",
            data=pdf_data,
            file_name=f"Reporte_Gastos_AS_{nombre_mes_actual.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

        excel_buf = BytesIO()
        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
            df_rep_excel = df_rep.copy()
            df_rep_excel["Monto ($)"] = df_rep_excel["monto"]
            df_rep_excel.drop(columns=["monto"]).to_excel(writer, index=False, sheet_name='Gastos')
        excel_buf.seek(0)

        col_d2.download_button(
            label="📊 Descargar Excel",
            data=excel_buf,
            file_name=f"Reporte_Gastos_AS_{nombre_mes_actual.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay información suficiente registrada este mes para exportar.")

# --- SECCIÓN 6: GESTIÓN DE USUARIOS (ADMIN) ---
elif opcion == "👥 Gestión de Usuarios" and es_admin:
    st.header("👥 Gestión y Control Global de Usuarios")
    
    st.subheader("Tabla Resumen de Todos los Usuarios")
    resumen_admin = []
    for u, udata in db_data.items():
        tot_f = sum(pf["monto"] for pf in udata.get("pagos_fijos", []) if pf["pagado"])
        tot_g = sum(g["monto"] for g in udata.get("gastos_diarios", []))
        tot = tot_f + tot_g
        ing = udata.get("ingreso_inicial", 0.0)
        resumen_admin.append({
            "Usuario": u.capitalize(),
            "Ingreso ($)": fmt_moneda(ing),
            "Gastado ($)": fmt_moneda(tot),
            "Saldo Restante": fmt_moneda(ing - tot),
            "Alcancía ($)": fmt_moneda(udata.get("alcancia", 0.0))
        })
    st.dataframe(pd.DataFrame(resumen_admin), use_container_width=True)

    st.divider()
    st.subheader("Crear un Nuevo Usuario")
    nu = st.text_input("Nuevo Usuario")
    np = st.text_input("Contraseña", type="password")
    if st.button("Crear Usuario"):
        if nu and np:
            usuarios[nu] = np
            guardar_json(USERS_FILE, usuarios)
            st.success(f"Usuario '{nu}' creado exitosamente.")
            st.rerun()
        else:
            st.warning("Completa usuario y contraseña.")