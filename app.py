"""
Aplicación Streamlit: Control de Gastos Mensuales
Diseño súper fácil e intuitivo (para niños de 10 años o personas sin experiencia en computación).
Acceso con calculadora y bienvenida de Adriana (Código 5861).
Incluye pagos fijos con fechas de vencimiento (ej: del 1 al 10), alertas y recordatorios automáticos.
Estética pastel en tonos rosados.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db
import categories as cat

# Configuración inicial de la página
st.set_page_config(
    page_title="Control de Gastos de Adriana 🌸",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar Base de Datos
db.init_db()

# Inyección de CSS Personalizado: Letras grandes, botones claros y diseño pastel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Fondo general suave */
    .stApp {
        background: linear-gradient(180deg, #fff5f7 0%, #fef0f4 50%, #fff7f9 100%);
        color: #3d2b35;
    }
    
    /* Botones Gigantes Principales */
    button[kind="primary"] {
        background: linear-gradient(135deg, #ff6584 0%, #ff8da1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 28px !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 6px 18px rgba(255, 101, 132, 0.4) !important;
        transition: all 0.25s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(255, 101, 132, 0.55) !important;
    }
    
    /* Botones Secundarios Claros */
    button[kind="secondary"] {
        background: #ffffff !important;
        color: #be123c !important;
        border: 2px solid #fecdd3 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 2px 8px rgba(244, 114, 182, 0.12) !important;
        transition: all 0.25s ease !important;
    }
    button[kind="secondary"]:hover {
        background: #fff1f2 !important;
        border-color: #fb7185 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Caja de Bienvenida con Calculadora */
    .calc-welcome-card {
        background: #ffffff;
        border: 2.5px solid #fbcfe8;
        border-radius: 30px;
        padding: 40px 32px;
        box-shadow: 0 16px 36px rgba(244, 114, 182, 0.18);
        text-align: center;
        max-width: 440px;
        margin: 40px auto 20px auto;
    }
    
    /* Icono Calculadora Estético */
    .calc-icon-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 90px;
        height: 90px;
        background: linear-gradient(135deg, #ffe4e6 0%, #fed7aa 100%);
        border: 3px solid #ff758c;
        border-radius: 26px;
        font-size: 3.2rem;
        box-shadow: 0 8px 20px rgba(255, 117, 140, 0.25);
        margin-bottom: 16px;
    }
    
    /* Tarjetas de Resumen Grandes */
    .resumen-card {
        border-radius: 22px;
        padding: 22px 24px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
        border: 2px solid rgba(255, 255, 255, 0.9);
        text-align: center;
    }
    .resumen-titulo {
        font-size: 1.05rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 6px;
    }
    .resumen-monto {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .resumen-subtexto {
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 6px;
        display: inline-block;
        padding: 3px 12px;
        border-radius: 12px;
    }
    
    /* Tarjetas de Alertas de Vencimiento */
    .alerta-card {
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .alerta-vencido {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        border-left: 6px solid #e11d48;
    }
    .alerta-por-vencer {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 6px solid #f59e0b;
    }
    .alerta-pagado {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 6px solid #16a34a;
    }
    
    /* Pasos sencillos numerados */
    .paso-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        background: #ff6584;
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 800;
        border-radius: 50%;
        margin-right: 10px;
    }
    
    .paso-titulo {
        font-size: 1.4rem;
        font-weight: 800;
        color: #4a2d3b;
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    
    input {
        font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- PANTALLA DE ENTRADA CON CALCULADORA Y BIENVENIDA DE ADRIANA -----------------
if "desbloqueado" not in st.session_state:
    st.session_state.desbloqueado = False

if not st.session_state.desbloqueado:
    col_c1, col_c2, col_c3 = st.columns([1, 1.4, 1])
    with col_c2:
        st.write("")
        st.markdown("""
        <div class="calc-welcome-card">
            <div class="calc-icon-badge">🧮</div>
            <h2 style="color: #be123c; margin-top: 4px; margin-bottom: 6px; font-weight: 800; font-size: 1.7rem;">
                🌸 Adriana te da la bienvenida 🌸
            </h2>
            <p style="color: #64748b; font-size: 1.05rem; margin-bottom: 16px;">
                Ingresá tu código para ver y anotar tus gastos de forma fácil.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_bienvenida_adriana"):
            codigo_ingreso = st.text_input(
                "🔑 Escribí el código de 4 números aquí:",
                type="password",
                placeholder="Por ejemplo: 5861",
                help="El código es 5861"
            )
            btn_entrar = st.form_submit_button("✨ ENTRAR A MIS CUENTAS ✨", type="primary", use_container_width=True)
            
            if btn_entrar:
                if db.verificar_codigo_acceso(codigo_ingreso):
                    st.session_state.desbloqueado = True
                    st.success("¡Código correcto! Entrando... ✨")
                    st.rerun()
                else:
                    st.error("❌ El código no es correcto. Acordate que es 5861. ¡Probá de nuevo!")

    st.stop()

