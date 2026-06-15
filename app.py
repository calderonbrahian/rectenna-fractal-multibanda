"""
Rectenna Fractal Multibanda — Demostración interactiva del proyecto de grado
============================================================================
Punto de entrada Streamlit. La navegación está pensada como **experiencia de
usuario**, no como índice del documento: 7 secciones principales (más una de
referencia). La aplicación abre en el **Resultado de referencia**, que responde
de inmediato qué logró el proyecto (quién lo hizo, qué se diseñó, qué resultado
se obtuvo y si es útil); las secciones siguientes permiten profundizar en el
recorrido narrativo del informe. Cada página indica, mediante el bloque "Dónde
se desarrolla en el proyecto", a qué sección del documento corresponde.

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

# 7 secciones principales + 1 de referencia. La app abre en el Resultado de
# referencia (primera página) para responder primero "¿qué logró el proyecto?".
page = st.navigation(
    {
        "Resultado del proyecto": [
            st.Page("pages/inicio.py",
                    title="Resultado de referencia",
                    icon=":material/verified:"),
        ],
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
