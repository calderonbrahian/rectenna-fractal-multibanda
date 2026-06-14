"""
Rectenna Fractal Multibanda — Demostración interactiva de la tesis
=================================================================
Punto de entrada Streamlit. La navegación sigue la secuencia narrativa del
informe de grado: el lector recorre la tesis de principio a fin, no un
conjunto de simulaciones independientes.

La calculadora-sandbox y la página de preparación de defensa se retiraron de
la aplicación (quedan archivadas en _archivado_pages/) por no formar parte
del informe. Cada página conservada corresponde a una sección del documento.

Ejecución local:
    .venv/Scripts/streamlit run app.py

Autor: Brahian Calderón Múnera · UdeA · 2026
"""

import streamlit as st

st.set_page_config(
    page_title="Rectenna Multibanda · UdeA",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navegación en secuencia narrativa, alineada con la estructura del informe.
page = st.navigation(
    {
        "1 · Resultado de referencia": [
            st.Page("pages/inicio.py",
                    title="Energía capturada — resultado oficial",
                    icon=":material/verified:"),
        ],
        "2 · Topologías evaluadas": [
            st.Page("pages/escenario_a.py",
                    title="Escenario A — Sierpinski (multibanda)",
                    icon=":material/cell_tower:"),
            st.Page("pages/escenario_b.py",
                    title="Escenario B — FLPDA Koch (UHF)",
                    icon=":material/radio:"),
        ],
        "3 · Aplicación del nodo IoT": [
            st.Page("pages/viabilidad_iot.py",
                    title="¿Qué se puede hacer con esa energía?",
                    icon=":material/sensors:"),
        ],
        "4 · Validación y análisis de error": [
            st.Page("pages/validacion.py",
                    title="Validación con literatura (Wang 2022)",
                    icon=":material/biotech:"),
            st.Page("pages/analisis_avanzado.py",
                    title="Análisis de incertidumbre",
                    icon=":material/analytics:"),
            st.Page("pages/sensibilidad.py",
                    title="Sensibilidad paramétrica",
                    icon=":material/tune:"),
        ],
        "5 · Información del proyecto": [
            st.Page("pages/acerca.py",
                    title="Metodología y referencias",
                    icon=":material/info:"),
        ],
    },
    position="sidebar",
)
page.run()
