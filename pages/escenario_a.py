"""
Escenario A — Sierpinski Gasket it.3, 1.8–5.8 GHz.
Tabs: S11 · Impedancia · PCE vs Pin · Geometría · Tabla

Escenario exploratorio (cotas superiores). El resultado cuantitativo del
proyecto está en el Escenario B. El tab de comparación de rectificadores
(media onda / doblador / Dickson) se retiró porque esa comparación no forma
parte del informe de grado: el trabajo adopta únicamente el doblador Greinacher.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from simulation.escenario_a import (
    run_bandas, run_sweep_freq, run_pce_vs_pin, run_geometry,
)
from plots.charts import (
    fig_s11, fig_impedancia, fig_sierpinski, fig_pce_pin,
)
from core.antenna import FractalAntenna
from utils.exportar import resultados_a_csv, sweep_a_csv
from utils.pagina import (encabezado, badge_exploracion,
                          control_interactivo, donde_se_desarrolla as _ref)
from utils.glosario import glosario_pagina
from configs.parametros import BANDS_A


def render():
    encabezado(
        "Escenario A — Sierpinski Gasket (exploración multibanda)",
        "Antena fractal it.3 · FR-4 · 1,84 / 3,68 / 7,36 GHz · Rectificador SMS7630",
        que_es=("Página de **exploración multibanda**: estudia la antena fractal de "
                 "Sierpinski iteración 3, que radia simultáneamente en tres bandas "
                 "armónicamente espaciadas, sobre fuentes urbanas como GSM, 5G y WiFi."),
        para_que_sirve=("Ilustrar cómo una sola antena fractal puede captar energía de "
                         "varias fuentes RF distintas gracias a la autoafinidad de su "
                         "geometría, y valorar si esas fuentes urbanas representan "
                         "oportunidades adicionales de recolección."),
        entradas=("Control de potencia de entrada Pin y selectores de banda, todos dentro "
                  "de la página. Topología de rectificación: doblador Greinacher (la del "
                  "proyecto)."),
        salidas=("S₁₁ vs frecuencia, impedancia compleja, PCE banda por banda, geometría "
                  "del fractal con iluminación de las bandas activas y tabla resumen."),
        como_leer=("Las **tres resonancias** del Sierpinski caen a f_k = f₀·2^k, es decir, "
                   "1,84, 3,68 y 7,36 GHz. En cada banda se ilumina un subconjunto distinto "
                   "de triángulos: 1 grande, 3 medianos o 9 pequeños. Esto es la firma "
                   "geométrica de la antena multibanda. **No cuantifica P_DC final** "
                   "porque los EIRP urbanos son variables; lee las cifras como cotas superiores."),
    )

    badge_exploracion("El Escenario A es **exploratorio**: su propósito es **mapear en qué "
                       "bandas urbanas** una antena fractal podría captar energía, no fijar "
                       "una cifra final. Por eso sus valores se leen como **cotas "
                       "superiores** (el resultado energético firme lo aporta el "
                       "**Escenario B**: TDT, 550 MHz, P_DC = 1 637,6 µW).")

    st.markdown(
        "Este escenario pone a prueba la pregunta que dejó abierta **Topologías**:"
    )
    st.info(
        "**¿Puede una sola antena fractal captar energía útil en varias bandas urbanas "
        "al mismo tiempo?**",
        icon=":material/help:",
    )
    st.markdown(
        "Para responderla se estudia una antena de Sierpinski que, por su autoafinidad, "
        "resuena en tres bandas (1,84 · 3,68 · 7,36 GHz). **Si la hipótesis fuera cierta**, "
        "deberíamos ver tres cosas a la vez: la antena adaptada (S₁₁ < −10 dB) en varias "
        "bandas, una impedancia cercana a 50 Ω en cada una y una conversión (PCE) "
        "apreciable en todas. Las pestañas siguientes comprueban, una a una, cuáles de esas "
        "condiciones se cumplen."
    )
    _ref("§2.3 Geometría fractal aplicada a antenas · §3.4.1 Sierpinski: modelo RLC y "
         "resonancias · §4.1 Escenario A — Sierpinski (1,8–5,8 GHz)")

    topology = 'doubler'
    with st.container(border=True):
        st.markdown("**:material/tune: Parámetros del Escenario A**")
        c_ctrl, c_info = st.columns([1, 1])
        with c_ctrl:
            Pin_dBm = st.slider(
                "Potencia de entrada Pin [dBm]",
                min_value=-30.0, max_value=0.0, value=-10.0, step=1.0,
                help="−10 dBm es el punto canónico de la validación con Wang (2022).",
            )
        with c_info:
            st.caption(":material/lock: Rectificación: **doblador Greinacher**, la "
                       "topología que adopta el proyecto.")
            st.caption("εᵣ FR-4 dinámico: 4.4 @ 1 GHz → 4.1 @ 5.8 GHz · "
                       "Ref: Wang et al. (2022) IEEE TAP")
        control_interactivo(
            magnitud="**Pin** es la potencia de RF que llega a la entrada del "
                     "rectificador, en dBm (escala logarítmica: +3 dB ≈ el doble de "
                     "potencia).",
            referencia="**−10 dBm**, el punto de comparación con Wang (2022) en el "
                       "régimen lineal del diodo.",
            al_subir="El diodo entra antes en conducción y la PCE sube hacia su techo "
                     "(~85 %): el doblador rinde mejor.",
            al_bajar="El diodo trabaja en zona sub-umbral, la PCE cae rápido y la "
                     "tensión puede no alcanzar el arranque del PMIC (130 mV).",
            limite="Por encima de ~0 dBm ya no es cosecha *ambiental* (sería una fuente "
                   "dedicada); por debajo de ~−30 dBm la conversión deja de ser útil.",
        )

    with st.spinner("Calculando bandas..."):
        bandas = run_bandas(topology=topology, Pin_dBm=Pin_dBm)
    with st.spinner("Barrido de frecuencia..."):
        sweep  = run_sweep_freq()

    pce_vals  = [b['PCE_pct'] for b in bandas]
    vdc_vals  = [b['Vdc_mV']  for b in bandas]
    pout_vals = [b['Pout_uW'] for b in bandas]

    st.markdown(
        "**Primera señal, antes del detalle.** Si la antena recolectara bien en varias "
        "bandas, esperaríamos una PCE **alta y pareja** entre ellas. Conviene mirar la "
        "media, la máxima y cuánto se separan:"
    )
    with st.container(horizontal=True):
        st.metric("Bandas analizadas",  len(bandas),                                border=True)
        st.metric("PCE media [%]",      f"{sum(pce_vals)/len(pce_vals):.1f}",        border=True)
        st.metric("PCE máx. [%]",       f"{max(pce_vals):.1f}",                      border=True)
        st.metric("Vdc máx. [mV]",      f"{max(vdc_vals):.0f}",                      border=True)
        st.metric("Pout máx. [µW]",     f"{max(pout_vals):.2f}",                     border=True)

    st.caption(
        ":material/lightbulb: Los valores son **bajos y desiguales**: la PCE media queda "
        "muy por debajo del techo del modelo (85 %) y la salida es de microvatios. Es la "
        "primera señal de que la multibanda no se está cumpliendo por igual —el **porqué** "
        "está en las pestañas siguientes—. Léelos como **cotas superiores**, no como "
        "resultado firme."
    )

    st.divider()

    glosario_pagina("S11", "adaptación", "ganancia", "impedancia", "PCE")
    tab_s11, tab_imp, tab_pce, tab_geom, tab_tabla = st.tabs([
        ":material/show_chart: S11",
        ":material/electrical_services: Impedancia",
        ":material/bolt: PCE vs Pin",
        ":material/shape_line: Geometría",
        ":material/table_view: Tabla",
    ])

    with tab_s11:
        st.markdown(
            "**La geometría multibanda existe, pero eso no asegura que la energía entre.** "
            "S₁₁ mide la **puerta de entrada** de la antena: qué fracción de la energía pasa "
            "y qué fracción rebota. La línea de **−10 dB** es el aprobado —por debajo, la "
            "energía entra; por encima, se refleja—. Si el fractal fuera multibanda "
            "*aprovechable*, la curva debería cruzar esa línea en cada una de sus "
            "resonancias. La prueba es contar en cuántas lo hace:"
        )
        bandas_dict = {b: f / 1e9 for b, f in BANDS_A.items()}
        fig = fig_s11(sweep['freqs_GHz'], sweep['s11_dB'],
                      'S11 — Sierpinski Gasket it.3 (sin IMN)', xunit='GHz', bandas=bandas_dict)
        st.plotly_chart(fig)
        st.markdown(
            "**¿Qué nos muestra esta evidencia?**\n\n"
            "El Sierpinski genera varias resonancias, pero **solo una de las siete bandas "
            "objetivo** —la de 5G en 3,5 GHz— cae con holgura por debajo de −10 dB "
            "(S₁₁ = −16,4 dB). En las demás, buena parte de la energía se refleja antes de "
            "entrar a la antena.\n\n"
            "Importa porque S₁₁ es la **primera condición de toda la cadena**: si la energía "
            "no entra, ninguna etapa posterior puede recuperarla. La multibanda *geométrica* "
            "no se está convirtiendo, al menos aquí, en multibanda *aprovechable*.\n\n"
            "Pero esto abre dos preguntas que S₁₁ por sí solo no responde: **¿por qué la "
            "antena se adapta justo en esas frecuencias y no en otras?** y **¿basta con que "
            "la energía entre para que se aproveche?** La primera se ve en *Impedancia*; la "
            "segunda, en *PCE vs Pin*."
        )
        _ref("§2.4.3 Coeficiente de reflexión y parámetros S · "
             "§4.1.1 Resultados del modelo computacional · "
             "Figura 1 (S₁₁ Sierpinski) · Tabla 2 (bandas del Escenario A)")

    with tab_imp:
        st.markdown(
            "S₁₁ mostró *que* la energía solo entra limpiamente en una banda. La impedancia "
            "de la antena explica **por qué**:"
        )
        fig = fig_impedancia(
            sweep['freqs_GHz'], sweep['Za_real'], sweep['Za_imag'],
            'Impedancia Zₐ(f) — Sierpinski (modelo RLC multimodo)'
        )
        st.plotly_chart(fig)
        st.markdown(
            "**Explóralo tú:** cambia entre GSM1800, WiFi 2,4 GHz y WiFi 5,8 GHz y observa "
            "cómo varían la resistencia (Re) y la parte reactiva (Im) con la frecuencia. "
            "¿Qué banda se acerca más al ideal de 50 Ω reales con reactancia casi nula?"
        )
        banda_z_sel = st.selectbox(
            "Leer impedancia en la banda:",
            [b['banda'] for b in bandas], index=2, key="banda_imp",
            help="La impedancia compleja Zₐ determina cuánta potencia entra al rectificador. "
                 "Lejos de 50 Ω reales → mala adaptación → η_mm baja.",
        )
        _bz = next(b for b in bandas if b['banda'] == banda_z_sel)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Re(Zₐ) @ {_bz['f_GHz']} GHz", f"{_bz['Za_real']:.1f} Ω",
                      delta=f"{_bz['Za_real'] - 50:+.0f} Ω vs 50 Ω ideal", delta_color="off")
        with col2:
            st.metric(f"Im(Zₐ) @ {_bz['f_GHz']} GHz", f"{_bz['Za_imag']:+.1f} Ω",
                      delta="reactiva ≠ 0 → requiere IMN", delta_color="off")
        with col3:
            st.metric("PCE en esa banda", f"{_bz['PCE_pct']:.1f} %",
                      delta="con red L adaptada", delta_color="off")
        st.markdown(
            "**Lo que vas viendo:** la impedancia solo se acerca a 50 Ω con reactancia nula "
            "**en las resonancias**; entre ellas, la parte reactiva crece y la antena "
            "refleja casi todo. Por eso la energía entra en puntos aislados y no en una "
            "banda ancha: es el mecanismo detrás de lo que mostró S₁₁.\n\n"
            "¿Y por qué las resonancias caen exactamente en 1,84, 3,68 y 7,36 GHz? La "
            "deducción a partir del modelo RLC multimodo y de la autoafinidad del fractal se "
            "desarrolla en **§3.4.1** del documento. Aquí se ve el resultado; la "
            "demostración está allí."
        )
        _ref("§2.4.2 Impedancia de entrada Zₐ · §3.4.1 Sierpinski: modelo RLC y resonancias")

    with tab_pce:
        col_f, _ = st.columns(2)
        with col_f:
            f_sel = st.selectbox("Banda de análisis", [b['banda'] for b in bandas], index=2,
                                 help="Elige en qué banda ver la curva PCE-vs-Pin. Es una "
                                      "vista; no cambia el modelo ni el resultado.")
        banda_data = next(b for b in bandas if b['banda'] == f_sel)
        f_GHz = banda_data['f_GHz']
        with st.spinner(f"Calculando PCE @ {f_GHz} GHz..."):
            sweep_pce = run_pce_vs_pin(f_GHz=f_GHz, topology=topology)
        st.markdown(
            "Supongamos que la energía sí entró en una banda. Queda la otra mitad de la "
            "pregunta: **¿cuánta de esa energía se convierte** en corriente continua? Esa es "
            "la eficiencia del rectificador (PCE).\n\n"
            "**Explóralo tú:** la forma de la curva es parecida en todas las bandas, pero la "
            "eficiencia que alcanzan no. Cambia la banda en el selector de arriba y compara "
            "la PCE para una misma potencia de entrada. ¿Convierten todas con la misma "
            "eficacia?"
        )
        fig = fig_pce_pin(
            sweep_pce['Pin_dBm'],
            {'PCE [%]': sweep_pce['PCE_pct']},
            f'PCE vs Pin — {f_sel} ({f_GHz} GHz) · {topology}'
        )
        st.plotly_chart(fig)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("IL red L", f"{sweep_pce['IL_dB']:.2f} dB")
        with col2:
            st.metric(f"PCE @ {Pin_dBm} dBm", f"{banda_data['PCE_pct']:.1f}%")
        st.markdown(
            "**Lo que se observa:** la PCE sube con Pin hasta el techo del modelo (~85 %), "
            "pero la energía ambiental llega débil (Pin ≤ −10 dBm) y el rectificador trabaja "
            "**muy por debajo** de ese techo. Y al comparar bandas, la conversión **no es la "
            "misma** en todas: ni siquiera la banda que mejor se adaptaba tiene por qué ser "
            "la que mejor convierte.\n\n"
            "Eso deja una pregunta para el final: **¿coinciden la banda mejor adaptada y la "
            "que más convierte?** Si no coinciden, ninguna banda reúne las dos virtudes a la "
            "vez —y eso se comprueba en la *Tabla*—. *(Curva derivada del modelo PCE–P_in "
            "del trabajo, Tabla 7.)*"
        )
        st.download_button(
            "Descargar CSV",
            sweep_a_csv(sweep_pce, ['Pin_dBm', 'PCE_pct', 'Vdc_mV']),
            file_name=f"pce_vs_pin_{f_sel}.csv", mime="text/csv",
        )
        _ref("§2.7 Física del diodo Schottky: modelo de Shockley · "
             "§3.5 Módulo 2 — Cadena RF-DC · "
             "Figura 2 (η_total por banda) · Tabla 2 · Tabla 7 (PCE–P_in)")

    with tab_geom:
        st.markdown(
            "Las pestañas anteriores mostraron que la energía no entra ni se convierte por "
            "igual en todas las bandas. Conviene entonces ver **por qué la antena es "
            "multibanda en primer lugar**: la respuesta está en su geometría."
        )
        it_geom = st.slider("Iteraciones a mostrar", 0, 4, 3, key='it_sierp',
                            help="Nivel de detalle del fractal a dibujar. Es una vista "
                                 "geométrica; no afecta los resultados.")
        with st.spinner("Generando geometría..."):
            triangulos = run_geometry(iterations=it_geom)
        st.plotly_chart(fig_sierpinski(triangulos, it_geom))
        ant_info = {
            'Tipo': 'Sierpinski Gasket', 'Iteraciones': 3, 'Sustrato': 'FR-4',
            'εᵣ @ f₀': '4.28 (interpolado)', 'h': '1.6 mm', 'tan δ': '0.02',
            'f₀': '1.84 GHz', 'Resonancias fractales': '1.84 · 3.68 · 7.36 GHz',
        }
        st.json(ant_info, expanded=False)

        st.divider()
        st.markdown("##### La antena en imágenes — *banda activa por escala fractal*")
        st.markdown(
            "**Antes de mover el control, predice:** al **duplicar** la frecuencia, ¿se "
            "activará una estructura más **grande** o más **pequeña**? ¿Una sola región o "
            "varias? Elige una resonancia y compruébalo en la visualización."
        )

        modo_sierp = st.segmented_control(
            "Modo de visualización",
            options=["Manual", "Auto-ciclar", "Comparar las 3"],
            default="Manual",
            key="modo_sierp",
        ) or "Manual"

        if modo_sierp == "Manual":
            f_active_ghz = st.select_slider(
                "Resonancia activa",
                options=[1.84, 3.68, 7.36],
                value=1.84,
                format_func=lambda v: f"{v:.2f} GHz  (f₀ · 2^{int(round(__import__('math').log2(v/1.84)))})",
                key="f_active_sierp",
            )
            st.plotly_chart(_fig_sierpinski_active(f_active_ghz),
                            width="stretch", key="sierp_manual")
        elif modo_sierp == "Auto-ciclar":
            st.caption(":material/play_circle: Cicla automáticamente entre las tres "
                        "resonancias cada 1,8 s. Ideal para mostrar la transición en vivo "
                        "durante la sustentación.")
            _sierp_animator()
        else:  # Comparar las 3
            st.caption(":material/grid_view: Las tres escalas radiantes en una sola vista. "
                        "Apreciar cómo la antena 'se subdivide' al subir la frecuencia.")
            cols = st.columns(3)
            for col, f in zip(cols, [1.84, 3.68, 7.36]):
                with col:
                    st.plotly_chart(_fig_sierpinski_active(f, compact=True),
                                    width="stretch", key=f"sierp_cmp_{f}")

        st.markdown(
            "**Lo que acabas de ver:** al subir de banda, los triángulos activos se hacen "
            "más **pequeños** y más **numerosos** (1 → 3 → 9). A cada frecuencia "
            "$f_k = f_0 \\cdot 2^k$ radia la escala $L_0/2^k$: eso es la **autoafinidad**. "
            "La antena no es una banda, son tres antenas anidadas, una por escala — la "
            "multibanda **es real y nace de la geometría**.\n\n"
            "Lo que la geometría no garantiza es que esas bandas sean *aprovechables*: eso "
            "es lo que miden S₁₁, la impedancia y la PCE. El desarrollo formal de la "
            "autosimilitud y su dimensión de Hausdorff está en **§2.3.1–§2.3.2**, y la "
            "verificación de las resonancias frente a Puente-Baliarda (1998), en la "
            "**Tabla 12**."
        )
        _ref("§2.3.1 Dimensión de Hausdorff y autosimilitud · "
             "§2.3.2 Triángulo de Sierpinski: propiedades y dimensionado · "
             "§3.4.1 Sierpinski: modelo RLC y resonancias · "
             "Tabla 12 (verificación de resonancias vs Puente-Baliarda 1998)")

    with tab_tabla:
        df = pd.DataFrame(bandas).rename(columns={
            'banda': 'Banda', 'f_GHz': 'f [GHz]',
            'Za_real': 'Re(Zₐ) [Ω]', 'Za_imag': 'Im(Zₐ) [Ω]',
            's11_dB': 'S11 [dB]', 'IL_dB': 'IL [dB]', 'VSWR': 'VSWR',
            'PCE_pct': 'PCE [%]', 'Vdc_mV': 'Vdc [mV]', 'Pout_uW': 'Pout [µW]',
            'L_nH': 'L [nH]', 'C_pF': 'C [pF]', 'topo_imn': 'IMN',
        })
        cols_show = ['Banda', 'f [GHz]', 'S11 [dB]', 'IL [dB]',
                     'PCE [%]', 'Vdc [mV]', 'Pout [µW]', 'L [nH]', 'C [pF]', 'IMN']
        st.markdown(
            "Esta tabla reúne, banda por banda, S₁₁, pérdidas, PCE y potencia de salida. En "
            "lugar de leerla entera, hazle una pregunta: **busca la banda con mejor S₁₁ (el "
            "más negativo) y la banda con mayor PCE. ¿Son la misma?**"
        )
        st.dataframe(df[cols_show], hide_index=True)
        st.download_button(
            "Descargar tabla CSV", resultados_a_csv(bandas),
            file_name=f"escenario_a_{topology}.csv", mime="text/csv",
        )
        st.caption(f"Pin = {Pin_dBm} dBm · Rectificación: doblador Greinacher · R_load = 1300 Ω (BQ25504)")
        st.markdown(
            "Si la mejor adaptación y la mejor conversión **no caen en la misma banda**, "
            "ninguna reúne a la vez las dos virtudes que la recolección necesita. Esa es, "
            "reunida, la respuesta del Escenario A a su pregunta: **una antena fractal "
            "multibanda, sin una red de adaptación dedicada por banda, no capta energía útil "
            "en varias bandas a la vez**. Es un hallazgo de exploración —cotas superiores—, "
            "no la cifra final del proyecto.\n\n"
            "El análisis completo de estas limitaciones, banda por banda, se desarrolla en "
            "**§5.1** y en la tabla de limitaciones **L1–L8** (Apéndice E). El resultado "
            "energético firme llega en el **Escenario B**."
        )
        _ref("§4.1 Escenario A — Sierpinski · §4.1.1 Resultados del modelo computacional · "
             "Tabla 2 (bandas del Escenario A y resultados del modelo)")


# ──────────────────────────────────────────────────────────────────────────────
#  Visualización conceptual: bandas activas del Sierpinski
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl="1h", show_spinner=False)
def _sierpinski_triangles_at_depth(depth: int):
    """Triángulos del Sierpinski Gasket a profundidad dada, geometría normalizada."""
    ant = FractalAntenna('sierpinski', iterations=max(depth, 0))
    return ant.geometry_points(max(depth, 0))


@st.fragment(run_every=1.8)
def _sierp_animator():
    """Cicla automáticamente entre las tres resonancias del Sierpinski.
    Solo afecta a este fragmento (el resto de la página no se re-ejecuta)."""
    if 'sierp_anim_idx' not in st.session_state:
        st.session_state.sierp_anim_idx = 0
    freqs = [1.84, 3.68, 7.36]
    idx = st.session_state.sierp_anim_idx
    st.plotly_chart(_fig_sierpinski_active(freqs[idx]),
                    width="stretch", key=f"sierp_anim_{idx}")
    st.session_state.sierp_anim_idx = (idx + 1) % 3


def _fig_sierpinski_active(freq_active_ghz: float, compact: bool = False):
    """Sierpinski con la escala radiante resaltada según f_k = f₀·2^k.
    compact=True: figura para usar en columnas estrechas (sin leyenda lateral)."""
    import math

    f0_ghz = 1.84
    k = int(round(math.log2(freq_active_ghz / f0_ghz)))
    k = max(0, min(k, 2))

    tris_base = _sierpinski_triangles_at_depth(3)
    tris_active = _sierpinski_triangles_at_depth(k)

    fig = go.Figure()

    for tri in tris_base:
        xs = [tri[0][0], tri[1][0], tri[2][0], tri[0][0]]
        ys = [tri[0][1], tri[1][1], tri[2][1], tri[0][1]]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor='rgba(96, 165, 250, 0.10)',
            line=dict(color='rgba(96, 165, 250, 0.30)', width=0.4),
            mode='lines', showlegend=False, hoverinfo='skip',
        ))

    for tri in tris_active:
        xs = [tri[0][0], tri[1][0], tri[2][0], tri[0][0]]
        ys = [tri[0][1], tri[1][1], tri[2][1], tri[0][1]]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor='rgba(251, 191, 36, 0.30)',
            line=dict(color='#FBBF24', width=2.8),
            mode='lines', showlegend=False, hoverinfo='skip',
        ))

    n_active = 3 ** k

    if compact:
        # Versión para 3 columnas: solo título centrado, sin leyenda lateral
        fig.add_annotation(
            x=0.5, y=1.06, xref='paper', yref='paper', xanchor='center',
            text=(f"<b>f_{k} = {freq_active_ghz:.2f} GHz</b><br>"
                  f"<i>{n_active} {'triángulo' if n_active == 1 else 'triángulos'}"
                  f" a escala L₀/{2**k}</i>"),
            showarrow=False, font=dict(color='#B45309', size=11),
            align='center',
            bgcolor='rgba(248, 250, 252, 0.9)',
            bordercolor='rgba(180, 83, 9, 0.45)', borderwidth=1, borderpad=5,
        )
        top_margin = 80
    else:
        # Versión normal: banderín izquierda + leyenda derecha
        fig.add_annotation(
            x=0.0, y=1.05, xref='paper', yref='paper', xanchor='left',
            text=(f"<b>f_{k} = {freq_active_ghz:.2f} GHz</b>  "
                  f"·  escala radiante L₀/{2**k}  "
                  f"·  <b>{n_active}</b> {'triángulo activo' if n_active == 1 else 'triángulos activos'}"),
            showarrow=False, font=dict(color='#B45309', size=12),
            bgcolor='rgba(248, 250, 252, 0.9)',
            bordercolor='rgba(180, 83, 9, 0.45)', borderwidth=1, borderpad=6,
        )
        leyenda = []
        for kk in range(3):
            fkk = f0_ghz * (2 ** kk)
            marker = "● " if kk == k else "○ "
            col = "#B45309" if kk == k else "#64748B"
            leyenda.append(
                f"<span style='color:{col}'>{marker}{fkk:.2f} GHz · {3**kk} tri.</span>"
            )
        fig.add_annotation(
            x=1.0, y=1.05, xref='paper', yref='paper', xanchor='right',
            text="<br>".join(leyenda),
            showarrow=False, font=dict(size=11),
            align='right',
        )
        top_margin = 70

    fig.update_layout(
        template='simple_white',
        height=380 if compact else 440,
        showlegend=False,
        xaxis=dict(scaleanchor='y', scaleratio=1, showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=20, r=20, t=top_margin, b=20),
    )
    return fig


render()
