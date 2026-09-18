import streamlit as st
import json
import os
import datetime

st.set_page_config(page_title="Mi Agenda & Calendario Pastel", page_icon="🌸", layout="wide")

# Estilos CSS personalizados con colores pasteles vivos y bonitos
st.markdown("""
<style>
    /* Fondo general suave */
    .stApp { 
        background: linear-gradient(135deg, #fefae0 0%, #f3e8ff 100%); 
    }
    
    /* Botones principales */
    .stButton>button {
        background: linear-gradient(90deg, #a855f7 0%, #ec4899 100%);
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(236, 72, 153, 0.2);
    }
    
    /* Tarjeta de eventos */
    .card-evento {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "datos.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if "usuarios" not in datos or "eventos" not in datos:
                    return {"usuarios": {"adriana": {"clave": "1234", "rol": "admin"}}, "eventos": []}
                return datos
        except:
            pass
    return {"usuarios": {"adriana": {"clave": "1234", "rol": "admin"}}, "eventos": []}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

datos = cargar_datos()

CATEGORIAS = {
    "✈️ Viajes": {"emoji": "✈️", "color": "#e0f2fe", "borde": "#38bdf8"},
    "🩺 Salud / Médico": {"emoji": "🩺", "color": "#ffe4e6", "borde": "#fb7185"},
    "💅 Estética / Belleza": {"emoji": "💅", "color": "#f3e8ff", "borde": "#c084fc"},
    "🏋️‍♀️ Gimnasio": {"emoji": "🏋️‍♀️", "color": "#dcfce7", "borde": "#4ade80"},
    "🎾 Pádel": {"emoji": "🎾", "color": "#fef9c3", "borde": "#facc15"},
    "📄 Vencimientos / Pólizas": {"emoji": "📄", "color": "#ffedd5", "borde": "#fb923c"},
    "🎂 Cumpleaños": {"emoji": "🎂", "color": "#fce7f3", "borde": "#f472b6"},
    "💰 Finanzas / Pagos": {"emoji": "💰", "color": "#ccfbf1", "borde": "#2dd4bf"},
    "📌 Otro": {"emoji": "📌", "color": "#f1f5f9", "borde": "#94a3b8"}
}

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
    st.session_state["rol_actual"] = None

# ----------------- LOGIN -----------------
if not st.session_state["usuario_actual"]:
    st.title("🌸 Inicio de Sesión — Mi Agenda")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_input = st.text_input("👤 Usuario:").strip().lower()
        pass_input = st.text_input("🔑 Contraseña:", type="password")
        if st.button("✨ Ingresar a la App"):
            if user_input in datos["usuarios"] and datos["usuarios"][user_input]["clave"] == pass_input:
                st.session_state["usuario_actual"] = user_input
                st.session_state["rol_actual"] = datos["usuarios"][user_input]["rol"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ----------------- BARRA LATERAL -----------------
st.sidebar.title(f"👑 ¡Hola, {st.session_state['usuario_actual'].capitalize()}!")

opciones_menu = ["📅 Mi Agenda Personal"]
if st.session_state["rol_actual"] == "admin":
    opciones_menu.append("⚙️ Gestión de Usuarios (Admin)")

opcion = st.sidebar.radio("Navegación:", opciones_menu)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["usuario_actual"] = None
    st.session_state["rol_actual"] = None
    st.rerun()

# ----------------- AGENDA -----------------
if opcion == "📅 Mi Agenda Personal":
    st.title("💖 Mi Agenda & Recordatorios Pastel")
    st.write("Agendá tus turnos, compromisos y vencimientos con avisos a medida.")

    with st.expander("➕ Agendar nuevo compromiso / turno", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("📝 Título (ej: Turno con Fabiana, Seguro Moto):")
            categoria = st.selectbox("🏷️ Categoría:", list(CATEGORIAS.keys()))
            fecha = st.date_input("📅 Fecha:", datetime.date.today())
            hora = st.time_input("⏰ Hora:", datetime.time(9, 0))

        with col2:
            alertas = st.multiselect(
                "🔔 ¿Cuándo querés que te avise?",
                ["1 semana antes", "2 días antes", "1 día antes", "2 horas antes", "30 minutos antes"],
                default=["1 día antes", "2 horas antes"]
            )
            notas = st.text_area("📌 Notas o detalles importantes:")

        if st.button("💖 Guardar en la Agenda"):
            if titulo:
                emoji = CATEGORIAS[categoria]["emoji"]
                nuevo_evento = {
                    "usuario": st.session_state["usuario_actual"],
                    "titulo": f"{emoji} {titulo}",
                    "categoria": categoria,
                    "fecha": str(fecha),
                    "hora": str(hora),
                    "alertas": alertas,
                    "notas": notas
                }
                datos["eventos"].append(nuevo_evento)
                guardar_datos(datos)
                st.success(f"¡Agendado exitosamente! {emoji} {titulo}")
                st.rerun()
            else:
                st.warning("Escribí un título para guardar.")

    st.markdown("---")
    st.subheader("📋 Mis compromisos registrados")

    eventos_propios = [e for e in datos["eventos"] if e.get("usuario") == st.session_state["usuario_actual"]]

    if eventos_propios:
        for ev in reversed(eventos_propios):
            info_cat = CATEGORIAS.get(ev["categoria"], {"color": "#f1f5f9", "borde": "#a855f7"})
            bg_color = info_cat["color"]
            border_color = info_cat["borde"]
            
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 16px; border-radius: 14px; border-left: 8px solid {border_color}; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <h3 style="margin: 0; color: #1e293b; font-size: 1.2rem;">{ev['titulo']}</h3>
                <p style="margin: 6px 0; color: #475569;">📅 <b>Fecha:</b> {ev['fecha']} | ⏰ <b>Hora:</b> {ev['hora']}</p>
                <p style="margin: 4px 0; color: #475569;">🔔 <b>Alertas:</b> {', '.join(ev['alertas']) if ev['alertas'] else 'Sin alertas'}</p>
                {f'<p style="margin: 4px 0; color: #475569;">📝 <b>Notas:</b> {ev["notas"]}</p>' if ev['notas'] else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aún no tenés compromisos cargados en tu cuenta.")

# ----------------- ADMIN -----------------
elif opcion == "⚙️ Gestión de Usuarios (Admin)":
    st.title("⚙️ Panel de Administración")
    
    t1, t2, t3, t4 = st.tabs(["➕ Crear Usuario", "🔑 Cambiar Contraseña", "🗑️ Eliminar Usuario", "👀 Ver Agendas"])

    with t1:
        st.subheader("Crear un nuevo usuario")
        nuevo_user = st.text_input("Nombre de usuario:").strip().lower()
        nueva_pass = st.text_input("Contraseña asignada:")
        es_admin = st.checkbox("¿Es Administrador?")
        
        if st.button("Crear Usuario"):
            if nuevo_user and nueva_pass:
                if nuevo_user in datos["usuarios"]:
                    st.error("El nombre de usuario ya existe.")
                else:
                    rol = "admin" if es_admin else "user"
                    datos["usuarios"][nuevo_user] = {"clave": nueva_pass, "rol": rol}
                    guardar_datos(datos)
                    st.success(f"Usuario '{nuevo_user}' creado.")
            else:
                st.warning("Completa usuario y contraseña.")

    with t2:
        st.subheader("Cambiar contraseña")
        user_mod = st.selectbox("Seleccionar usuario:", list(datos["usuarios"].keys()))
        pass_nueva = st.text_input("Nueva contraseña:", key="mod_pass")
        if st.button("Guardar Contraseña"):
            if pass_nueva:
                datos["usuarios"][user_mod]["clave"] = pass_nueva
                guardar_datos(datos)
                st.success(f"Contraseña actualizada para {user_mod}.")

    with t3:
        st.subheader("Eliminar usuario")
        user_del = st.selectbox("Seleccionar usuario a eliminar:", [u for u in datos["usuarios"].keys() if u != "adriana"])
        if st.button("Eliminar"):
            if user_del:
                del datos["usuarios"][user_del]
                datos["eventos"] = [e for e in datos["eventos"] if e.get("usuario") != user_del]
                guardar_datos(datos)
                st.success(f"Usuario '{user_del}' eliminado.")
                st.rerun()

    with t4:
        st.subheader("Supervisar agendas")
        user_ver = st.selectbox("Elegí el usuario:", list(datos["usuarios"].keys()))
        eventos_ver = [e for e in datos["eventos"] if e.get("usuario") == user_ver]
        if eventos_ver:
            for ev in eventos_ver:
                st.write(f"- **{ev['titulo']}** | Fecha: {ev['fecha']} {ev['hora']}")
        else:
            st.info(f"'{user_ver}' no tiene eventos.")