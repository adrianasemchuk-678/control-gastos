"""
Módulo de base de datos para Control de Gastos Mensuales.
Diseño simple, robusto y directo ("tranqui").
Incluye gestión y modificación de pagos fijos mensuales con ventanas de vencimiento.
Por defecto inicia todo en cero (sin datos precargados).
Soporte dual: Nube Supabase (si está configurada) o SQLite local automático.
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
import supabase_db as sdb

DB_PATH = os.path.join(os.path.dirname(__file__), "gastos.db")
CODIGO_ACCESO_CORRECTO = "5861"


def get_connection():
    """Retorna una conexión a la base de datos SQLite local."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_cloud_active() -> bool:
    """Indica si la aplicación está operando conectada a Supabase en la nube."""
    return sdb.get_supabase_client() is not None


def verificar_codigo_acceso(codigo_ingresado: str) -> bool:
    """Verifica si el código ingresado coincide con el código único 5861."""
    return str(codigo_ingresado).strip() == CODIGO_ACCESO_CORRECTO


def save_supabase_config(url: str, key: str):
    """Guarda las credenciales de Supabase en la configuración."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('supabase_url', ?)", (url.strip(),))
        cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('supabase_key', ?)", (key.strip(),))
        conn.commit()


def remove_supabase_config():
    """Elimina las credenciales de Supabase guardadas localmente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM configuracion WHERE clave IN ('supabase_url', 'supabase_key')")
        conn.commit()


def init_db():
    """Inicializa las tablas de la base de datos local SQLite en cero."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)

        # 2. Gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                categoria TEXT NOT NULL,
                icono TEXT NOT NULL,
                monto REAL NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Pagos Fijos Mensuales (con rango de vencimiento del 1 al 10, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos_fijos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT NOT NULL,
                icono TEXT NOT NULL,
                dia_desde INTEGER NOT NULL DEFAULT 1,
                dia_hasta INTEGER NOT NULL DEFAULT 10,
                activo INTEGER DEFAULT 1,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Historial de Pagos Fijos Pagados (por mes y año)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos_fijos_historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pago_fijo_id INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                anio INTEGER NOT NULL,
                fecha_pago TEXT NOT NULL,
                monto REAL NOT NULL,
                UNIQUE(pago_fijo_id, mes, anio)
            )
        """)

        # Todo arranca en cero por defecto
        cursor.execute("SELECT valor FROM configuracion WHERE clave = 'sueldo_mensual'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO configuracion (clave, valor) VALUES ('sueldo_mensual', '0')")

        cursor.execute("SELECT valor FROM configuracion WHERE clave = 'meta_ahorro_pct'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO configuracion (clave, valor) VALUES ('meta_ahorro_pct', '20')")

        conn.commit()


def reset_all_to_zero():
    """Limpia todos los datos cargados para dejar la aplicación completamente en cero."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE configuracion SET valor = '0' WHERE clave = 'sueldo_mensual'")
        cursor.execute("DELETE FROM gastos")
        cursor.execute("DELETE FROM pagos_fijos")
        cursor.execute("DELETE FROM pagos_fijos_historial")
        conn.commit()


# ----------------- CONFIGURACIÓN (SUELDO & METAS) -----------------

def get_setting(key: str, default: str = "") -> str:
    """Obtiene un valor de configuración."""
    if is_cloud_active():
        val = sdb.sb_get_user_setting(1, key, default)
        if val:
            return val

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (key,))
        row = cursor.fetchone()
        return row["valor"] if row else default


def set_setting(key: str, value: str):
    """Guarda un valor de configuración."""
    if is_cloud_active():
        sdb.sb_set_user_setting(1, key, value)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO configuracion (clave, valor)
            VALUES (?, ?)
            ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor
        """, (key, str(value)))
        conn.commit()


# ----------------- GESTIÓN DE GASTOS -----------------

def add_expense(fecha: str, descripcion: str, categoria: str, icono: str, monto: float) -> int:
    """Registra un nuevo gasto."""
    if is_cloud_active():
        cloud_id = sdb.sb_add_expense(fecha, descripcion, categoria, icono, monto, usuario_id=1)
        if cloud_id:
            return cloud_id

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gastos (fecha, descripcion, categoria, icono, monto)
            VALUES (?, ?, ?, ?, ?)
        """, (fecha, descripcion.strip(), categoria, icono, float(monto)))
        conn.commit()
        return cursor.lastrowid


def get_expenses(mes: Optional[int] = None, anio: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retorna la lista de gastos para el período seleccionado."""
    if is_cloud_active():
        gastos_nube = sdb.sb_get_expenses(usuario_id=1, mes=mes, anio=anio)
        if gastos_nube:
            return gastos_nube

    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, fecha, descripcion, categoria, icono, monto FROM gastos"
        params = []

        if mes is not None and anio is not None:
            prefix = f"{anio:04d}-{mes:02d}%"
            query += " WHERE fecha LIKE ?"
            params.append(prefix)
        elif anio is not None:
            prefix = f"{anio:04d}%"
            query += " WHERE fecha LIKE ?"
            params.append(prefix)

        query += " ORDER BY fecha DESC, id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def delete_expense(expense_id: int) -> bool:
    """Elimina un gasto por su ID."""
    if is_cloud_active():
        sdb.sb_delete_expense(expense_id)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gastos WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_expenses():
    """Elimina todos los gastos registrados."""
    if is_cloud_active():
        sdb.sb_clear_user_expenses(usuario_id=1)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gastos")
        conn.commit()


