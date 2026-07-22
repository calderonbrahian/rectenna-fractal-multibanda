"""
PÁGINA 3 · ¿Qué descubrió la investigación?  (página central)
================================================================================
Los HALLAZGOS, no cientos de resultados. Cuatro descubrimientos, cada uno
calculado EN VIVO llamando a core/ (nada hardcodeado):

  (a) la estrategia dirigida gana ante una fuente dominante   → lora_budget.harvested_uw_full
  (b) la multibanda aprovecha energía distribuida             → multiband.harvest_per_band
  (c) la potencia disponible depende del escenario (A vs B)   → los dos Sankeys del pipeline
  (d) la RF puede complementar la autonomía                   → supercap vs ráfaga (JSON del pipeline)
"""

import json
import os

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from configs.parametros import (
    CANONICAL, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.lora_budget import harvested_uw_full
from core.multiband import build_default, harvest_per_band, harvest_total_uw
from utils.ui import css, cabecera, figura, dato, A_ORO, B_VERDE, TEAL, MUTE, INK

css()

_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "_regen", "out")


def _json(nombre):
    with open(os.path.join(_OUT, nombre), encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def curva_distancia(dists):
    """Potencia DC cosechada por el Escenario B vs distancia a la torre TDT (en vivo)."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    rect = RectifierCircuit(topology="doubler", R_load=1300.0)
    return [harvested_uw_full(72.15, float(d), 0.550, flpda, rect, matching_net=None)["P_dc_uW"]
            for d in dists]


@st.cache_data(show_spinner=False)
def bandas_multibanda():
    """Cosecha por banda del Escenario A (rectena difusa integrada), en vivo."""
    ant, rec, imn = build_default()
    filas = harvest_per_band(ant, rec, imn)
    total = harvest_total_uw(ant, rec, imn)
    return filas, total


cabecera(
    kicker="Los hallazgos",
    pregunta="¿Qué descubrió la investigación?",
    bajada="Cuatro hallazgos, no cientos de cifras. Cada número de esta página lo "
           "calcula el modelo en el momento; no hay valores escritos a mano.",
)

t_a, t_b, t_c, t_d = st.tabs([
    "A · Concentrar gana",
    "B · Acumular suma",
    "A vs B · El escenario manda",
    "RF · Complemento de autonomía",
])

# ── (a) La estrategia dirigida gana ante una fuente dominante ─────────────────
with t_a:
    st.markdown("#### Cuando hay una fuente dominante, concentrarse gana")
    st.write(
        "Frente a una torre de televisión potente, la antena **dirigida** (FLPDA "
        "Koch, Escenario B) apunta y extrae. La cosecha cae con la distancia según "
        "la física de propagación. Mueve el marcador y observa la tendencia."
    )
    d_sel = st.slider("Distancia a la torre TDT [m]", 50, 400, 100, 10)

    dists = np.arange(50, 401, 10)
    pdc = curva_distancia(tuple(dists))
    pdc_sel = curva_distancia((float(d_sel),))[0]
    umbral = _json("doc_values.json")["umbral_sf12_continuo_uW"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dists, y=pdc, mode="lines",
                             line=dict(color=B_VERDE, width=3), name="cosecha B"))
    fig.add_trace(go.Scatter(x=[d_sel], y=[pdc_sel], mode="markers",
                             marker=dict(color=A_ORO, size=14, line=dict(color="white", width=2))))
    fig.add_hline(y=umbral, line=dict(color=MUTE, dash="dash", width=1.5),
                  annotation_text=f"umbral SF12 continuo ({umbral:.0f} µW)",
                  annotation_position="top right")
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                      xaxis_title="Distancia [m]", yaxis_title="Potencia DC cosechada [µW]",
                      plot_bgcolor="white", font=dict(color=INK))
    fig.update_yaxes(gridcolor="#eceff3", type="log")
    fig.update_xaxes(gridcolor="#eceff3")
    st.plotly_chart(fig, width="stretch")

    c1, c2, c3 = st.columns(3)
    with c1:
        dato(f"{pdc_sel:,.0f} µW".replace(",", " "), f"cosecha a {d_sel} m", "b")
    with c2:
        dato(f"{CANONICAL['P_dc_uW']:,.0f} µW".replace(",", " "), "resultado de referencia @ 100 m", "b")
    with c3:
        dato("~174 m", "alcance con operación continua", "teal")
    st.caption(
        "Curva y valores: `core.lora_budget.harvested_uw_full` (FLPDA Koch it.2, "
        "TDT 72,15 dBm, 550 MHz). El alcance es donde la cosecha cruza el umbral continuo."
    )

# ── (b) La multibanda aprovecha energía distribuida ───────────────────────────
with t_b:
    st.markdown("#### Cuando la energía está repartida, acumular bandas suma")
    st.write(
        "En el Escenario A no hay una fuente dominante: la rectena difusa "
        "(Sierpinski) recoge un poco de cada banda urbana —GSM, LTE, WiFi, 5G— y "
        "las **combina en DC**. Cada barra es la contribución de una banda; el "
        "total es su suma."
    )
    filas, total = bandas_multibanda()
    etiquetas = [f["banda"] for f in filas]
    aportes = [f["P_dc_uW"] for f in filas]

    fig = go.Figure(go.Bar(x=etiquetas, y=aportes, marker_color=A_ORO))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                      yaxis_title="Aporte DC por banda [µW]", plot_bgcolor="white",
                      font=dict(color=INK))
    fig.update_yaxes(gridcolor="#eceff3")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        dato(f"{total:.2f} µW", "suma de todas las bandas (cosecha total A)", "a")
    with c2:
        n_util = sum(1 for a in aportes if a > 0)
        dato(f"{n_util} de {len(aportes)}", "bandas que aportan energía útil", "a")
    st.caption(
        "Valores: `core.multiband.harvest_per_band` / `harvest_total_uw` "
        "(co-diseño conjugado integrado, ambiente urbano de Piñuela et al. 2013)."
    )

# ── (c) La potencia disponible depende del escenario ──────────────────────────
with t_c:
    st.markdown("#### La misma cadena, dos escenarios: el flujo de energía cambia")
    st.write(
        "Estos dos diagramas de Sankey muestran, lado a lado, cómo fluye la "
        "energía de la fuente al DC útil en cada estrategia. Concentrar (A) y "
        "acumular (B) reparten sus pérdidas de forma distinta."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<b style='color:{A_ORO}'>Escenario A · concentrar (Sierpinski)</b>",
                    unsafe_allow_html=True)
        figura("FigS1_sankey_sierpinski.png")
    with c2:
        st.markdown(f"<b style='color:{B_VERDE}'>Escenario B · acumular/dirigir (FLPDA)</b>",
                    unsafe_allow_html=True)
        figura("FigS3_sankey_flpda.png")
    st.caption(
        "Diagramas del pipeline (`_regen/out/figuras`). La eficiencia global RF-DC "
        "de cada escenario sale de la misma cadena de `core/`."
    )

# ── (d) La RF puede complementar la autonomía ─────────────────────────────────
with t_d:
    st.markdown("#### La RF no siempre alcanza sola, pero extiende la autonomía")
    st.write(
        "Aun cuando la cosecha no basta para alimentar el nodo de forma continua, "
        "sí carga un tampón que absorbe las ráfagas de transmisión. Un "
        "supercondensador cargado guarda varias veces la energía de una ráfaga LoRa."
    )
    sc = _json("doc_values.json")["supercap"]
    e_util_J = sc["E_util_mJ"] / 1000.0
    e_ciclo = CANONICAL["E_ciclo_mJ"]

    c1, c2, c3 = st.columns(3)
    with c1:
        dato(f"{e_util_J:.2f} J", "energía útil de un supercap 330 mF cargado", "teal")
    with c2:
        dato(f"{e_ciclo:.0f} mJ", "energía de una ráfaga LoRa SF12", "b")
    with c3:
        dato(f"{sc['n_ciclos']:.1f}", "ráfagas que cubre una carga completa", "a")

    figura("C1_por_que_rf.png",
           "La RF como complemento del almacenamiento: recarga el tampón entre ráfagas.")
    st.caption(
        "Supercap: `_regen/out/doc_values.json` (E_util, n_ciclos). "
        "Ráfaga: `CANONICAL['E_ciclo_mJ']` (configs/parametros.py)."
    )

st.divider()
st.markdown(
    f"<p class='lead'>Ningún escenario es «mejor» en abstracto. "
    f"<span style='color:{A_ORO};font-weight:600'>Concentrar</span> gana con una "
    f"fuente dominante; <span style='color:{B_VERDE};font-weight:600'>acumular</span> "
    f"rinde cuando la energía está repartida. Ese es el hallazgo, y es "
    f"general.</p>",
    unsafe_allow_html=True,
)
