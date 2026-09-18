import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración inicial de la página
st.set_page_config(page_title="Control de Gastos & Alcancía", page_icon="🌸", layout="wide")

# Estilos visuales sencillos y amigables
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { background-color: #FFB6C1; color: black; border-radius: 10px; font-weight: bold; }
    .metric-box { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Inicializar Variables de Sesión (Memoria de la App)
if 'ingreso_inicial' not in st.session_state:
    st.session_state.ingreso_inicial = 0.0
if 'gastos' not in st.session_state:
    st.session_state.gastos = []
if 'pagos_fijos' not in st.session_state:
    st.session_state.pagos_fijos = []

# Mapeo de Emojis por Categoría
EMOJIS_CATEGORIAS = {
    "Supermercado": "🛒",
    "Servicios / Facturas": "💡",
    "Alquiler": "🏠",
    "Comida / Salidas": "🍕",
    "Transporte": "🚌",
    "Entretenimiento": "🎮",
    "Salud / Personal": "💊",
    "Otros": "📦"
}

st.title("🌸 Control de Gastos & Alcancía de Ahorro")

# --- SECCIÓN 1: INGRESO MENSUAL ---
st.sidebar.header("⚙️ Configuración")
nuevo_ingreso = st.sidebar.number_input("Ingreso / Sueldo del Mes ($):", min_value=0.0, value=st.session_state.ingreso_inicial, step=10000.0)
st.session_state.ingreso_inicial = nuevo_ingreso

# Cálculo del saldo actual
total_gastos = sum(g['monto'] for g in st.session_state.gastos)
total_fijos_pagados = sum(p['monto'] for p in st.session_state.pagos_fijos if p['pagado'])
saldo_restante = st.session_state.ingreso_inicial - total_gastos - total_fijos_pagados

# Muestra de Métricas Principales
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("💰 Ingreso Inicial", f"${st.session_state.ingreso_inicial:,.2f}")
col_m2.metric("💸 Gastos Totales", f"${(total_gastos + total_fijos_pagados):,.2f}")
col_m3.metric("🟢 Saldo Disponible", f"${saldo_restante:,.2f}")

st.divider()

# --- SECCIÓN 2: PAGOS FIJOS Y GASTOS DIARIOS ---
tab_fijos, tab_gastos, tab_reportes = st.tabs(["📌 Pagos Fijos", "🛒 Gastos Diarios", "📊 Reporte & Exportación"])

with tab_fijos:
    st.subheader("📌 Registro de Pagos Fijos")
    
    with st.form("form_fijos", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        concepto_fijo = col_f1.text_input("Concepto (ej. Alquiler, Luz)")
        monto_fijo = col_f2.number_input("Monto ($)", min_value=0.0, step=1000.0)
        vencimiento_fijo = col_f3.text_input("Vencimiento (ej. Del 1 al 10)")
        btn_fijo = st.form_submit_button("Añadir Pago Fijo")
        
        if btn_fijo and concepto_fijo and monto_fijo > 0:
            st.session_state.pagos_fijos.append({
                "id": len(st.session_state.pagos_fijos),
                "concepto": concepto_fijo,
                "monto": monto_fijo,
                "vencimiento": vencimiento_fijo,
                "pagado": False
            })
            st.success(f"Pago fijo '{concepto_fijo}' agregado correctamente.")
            st.rerun()

    # Tabla interactiva de Pagos Fijos
    if st.session_state.pagos_fijos:
        st.write("### Mis Compromisos Fijos")
        for i, pf in enumerate(st.session_state.pagos_fijos):
            col_pf1, col_pf2, col_pf3, col_pf4, col_pf5 = st.columns([2, 1, 1, 1, 1])
            col_pf1.write(f"**{pf['concepto']}**")
            col_pf2.write(f"${pf['monto']:,.2f}")
            col_pf3.write(f"🗓️ {pf['vencimiento']}")
            
            # Botón Marcar Pagado
            estado_label = "✅ Pagado" if pf['pagado'] else "💳 Marcar Pagado"
            if col_pf4.button(estado_label, key=f"pag_{i}"):
                st.session_state.pagos_fijos[i]['pagado'] = not st.session_state.pagos_fijos[i]['pagado']
                st.rerun()
                
            # Botón Eliminar
            if col_pf5.button("🗑️", key=f"del_pf_{i}"):
                st.session_state.pagos_fijos.pop(i)
                st.rerun()

with tab_gastos:
    st.subheader("🛒 Cargar Gastos Diarios")
    
    with st.form("form_gastos", clear_on_submit=True):
        col_g1, col_g2, col_g3 = st.columns([2, 1, 1])
        cat_gasto = col_g1.selectbox("Categoría", list(EMOJIS_CATEGORIAS.keys()))
        monto_gasto = col_g2.number_input("Monto ($)", min_value=0.0, step=500.0)
        fecha_gasto = col_g3.date_input("Fecha")
        desc_gasto = st.text_input("Detalle corto (opcional)")
        btn_gasto = st.form_submit_button("Registrar Gasto")
        
        if btn_gasto and monto_gasto > 0:
            emoji = EMOJIS_CATEGORIAS.get(cat_gasto, "📦")
            st.session_state.gastos.append({
                "fecha": fecha_gasto.strftime("%Y-%m-%d"),
                "categoria": f"{emoji} {cat_gasto}",
                "detalle": desc_gasto if desc_gasto else cat_gasto,
                "monto": monto_gasto
            })
            st.success("Gasto registrado con éxito.")
            st.rerun()

    # Listado de Gastos
    if st.session_state.gastos:
        st.write("### Historial de Gastos")
        df_gastos = pd.DataFrame(st.session_state.gastos)
        st.dataframe(df_gastos, use_container_width=True)

with tab_reportes:
    st.subheader("📊 Reporte Resumido y Descargas")
    
    # Preparar Datos Consolidados
    todos_los_gastos = []
    for g in st.session_state.gastos:
        todos_los_gastos.append(g)
    for pf in st.session_state.pagos_fijos:
        if pf['pagado']:
            todos_los_gastos.append({
                "fecha": "Pago Fijo",
                "categoria": "💡 Servicios / Facturas",
                "detalle": pf['concepto'],
                "monto": pf['monto']
            })

    if todos_los_gastos:
        df_totales = pd.DataFrame(todos_los_gastos)
        
        # Gráfico por Categoría
        fig, ax = plt.subplots(figsize=(6, 3))
        resumen_cat = df_totales.groupby("categoria")["monto"].sum()
        resumen_cat.plot(kind="pie", autopct="%1.1f%%", ax=ax, colors=['#FFB6C1', '#87CEFA', '#98FB98', '#DDA0DD', '#F0E68C'])
        ax.set_ylabel("")
        ax.set_title("Distribución de Gastos")
        st.pyplot(fig)

        # Función para generar el PDF de una sola página
        def generar_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#333333"))
            
            elements.append(Paragraph("🌸 Resumen Mensual de Control de Gastos", title_style))
            elements.append(Spacer(1, 10))
            
            # Tabla de Resumen
            data_resumen = [
                ["Ingreso Inicial", f"${st.session_state.ingreso_inicial:,.2f}"],
                ["Gastos Totales", f"${(total_gastos + total_fijos_pagados):,.2f}"],
                ["Saldo Restante", f"${saldo_restante:,.2f}"]
            ]
            t_resumen = Table(data_resumen, colWidths=[200, 200])
            t_resumen.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF0F5")),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 1, colors.white)
            ]))
            elements.append(t_resumen)
            elements.append(Spacer(1, 15))
            
            # Guardar imagen del gráfico en PDF
            img_buf = BytesIO()
            fig.savefig(img_buf, format='png', bbox_inches='tight')
            img_buf.seek(0)
            elements.append(Image(img_buf, width=300, height=150))
            elements.append(Spacer(1, 15))

            # Tabla de Gastos
            data_tabla = [["Fecha", "Categoría", "Detalle", "Monto"]]
            for item in todos_los_gastos:
                data_tabla.append([item["fecha"], item["categoria"], item["detalle"], f"${item['monto']:,.2f}"])
                
            t_detalle = Table(data_tabla, colWidths=[80, 150, 170, 80])
            t_detalle.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFB6C1")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
            ]))
            elements.append(t_detalle)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer

        # Botones de Descarga
        col_d1, col_d2 = st.columns(2)
        
        # Descarga PDF
        pdf_bytes = generar_pdf()
        col_d1.download_button(
            label="📄 Descargar Resumen en PDF",
            data=pdf_bytes,
            file_name="resumen_gastos.pdf",
            mime="application/pdf"
        )
        
        # Descarga Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_totales.to_excel(writer, index=False, sheet_name='Gastos')
        excel_buffer.seek(0)
        
        col_d2.download_button(
            label="📊 Descargar Excel",
            data=excel_buffer,
            file_name="gastos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Agrega gastos o pagos fijos para habilitar el reporte y las descargas.")