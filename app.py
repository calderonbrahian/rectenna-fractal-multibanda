"""
Rectenna Fractal Multibanda — Dashboard Interactivo (revisión 2026-05-28)
=========================================================================
Punto de entrada Streamlit. Navegación organizada por la pregunta que
responde cada página, no por la herramienta técnica que la implementa.

Estructura:
    Tesis            — Resultados oficiales (read-only, protegidos por test)
    Aplicación IoT   — Viabilidad operativa del nodo
    Diagnóstico      — Diagnóstico paramétrico por escenario
    Exploración      — Sandbox con sliders + análisis de incertidumbre
    Validación       — Cruce con literatura + comparación con Carrel
    Defensa          — Preguntas pre-respondidas del jurado + L1–L8 + What-if
    Info             — Acerca / referencias

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

page = st.navigation(
    {
        "Resultados de Referencia del Proyecto": [
            st.Page("pages/inicio.py",
                    title="Resultados oficiales",
                    icon=":material/verified:"),
        ],
        "Aplicación del nodo IoT": [
            st.Page("pages/viabilidad_iot.py",
                    title="Viabilidad energética IoT",
                    icon=":material/cell_tower:"),
        ],
        "Diagnóstico del modelo": [
            st.Page("pages/escenario_b.py",
                    title="Escenario B — FLPDA Koch (cuantitativo)",
                    icon=":material/radio:"),
            st.Page("pages/escenario_a.py",
                    title="Escenario A — Sierpinski (multibanda)",
                    icon=":material/cell_tower:"),
        ],
        "Exploración paramétrica": [
            st.Page("pages/calculadora.py",
                    title="Calculadora del modelo",
                    icon=":material/calculate:"),
            st.Page("pages/analisis_avanzado.py",
                    title="Análisis avanzado",
                    icon=":material/analytics:"),
            st.Page("pages/sensibilidad.py",
                    title="Sensibilidad paramétrica",
                    icon=":material/tune:"),
        ],
        "Validación con literatura": [
            st.Page("pages/validacion.py",
                    title="Validación cruzada",
                    icon=":material/biotech:"),
        ],
        "Preparación para defensa": [
            st.Page("pages/jurado.py",
                    title="Pregunta del jurado",
                    icon=":material/quiz:"),
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
