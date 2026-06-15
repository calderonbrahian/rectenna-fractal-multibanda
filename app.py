"""
Rectenna Fractal Multibanda — Demostración interactiva del proyecto de grado
============================================================================
Punto de entrada Streamlit. La navegación sigue el recorrido narrativo del
informe de grado en 11 secciones: el lector recorre el trabajo de principio a
fin (problema → contexto → topologías → metodología → escenarios → comparación
→ resultado → aplicación → validación → conclusiones), no un conjunto de
simulaciones independientes. Cada página corresponde a una sección del informe
e indica, mediante el bloque "Dónde se desarrolla en el proyecto", dónde
profundizar en el documento.

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
        "1 · El problema": [
            st.Page("pages/problema.py",
                    title="La batería como límite del IoT",
                    icon=":material/battery_alert:"),
        ],
        "2 · Contexto": [
            st.Page("pages/contexto.py",
                    title="Qué es una rectena",
                    icon=":material/bolt:"),
        ],
        "3 · Topologías evaluadas": [
            st.Page("pages/topologias.py",
                    title="Sierpinski y FLPDA Koch",
                    icon=":material/category:"),
        ],
        "4 · Metodología": [
            st.Page("pages/metodologia.py",
                    title="Metodología de simulación",
                    icon=":material/build:"),
        ],
        "5–6 · Escenarios evaluados": [
            st.Page("pages/escenario_a.py",
                    title="Escenario A — Sierpinski (multibanda)",
                    icon=":material/cell_tower:"),
            st.Page("pages/escenario_b.py",
                    title="Escenario B — FLPDA Koch (UHF)",
                    icon=":material/radio:"),
        ],
        "7 · Comparación": [
            st.Page("pages/comparacion.py",
                    title="Comparación de los dos escenarios",
                    icon=":material/compare:"),
        ],
        "8 · Energía capturada": [
            st.Page("pages/inicio.py",
                    title="Resultado de referencia del proyecto",
                    icon=":material/verified:"),
        ],
        "9 · Aplicación del nodo IoT": [
            st.Page("pages/viabilidad_iot.py",
                    title="¿Qué se puede hacer con esa energía?",
                    icon=":material/sensors:"),
        ],
        "10 · Validación y análisis de error": [
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
        "11 · Conclusiones": [
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
