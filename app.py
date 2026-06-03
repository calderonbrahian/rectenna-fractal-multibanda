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
                       (oculta en deploy público — solo local)
    Info             — Acerca / referencias

Ejecución local (muestra todas las páginas):
    .venv/Scripts/streamlit run app.py

Ejecución en deploy público (oculta 'Preparación para defensa'):
    set RFEH_PUBLIC_DEPLOY=true  &&  streamlit run app.py
    (En Streamlit Cloud: añadir RFEH_PUBLIC_DEPLOY="true" en Secrets.)

Autor: Brahian Calderón Múnera · UdeA · 2026
"""

import os
import streamlit as st

# ── Modo de deploy ───────────────────────────────────────────────────────────
# RFEH_PUBLIC_DEPLOY=true oculta la sección "Preparación para defensa" (jurado).
# Por defecto (no seteada) se muestra todo (modo local / preparación).
# En Streamlit Cloud: configurar como secreto.
def _is_public_deploy() -> bool:
    env = os.environ.get("RFEH_PUBLIC_DEPLOY", "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        val = st.secrets.get("RFEH_PUBLIC_DEPLOY", "")
        if str(val).strip().lower() in ("1", "true", "yes", "on"):
            return True
    except Exception:
        pass
    return False


PUBLIC_DEPLOY = _is_public_deploy()

st.set_page_config(
    page_title="Rectenna Multibanda · UdeA",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)


_nav_sections = {
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
    "Información del proyecto": [
        st.Page("pages/acerca.py",
                title="Metodología y referencias",
                icon=":material/info:"),
    ],
}

# La sección "Preparación para defensa" SOLO se muestra en modo local.
if not PUBLIC_DEPLOY:
    _nav_sections["Preparación para defensa"] = [
        st.Page("pages/jurado.py",
                title="Pregunta del jurado",
                icon=":material/quiz:"),
    ]

page = st.navigation(_nav_sections, position="sidebar")
page.run()
