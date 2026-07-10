"""
Rectenna Fractal Multibanda — Demostración interactiva del proyecto de grado
============================================================================
Punto de entrada Streamlit. La experiencia tiene DOS NIVELES claramente
diferenciados:

  NIVEL 1 · DEMOSTRACIÓN (3 min) — para quien nunca vio el proyecto. Explica en
  pocos minutos el problema, la pregunta, la metodología (el aporte), qué se
  demostró y por qué el caso colombiano es solo la demostración. Mucho apoyo
  visual, pocas cifras. Usa las figuras del pipeline (`_regen/out/figuras/`).

  NIVEL 2 · LABORATORIO — para quien quiere profundizar: escenarios, simulación,
  sensibilidades, validación, comparación y análisis avanzado.

Toda figura proviene del pipeline (única fuente gráfica del documento, la app y
el póster). Regenerar: `python _regen/generate_artifacts.py`.

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
        # ── NIVEL 1 · Demostración (3 minutos) ────────────────────────────────
        "Demostración · 3 min": [
            st.Page("pages/demo_1_problema.py",
                    title="1 · El problema y la pregunta",
                    icon=":material/battery_alert:", default=True),
            st.Page("pages/demo_2_metodo.py",
                    title="2 · La metodología (el aporte)",
                    icon=":material/schema:"),
            st.Page("pages/demo_3_resultados.py",
                    title="3 · Qué se demostró",
                    icon=":material/verified:"),
            st.Page("pages/demo_4_aporte.py",
                    title="4 · El aporte y su alcance",
                    icon=":material/flag:"),
        ],
        # ── NIVEL 2 · Laboratorio ─────────────────────────────────────────────
        "Laboratorio · Escenarios": [
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
        "Laboratorio · Caso y viabilidad": [
            st.Page("pages/inicio.py",
                    title="Resultado de referencia",
                    icon=":material/verified:"),
            st.Page("pages/viabilidad_iot.py",
                    title="Viabilidad del nodo IoT",
                    icon=":material/sensors:"),
        ],
        "Laboratorio · Validación y análisis": [
            st.Page("pages/validacion.py",
                    title="Validación (Wang 2022)",
                    icon=":material/biotech:"),
            st.Page("pages/analisis_avanzado.py",
                    title="Incertidumbre (Monte Carlo)",
                    icon=":material/analytics:"),
            st.Page("pages/sensibilidad.py",
                    title="Sensibilidad paramétrica",
                    icon=":material/tune:"),
        ],
        "Laboratorio · Cierre y referencia": [
            st.Page("pages/conclusiones.py",
                    title="Conclusiones y limitaciones",
                    icon=":material/flag:"),
            st.Page("pages/acerca.py",
                    title="Metodología y referencias",
                    icon=":material/info:"),
        ],
    },
    position="sidebar",
)
page.run()
