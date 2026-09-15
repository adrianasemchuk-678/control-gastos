"""
Módulo de base de datos para Control de Gastos Mensuales.
Diseño simple, robusto y directo ("tranqui").
Incluye gestión de pagos fijos mensuales con ventanas de vencimiento (ej: del 1 al 10).
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
