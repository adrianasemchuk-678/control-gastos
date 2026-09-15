# 🧮 Mis Cuentas Fáciles - Control de Gastos & Alcancía de Ahorro 🌸

Aplicación web interactiva desarrollada en **Python** con **Streamlit** para el control de gastos mensuales, presupuesto y recordatorios de pagos fijos (como alquiler, luz, internet).

Diseñada especialmente para ser **ultra intuitiva, clara y fácil de usar** para cualquier persona o niño, con una estética en tonos pasteles y rosados.

---

## ✨ Características Principales

- 🧮 **Pantalla de bienvenida:** Saludo de Adriana y acceso protegido mediante código numérico de 4 dígitos (`5861`).
- 💵 **Paso 1 - Tu dinero:** Ingreso y guardado del sueldo mensual o plata disponible.
- 📊 **Paso 2 - Resumen visual:** 3 tarjetas gigantes con tu dinero inicial, lo que gastaste y la plata que te queda en el bolsillo.
- 🔔 **Paso 3 - Pagos fijos y vencimientos:** Alertas automáticas para pagos fijos del mes (ej: alquiler del 1 al 10). Avisa si están por vencer o vencidos, y permite marcarlos como pagados con 1 clic.
- ➕ **Paso 4 - Gastos diarios con 1 toque:** Botones rápidos para supermercado, farmacia, salidas, transporte, con asignación automática de íconos.
- 🍩 **Paso 5 - Gráficos coloridos:** Gráfico de torta pastel que muestra en qué se fue la plata de forma visual.
- 📋 **Paso 6 - Lista de gastos:** Historial completo con opción de descargar a Excel (CSV) o borrar gastos fácilmente si hubo un error.
- ☁️ **Persistencia en la nube:** Conexión nativa con Supabase (PostgreSQL) y respaldo local en SQLite.

---

## 🚀 Despliegue en Streamlit Community Cloud

1. Sube este repositorio a tu cuenta de **GitHub**.
2. Ingresa a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de GitHub.
3. Haz clic en **"New app"**.
4. Selecciona este repositorio, la rama `main` y en *Main file path* coloca: `app.py`.
5. *(Opcional)* Si usas **Supabase**, ve a *Advanced settings -> Secrets* y añade:
   ```toml
   SUPABASE_URL = "https://tu-proyecto.supabase.co"
   SUPABASE_KEY = "tu-clave-anon-o-service-role"
   ```
6. Haz clic en **"Deploy!"** y ¡listo! Tu aplicación estará funcionando en internet con su propio link público.

---

## 💻 Ejecución Local

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicia la aplicación:
   ```bash
   streamlit run app.py
   ```
   O haz doble clic en `run.bat` en Windows.
