import os
import sqlite3

# Intentar importar Supabase si está configurado
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except ImportError:
    supabase = None

DB_NAME = "gastos.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    
    # Crear tabla Gastos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            usuario TEXT NOT NULL
        )
    """)

    # Crear tabla Pagos Fijos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos_fijos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            dia_vencimiento INTEGER NOT NULL,
            usuario TEXT NOT NULL
        )
    """)
    
    # Insertar usuarios base si está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO usuarios (nombre) VALUES (?)", [("Adriana",), ("Diego",)])
        
    conn.commit()
    conn.close()

# --- USUARIOS ---

def obtener_usuarios():
    init_db()  # Asegura que las tablas existan antes de consultar
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios ORDER BY nombre ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["nombre"] for row in rows]

def agregar_usuario(nombre):
    init_db()
    nombre_limpio = nombre.strip().capitalize()
    if not nombre_limpio:
        return
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre_limpio,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# --- GASTOS ---

def obtener_gastos(usuario_filtro=None):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    if usuario_filtro and usuario_filtro != "Todos":
        cursor.execute("SELECT * FROM gastos WHERE usuario = ? ORDER BY fecha DESC", (usuario_filtro,))
    else:
        cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def registrar_gasto(fecha, concepto, monto, categoria, usuario):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gastos (fecha, concepto, monto, categoria, usuario) VALUES (?, ?, ?, ?, ?)",
        (str(fecha), concepto, float(monto), categoria, usuario)
    )
    conn.commit()
    conn.close()

# --- PAGOS FIJOS ---

def obtener_pagos_fijos(usuario_filtro=None):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    if usuario_filtro and usuario_filtro != "Todos":
        cursor.execute("SELECT * FROM pagos_fijos WHERE usuario = ? ORDER BY dia_vencimiento ASC", (usuario_filtro,))
    else:
        cursor.execute("SELECT * FROM pagos_fijos ORDER BY dia_vencimiento ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def agregar_pago_fijo(concepto, monto, dia_vencimiento, usuario):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pagos_fijos (concepto, monto, dia_vencimiento, usuario) VALUES (?, ?, ?, ?)",
        (concepto, float(monto), int(dia_vencimiento), usuario)
    )
    conn.commit()
    conn.close()

def actualizar_pago_fijo(id_pago, concepto, monto, dia_vencimiento):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pagos_fijos SET concepto = ?, monto = ?, dia_vencimiento = ? WHERE id = ?",
        (concepto, float(monto), int(dia_vencimiento), id_pago)
    )
    conn.commit()
    conn.close()

def eliminar_pago_fijo(id_pago):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pagos_fijos WHERE id = ?", (id_pago,))
    conn.commit()
    conn.close()

# --- ADMINISTRACIÓN ---

def borrar_todos_los_datos():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos")
    cursor.execute("DELETE FROM pagos_fijos")
    conn.commit()
    conn.close()

# Forzar inicialización al importar
init_db()