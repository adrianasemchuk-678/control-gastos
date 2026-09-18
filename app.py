import streamlit as st
import datetime
import database as db

# Configuración adaptable a pantallas de celulares
st.set_page_config(page_title="Control de Gastos", page_icon="🌷", layout="centered")

# Estilo Nude (tonos crema, beige y café suave)
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF6F0;
        color: #4A3E3D;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    div[data-testid="stSidebar"] {
        background-color: #F3ECE1;
    }
    div[data-testid="stForm"] {
        background-color: #F8F1E7;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #E5D9CC;
    }
    .card-box {
        background-color: #FFFFFF;
        border-left: 5px solid #C8A282;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.03);
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# PIN constante del Admin
PIN_ADMIN_CORRECTO = "5861"

st.title("🌷 Control de Gastos")

# --- BARRA LATERAL (PERMISOS Y USUARIOS) ---
st.sidebar.header("🔑 Acceso y Permisos")

pin_ingresado = st.sidebar.text_input("Código de Acceso / PIN Admin", type="password", help="Ingresa 5861 para modo Administrador")
es_admin = (pin_ingresado == PIN_ADMIN_CORRECTO)

if es_admin:
    st.sidebar.success("🔓 Modo Administrador Activo")
else:
    if pin_ingresado != "":
        st.sidebar.error("PIN Incorrecto")
    st.sidebar.info("🔒 Modo Usuario Común")

st.sidebar.divider()

# Cargar lista dinámica de usuarios
lista_usuarios = db.obtener_usuarios()

# Selección de Usuario Actual
st.sidebar.subheader("👤 Mi Usuario")
usuario_activo = st.sidebar.selectbox("¿Quién está usando la app?", lista_usuarios)

# Opción para agregar nuevo usuario
with st.sidebar.expander("➕ Crear nuevo usuario"):
    nuevo_nombre = st.text_input("Nombre de la nueva persona:")
    if st.button("Guardar Usuario"):
        if nuevo_nombre.strip():
            db.agregar_usuario(nuevo_nombre)
            st.sidebar.success(f"¡Usuario '{nuevo_nombre}' creado!")
            st.rerun()

# Filtro de visualización (Solo activo si es Administrador)
if es_admin:
    st.sidebar.divider()
    st.sidebar.subheader("👀 Vista Global (Admin)")
    opciones_filtro = ["Todos"] + lista_usuarios
    usuario_filtro = st.sidebar.selectbox("Filtrar registros por:", opciones_filtro)
else:
    # El usuario común solo ve sus propios datos
    usuario_filtro = usuario_activo

# --- PESTAÑAS PRINCIPALES ---
tab_gastos, tab_pagos, tab_admin = st.tabs(["💸 Registrar Gastos", "📅 Pagos Fijos", "⚙️ Ajustes"])

# ==========================================
# PESTAÑA 1: GASTOS DIARIOS
# ==========================================
with tab_gastos:
    st.subheader(f"Registrar Gasto a nombre de: **{usuario_activo}**")
    
    with st.form("form_gasto"):
        f_fecha = st.date_input("Fecha", datetime.date.today())
        f_concepto = st.text_input("¿En qué gastaste? (Ej: Panadería, Nafta)")
        f_monto = st.number_input("Monto ($)", min_value=0.0, step=50.0)
        f_cat = st.selectbox("Categoría", ["Alimentación", "Transporte", "Servicios", "Salidas / Ocio", "Salud / Deporte", "Otros"])
        
        btn_gasto = st.form_submit_button("Guardar Gasto")
        if btn_gasto:
            if f_concepto.strip() and f_monto > 0:
                db.registrar_gasto(f_fecha, f_concepto, f_monto, f_cat, usuario_activo)
                st.success("¡Gasto guardado correctamente!")
                st.rerun()
            else:
                st.warning("Completa la descripción y un monto válido.")

    st.divider()
    
    st.subheader(f"📋 Mis Gastos ({'Todos' if es_admin and usuario_filtro=='Todos' else usuario_filtro})")
    gastos = db.obtener_gastos(usuario_filtro)
    
    if not gastos:
        st.info("No hay gastos registrados para este filtro.")
    else:
        total_gastado = sum(g["monto"] for g in gastos)
        st.markdown(f"### **Total:** `${total_gastado:,.2f}`")
        
        for g in gastos:
            st.markdown(f"""
                <div class="card-box">
                    <b>{g['concepto']}</b> — ${g['monto']:,.2f}<br>
                    <small>📅 {g['fecha']} | 📁 {g['categoria']} | 👤 {g['usuario']}</small>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: PAGOS FIJOS Y RECORDATORIOS
# ==========================================
with tab_pagos:
    st.subheader("Pagos Fijos del Mes")
    
    with st.expander("➕ Agregar nuevo Pago Fijo", expanded=False):
        with st.form("form_pago_fijo"):
            pf_concepto = st.text_input("Nombre del servicio o pago (Ej: Luz, Internet)")
            pf_monto = st.number_input("Monto aproximado ($)", min_value=0.0, step=100.0)
            pf_dia = st.number_input("Día de vencimiento (1 al 31)", min_value=1, max_value=31, value=10)
            
            if st.form_submit_button("Guardar Pago Fijo"):
                if pf_concepto.strip():
                    db.agregar_pago_fijo(pf_concepto, pf_monto, pf_dia, usuario_activo)
                    st.success("Pago fijo agregado con éxito.")
                    st.rerun()

    st.divider()
    
    pagos = db.obtener_pagos_fijos(usuario_filtro)
    
    if not pagos:
        st.info("No hay pagos fijos registrados.")
    else:
        if "edit_id" not in st.session_state:
            st.session_state.edit_id = None

        for p in pagos:
            p_id = p["id"]
            
            # Modo Edición
            if st.session_state.edit_id == p_id:
                with st.form(f"edit_pago_{p_id}"):
                    e_concepto = st.text_input("Concepto", value=p["concepto"])
                    e_monto = st.number_input("Monto ($)", min_value=0.0, value=float(p["monto"]))
                    e_dia = st.number_input("Día", min_value=1, max_value=31, value=int(p["dia_vencimiento"]))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾 Guardar"):
                            db.actualizar_pago_fijo(p_id, e_concepto, e_monto, e_dia)
                            st.session_state.edit_id = None
                            st.rerun()
                    with c2:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state.edit_id = None
                            st.rerun()
            else:
                st.markdown(f"""
                    <div class="card-box">
                        <b style="font-size:1.1em;">{p['concepto']}</b> — ${p['monto']:,.2f}<br>
                        <small>📆 Vence el día <b>{p['dia_vencimiento']}</b> | 👤 {p['usuario']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                c_edit, c_del, _ = st.columns([1, 1, 2])
                with c_edit:
                    if st.button("✏️ Editar", key=f"btn_ed_{p_id}"):
                        st.session_state.edit_id = p_id
                        st.rerun()
                with c_del:
                    if st.button("🗑️ Eliminar", key=f"btn_del_{p_id}"):
                        db.eliminar_pago_fijo(p_id)
                        st.rerun()

# ==========================================
# PESTAÑA 3: OPCIONES DE ADMINISTRADOR
# ==========================================
with tab_admin:
    st.subheader("Opciones Avanzadas")
    
    if es_admin:
        st.warning("⚠️ Zona de Mantenimiento (Solo Administrador)")
        if st.button("🗑️ Borrar datos de prueba", type="primary"):
            db.borrar_todos_los_datos()
            st.success("¡Se eliminaron todos los gastos y pagos fijos registrados!")
            st.rerun()
    else:
        st.info("🔒 Necesitas ingresar el PIN de Administrador (5861) en la barra lateral para acceder a esta sección.")