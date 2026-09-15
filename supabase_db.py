"""
Módulo de conexión y operaciones con Supabase (Nube).
Permite persistir usuarios, configuraciones y gastos en PostgreSQL alojado en Supabase.
"""

import os
from typing import Optional, List, Dict, Any, Tuple
import streamlit as st
from supabase import create_client, Client


def get_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Obtiene las credenciales de Supabase desde:
    1. Streamlit secrets (.streamlit/secrets.toml)
    2. Variables de entorno (SUPABASE_URL, SUPABASE_KEY)
    3. Almacenamiento local SQLite
    """
    # 1. Streamlit secrets
    try:
        if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            if url and key and "tu-proyecto" not in url:
                return url.strip(), key.strip()
    except Exception:
        pass

    # 2. Variables de entorno
    env_url = os.environ.get("SUPABASE_URL")
    env_key = os.environ.get("SUPABASE_KEY")
    if env_url and env_key:
        return env_url.strip(), env_key.strip()

    # 3. Almacenamiento en SQLite local
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "gastos.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT clave, valor FROM configuracion WHERE clave IN ('supabase_url', 'supabase_key')")
            rows = dict(cur.fetchall())
            conn.close()
            url = rows.get("supabase_url")
            key = rows.get("supabase_key")
            if url and key and "tu-proyecto" not in url:
                return url.strip(), key.strip()
    except Exception:
        pass

    return None, None


_client_cache: Optional[Client] = None
_client_credentials: Tuple[Optional[str], Optional[str]] = (None, None)


def get_supabase_client() -> Optional[Client]:
    """Retorna una instancia activa del cliente de Supabase si las credenciales están configuradas."""
    global _client_cache, _client_credentials
    url, key = get_supabase_credentials()
    if not url or not key:
        return None

    if _client_cache and _client_credentials == (url, key):
        return _client_cache

    try:
        client = create_client(url, key)
        _client_cache = client
        _client_credentials = (url, key)
        return client
    except Exception as e:
        print(f"Error conectando con Supabase: {e}")
        return None


def test_supabase_connection(url: str, key: str) -> Tuple[bool, str]:
    """Prueba si las credenciales de Supabase son válidas y si las tablas están listas."""
    try:
        client = create_client(url.strip(), key.strip())
        # Intentar consultar la tabla gastos o usuarios
        res = client.table("gastos").select("id").limit(1).execute()
        return True, "¡Conexión exitosa a Supabase! Tablas encontradas y listas para usar."
    except Exception as e:
        err_msg = str(e)
        if "relation" in err_msg and "does not exist" in err_msg:
            return False, (
                "Se conectó con Supabase pero las tablas aún no existen. "
                "Copia y ejecuta el script 'schema_supabase.sql' en el SQL Editor de tu proyecto Supabase."
            )
        return False, f"No se pudo conectar a Supabase: {err_msg}"


# ----------------- OPERACIONES EN LA NUBE CON SUPABASE -----------------

def sb_authenticate_user(email: str, password: str, verify_pwd_fn) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Autentica a un usuario en Supabase."""
    client = get_supabase_client()
    if not client:
        return "CLIENT_ERROR", None

    try:
        res = client.table("usuarios").select("*").ilike("email", email.strip().lower()).execute()
        if not res.data or len(res.data) == 0:
            return "INVALID_CREDENTIALS", None

        user_data = res.data[0]
        if not verify_pwd_fn(password, user_data["password_hash"], user_data["salt"]):
            return "INVALID_CREDENTIALS", None

        if int(user_data.get("activo", 0)) != 1:
            return "INACTIVE", user_data

        return "SUCCESS", user_data
    except Exception as e:
        print(f"Error sb_authenticate_user: {e}")
        return "ERROR", None


def sb_register_user(nombre: str, email: str, pwd_hash: str, salt: str, activo: int = 1, rol: str = "usuario") -> Tuple[bool, str]:
    """Registra un nuevo usuario en Supabase."""
    client = get_supabase_client()
    if not client:
        return False, "Cliente de Supabase no disponible."

    try:
        data = {
            "nombre": nombre.strip(),
            "email": email.strip().lower(),
            "password_hash": pwd_hash,
            "salt": salt,
            "activo": int(activo),
            "rol": rol
        }
        res = client.table("usuarios").insert(data).execute()
        if res.data:
            return True, "Usuario registrado en la nube."
        return False, "No se pudo insertar el usuario."
    except Exception as e:
        err = str(e)
        if "duplicate key" in err or "unique" in err.lower():
            return False, "Ese correo electrónico ya está registrado en Supabase."
        return False, f"Error al registrar usuario: {err}"


def sb_get_all_users() -> List[Dict[str, Any]]:
    """Obtiene todos los usuarios de Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = client.table("usuarios").select("id, nombre, email, activo, rol, creado_en").order("id").execute()
        return res.data or []
    except Exception as e:
        print(f"Error sb_get_all_users: {e}")
        return []


def sb_set_user_active_status(user_id: int, activo: int) -> bool:
    """Actualiza el estado de activación en Supabase."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        res = client.table("usuarios").update({"activo": int(activo)}).eq("id", user_id).execute()
        return bool(res.data)
    except Exception as e:
        print(f"Error sb_set_user_active_status: {e}")
        return False


