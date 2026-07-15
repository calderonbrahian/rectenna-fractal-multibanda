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
        "① La historia · ¿qué problema y por qué?": [
            st.Page("pages/demo_1_problema.py",
                    title="El problema y la pregunta",
                    icon=":material/battery_alert:", default=True),
            st.Page("pages/demo_2_metodo.py",
                    title="Cómo se abordó",
                    icon=":material/schema:"),
        ],
        "② Los resultados · ¿qué se obtuvo?": [
            st.Page("pages/demo_3_resultados.py",
                    title="Qué se obtuvo (en breve)",
                    icon=":material/lightbulb:"),
            st.Page("pages/inicio.py",
                    title="Resultado de referencia",
                    icon=":material/verified:"),
        ],
        "③ El modelo · ¿cómo funciona?": [
            st.Page("pages/escenario_a.py",
                    title="Escenario A — Sierpinski",
                    icon=":material/cell_tower:"),
            st.Page("pages/escenario_b.py",
                    title="Escenario B — FLPDA Koch",
                    icon=":material/radio:"),
            st.Page("pages/comparacion.py",
                    title="¿Por qué la FLPDA? (comparación)",
                    icon=":material/compare:"),
            st.Page("pages/viabilidad_iot.py",
                    title="¿Alcanza para un nodo IoT?",
                    icon=":material/sensors:"),
        ],
        "④ La matemática · ecuaciones, constantes y código": [
            st.Page("pages/detras_del_modelo.py",
                    title="Detrás del modelo",
                    icon=":material/function:"),
        ],
        "⑤ ¿Es creíble? · validación e incertidumbre": [
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
        "⑥ Cierre · conclusiones y referencias": [
            st.Page("pages/conclusiones.py",
                    title="Conclusiones y limitaciones",
                    icon=":material/flag:"),
            st.Page("pages/demo_4_aporte.py",
                    title="El estudio y su alcance",
                    icon=":material/straighten:"),
            st.Page("pages/acerca.py",
                    title="Metodología y referencias",
                    icon=":material/info:"),
        ],
    },
    position="sidebar",
)
page.run()
