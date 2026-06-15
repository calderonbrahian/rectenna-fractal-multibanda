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
from utils.pagina import (encabezado, badge_exploracion, correspondencia,
                          control_interactivo, donde_se_desarrolla as _ref)
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

    badge_exploracion("Las cifras del Escenario A son **cotas superiores**, no el "
                       "resultado cuantitativo del proyecto. El resultado energético firme "
                       "lo aporta el **Escenario B** (TDT, 550 MHz, P_DC = 1 637,6 µW).")

    st.markdown(
        "Esta página explora el **Escenario A**: una antena fractal de Sierpinski que, "
        "por su autoafinidad, resuena en tres bandas (1,84 · 3,68 · 7,36 GHz). Aborda si "
        "distintas fuentes de RF del entorno urbano podrían representar oportunidades de "
        "recolección; no fija una cifra de energía final."
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

    with st.container(horizontal=True):
        st.metric("Bandas analizadas",  len(bandas),                                border=True)
        st.metric("PCE media [%]",      f"{sum(pce_vals)/len(pce_vals):.1f}",        border=True)
        st.metric("PCE máx. [%]",       f"{max(pce_vals):.1f}",                      border=True)
        st.metric("Vdc máx. [mV]",      f"{max(vdc_vals):.0f}",                      border=True)
        st.metric("Pout máx. [µW]",     f"{max(pout_vals):.2f}",                     border=True)

    st.divider()

    tab_s11, tab_imp, tab_pce, tab_geom, tab_tabla = st.tabs([
        ":material/show_chart: S11",
        ":material/electrical_services: Impedancia",
        ":material/bolt: PCE vs Pin",
        ":material/shape_line: Geometría",
        ":material/table_view: Tabla",
    ])

    with tab_s11:
        bandas_dict = {b: f / 1e9 for b, f in BANDS_A.items()}
        fig = fig_s11(sweep['freqs_GHz'], sweep['s11_dB'],
                      'S11 — Sierpinski Gasket it.3 (sin IMN)', xunit='GHz', bandas=bandas_dict)
        st.plotly_chart(fig)
        correspondencia('directa',
                        "Reproduce la **Figura 1** del trabajo: S₁₁ vs frecuencia del "
                        "Sierpinski it. 3 sobre FR-4.")
        st.info(
            "**Nota:** S11 corresponde a la antena **sin** red de adaptación. "
            "La métrica de sistema relevante es la PCE con IMN (ver pestaña PCE).",
            icon=":material/info:",
        )
        st.markdown(
            ":material/lightbulb: **Qué concluye el trabajo.** El Sierpinski it. 3 sobre "
            "FR-4 solo cae por debajo de −10 dB en **1 de las 7 bandas objetivo** "
            "(5G-3,5 GHz, S₁₁ = −16,4 dB). Por eso el informe cuestiona el valor del "
            "fractal puro —sin elementos adicionales— para recolección multibanda (§5.1)."
        )
        _ref("§2.4.3 Coeficiente de reflexión y parámetros S · "
             "§4.1.1 Resultados del modelo computacional · "
             "Figura 1 (S₁₁ Sierpinski) · Tabla 2 (bandas del Escenario A)")

    with tab_imp:
        fig = fig_impedancia(
            sweep['freqs_GHz'], sweep['Za_real'], sweep['Za_imag'],
            'Impedancia Zₐ(f) — Sierpinski (modelo RLC multimodo)'
        )
        st.plotly_chart(fig)
        correspondencia('complementaria',
                        "No aparece literal en la tesis; visualiza la impedancia Zₐ(f) "
                        "del modelo RLC de §3.4.1 para ver dónde la antena entrega potencia.")
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
        st.caption(
            ":material/visibility: **Qué observar físicamente:** en las resonancias "
            "(1,84 / 3,68 / 7,36 GHz) la parte imaginaria cruza por cero y la real se "
            "acerca a valores manejables — ahí la antena entrega potencia. Entre "
            "resonancias, |Im(Zₐ)| crece y la antena refleja casi todo. Cambia la banda "
            "del selector y compara los tres números."
        )
        _ref("§2.4.2 Impedancia de entrada Zₐ · §3.4.1 Sierpinski: modelo RLC y resonancias")

    with tab_pce:
        col_f, _ = st.columns(2)
        with col_f:
            f_sel = st.selectbox("Banda de análisis", [b['banda'] for b in bandas], index=2)
        banda_data = next(b for b in bandas if b['banda'] == f_sel)
        f_GHz = banda_data['f_GHz']
        with st.spinner(f"Calculando PCE @ {f_GHz} GHz..."):
            sweep_pce = run_pce_vs_pin(f_GHz=f_GHz, topology=topology)
        fig = fig_pce_pin(
            sweep_pce['Pin_dBm'],
            {'PCE [%]': sweep_pce['PCE_pct']},
            f'PCE vs Pin — {f_sel} ({f_GHz} GHz) · {topology}'
        )
        st.plotly_chart(fig)
        correspondencia('derivada',
                        "Construida con el modelo PCE–P_in de la tesis (Tabla 7), evaluado "
                        "banda por banda del Escenario A (η por banda en la Figura 2).")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("IL red L", f"{sweep_pce['IL_dB']:.2f} dB")
        with col2:
            st.metric(f"PCE @ {Pin_dBm} dBm", f"{banda_data['PCE_pct']:.1f}%")
        st.caption(
            ":material/lightbulb: **Cómo se interpreta.** La PCE crece con Pin hasta "
            "saturar en el techo del modelo (~85 %). A la potencia de cosecha real "
            "(Pin ≤ −10 dBm) opera lejos de ese techo: por eso las cifras del Escenario A "
            "son **cotas superiores**, no el resultado firme."
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
        it_geom = st.slider("Iteraciones a mostrar", 0, 4, 3, key='it_sierp')
        with st.spinner("Generando geometría..."):
            triangulos = run_geometry(iterations=it_geom)
        st.plotly_chart(fig_sierpinski(triangulos, it_geom))
        correspondencia('complementaria',
                        "No aparece literal en la tesis; dibuja la geometría del Sierpinski "
                        "(it. 0–4) para ilustrar la autosimilitud descrita en §2.3.2.")
        ant_info = {
            'Tipo': 'Sierpinski Gasket', 'Iteraciones': 3, 'Sustrato': 'FR-4',
            'εᵣ @ f₀': '4.28 (interpolado)', 'h': '1.6 mm', 'tan δ': '0.02',
            'f₀': '1.84 GHz', 'Resonancias fractales': '1.84 · 3.68 · 7.36 GHz',
        }
        st.json(ant_info, expanded=False)

        st.divider()
        st.markdown("##### La antena en imágenes — *banda activa por escala fractal*")
        st.markdown(
            "La propiedad multibanda del Sierpinski viene de su **autoafinidad**: a cada "
            "frecuencia $f_k = f_0 \\cdot 2^k$, los triángulos cuya escala es "
            "$L_0 / 2^k$ son los que radian. Al duplicar la frecuencia, los triángulos "
            "activos se reducen a la mitad y aparecen tres copias en lugar de una. "
            "Esto es lo que la antena *hace* en cada banda."
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

        st.caption(
            ":material/lightbulb: Los triángulos **amarillos brillantes** son los radiadores "
            "activos (perímetros ≈ λ/2 a la f seleccionada). El fondo azul tenue es la "
            "estructura fractal completa. **Lectura clave:** la antena no es una banda, "
            "son tres antenas geométricamente anidadas, una por cada escala."
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
        st.dataframe(df[cols_show], hide_index=True)
        st.download_button(
            "Descargar tabla CSV", resultados_a_csv(bandas),
            file_name=f"escenario_a_{topology}.csv", mime="text/csv",
        )
        st.caption(f"Pin = {Pin_dBm} dBm · Rectificación: doblador Greinacher · R_load = 1300 Ω (BQ25504)")
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