# ----------------- PAGOS FIJOS MENSUALES Y VENCIMIENTOS -----------------

def get_pagos_fijos() -> List[Dict[str, Any]]:
    """Retorna todos los pagos fijos registrados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, monto, categoria, icono, dia_desde, dia_hasta, activo FROM pagos_fijos WHERE activo = 1 ORDER BY dia_hasta ASC")
        return [dict(r) for r in cursor.fetchall()]


def get_pago_fijo_by_id(pago_fijo_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene los datos de un pago fijo específico por su ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, monto, categoria, icono, dia_desde, dia_hasta FROM pagos_fijos WHERE id = ?", (int(pago_fijo_id),))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_pago_fijo(nombre: str, monto: float, categoria: str, icono: str, dia_desde: int, dia_hasta: int) -> int:
    """Crea un nuevo pago fijo recurrente mensual."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pagos_fijos (nombre, monto, categoria, icono, dia_desde, dia_hasta)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre.strip(), float(monto), categoria, icono, int(dia_desde), int(dia_hasta)))
        conn.commit()
        return cursor.lastrowid


def update_pago_fijo(pago_fijo_id: int, nombre: str, monto: float, categoria: str, icono: str, dia_desde: int, dia_hasta: int) -> bool:
    """Modifica los datos de un pago fijo ya existente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pagos_fijos 
            SET nombre = ?, monto = ?, categoria = ?, icono = ?, dia_desde = ?, dia_hasta = ?
            WHERE id = ?
        """, (nombre.strip(), float(monto), categoria, icono, int(dia_desde), int(dia_hasta), int(pago_fijo_id)))
        conn.commit()
        return cursor.rowcount > 0


def delete_pago_fijo(pago_fijo_id: int) -> bool:
    """Elimina un pago fijo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pagos_fijos WHERE id = ?", (int(pago_fijo_id),))
        cursor.execute("DELETE FROM pagos_fijos_historial WHERE pago_fijo_id = ?", (int(pago_fijo_id),))
        conn.commit()
        return cursor.rowcount > 0


def get_estado_pagos_fijos(mes: int, anio: int) -> List[Dict[str, Any]]:
    """Calcula para cada pago fijo su estado en el mes dado."""
    pagos = get_pagos_fijos()
    hoy = date.today()
    dia_actual = hoy.day if (hoy.month == mes and hoy.year == anio) else 15

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pago_fijo_id, fecha_pago, monto FROM pagos_fijos_historial WHERE mes = ? AND anio = ?", (mes, anio))
        historial_mes = {row["pago_fijo_id"]: dict(row) for row in cursor.fetchall()}

    resultado = []
    for p in pagos:
        p_id = p["id"]
        dia_desde = p["dia_desde"]
        dia_hasta = p["dia_hasta"]
        
        item = dict(p)
        if p_id in historial_mes:
            item["pagado"] = True
            item["estado"] = "pagado"
            item["fecha_pago"] = historial_mes[p_id]["fecha_pago"]
        else:
            item["pagado"] = False
            item["fecha_pago"] = None
            if dia_actual > dia_hasta:
                item["estado"] = "vencido"
            elif dia_desde <= dia_actual <= dia_hasta:
                item["estado"] = "por_vencer"
            else:
                item["estado"] = "proximo"

        resultado.append(item)

    return resultado


def marcar_pago_fijo_como_pagado(pago_fijo_id: int, mes: int, anio: int, fecha_pago: Optional[str] = None):
    """
    Registra el pago fijo como pagado para el mes actual y lo añade automáticamente
    a la lista de gastos del mes para que reste de la plata disponible.
    """
    if not fecha_pago:
        fecha_pago = date.today().strftime("%Y-%m-%d")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pagos_fijos WHERE id = ?", (int(pago_fijo_id),))
        pago = cursor.fetchone()
        if not pago:
            return

        pago_dict = dict(pago)

        cursor.execute("""
            INSERT OR REPLACE INTO pagos_fijos_historial (pago_fijo_id, mes, anio, fecha_pago, monto)
            VALUES (?, ?, ?, ?, ?)
        """, (int(pago_fijo_id), int(mes), int(anio), fecha_pago, pago_dict["monto"]))
        conn.commit()

    desc = f"Pago fijo: {pago_dict['nombre']}"
    add_expense(
        fecha=fecha_pago,
        descripcion=desc,
        categoria=pago_dict["categoria"],
        icono=pago_dict["icono"],
        monto=pago_dict["monto"]
    )


def migrate_local_to_cloud() -> Tuple[bool, str]:
    """Copia los gastos locales a Supabase."""
    client = sdb.get_supabase_client()
    if not client:
        return False, "Supabase no está conectado."

    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT fecha, descripcion, categoria, icono, monto FROM gastos")
            gastos_locales = [dict(r) for r in cur.fetchall()]
            for g in gastos_locales:
                g["usuario_id"] = 1
            if gastos_locales:
                client.table("gastos").insert(gastos_locales).execute()

        return True, f"Migración lista: {len(gastos_locales)} gastos subidos a la nube."
    except Exception as e:
        return False, f"Error durante la migración: {e}"