def sb_get_user_setting(user_id: int, key: str, default: str = "") -> str:
    """Obtiene una configuración de usuario en Supabase."""
    client = get_supabase_client()
    if not client:
        return default
    try:
        full_key = f"user_{user_id}_{key}"
        res = client.table("configuracion").select("valor").eq("clave", full_key).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["valor"]
        # Fallback a global
        res_global = client.table("configuracion").select("valor").eq("clave", key).execute()
        if res_global.data and len(res_global.data) > 0:
            return res_global.data[0]["valor"]
        return default
    except Exception as e:
        print(f"Error sb_get_user_setting: {e}")
        return default


def sb_set_user_setting(user_id: int, key: str, value: str):
    """Guarda una configuración de usuario en Supabase (Upsert)."""
    client = get_supabase_client()
    if not client:
        return
    try:
        full_key = f"user_{user_id}_{key}"
        client.table("configuracion").upsert({"clave": full_key, "valor": str(value)}).execute()
    except Exception as e:
        print(f"Error sb_set_user_setting: {e}")


def sb_add_expense(fecha: str, descripcion: str, categoria: str, icono: str, monto: float, usuario_id: int) -> int:
    """Registra un nuevo gasto en la nube Supabase."""
    client = get_supabase_client()
    if not client:
        return 0
    try:
        data = {
            "usuario_id": int(usuario_id),
            "fecha": fecha,
            "descripcion": descripcion.strip(),
            "categoria": categoria,
            "icono": icono,
            "monto": float(monto)
        }
        res = client.table("gastos").insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["id"]
        return 0
    except Exception as e:
        print(f"Error sb_add_expense: {e}")
        return 0


def sb_get_expenses(usuario_id: int, mes: Optional[int] = None, anio: Optional[int] = None) -> List[Dict[str, Any]]:
    """Obtiene los gastos del usuario desde Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        query = client.table("gastos").select("*").eq("usuario_id", int(usuario_id))
        if mes is not None and anio is not None:
            prefix = f"{anio:04d}-{mes:02d}"
            # Fechas del mes (YYYY-MM-01 a YYYY-MM-31)
            query = query.gte("fecha", f"{prefix}-01").lte("fecha", f"{prefix}-31")
        elif anio is not None:
            query = query.gte("fecha", f"{anio:04d}-01-01").lte("fecha", f"{anio:04d}-12-31")

        res = query.order("fecha", desc=True).order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Error sb_get_expenses: {e}")
        return []


def sb_delete_expense(expense_id: int, usuario_id: Optional[int] = None) -> bool:
    """Elimina un gasto en Supabase."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        query = client.table("gastos").delete().eq("id", expense_id)
        if usuario_id is not None:
            query = query.eq("usuario_id", int(usuario_id))
        res = query.execute()
        return bool(res.data)
    except Exception as e:
        print(f"Error sb_delete_expense: {e}")
        return False


def sb_clear_user_expenses(usuario_id: int) -> bool:
    """Elimina todos los gastos de un usuario en Supabase."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        res = client.table("gastos").delete().eq("usuario_id", int(usuario_id)).execute()
        return True
    except Exception as e:
        print(f"Error sb_clear_user_expenses: {e}")
        return False


def sb_seed_demo_data(usuario_id: int, mes: int, anio: int):
    """Carga gastos de ejemplo en Supabase."""
    client = get_supabase_client()
    if not client:
        return
    demo_items = [
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-02", "descripcion": "Carga tarjeta SUBE para la semana", "categoria": "🚌 Transporte / SUBE", "icono": "🚌", "monto": 4500},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-04", "descripcion": "Merienda con amigos en cafetería", "categoria": "🎬 Ocio / Salidas & Juegos", "icono": "🎬", "monto": 8200},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-06", "descripcion": "Suscripción Spotify mensual", "categoria": "🎬 Ocio / Salidas & Juegos", "icono": "🎬", "monto": 3800},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-08", "descripcion": "Juego en Steam / Pase de batalla", "categoria": "🎬 Ocio / Salidas & Juegos", "icono": "🎬", "monto": 12000},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-10", "descripcion": "Kiosco: golosinas y gaseosa", "categoria": "🛒 Snacks, Kiosco & Comida", "icono": "🛒", "monto": 3200},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-12", "descripcion": "Almuerzo hamburguesa Mostaza", "categoria": "🛒 Snacks, Kiosco & Comida", "icono": "🛒", "monto": 9500},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-15", "descripcion": "Recarga de gigas para el celular", "categoria": "📱 Celular & Conectividad", "icono": "📱", "monto": 6000},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-18", "descripcion": "Remera en tienda de ropa", "categoria": "👕 Ropa & Zapatillas", "icono": "👕", "monto": 22000},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-20", "descripcion": "Cuaderno y marcadores para el colegio", "categoria": "🎓 Colegio, Cursos & Libros", "icono": "🎓", "monto": 7800},
        {"usuario_id": int(usuario_id), "fecha": f"{anio:04d}-{mes:02d}-22", "descripcion": "Alimento y snack para la mascota", "categoria": "🐾 Mascotas", "icono": "🐾", "monto": 8500}
    ]
    try:
        client.table("gastos").insert(demo_items).execute()
    except Exception as e:
        print(f"Error sb_seed_demo_data: {e}")
