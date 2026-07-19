"""
Sección 7 · Comparación de los dos escenarios.
Narrativa y Tabla 3 derivadas de §5.4 (Análisis comparativo de los dos
escenarios) del informe de grado. Página de lectura.
"""

import json
import os

import streamlit as st
import pandas as pd
from utils.pagina import encabezado, donde_se_desarrolla as _ref
from utils.glosario import glosario_pagina
from core.patch import MicrostripPatchAntenna
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from configs.parametros import FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ

_REGEN_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "_regen", "out")
_FIG_DIR = os.path.join(_REGEN_OUT, "figuras")

_ANTENAS_CMP = {
    "Sierpinski (fractal)":  "sierpinski",
    "Parche microcinta":     "patch",
    "FLPDA Koch":            "flpda",
}
_SUSTRATOS_CMP = {
    "FR-4":            "FR4",
    "RT/duroid 5880":  "RT5880",
    "RO4003C":         "RO4003C",
}


@st.cache_data(ttl="1h", show_spinner=False)
def _cargar_json(nombre: str):
    """Carga un JSON derivado de `_regen/out/`; None si no existe."""
    path = os.path.join(_REGEN_OUT, nombre)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl="1h", show_spinner=False)
def _antena_comparativa(antena_kind: str, sustrato_kind: str):
    """
    Instancia en vivo la antena elegida y devuelve sus métricas de
    caracterización (dimensiones, resonancias, ganancia, η_rad).
    Llama directamente a los modelos de `core/` — nada a mano.
    """
    if antena_kind == "sierpinski":
        ant = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
        f0 = 1.84e9
        dims = None
        resonancias_ghz = [round(f / 1e9, 3) for f in ant.fractal_resonances_hz if f < 7e9]
        ds_key = "sierpinski"
    elif antena_kind == "patch":
        f0 = 2.45e9
        ant = MicrostripPatchAntenna(f0, sustrato_kind)
        dims = ant.dimensions()
        resonancias_ghz = [round(f / 1e9, 3) for f in ant.resonances()]
        ds_key = f"patch_{sustrato_kind}"
    else:  # flpda
        ant = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                         f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
        f0 = 550e6
        dims = None
        resonancias_ghz = sorted({round(f / 1e9, 3) for f in ant.resonant_freqs
                                  if ant.f_low <= f <= ant.f_high})
        ds_key = "flpda"

    return {
        'dims': dims,
        'resonancias_ghz': resonancias_ghz,
        'gain_dBi_f0': round(float(ant.gain_dBi(f0)), 3),
        'eta_rad_f0':  round(float(ant.eta_rad(f0)), 4),
        'f0_ghz':      round(f0 / 1e9, 3),
        'ds_key':      ds_key,
    }