# ----------------- DENTRO DE LA APLICACIÓN -----------------

def fmt_pesos(num):
    return f"${num:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

hoy = date.today()
nombres_meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
mes_nombre_actual = nombres_meses[hoy.month - 1]
anio_actual = hoy.year

# Barra superior clara
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.title("🧮 Mis Cuentas Fáciles")
    st.markdown(f"🌸 ¡Hola! Estamos viendo tus cuentas de **{mes_nombre_actual} de {anio_actual}**")
with col_top2:
    st.write("")
    if st.button("🔒 Salir / Cerrar", type="secondary", use_container_width=True):
        st.session_state.desbloqueado = False
        st.rerun()

st.write("")

# ----------------- PASO 1: TU DINERO (SUELDO O PLATA DEL MES) -----------------
sueldo_guardado = float(db.get_setting("sueldo_mensual", "350000"))

with st.container():
    st.markdown("""
    <div class="paso-titulo">
        <span class="paso-badge">1</span> ¿Cuánta plata tenés este mes?
    </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([3, 1.5])
    with col_s1:
        sueldo_nuevo = st.number_input(
            "Escribí acá cuánto dinero tenés en total (tu sueldo o plata ahorrada):",
            min_value=0.0,
            value=sueldo_guardado,
            step=10000.0,
            format="%.2f"
        )
    with col_s2:
        st.write("")
        st.write("")
        if st.button("💾 Guardar este dinero", type="primary", use_container_width=True):
            db.set_setting("sueldo_mensual", str(sueldo_nuevo))
            st.success("¡Listo! Ya quedó guardado cuánto dinero tenés. 🌸")
            st.rerun()

st.write("")

# ----------------- PASO 2: EL RESUMEN CLARO (CÓMO VENÍS) -----------------
gastos_lista = db.get_expenses(mes=hoy.month, anio=anio_actual)
df_gastos = pd.DataFrame(gastos_lista)

total_gastos = df_gastos["monto"].sum() if not df_gastos.empty else 0.0
plata_restante = sueldo_guardado - total_gastos

st.markdown("""
<div class="paso-titulo">
    <span class="paso-badge">2</span> ¿Cómo venís con tu dinero?
</div>
""", unsafe_allow_html=True)

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown(f"""
    <div class="resumen-card" style="background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%); border-color: #7dd3fc;">
        <div class="resumen-titulo">💵 TU DINERO INICIAL</div>
        <div class="resumen-monto" style="color: #0369a1;">{fmt_pesos(sueldo_guardado)}</div>
        <div class="resumen-subtexto" style="background: #bae6fd; color: #075985;">Total disponible</div>
    </div>
    """, unsafe_allow_html=True)

with col_r2:
    st.markdown(f"""
    <div class="resumen-card" style="background: linear-gradient(135deg, #ffe4e6 0%, #fff1f2 100%); border-color: #fca5a5;">
        <div class="resumen-titulo">💸 LO QUE YA GASTASTE</div>
        <div class="resumen-monto" style="color: #be123c;">{fmt_pesos(total_gastos)}</div>
        <div class="resumen-subtexto" style="background: #fecdd3; color: #9f1239;">Gastos anotados</div>
    </div>
    """, unsafe_allow_html=True)

with col_r3:
    color_fondo_saldo = "#f0fdf4" if plata_restante >= 0 else "#fef2f2"
    color_borde_saldo = "#86efac" if plata_restante >= 0 else "#f87171"
    color_texto_saldo = "#15803d" if plata_restante >= 0 else "#b91c1c"
    mensaje_saldo = "¡Te queda en el bolsillo!" if plata_restante >= 0 else "¡Ojo, gastaste de más!"
    
    st.markdown(f"""
    <div class="resumen-card" style="background: {color_fondo_saldo}; border-color: {color_borde_saldo};">
        <div class="resumen-titulo">🐷 PLATA QUE TE QUEDA</div>
        <div class="resumen-monto" style="color: {color_texto_saldo};">{fmt_pesos(plata_restante)}</div>
        <div class="resumen-subtexto" style="background: {'#bbf7d0' if plata_restante >= 0 else '#fecaca'}; color: {color_texto_saldo};">
            {mensaje_saldo}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ----------------- PASO 3: PAGOS FIJOS Y VENCIMIENTOS (DEL 1 AL 10) -----------------
st.markdown("""
<div class="paso-titulo">
    <span class="paso-badge">3</span> 🔔 Pagos fijos del mes y recordatorios de vencimiento
</div>
""", unsafe_allow_html=True)

st.caption("Aquí ves los pagos que tenés todos los meses (como alquiler, luz, internet). La app te avisa si están por vencer o si todavía no los pagaste.")

# Obtener estado de los pagos fijos para este mes
estados_pagos = db.get_estado_pagos_fijos(hoy.month, anio_actual)

# Revisar si hay alguno pendiente o vencido
pagos_pendientes = [p for p in estados_pagos if not p["pagado"]]
pagos_vencidos = [p for p in estados_pagos if p["estado"] == "vencido"]

if pagos_vencidos:
    st.error(f"🚨 **¡Atención! Hay {len(pagos_vencidos)} pago(s) que ya vencieron este mes y todavía no figuran como pagados.** Mirá la lista abajo:")

for pago in estados_pagos:
    p_id = pago["id"]
    nombre = pago["nombre"]
    monto = pago["monto"]
    d_desde = pago["dia_desde"]
    d_hasta = pago["dia_hasta"]
    icono = pago["icono"]
    estado = pago["estado"]

    col_box, col_accion = st.columns([3.8, 1.2])

    with col_box:
        if estado == "pagado":
            st.markdown(f"""
            <div class="alerta-card alerta-pagado">
                <div>
                    <span style="font-size: 1.4rem;">{icono}</span>
                    <strong style="font-size: 1.1rem; color: #166534; margin-left: 6px;">{nombre}</strong>
                    <span style="color: #15803d; font-weight: 700; margin-left: 10px;">{fmt_pesos(monto)}</span>
                    <br><small style="color: #166534; margin-left: 30px;">✅ ¡Pagado este mes! Ya está restado de tus cuentas.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif estado == "vencido":
            st.markdown(f"""
            <div class="alerta-card alerta-vencido">
                <div>
                    <span style="font-size: 1.4rem;">🚨</span>
                    <strong style="font-size: 1.1rem; color: #9f1239; margin-left: 6px;">{nombre}</strong>
                    <span style="color: #be123c; font-weight: 800; margin-left: 10px;">{fmt_pesos(monto)}</span>
                    <br><small style="color: #b91c1c; margin-left: 30px; font-weight: 700;">
                        ⚠️ Vencía el día {d_hasta}. ¡Todavía no lo pagaste!
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif estado == "por_vencer":
            st.markdown(f"""
            <div class="alerta-card alerta-por-vencer">
                <div>
                    <span style="font-size: 1.4rem;">⏰</span>
                    <strong style="font-size: 1.1rem; color: #92400e; margin-left: 6px;">{nombre}</strong>
                    <span style="color: #b45309; font-weight: 800; margin-left: 10px;">{fmt_pesos(monto)}</span>
                    <br><small style="color: #78350f; margin-left: 30px;">
                        📅 Se paga del {d_desde} al {d_hasta}. ¡Es momento de pagarlo!
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alerta-card" style="background: #f8fafc; border-left: 6px solid #94a3b8;">
                <div>
                    <span style="font-size: 1.4rem;">{icono}</span>
                    <strong style="font-size: 1.1rem; color: #334155; margin-left: 6px;">{nombre}</strong>
                    <span style="color: #475569; font-weight: 700; margin-left: 10px;">{fmt_pesos(monto)}</span>
                    <br><small style="color: #64748b; margin-left: 30px;">Próximo a vencer: se paga del {d_desde} al {d_hasta}.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_accion:
        st.write("")
        if not pago["pagado"]:
            if st.button(f"✅ Ya lo pagué", key=f"btn_pagar_{p_id}", type="primary", use_container_width=True):
                db.marcar_pago_fijo_como_pagado(p_id, hoy.month, anio_actual)
                st.success(f"¡Genial! Anotamos el pago de {nombre} por {fmt_pesos(monto)}.")
                st.rerun()
        else:
            st.markdown("<div style='color: #16a34a; font-weight: 800; text-align: center; padding-top: 10px;'>✔️ Al día</div>", unsafe_allow_html=True)

# Formulario para agregar otro pago fijo
with st.expander("➕ ¿Querés agregar otro pago fijo para que te recuerde todos los meses?"):
    st.markdown("Escribí acá si tenés otro gasto fijo que pagás todos los meses (por ejemplo: cuota de la escuela, gimnasio, gas):")
    col_np1, col_np2, col_np3 = st.columns([3, 2, 2])
    with col_np1:
        nuevo_pf_nombre = st.text_input("Nombre del gasto fijo:", placeholder="Ej: Expensas del edificio, Escuela...")
    with col_np2:
        nuevo_pf_monto = st.number_input("Monto aproximado ($):", min_value=0.0, step=1000.0, format="%.2f", key="nuevo_pf_monto")
    with col_np3:
        nuevo_pf_cat = st.selectbox("Categoría:", options=cat.get_categories_list(), key="nuevo_pf_cat")

    col_dia1, col_dia2 = st.columns(2)
    with col_dia1:
        dia_desde_val = st.number_input("¿Desde qué día del mes se puede pagar?", min_value=1, max_value=31, value=1)
    with col_dia2:
        dia_hasta_val = st.number_input("¿Hasta qué día del mes tenés tiempo de pagar? (Límite)", min_value=1, max_value=31, value=10)

    if st.button("💾 Guardar este pago fijo para todos los meses", type="primary"):
        if not nuevo_pf_nombre.strip() or nuevo_pf_monto <= 0:
            st.error("Por favor completá el nombre y un monto mayor a cero.")
        else:
            ico = cat.get_category_icon(nuevo_pf_cat)
            db.add_pago_fijo(nuevo_pf_nombre, nuevo_pf_monto, nuevo_pf_cat, ico, dia_desde_val, dia_hasta_val)
            st.success(f"¡Listo! '{nuevo_pf_nombre}' te avisará todos los meses del {dia_desde_val} al {dia_hasta_val}. 🌸")
            st.rerun()

st.write("")

# ----------------- PASO 4: ANOTAR UN GASTO EXTRA O DIARIO -----------------
st.markdown("""
<div class="paso-titulo">
    <span class="paso-badge">4</span> Anotar otros gastos del día (supermercado, salidas, etc.)
</div>
""", unsafe_allow_html=True)

st.markdown("**👉 Tocá uno de estos botones si fue alguno de estos gastos:**")
col_b1, col_b2, col_b3, col_b4 = st.columns(4)

if "descripcion_rapida" not in st.session_state:
    st.session_state.descripcion_rapida = ""
if "categoria_rapida" not in st.session_state:
    st.session_state.categoria_rapida = None

with col_b1:
    if st.button("🛒 Super / Comida", use_container_width=True):
        st.session_state.descripcion_rapida = "Supermercado y comida"
        st.session_state.categoria_rapida = "🛒 Snacks, Kiosco & Comida"
    if st.button("💊 Farmacia / Remedios", use_container_width=True):
        st.session_state.descripcion_rapida = "Farmacia y medicamentos"
        st.session_state.categoria_rapida = "💊 Salud, Cuidado & Farmacia"

with col_b2:
    if st.button("💡 Luz / Gas / Celular", use_container_width=True):
        st.session_state.descripcion_rapida = "Factura de servicios o celular"
        st.session_state.categoria_rapida = "📱 Celular & Conectividad"
    if st.button("👕 Ropa / Zapatillas", use_container_width=True):
        st.session_state.descripcion_rapida = "Ropa o calzado"
        st.session_state.categoria_rapida = "👕 Ropa & Zapatillas"

with col_b3:
    if st.button("🏠 Casa / Hogar", use_container_width=True):
        st.session_state.descripcion_rapida = "Gastos de la casa"
        st.session_state.categoria_rapida = "🏠 Alquiler & Hogar"
    if st.button("🎬 Salidas / Paseos", use_container_width=True):
        st.session_state.descripcion_rapida = "Salida a comer o paseo"
        st.session_state.categoria_rapida = "🎬 Ocio / Salidas & Juegos"

with col_b4:
    if st.button("🚌 SUBE / Nafta / Viaje", use_container_width=True):
        st.session_state.descripcion_rapida = "Carga de SUBE o combustible"
        st.session_state.categoria_rapida = "🚌 Transporte / SUBE"
    if st.button("🐾 Comida de Mascota", use_container_width=True):
        st.session_state.descripcion_rapida = "Alimento para la mascota"
        st.session_state.categoria_rapida = "🐾 Mascotas"

with st.container():
    st.write("")
    col_f1, col_f2, col_f3 = st.columns([3, 2, 2.5])
    
    with col_f1:
        desc_input = st.text_input(
            "1️⃣ ¿En qué gastaste?",
            value=st.session_state.descripcion_rapida,
            placeholder="Ejemplo: Compré verduras, helado, nafta...",
            key="input_desc_simple"
        )
    
    with col_f2:
        monto_input = st.number_input(
            "2️⃣ ¿Cuánta plata fue? ($)",
            min_value=0.0,
            step=500.0,
            format="%.2f",
            key="input_monto_simple"
        )

    lista_cats = cat.get_categories_list()
    cat_detectada = cat.detect_category_from_text(desc_input)
    
    idx_cat = 0
    if st.session_state.categoria_rapida and st.session_state.categoria_rapida in lista_cats:
        idx_cat = lista_cats.index(st.session_state.categoria_rapida)
    elif desc_input and cat_detectada in lista_cats:
        idx_cat = lista_cats.index(cat_detectada)

    with col_f3:
        cat_elegida = st.selectbox(
            "3️⃣ Categoría (se elige sola)",
            options=lista_cats,
            index=idx_cat,
            key="input_cat_simple"
        )

    st.write("")
    btn_guardar_gasto = st.button("✨ ¡LISTO! GUARDAR ESTE GASTO ✨", type="primary", use_container_width=True)

    if btn_guardar_gasto:
        if not desc_input.strip():
            st.error("⚠️ Por favor escribe en qué gastaste.")
        elif monto_input <= 0:
            st.error("⚠️ Por favor escribe cuánta plata fue (un número mayor a cero).")
        else:
            icono = cat.get_category_icon(cat_elegida)
            db.add_expense(
                fecha=hoy.strftime("%Y-%m-%d"),
                descripcion=desc_input.strip(),
                categoria=cat_elegida,
                icono=icono,
                monto=monto_input
            )
            st.session_state.descripcion_rapida = ""
            st.session_state.categoria_rapida = None
            st.success(f"🎉 ¡Gasto guardado con éxito! Anotaste **{desc_input.strip()}** por **{fmt_pesos(monto_input)}**.")
            st.rerun()

st.write("")

# ----------------- PASO 5: ¿EN QUÉ SE FUE LA PLATA? -----------------
st.markdown("""
<div class="paso-titulo">
    <span class="paso-badge">5</span> ¿En qué gastaste más este mes?
</div>
""", unsafe_allow_html=True)

if df_gastos.empty:
    st.info("👋 Todavía no anotaste ningún gasto este mes. ¡Anotá el primero arriba para ver los gráficos!")
else:
    df_cat = df_gastos.groupby(["categoria", "icono"])["monto"].sum().reset_index()
    df_cat = df_cat.sort_values(by="monto", ascending=False)
    df_cat["porcentaje"] = (df_cat["monto"] / df_cat["monto"].sum()) * 100.0
    df_cat["color"] = df_cat["categoria"].apply(cat.get_category_color)

    col_g1, col_g2 = st.columns([1.2, 1])

    with col_g1:
        fig_pie = px.pie(
            df_cat,
            names="categoria",
            values="monto",
            hole=0.42,
            color="categoria",
            color_discrete_map={row["categoria"]: row["color"] for _, row in df_cat.iterrows()}
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>',
            marker=dict(line=dict(color='#ffffff', width=2))
        )
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=340,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        st.markdown("##### 👛 La lista de lo que más gastaste:")
        for _, row in df_cat.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; border-radius: 12px; padding: 10px 16px; margin-bottom: 8px; border-left: 6px solid {row['color']}; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <span style="font-size: 1.05rem;">{row['icono']} <strong>{row['categoria']}</strong></span>
                <span style="font-size: 1.05rem;"><strong>{fmt_pesos(row['monto'])}</strong> <small style="color: #be123c;">({row['porcentaje']:.0f}%)</small></span>
            </div>
            """, unsafe_allow_html=True)

st.write("")

# ----------------- PASO 6: LA LISTA COMPLETA Y BORRADO FÁCIL -----------------
st.markdown("""
<div class="paso-titulo">
    <span class="paso-badge">6</span> Todos los gastos que anotaste
</div>
""", unsafe_allow_html=True)

if not df_gastos.empty:
    df_mostrar = df_gastos[["fecha", "icono", "descripcion", "categoria", "monto"]].copy()
    df_mostrar.columns = ["Fecha", "Ícono", "En qué gastaste", "Categoría", "Monto"]
    df_mostrar["Monto"] = df_mostrar["Monto"].map(lambda x: fmt_pesos(x))
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    col_csv, col_del = st.columns([1, 1.5])
    with col_csv:
        csv_bytes = df_gastos[["fecha", "descripcion", "categoria", "monto"]].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Guardar lista en Excel (CSV)",
            data=csv_bytes,
            file_name=f"mis_cuentas_{mes_nombre_actual}_{anio_actual}.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True
        )
    with col_del:
        with st.expander("❌ ¿Te equivocaste al anotar algo? Hacé clic acá para borrarlo"):
            opciones_para_borrar = {
                f"{row['fecha']} - {row['icono']} {row['descripcion']} ({fmt_pesos(row['monto'])})": row['id']
                for _, row in df_gastos.iterrows()
            }
            elegido = st.selectbox("Elegí el gasto que querés borrar:", options=list(opciones_para_borrar.keys()))
            if st.button("🗑️ Sí, borrar este gasto", type="secondary"):
                id_borrar = opciones_para_borrar[elegido]
                db.delete_expense(id_borrar)
                st.success("¡Gasto borrado con éxito!")
                st.rerun()
else:
    st.caption("Aún no hay gastos registrados.")
