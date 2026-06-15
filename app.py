"""
Rectenna Fractal Multibanda — Demostración interactiva del proyecto de grado
============================================================================
Punto de entrada Streamlit. La navegación está pensada como **experiencia de
usuario** y sigue el principio "primero explicar, luego justificar, finalmente
mostrar resultados": 7 secciones principales (más una de referencia) en orden
narrativo — Introducción → Diseño y metodología → Escenarios estudiados →
Resultados → Aplicación al nodo IoT → Validación → Conclusiones. La aplicación
abre en la Introducción (el problema y la identidad del trabajo). Cada página
indica, con el bloque "Dónde se desarrolla en el proyecto", a qué sección del
documento corresponde.

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

# 7 secciones principales + 1 de referencia, en orden narrativo. La app abre en
# la Introducción: primero el problema, luego la solución, después los resultados.
page = st.navigation(
    {
        "Introducción": [
            st.Page("pages/problema.py",
                    title="El problema del IoT",
                    icon=":material/battery_alert:"),
            st.Page("pages/contexto.py",
                    title="Qué es una rectena",
                    icon=":material/bolt:"),
        ],
        "Diseño y metodología": [
            st.Page("pages/topologias.py",
                    title="Topologías evaluadas",
                    icon=":material/category:"),
            st.Page("pages/metodologia.py",
                    title="Metodología de simulación",
                    icon=":material/build:"),
        ],
        "Escenarios estudiados": [
            st.Page("pages/escenario_a.py",
                    title="Escenario A — Sierpinski",
                    icon=":material/cell_tower:"),
            st.Page("pages/escenario_b.py",
                    title="Escenario B — FLPDA Koch",
                    icon=":material/radio:"),
            st.Page("pages/comparacion.py",
                    title="Comparación de escenarios",
                    icon=":material/compare:"),
        ],
        "Resultados del proyecto": [
            st.Page("pages/inicio.py",
                    title="Resultado de referencia",
                    icon=":material/verified:"),
        ],
        "Aplicación al nodo IoT": [
            st.Page("pages/viabilidad_iot.py",
                    title="¿Qué se puede hacer con esa energía?",
                    icon=":material/sensors:"),
        ],
        "Validación del modelo": [
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
        "Conclusiones": [
            st.Page("pages/conclusiones.py",
                    title="Conclusiones y limitaciones",
                    icon=":material/flag:"),
        ],
        "Información del proyecto": [
            st.Page("pages/acerca.py",
                    title="Metodología y referencias",
                    icon=":material/info:"),
        ],
    },
    position="sidebar",
)
page.run()
