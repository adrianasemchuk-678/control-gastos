import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
import supabase_db as sdb

DB_PATH = os.path.join(os.path.dirname(__file__), "gastos.db")
CODIGO_ACCESO_CORRECTO = "5861"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if sdb.is_supabase_enabled():
        sdb.init_supabase_db()
        return

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT UNIQUE,
            monto REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            categoria TEXT,
            monto REAL,
            descripcion TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fijos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT,
            monto REAL,
            dia_vencimiento INTEGER,
            pagado INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def guardar_presupuesto(mes: str, monto: float):
    if sdb.is_supabase_enabled():
        return sdb.guardar_presupuesto(mes, monto)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO presupuestos (mes, monto) VALUES (?, ?)
        ON CONFLICT(mes) DO UPDATE SET monto=excluded.monto
    ''', (mes, monto))
    conn.commit()
    conn.close()

def obtener_presupuesto(mes: str) -> float:
    if sdb.is_supabase_enabled():
        return sdb.obtener_presupuesto(mes)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT monto FROM presupuestos WHERE mes = ?', (mes,))
    row = cursor.fetchone()
    conn.close()
    return row['monto'] if row else 0.0

def agregar_gasto(fecha: str, categoria: str, monto: float, descripcion: str):
    if sdb.is_supabase_enabled():
        return sdb.agregar_gasto(fecha, categoria, monto, descripcion)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gastos (fecha, categoria, monto, descripcion)
        VALUES (?, ?, ?, ?)
    ''', (fecha, categoria, monto, descripcion))
    conn.commit()
    conn.close()

def obtener_gastos_mes(mes: str) -> List[Dict[str, Any]]:
    if sdb.is_supabase_enabled():
        return sdb.obtener_gastos_mes(mes)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gastos WHERE fecha LIKE ? ORDER BY fecha DESC', (f'{mes}%',))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def eliminar_gasto(gasto_id: int):
    if sdb.is_supabase_enabled():
        return sdb.eliminar_gasto(gasto_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
    conn.commit()
    conn.close()

def obtener_fijos() -> List[Dict[str, Any]]:
    if sdb.is_supabase_enabled():
        return sdb.obtener_fijos()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fijos ORDER BY dia_vencimiento ASC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def agregar_fijo(concepto: str, monto: float, dia_vencimiento: int):
    if sdb.is_supabase_enabled():
        return sdb.agregar_fijo(concepto, monto, dia_vencimiento)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fijos (concepto, monto, dia_vencimiento)
        VALUES (?, ?, ?)
    ''', (concepto, monto, dia_vencimiento))
    conn.commit()
    conn.close()

def cambiar_estado_fijo(fijo_id: int, pagado: bool):
    if sdb.is_supabase_enabled():
        return sdb.cambiar_estado_fijo(fijo_id, pagado)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE fijos SET pagado = ? WHERE id = ?', (1 if pagado else 0, fijo_id))
    conn.commit()
    conn.close()

def eliminar_fijo(fijo_id: int):
    if sdb.is_supabase_enabled():
        return sdb.eliminar_fijo(fijo_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM fijos WHERE id = ?', (fijo_id,))
    conn.commit()
    conn.close()