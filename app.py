"""
Rectenna Fractal Multibanda — Demostración interactiva del proyecto de grado
============================================================================
Punto de entrada Streamlit. La experiencia tiene DOS NIVELES claramente
diferenciados:

  NIVEL 1 · DEMOSTRACIÓN (3 min) — para quien nunca vio el proyecto. Explica en
  pocos minutos el problema, la pregunta, la metodología del estudio, qué se
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

# ── Navegación narrativa en capas ─────────────────────────────────────────────
# Un solo recorrido guiado, no dos silos. Cada sección responde una pregunta y
# lleva a la siguiente: historia → resultados → modelo → matemática → validación
# → cierre. Quien quiera profundizar encuentra toda la matemática en «④».
page = st.navigation(
    {
        "1 · Historia": [
            st.Page("pages/demo_1_problema.py", title="El problema",
                    icon=":material/battery_alert:", default=True),
            st.Page("pages/demo_2_metodo.py", title="Cómo se abordó",
                    icon=":material/schema:"),
        ],
        "2 · Resultados": [
            st.Page("pages/demo_3_resultados.py", title="Qué se obtuvo",
                    icon=":material/lightbulb:"),
            st.Page("pages/inicio.py", title="Resultado de referencia",
                    icon=":material/verified:"),
        ],
        "3 · El modelo": [
            st.Page("pages/escenario_a.py", title="Escenario A · Sierpinski",
                    icon=":material/cell_tower:"),
            st.Page("pages/escenario_b.py", title="Escenario B · FLPDA Koch",
                    icon=":material/radio:"),
            st.Page("pages/comparacion.py", title="Comparación",
                    icon=":material/compare:"),
            st.Page("pages/viabilidad_iot.py", title="Viabilidad IoT",
                    icon=":material/sensors:"),
        ],
        "4 · La matemática": [
            st.Page("pages/detras_del_modelo.py", title="Detrás del modelo",
                    icon=":material/function:"),
        ],
        "5 · Validación": [
            st.Page("pages/validacion.py", title="Validación (Wang)",
                    icon=":material/biotech:"),
            st.Page("pages/analisis_avanzado.py", title="Incertidumbre (MC)",
                    icon=":material/analytics:"),
            st.Page("pages/sensibilidad.py", title="Sensibilidad",
                    icon=":material/tune:"),
        ],
        "6 · Cierre": [
            st.Page("pages/conclusiones.py", title="Conclusiones",
                    icon=":material/flag:"),
            st.Page("pages/demo_4_aporte.py", title="Alcance del estudio",
                    icon=":material/straighten:"),
            st.Page("pages/acerca.py", title="Metodología y refs.",
                    icon=":material/info:"),
        ],
    },
    position="sidebar",
)
page.run()
