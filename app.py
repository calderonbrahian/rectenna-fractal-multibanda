"""
Rectena Fractal Multibanda — herramienta para COMPRENDER el modelo y REPRODUCIR
la investigación.
================================================================================
La aplicación es una extensión del documento de grado, no una plataforma de
simulación. Cuatro páginas, cuatro preguntas:

    1 · ¿Qué problema resuelve?        (la historia y la pregunta de investigación)
    2 · ¿Cómo funciona el modelo?      (la cadena energética explorable)
    3 · ¿Qué descubrió la investigación?  (los hallazgos — página central)
    4 · ¿Cómo reproducirlo?            (código, pruebas, pipeline y mini-demo)

Todo valor mostrado proviene EN VIVO de core/ y configs/, o de los JSON del
pipeline (_regen/out). La app no define números ni figuras propias.

Hilo conductor: A (concentrar en una fuente dominante) vs B (acumular energía
distribuida). Paleta oro/verde del proyecto (SSOT: _regen/estilo.py).

Ejecución local:
    .venv/Scripts/streamlit run app.py

Autor: Brahian Calderón Múnera · UdeA · 2026
"""

import streamlit as st

st.set_page_config(
    page_title="Rectena Multibanda · UdeA",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

page = st.navigation([
    st.Page("pages/1_El_problema.py", title="El problema",
            icon=":material/help:", default=True),
    st.Page("pages/2_El_modelo.py", title="El modelo",
            icon=":material/schema:"),
    st.Page("pages/3_Los_hallazgos.py", title="Los hallazgos",
            icon=":material/lightbulb:"),
    st.Page("pages/4_Reproducir.py", title="Reproducir",
            icon=":material/replay:"),
], position="sidebar")

page.run()
