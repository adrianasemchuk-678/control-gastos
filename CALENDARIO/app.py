def generar_link_google_calendar(titulo, fecha_str, hora_str, notas):
    # Formato de fecha local sin forzar UTC (Z) para que respete tu zona horaria de Argentina
    try:
        partes_hora = hora_str.split(":")
        h, m = partes_hora[0].zfill(2), partes_hora[1].zfill(2)
    except:
        h, m = "09", "00"
    
    f_limpia = fecha_str.replace("-", "")
    
    # Horario de inicio y fin (1 hora de duración)
    inicio = f"{f_limpia}T{h}{m}00"
    
    # Calcular fin (+1 hora)
    h_fin = str((int(h) + 1) % 24).zfill(2)
    fin = f"{f_limpia}T{h_fin}{m}00"
    
    params = {
        "action": "TEMPLATE",
        "text": titulo,
        "dates": f"{inicio}/{fin}",
        "details": notas,
        "ctz": "America/Argentina/Buenos_Aires"
    }
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"