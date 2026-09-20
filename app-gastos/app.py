import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

# Configuración de la página
st.set_page_config(
    page_title="Control de Gastos AS", page_icon="💰", layout="wide"
)

# Estilos personalizados (Diseño AS)
st.markdown(
    """
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Conexión a Google Sheets usando los secrets de Streamlit
@st.cache_resource
py
def conectar_gsheets():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  # Carga credenciales desde st.secrets
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


try:
  client = conectar_gsheets()
  sheet_id = "1vHTsp8RIJRzgMdPL2bYHIT0skQ_orYyUbCjbPVyHq4"
  spreadsheet = client.open_by_key(sheet_id)
except Exception as e:
  st.error(
      f"Error al conectar con Google Sheets. Verificá tus secrets. Detalle: {e}"
  )
  st.stop()

# Control de Autenticación con la solapa 'usuarios'
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("🔐 Iniciar Sesión - Control de Gastos AS")
  usuario_input = st.text_input("Usuario")
  password_input = st.text_input("Contraseña", type="password")

  if st.button("Ingresar"):
    try:
      ws_usuarios = spreadsheet.worksheet("usuarios")
      usuarios_data = ws_usuarios.get_all_records()
      df_usuarios = pd.DataFrame(usuarios_data)

      # Validar credenciales contra Google Sheets
      usuario_valido = df_usuarios[
          (df_usuarios["usuario"].astype(str) == usuario_input)
          & (df_usuarios["password"].astype(str) == password_input)
      ]

      if not usuario_valido.empty:
        st.session_state.autenticado = True
        st.session_state.usuario = usuario_input
        st.rerun()
      else:
        st.error("Usuario o contraseña incorrectos")
    except Exception as e:
      st.error(f"Error al validar usuarios: {e}")
  st.stop()

# --- A PARTIR DE ACÁ CORRESPONDE A TU APLICACIÓN COMPLETA Y SU DISEÑO ---
st.sidebar.title(f"👋 Hola, {st.session_state.usuario}")
menu = st.sidebar.radio(
    "Menú Principal",
    ["📊 Panel de Control", "➕ Registrar Gasto", "🎯 Alcancía", "📁 Reportes"],
)

# Cargar datos de finanzas
try:
  ws_finanzas = spreadsheet.worksheet("finanzas")
  finanzas_data = ws_finanzas.get_all_records()
  df_finanzas = (
      pd.DataFrame(finanzas_data)
      if finanzas_data
      else pd.DataFrame(
          columns=["Fecha", "Categoría", "Monto", "Descripción", "Tipo"]
      )
  )
except Exception:
  df_finanzas = pd.DataFrame(
      columns=["Fecha", "Categoría", "Monto", "Descripción", "Tipo"]
  )

if menu == "📊 Panel de Control":
  st.title("📊 Panel de Control - Adriana Semchuk (AS)")
  st.markdown("---")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric("Balance Total", "$ 0.00", "0%")
  with col2:
    st.metric("Gastos del Mes", "$ 0.00", "0%")
  with col3:
    st.metric("Ahorros (Alcancía)", "$ 0.00", "0%")

  st.subheader("📝 Últimos Movimientos")
  if not df_finanzas.empty:
    st.dataframe(df_finanzas, use_container_width=True)
  else:
    st.info("No hay movimientos registrados todavía en Google Sheets.")

elif menu == "➕ Registrar Gasto":
  st.title("➕ Registrar Nuevo Movimiento")
  st.markdown("---")

  with st.form("form_gasto"):
    fecha = st.date_input("Fecha")
    tipo = st.selectbox("Tipo", ["Gasto 💸", "Ingreso 💰"])

    # Categorías con Emojis automáticos solicitados
    categoria_opciones = {
        "Médico / Salud 🩺": "Médico",
        "Estética 💅": "Estética",
        "Gimnasio / Deportes 🏋️‍♀️": "Gimnasio",
        "Supermercado 🛒": "Supermercado",
        "Otros 📌": "Otros",
    }
    categoria_sel = st.selectbox("Categoría", list(categoria_opciones.keys()))
    monto = st.number_input("Monto ($)", min_value=0.0, step=100.0)
    descripcion = st.text_input("Descripción / Nota")

    submitted = st.form_submit_button("Guardar en Google Sheets")
    if submitted:
      nuevo_registro = [
          str(fecha),
          categoria_sel,
          monto,
          descripcion,
          tipo,
      ]
      ws_finanzas.append_row(nuevo_registro)
      st.success("¡Movimiento guardado exitosamente en tu Google Drive! 🎉")
      st.rerun()

elif menu == "🎯 Alcancía":
  st.title("🎯 Meta de Ahorro / Alcancía")
  st.markdown("---")
  st.info("Configura tus metas de ahorro y visualiza tu progreso mes a mes.")

elif menu == "📁 Reportes":
  st.title("📁 Reportes y Exportación")
  st.markdown("---")
  st.write("Acá podrás descargar tus reportes en Excel y PDF.")

if st.sidebar.button("Cerrar Sesión"):
  st.session_state.autenticado = False
  st.rerun()