"""
PÁGINA 4 · ¿Cómo reproducir la investigación?
================================================================================
La app como extensión del documento y del código. Repositorio, estructura,
pruebas automatizadas, pipeline de figuras y una mini-demo de 2-3 sliders que
recalculan la cadena completa EN VIVO (`core.lora_budget.harvested_uw_full`),
mostrando que el modelo responde. Cierre del recorrido.
"""

import streamlit as st

from configs.parametros import (
    CANONICAL, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.lora_budget import harvested_uw_full
from utils.ui import css, cabecera, dato, A_ORO, B_VERDE, TEAL, INK, MUTE

css()

REPO = "https://github.com/calderonbrahian/rectenna-fractal-multibanda"

cabecera(
    kicker="Reproducir",
    pregunta="¿Cómo comprobar que esto es cierto?",
    bajada="El modelo es la fuente de verdad: código abierto, pruebas automáticas y "
           "un pipeline que regenera cada figura y cada cifra del documento.",
)

# ── Repositorio y estructura ──────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    dato("101", "pruebas automatizadas (física + regresión)", "b")
with c2:
    dato("SSOT", "un solo origen para cada número", "teal")
with c3:
    dato("1 pipeline", "documento, app y póster comparten figuras", "a")

st.markdown(f"**Repositorio:** [`{REPO}`]({REPO})  ·  privado, acceso bajo autorización del autor.")

st.markdown("#### Cómo está organizado el código")
st.code(
    "core/       modelo físico validado (antenas, rectificador, enlace, multibanda)\n"
    "configs/    parámetros y valores CANÓNICOS (única fuente de verdad)\n"
    "_regen/     pipeline: regenera figuras y JSON de resultados\n"
    "pages/      esta app — consume core/ y las figuras, no define números\n"
    "tests/      101 pruebas: física, regresión canónica y humo del pipeline",
    language="text",
)

st.markdown("#### Reproducirlo de punta a punta")
st.code(
    "# 1. Verificar el modelo (101 pruebas)\n"
    ".venv/Scripts/python.exe -m pytest tests/ -q\n\n"
    "# 2. Regenerar todas las figuras y valores del documento\n"
    "python _regen/generate_artifacts.py\n\n"
    "# 3. Levantar esta aplicación\n"
    ".venv/Scripts/streamlit run app.py",
    language="bash",
)

st.divider()

# ── Mini-demo: la cadena en vivo ──────────────────────────────────────────────
st.markdown("#### Compruébalo tú: mueve los parámetros, el modelo recalcula")
st.write(
    "Estos tres controles alimentan la **cadena completa** del Escenario B. Con "
    "los valores de referencia (72,15 dBm · 100 m · 550 MHz) el modelo reproduce "
    f"el resultado canónico de **{CANONICAL['P_dc_uW']:,.0f} µW**. Cámbialos y verás "
    "cómo responde cada eslabón.".replace(",", " ")
)

c1, c2, c3 = st.columns(3)
with c1:
    eirp = st.slider("EIRP de la fuente [dBm]", 40.0, 75.0, 72.15, 0.05)
with c2:
    dist = st.slider("Distancia [m]", 50, 400, 100, 10)
with c3:
    freq = st.slider("Frecuencia [MHz]", 470, 900, 550, 10)

flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                   f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
rect = RectifierCircuit(topology="doubler", R_load=1300.0)
res = harvested_uw_full(eirp, float(dist), freq / 1000.0, flpda, rect, matching_net=None)

m1, m2, m3, m4 = st.columns(4)
with m1:
    dato(f"{res['P_rf_dBm']:.1f} dBm", "potencia en la antena", "teal")
with m2:
    dato(f"{res['PCE']*100:.0f} %", "eficiencia del rectificador", "teal")
with m3:
    dato(f"{res['P_dc_uW']:,.0f} µW".replace(",", " "), "potencia DC útil", "b")
with m4:
    estado = "sí" if res["coldstart_ok"] else "no"
    dato(estado, "arranca en frío (>130 mV)", "a" if res["coldstart_ok"] else "b")

es_ref = abs(eirp - 72.15) < 1e-6 and dist == 100 and freq == 550
if es_ref:
    st.success(
        f"Con los valores de referencia el modelo entrega {res['P_dc_uW']:,.0f} µW, "
        f"idéntico al valor canónico del documento.".replace(",", " ")
    )
st.caption("Cadena completa en vivo: `core.lora_budget.harvested_uw_full` (FLPDA Koch it.2 + rectificador SMS7630).")

st.divider()

# ── Cierre ────────────────────────────────────────────────────────────────────
st.markdown("### El mensaje de cierre")
st.markdown(
    f"<p class='lead'>La energía de radiofrecuencia del entorno puede alimentar "
    f"sensores de bajo consumo, y la <b>estrategia de captación importa</b>: "
    f"<span style='color:{A_ORO};font-weight:600'>concentrar</span> ante una fuente "
    f"dominante, <span style='color:{B_VERDE};font-weight:600'>acumular</span> cuando "
    f"la energía está repartida. El caso de Medellín es la demostración; el método, "
    f"el código y las pruebas hacen que cualquiera pueda comprobarlo y llevarlo a "
    f"otro escenario.</p>",
    unsafe_allow_html=True,
)
st.caption("Brahian Calderón Múnera · Ingeniería de Telecomunicaciones · Universidad de Antioquia · 2026")
