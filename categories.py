"""
Módulo de categorías e íconos para el Control de Gastos Mensuales.
Optimizado para ser súper intuitivo, práctico y cercano para jóvenes y adolescentes.
"""

import re

CATEGORIES = {
    "🎬 Ocio / Salidas & Juegos": {
        "icon": "🎬",
        "color": "#F472B6",  # Pastel rosa chicle vibrante
        "keywords": [
            "salida", "juego", "steam", "robux", "fortnite", "valorant", "minecraft",
            "playstation", "ps plus", "xbox", "game pass", "nintendo", "skin", "pase",
            "cine", "recital", "concierto", "fiesta", "boliche", "cumple", "starbucks",
            "cafe", "merienda", "mcdonalds", "mostaza", "burger", "helado", "netflix",
            "spotify", "disney", "twitch", "youtube"
        ]
    },
    "🛒 Snacks, Kiosco & Comida": {
        "icon": "🛒",
        "color": "#86EFAC",  # Pastel verde menta fresco
        "keywords": [
            "kiosco", "alfajor", "galletitas", "golosina", "chicle", "lays", "doritos",
            "papas", "gaseosa", "coca", "pepsi", "agua", "almuerzo", "cena", "delivery",
            "pedidosya", "rappi", "empanadas", "pizza", "panaderia", "super", "supermercado",
            "coto", "dia", "carrefour"
        ]
    },
    "🚌 Transporte / SUBE": {
        "icon": "🚌",
        "color": "#FDA4AF",  # Pastel coral rosado
        "keywords": [
            "sube", "colectivo", "bondi", "tren", "subte", "pasaje", "uber", "cabify",
            "didi", "taxi", "remis", "bici", "combustible", "nafta", "gasoil"
        ]
    },
    "👕 Ropa & Zapatillas": {
        "icon": "👕",
        "color": "#C084FC",  # Pastel lila / lavanda
        "keywords": [
            "ropa", "zapas", "zapatillas", "remera", "buzo", "pantalon", "campera",
            "gorra", "medias", "mochila", "shein", "zara", "nike", "adidas", "puma",
            "tienda", "shopping"
        ]
    },
    "📱 Celular & Conectividad": {
        "icon": "📱",
        "color": "#FDE047",  # Pastel amarillo manteca cálido
        "keywords": [
            "recarga", "gigas", "datos", "personal", "claro", "movistar", "tuenti",
            "celular", "internet", "wifi", "cable", "luz", "electricidad"
        ]
    },
    "🎓 Colegio, Cursos & Libros": {
        "icon": "🎓",
        "color": "#A5B4FC",  # Pastel índigo suave
        "keywords": [
            "colegio", "escuela", "facu", "fotocopia", "fotocopias", "cuaderno",
            "libreria", "lapicera", "cartuchera", "libro", "curso", "ingles",
            "utiles", "impresion", "apuntes"
        ]
    },
    "💊 Salud, Cuidado & Farmacia": {
        "icon": "💊",
        "color": "#6EE7B7",  # Pastel aguamarina
        "keywords": [
            "farmacia", "farmacity", "remedio", "medicamento", "medico", "dentista",
            "crema", "shampoo", "cuidado personal", "skincare", "barberia", "peluqueria",
            "corte de pelo", "maquillaje"
        ]
    },
    "🐾 Mascotas": {
        "icon": "🐾",
        "color": "#FDBA74",  # Pastel melocotón
        "keywords": [
            "mascota", "perro", "gato", "veterinaria", "alimento", "snack perro",
            "pet shop", "juguete mascota"
        ]
    },
    "🏠 Alquiler & Hogar": {
        "icon": "🏠",
        "color": "#93C5FD",  # Pastel azul cielo suave
        "keywords": [
            "alquiler", "expensa", "expensas", "casa", "depto", "mueble"
        ]
    },
    "💳 Deudas / Tarjetas": {
        "icon": "💳",
        "color": "#FB7185",  # Pastel frambuesa
        "keywords": [
            "deuda", "le debo", "devolver", "prestamo", "tarjeta", "cuota"
        ]
    },
    "📦 Otros Gustitos": {
        "icon": "📦",
        "color": "#CBD5E1",  # Pastel gris perla suave
        "keywords": [
            "otros", "varios", "regalo", "gustito", "extra", "imprevisto"
        ]
    }
}

DEFAULT_CATEGORY = "📦 Otros Gustitos"


def get_categories_list():
    """Retorna la lista ordenada de nombres de categorías con sus íconos."""
    return list(CATEGORIES.keys())


def get_category_icon(category_name: str) -> str:
    """Retorna el emoji de la categoría especificada."""
    return CATEGORIES.get(category_name, {}).get("icon", "🌸")


def get_category_color(category_name: str) -> str:
    """Retorna el color hexadecimal pastel asociado a la categoría."""
    return CATEGORIES.get(category_name, {}).get("color", "#F472B6")


def detect_category_from_text(text: str) -> str:
    """
    Analiza la descripción y detecta de manera inteligente la categoría,
    pensado para hábitos y vocabulario habitual de jóvenes.
    """
    if not text or not text.strip():
        return DEFAULT_CATEGORY

    clean_text = text.lower()
    tokens = re.findall(r'\b\w+\b', clean_text)

    for cat_name, info in CATEGORIES.items():
        if cat_name == DEFAULT_CATEGORY:
            continue
        for kw in info["keywords"]:
            if " " in kw:
                if kw in clean_text:
                    return cat_name
            else:
                if kw in tokens or any(kw in token for token in tokens if len(kw) >= 4):
                    return cat_name

    return DEFAULT_CATEGORY