def render():
    encabezado(
        ":material/compare: Comparación de los dos escenarios",
        "Sierpinski (A) frente a FLPDA Koch (B): no cuál es mejor, sino para qué",
        que_es=("Sintetiza la comparación técnica entre las dos topologías estudiadas, "
                "criterio por criterio."),
        para_que_sirve=("Ver lado a lado las diferencias y entender que cada topología "
                        "encaja en un escenario de despliegue distinto."),
        entradas="Ninguna; es una página de lectura.",
        salidas="La tabla comparativa integral (Tabla 3 del informe) y su lectura.",
    )

    st.markdown(
        "La diferencia de ganancia entre el Sierpinski (omnidireccional, 2,5–3,5 dBi) y "
        "la FLPDA (directiva, 4,83 dBi de media en banda, 4,97 dBi a la frecuencia "
        "de referencia de 550 MHz) no dice cuál diseño es superior. Dice para qué "
        "situación de despliegue conviene cada uno."
    )

    tabla10 = [
        ("Rango espectral",        "1,8–5,8 GHz",            "470–900 MHz"),
        ("Tamaño físico",          "~39 × 34 mm² (PCB)",     "Boom de 500 mm"),
        ("Patrón de radiación",    "Omnidireccional",        "Directivo (end-fire)"),
        ("Ganancia típica",        "2,5–3,5 dBi",            "4,83 dBi (media en banda)"),
        ("S₁₁ < −10 dB",           "1/7 (50 Ω) · 6/7 (integrado)", "Continuo 470–900 MHz"),
        ("Fuentes objetivo",       "WiFi, LTE, 5G sub-6",    "TDT, LTE 700, GSM 850"),
        ("P_DC a 100 m de fuente", "~0,3–8 µW (interior)",   "1 335 µW (TDT 10 kW)"),
        ("Escenario óptimo",       "IoT interior / portátil","Estación exterior fija"),
        ("Carga viable",           "Sensor ADC / reporte esporádico", "Nodo LoRa SF12"),
        ("η_total (rango)",        "1,0–13,8 % (por banda)", "28–67 % (varía con P_in; tope 67 % por PCE 0,85)"),
    ]
    df = pd.DataFrame(tabla10, columns=["Criterio", "Escenario A — Sierpinski it. 3",
                                        "Escenario B — FLPDA Koch it. 2"])
    st.dataframe(df, hide_index=True, height=420,
                 column_config={
                     "Criterio": st.column_config.TextColumn("Criterio", width="medium"),
                 })
    st.caption("El cap de PCE = 85 % es el límite del rectificador, no de η_total.")
    st.caption(
        ":material/lightbulb: **Filas decisivas:** la ganancia (B concentra más energía "
        "hacia la fuente), el S₁₁ (B está adaptada en toda la banda; A en 1 de 7 con línea "
        "de 50 Ω y 6 de 7 con co-diseño conjugado integrado) y "
        "la P_DC (solo B la cuantifica) son las que inclinan la elección hacia B para una "
        "estación fija."
    )
    glosario_pagina("ganancia", "S11", "η_total", "P_DC")

    st.divider()

    # ── Estudio comparativo de geometrías y sustratos (etapa F0/G0) ─────────────
    st.subheader(":material/compare_arrows: Estudio comparativo de geometrías y sustratos")
    st.markdown(
        "Más allá de A frente a B, este estudio caracteriza **cada geometría sobre "
        "distintos sustratos** con el mismo modelo analítico de cavidad (Balanis, "
        "cap. 14): dimensiones, resonancias, ganancia realizada y eficiencia de "
        "radiación. Elige una antena y un sustrato para ver su ficha técnica."
    )

    c_ant, c_sub = st.columns(2)
    with c_ant:
        antena_label = st.selectbox(
            "Antena", list(_ANTENAS_CMP), key="cmp_antena",
            help="Las tres topologías del proyecto, evaluadas con el mismo modelo "
                 "de cavidad / caracterización.",
        )
    antena_kind = _ANTENAS_CMP[antena_label]

    with c_sub:
        if antena_kind == "patch":
            sustrato_label = st.selectbox(
                "Sustrato", list(_SUSTRATOS_CMP), key="cmp_sustrato",
                help="El parche microcinta está calibrado sobre los tres sustratos "
                     "del catálogo (core.substrates).",
            )
            sustrato_kind = _SUSTRATOS_CMP[sustrato_label]
        else:
            st.selectbox("Sustrato", ["FR-4 (única calibración disponible)"],
                        disabled=True, key="cmp_sustrato_fijo")
            sustrato_kind = "FR4"
            st.caption(":material/info: La Sierpinski y la FLPDA de este estudio "
                       "están calibradas solo sobre FR-4; el parche sí varía por sustrato.")

    metr = _antena_comparativa(antena_kind, sustrato_kind)

    st.markdown("##### Dimensiones, resonancias y desempeño")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("f₀ de diseño", f"{metr['f0_ghz']:.3f} GHz")
    with col2:
        st.metric("Ganancia G(f₀)", f"{metr['gain_dBi_f0']:.2f} dBi")
    with col3:
        st.metric("η_rad(f₀)", f"{metr['eta_rad_f0']*100:.1f} %")
    with col4:
        st.metric("Resonancias", len(metr['resonancias_ghz']))

    st.caption("Resonancias [GHz]: " + ", ".join(f"{f:.3f}" for f in metr['resonancias_ghz']))

    if metr['dims'] is not None:
        st.markdown("**Dimensiones físicas** (`MicrostripPatchAntenna.dimensions()`):")
        df_dims = pd.DataFrame([metr['dims']]).T.rename(columns={0: "Valor"})
        st.dataframe(df_dims, column_config={"Valor": st.column_config.NumberColumn("Valor")})

    # ── Ficha técnica (hoja de datos derivada) ───────────────────────────────
    datasheet = _cargar_json("datasheet_values.json")
    st.markdown("##### Ficha técnica")
    if datasheet is not None and metr['ds_key'] in datasheet:
        ficha = datasheet[metr['ds_key']]
        st.json(ficha, expanded=False)
        energia = ficha.get('energia', {})
        if energia.get('P_dc_uW') is not None:
            st.caption(
                f":material/bolt: Energía cosechada en el escenario "
                f"«{energia.get('escenario', '—')}»: **{energia['P_dc_uW']} µW**."
            )
    else:
        st.info(
            "No hay ficha técnica derivada para esta combinación antena×sustrato "
            "(`_regen/out/datasheet_values.json`); se muestran arriba solo las "
            "métricas calculadas en vivo.",
            icon=":material/info:",
        )

    # ── Figuras de caracterización ────────────────────────────────────────────
    st.markdown("##### Figuras de caracterización")
    fig_map = {
        "sierpinski": ("FigD1_caracterizacion_sierpinski.png", "Sierpinski Gasket it.3"),
        "patch":      ("FigD2_caracterizacion_parche.png",     "Parche microcinta"),
        "flpda":      ("FigD3_caracterizacion_flpda.png",      "FLPDA Koch it.2"),
    }
    fig_name, fig_caption = fig_map[antena_kind]
    fig_path = os.path.join(_FIG_DIR, fig_name)
    if os.path.isfile(fig_path):
        st.image(fig_path, caption=f"Caracterización — {fig_caption}", width="stretch")
    else:
        st.caption(f":material/image_not_supported: Figura {fig_name} no generada aún.")

    if antena_kind == "patch":
        c_p1, c_p2 = st.columns(2)
        p1_path = os.path.join(_FIG_DIR, "FigP1_geometria_parche.png")
        p2_path = os.path.join(_FIG_DIR, "FigP2_s11_parche_sustratos.png")
        with c_p1:
            if os.path.isfile(p1_path):
                st.image(p1_path, caption="Geometría del parche (inset feed)", width="stretch")
        with c_p2:
            if os.path.isfile(p2_path):
                st.image(p2_path, caption="S₁₁ del parche en los tres sustratos", width="stretch")

    p3_path = os.path.join(_FIG_DIR, "FigP3_comparativa_antenas.png")
    if os.path.isfile(p3_path):
        st.image(p3_path, caption="Comparativa integral de las tres antenas", width="stretch")

    st.caption(
        ":material/lightbulb: El sustrato importa tanto como la geometría: un "
        "RT/duroid 5880 (tan δ = 0,0009) recorta pérdidas dieléctricas frente al "
        "FR-4 (tan δ ≈ 0,02) y sube η_rad de forma apreciable en el mismo parche."
    )
    _ref("Etapa F0/G0 — estudio comparativo antena × sustrato · "
         "_regen/derive_comparative_values.py · _regen/derive_datasheet.py")

    st.divider()

    with st.container(border=True):
        st.markdown("#### :material/flag: Conclusión del trabajo de grado")
        st.markdown(
            "- El Escenario A (Sierpinski) muestra el comportamiento multibanda del fractal "
            "y explora si fuentes urbanas (WiFi/LTE/5G) podrían sumar energía. No fija una "
            "cifra: sus resultados son cotas superiores.\n"
            "- El Escenario B (FLPDA Koch), ante una fuente concreta y bien caracterizada "
            "como la TDT del Cerro Nutibara, cuantifica la potencia útil: P_DC = 1 335 µW, "
            "suficiente para un nodo LoRa SF12.\n"
            "- El resultado principal se construye sobre B porque es el único escenario con "
            "la fuente bien definida. Su mayor ganancia media en banda (4,83 frente a "
            "2,5–3,5 dBi) y su adaptación continua en toda la banda hacen que B sostenga "
            "el resultado energético firme del proyecto, mientras A queda como exploración "
            "complementaria."
        )

    _ref("§5.4 Análisis comparativo de los dos escenarios · §5.1 Escenario A · "
         "§5.2 Escenario B · Tabla 3 (comparación técnica integral) · "
         "Figura 15 (PCE vs P_in, ambos escenarios)")

    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/inicio.py",
                     label="Ver el resultado de referencia (B) →", icon=":material/verified:")
    with col2:
        st.page_link("pages/conclusiones.py",
                     label="Ir a las conclusiones →", icon=":material/flag:")


render()
