import streamlit as st
import gspread

def conectar_gsheets():
    # Conexión usando los secretos configurados en Streamlit Cloud
    credenciales = dict(st.secrets["gspread"])
    gc = gspread.service_account_from_dict(credenciales)
    sh = gc.open("db_gastos")
    return sh

def obtener_usuarios():
    try:
        sh = conectar_gsheets()
        worksheet = sh.worksheet("usuarios")
        data = worksheet.get_all_records()
        # Extrae la columna 'usuario' de la planilla
        return [str(row.get("usuario")) for row in data if row.get("usuario")]
    except Exception:
        return ["Admin", "Mica"]

def agregar_usuario(nombre, password="123"):
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        return
    sh = conectar_gsheets()
    worksheet = sh.worksheet("usuarios")
    usuarios_actuales = obtener_usuarios()
    if nombre_limpio not in usuarios_actuales:
        worksheet.append_row([nombre_limpio, str(password)])

def obtener_gastos(usuario_filtro=None):
    try:
        sh = conectar_gsheets()
        worksheet = sh.worksheet("finanzas")
        data = worksheet.get_all_records()
        if usuario_filtro and usuario_filtro != "Todos":
            data = [row for row in data if row.get("usuario") == usuario_filtro]
        return data
    except Exception:
        return []

def registrar_gasto(fecha, concepto, monto, categoria, usuario):
    sh = conectar_gsheets()
    worksheet = sh.worksheet("finanzas")
    worksheet.append_row([str(fecha), concepto, float(monto), categoria, usuario])

def obtener_pagos_fijos(usuario_filtro=None):
    return []

def agregar_pago_fijo(concepto, monto, dia_vencimiento, usuario):
    pass

def actualizar_pago_fijo(id_pago, concepto, monto, dia_vencimiento):
    pass

def eliminar_pago_fijo(id_pago):
    pass

def borrar_todos_los_datos():
    pass
import streamlit as st
import gspread

def conectar_gsheets():
    credenciales = dict(st.secrets["gspread"])
    gc = gspread.service_account_from_dict(credenciales)
    sh = gc.open("db_gastos")
    return sh

def obtener_usuarios():
    try:
        sh = conectar_gsheets()
        worksheet = sh.worksheet("usuarios")
        return worksheet.get_all_records()
    except Exception:
        return []

def agregar_usuario(nombre, password="123"):
    nombre_limpio = str(nombre).strip()
    if not nombre_limpio:
        return False
    sh = conectar_gsheets()
    worksheet = sh.worksheet("usuarios")
    registros = worksheet.get_all_records()
    nombres_existentes = [str(r.get("usuario", "")).strip().lower() for r in registros]
    
    if nombre_limpio.lower() not in nombres_existentes:
        worksheet.append_row([nombre_limpio, str(password)])
        return True
    return False

def obtener_gastos(usuario_filtro=None):
    try:
        sh = conectar_gsheets()
        worksheet = sh.worksheet("finanzas")
        data = worksheet.get_all_records()
        if usuario_filtro and usuario_filtro != "Todos":
            data = [row for row in data if str(row.get("usuario", "")).strip().lower() == str(usuario_filtro).strip().lower()]
        return data
    except Exception:
        return []

def registrar_gasto(fecha, concepto, monto, categoria, usuario):
    sh = conectar_gsheets()
    worksheet = sh.worksheet("finanzas")
    worksheet.append_row([str(fecha), concepto, float(monto), categoria, usuario])

def obtener_pagos_fijos(usuario_filtro=None):
    return []

def agregar_pago_fijo(concepto, monto, dia_vencimiento, usuario):
    pass

def actualizar_pago_fijo(id_pago, concepto, monto, dia_vencimiento):
    pass

def eliminar_pago_fijo(id_pago):
    pass

def borrar_todos_los_datos():
    pass