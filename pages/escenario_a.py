"""
Escenario A — Sierpinski Gasket it.3, 1.8–5.8 GHz.
Tabs: S11 · Impedancia · PCE vs Pin · Topologías · Geometría · Tabla
(Tab "Patrón" eliminado por ser decorativo: la fórmula heurística no se valida ni
consume aguas abajo. Tab "Topologías" se mantiene como exploración honesta.)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from simulation.escenario_a import (
    run_bandas, run_sweep_freq, run_pce_vs_pin,
    run_pce_topologias, run_geometry,
)
from plots.charts import (
    fig_s11, fig_gain, fig_impedancia, fig_sierpinski,
    fig_pce_pin,
)
from core.antenna import FractalAntenna
from utils.circuit_drawing import (
    draw_capacitor, draw_wire, draw_gnd, draw_diode_right, draw_diode_up,
)
from utils.exportar import resultados_a_csv, sweep_a_csv
from utils.pagina import encabezado, badge_exploracion
from configs.parametros import BANDS_A


def render():
    encabezado(
        "Escenario A — Sierpinski Gasket (exploración multibanda)",
        "Antena fractal it.3 · FR-4 · 1,84 / 3,68 / 7,36 GHz · Rectificador SMS7630",
        que_es=("Página de **exploración multibanda**: estudia la antena fractal de "
                 "Sierpinski iteración 3, que radia simultáneamente en tres bandas "
                 "armónicamente espaciadas, sobre fuentes urbanas como GSM, 5G y WiFi."),
        para_que_sirve=("Demostrar que una sola antena fractal puede recolectar energía "
                         "de varias fuentes RF distintas gracias a la autoafinidad de su "
                         "geometría. Compara también las 3 topologías rectificadoras "
                         "(halfwave / doubler / dickson3) que justifican la elección de la tesis."),
        entradas=("Slider de potencia de entrada Pin en la barra lateral; selectores de "
                  "banda dentro de cada tab. Topología canónica = doubler (fija en sidebar)."),
        salidas=("S₁₁ vs frecuencia, impedancia compleja, PCE banda por banda, comparativa "
                  "de topologías con esquemáticos visuales, geometría del fractal con "
                  "iluminación de las bandas activas y tabla resumen."),
        como_leer=("Las **tres resonancias** del Sierpinski caen a f_k = f₀·2^k, es decir, "
                   "1,84, 3,68 y 7,36 GHz. En cada banda se ilumina un subconjunto distinto "
                   "de triángulos: 1 grande, 3 medianos o 9 pequeños. Esto es la firma "
                   "geométrica de la antena multibanda. **No cuantifica P_DC final** "
                   "porque los EIRP urbanos son variables; lee las cifras como cotas superiores."),
    )

    badge_exploracion("Las cifras del Escenario A son **cotas superiores**, no resultado "
                       "oficial. El resultado cuantitativo defendido por la tesis está en "
                       "el **Escenario B** (TDT, 550 MHz, P_DC = 1 637,6 µW).")

    with st.sidebar:
        st.subheader("Parámetros Esc. A")
        st.caption(":material/lock: Topología fija: **doubler** (canónica de la tesis). "
                    "Para comparar contra halfwave/dickson3, usa el tab *Topologías* "
                    "dentro de esta página.")
        topology = 'doubler'
        Pin_dBm = st.slider(
            "Potencia de entrada Pin [dBm]",
            min_value=-30.0, max_value=0.0, value=-10.0, step=1.0,
            help="−10 dBm es el punto canónico de la validación con Wang (2022).",
        )
        st.caption("εᵣ FR-4 dinámico: 4.4 @ 1 GHz → 4.1 @ 5.8 GHz")
        st.caption("Ref: Wang et al. (2022) IEEE TAP")

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

    tab_s11, tab_imp, tab_pce, tab_topo, tab_geom, tab_tabla = st.tabs([
        ":material/show_chart: S11",
        ":material/electrical_services: Impedancia",
        ":material/bolt: PCE vs Pin",
        ":material/device_hub: Topologías (exploración)",
        ":material/shape_line: Geometría",
        ":material/table_view: Tabla",
    ])

    with tab_s11:
        bandas_dict = {b: f / 1e9 for b, f in BANDS_A.items()}
        fig = fig_s11(sweep['freqs_GHz'], sweep['s11_dB'],
                      'S11 — Sierpinski Gasket it.3 (sin IMN)', xunit='GHz', bandas=bandas_dict)
        st.plotly_chart(fig)
        st.info(
            "**Nota:** S11 corresponde a la antena **sin** red de adaptación. "
            "La métrica de sistema relevante es la PCE con IMN (ver tab PCE).",
            icon=":material/info:",
        )

    with tab_imp:
        fig = fig_impedancia(
            sweep['freqs_GHz'], sweep['Za_real'], sweep['Za_imag'],
            'Impedancia Zₐ(f) — Sierpinski (modelo RLC multimodo)'
        )
        st.plotly_chart(fig)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Re(Zₐ) @ 2.45 GHz", f"{bandas[2]['Za_real']:.1f} Ω")
        with col2:
            st.metric("Im(Zₐ) @ 2.45 GHz", f"{bandas[2]['Za_imag']:+.1f} Ω")

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
        col1, col2 = st.columns(2)
        with col1:
            st.metric("IL red L", f"{sweep_pce['IL_dB']:.2f} dB")
        with col2:
            st.metric(f"PCE @ {Pin_dBm} dBm", f"{banda_data['PCE_pct']:.1f}%")
        st.download_button(
            "Descargar CSV",
            sweep_a_csv(sweep_pce, ['Pin_dBm', 'PCE_pct', 'Vdc_mV']),
            file_name=f"pce_vs_pin_{f_sel}.csv", mime="text/csv",
        )

    with tab_topo:
        st.info(
            ":material/info: **Comparación de topologías a título exploratorio.** La "
            "tesis adopta exclusivamente la topología **doubler** (Greinacher); las "
            "curvas de halfwave y dickson3 se muestran para contextualizar la elección, "
            "no como parte de los resultados oficiales del trabajo. "
            "**Este tab barre Pin internamente** (no depende del slider Pin del sidebar).",
            icon=":material/info:",
        )

        # ── Los tres circuitos lado a lado (visualización conceptual) ───────
        st.markdown("##### Las tres topologías en sus circuitos")
        col_h, col_d, col_k = st.columns(3)
        with col_h:
            st.markdown("**Halfwave · N=1**")
            st.plotly_chart(_fig_topo_halfwave(), width="stretch")
            st.markdown("V_DC ≈ V_pk − V_f")
            st.caption("1 diodo · 1 cap · pérdida 1 V_f")
        with col_d:
            st.markdown("**Doubler ★ (tesis)**")
            st.plotly_chart(_fig_topo_doubler(), width="stretch")
            st.markdown("V_DC ≈ 2·(V_pk − V_f)")
            st.caption("2 diodos · 2 caps · pérdida 2 V_f, sale 2× la tensión")
        with col_k:
            st.markdown("**Dickson · N=3**")
            st.plotly_chart(_fig_topo_dickson3(), width="stretch")
            st.markdown("V_DC ≈ 3·(V_pk − V_f)·η_etapa")
            st.caption("3 etapas · 6 diodos · más V_DC pero más V_f en serie")

        st.markdown("")
        st.markdown(
            ":material/lightbulb: **Por qué doubler.** Halfwave entrega muy poca "
            "tensión para microvatios entrantes (el cold-start del PMIC requiere "
            "≥130 mV). Dickson 3 entrega más V_DC nominal pero acumula 3 caídas V_f "
            "(~3·150 mV = 450 mV de pérdida) y su PCE colapsa a Pin baja. **Doubler "
            "es el punto de equilibrio** entre tensión útil y pérdidas."
        )

        st.divider()
        st.markdown("##### Comportamiento sobre la frecuencia y la potencia de entrada")
        f_t = st.selectbox("Frecuencia", [b['banda'] for b in bandas], index=2, key='f_topo')
        f_t_GHz = next(b['f_GHz'] for b in bandas if b['banda'] == f_t)
        with st.spinner("Comparando topologías..."):
            topo_data = run_pce_topologias(f_GHz=f_t_GHz)
        fig = fig_pce_pin(
            topo_data['Pin_dBm'],
            {'Media onda': topo_data['halfwave'],
             'Doblador ×2 (tesis)': topo_data['doubler'],
             'Dickson ×3': topo_data['dickson3']},
            f'PCE vs Pin — Comparativa topologías @ {f_t_GHz} GHz',
        )
        st.plotly_chart(fig)
        st.caption(
            "**halfwave**: 1 diodo, N=1 | **doubler**: 2 diodos, N=2 ← topología canónica de la tesis | "
            "**dickson3**: 6 diodos, N=3 (mayor V_dc, menor PCE a baja Pin)"
        )

    with tab_geom:
        it_geom = st.slider("Iteraciones a mostrar", 0, 4, 3, key='it_sierp')
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
        st.caption(f"Pin = {Pin_dBm} dBm · Topología: {topology} · R_load = 1300 Ω (BQ25504)")


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
            showarrow=False, font=dict(color='#FBBF24', size=11),
            align='center',
            bgcolor='rgba(248, 250, 252, 0.9)',
            bordercolor='rgba(251, 191, 36, 0.45)', borderwidth=1, borderpad=5,
        )
        top_margin = 80
    else:
        # Versión normal: banderín izquierda + leyenda derecha
        fig.add_annotation(
            x=0.0, y=1.05, xref='paper', yref='paper', xanchor='left',
            text=(f"<b>f_{k} = {freq_active_ghz:.2f} GHz</b>  "
                  f"·  escala radiante L₀/{2**k}  "
                  f"·  <b>{n_active}</b> {'triángulo activo' if n_active == 1 else 'triángulos activos'}"),
            showarrow=False, font=dict(color='#FBBF24', size=12),
            bgcolor='rgba(248, 250, 252, 0.9)',
            bordercolor='rgba(251, 191, 36, 0.45)', borderwidth=1, borderpad=6,
        )
        leyenda = []
        for kk in range(3):
            fkk = f0_ghz * (2 ** kk)
            marker = "● " if kk == k else "○ "
            col = "#FBBF24" if kk == k else "#94A3B8"
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


# ──────────────────────────────────────────────────────────────────────────────
#  Topologías rectificadoras: esquemáticos compactos
# ──────────────────────────────────────────────────────────────────────────────

def _topo_blank_fig():
    fig = go.Figure()
    fig.update_layout(
        template='simple_white', height=200, showlegend=False,
        xaxis=dict(visible=False, range=[-0.5, 6]),
        yaxis=dict(visible=False, range=[-0.5, 3.0], scaleanchor='x', scaleratio=1),
        margin=dict(l=5, r=5, t=10, b=10),
    )
    return fig


# (Primitivas de dibujo movidas a utils/circuit_drawing.py — importadas arriba)


def _fig_topo_halfwave():
    """Rectificador media onda: V_in ─[C1]─●─[D1►]─●── V_DC, C2 a GND."""
    fig = _topo_blank_fig()
    y_top = 2.0; y_bot = 0.3

    # Input
    fig.add_annotation(x=0.0, y=y_top + 0.25, text="<b>V_in</b>", showarrow=False,
                       font=dict(color="#0EA5E9", size=10))
    draw_wire(fig, 0.0, y_top, 0.5, y_top)
    # C1
    draw_capacitor(fig, 0.5, y_top)
    fig.add_annotation(x=0.6, y=y_top + 0.50, text="C1", showarrow=False,
                       font=dict(color="#475569", size=10))
    draw_wire(fig, 0.7, y_top, 1.4, y_top)
    # D1 (apunta a la derecha)
    draw_diode_right(fig, 1.4, 2.2, y_top, color='#FBBF24')
    fig.add_annotation(x=1.8, y=y_top + 0.45, text="<b>D1</b>", showarrow=False,
                       font=dict(color="#FBBF24", size=10))
    # Wire to V_DC node
    draw_wire(fig, 2.12, y_top, 3.0, y_top)
    fig.add_annotation(x=3.2, y=y_top + 0.25, text="<b>V_DC</b>", showarrow=False,
                       font=dict(color="#34D399", size=11))
    # C2 vertical (de V_DC a GND)
    draw_capacitor(fig, 3.0, y_top - 0.75, vertical=True)
    fig.add_annotation(x=3.45, y=y_top - 0.75, text="C2", showarrow=False,
                       font=dict(color="#475569", size=10))
    draw_wire(fig, 3.0, y_top, 3.0, y_top - 0.55)
    draw_wire(fig, 3.0, y_top - 0.95, 3.0, y_bot)
    # GND rail
    draw_wire(fig, 0.0, y_top, 0.0, y_bot)
    draw_wire(fig, 0.0, y_bot, 3.0, y_bot)
    draw_gnd(fig, 1.5, y_bot)
    return fig


def _fig_topo_doubler():
    """Doblador Greinacher simplificado."""
    fig = _topo_blank_fig()
    y_top = 2.0; y_bot = 0.3

    fig.add_annotation(x=0.0, y=y_top + 0.25, text="<b>V_in</b>", showarrow=False,
                       font=dict(color="#0EA5E9", size=10))
    draw_wire(fig, 0.0, y_top, 0.5, y_top)
    # C1
    draw_capacitor(fig, 0.5, y_top)
    fig.add_annotation(x=0.6, y=y_top + 0.50, text="C1", showarrow=False,
                       font=dict(color="#475569", size=10))
    draw_wire(fig, 0.7, y_top, 1.5, y_top)
    # Node X (entre C1 y D2)
    fig.add_annotation(x=1.5, y=y_top + 0.30, text="X", showarrow=False,
                       font=dict(color="#0F172A", size=10))
    fig.add_shape(type='circle', x0=1.45, y0=y_top - 0.05, x1=1.55, y1=y_top + 0.05,
                  fillcolor="#0F172A", line_color="#0F172A")

    # D1 hacia GND (apunta hacia arriba)
    draw_wire(fig, 1.5, y_top, 1.5, y_top - 0.50)
    draw_diode_up(fig, 1.5, y_bot + 0.05, y_top - 0.50)
    fig.add_annotation(x=1.85, y=(y_top + y_bot) / 2 - 0.3, text="<b>D1</b>",
                       showarrow=False, font=dict(color="#FBBF24", size=10))

    # D2 hacia V_DC
    draw_diode_right(fig, 1.7, 2.5, y_top)
    fig.add_annotation(x=2.1, y=y_top + 0.45, text="<b>D2</b>", showarrow=False,
                       font=dict(color="#FBBF24", size=10))
    draw_wire(fig, 2.42, y_top, 3.0, y_top)
    fig.add_annotation(x=3.2, y=y_top + 0.25, text="<b>V_DC</b>", showarrow=False,
                       font=dict(color="#34D399", size=11))
    # C2 a GND
    draw_capacitor(fig, 3.0, y_top - 0.75, vertical=True)
    fig.add_annotation(x=3.45, y=y_top - 0.75, text="C2", showarrow=False,
                       font=dict(color="#475569", size=10))
    draw_wire(fig, 3.0, y_top, 3.0, y_top - 0.55)
    draw_wire(fig, 3.0, y_top - 0.95, 3.0, y_bot)
    # GND rail
    draw_wire(fig, 0.0, y_top, 0.0, y_bot)
    draw_wire(fig, 0.0, y_bot, 3.0, y_bot)
    draw_gnd(fig, 1.5, y_bot)
    return fig


def _fig_topo_dickson3():
    """Multiplicador Dickson 3 etapas (simplificado): 3 diodos en cascada con
    capacitores entre etapas. La ganancia de tensión es 3·V_pk en ideal."""
    fig = _topo_blank_fig()
    y_top = 2.0; y_bot = 0.3

    fig.add_annotation(x=0.0, y=y_top + 0.25, text="<b>V_in</b>", showarrow=False,
                       font=dict(color="#0EA5E9", size=10))
    draw_wire(fig, 0.0, y_top, 0.4, y_top)
    # Tres etapas: diodo + cap a GND
    diode_positions = [(0.5, 1.1), (1.5, 2.1), (2.5, 3.1)]
    for i, (x0, x1) in enumerate(diode_positions, start=1):
        draw_diode_right(fig, x0, x1, y_top)
        fig.add_annotation(x=(x0 + x1) / 2, y=y_top + 0.45,
                           text=f"<b>D{i}</b>", showarrow=False,
                           font=dict(color="#FBBF24", size=10))
        # Cap a GND tras cada diodo
        cap_x = x1 - 0.08
        draw_capacitor(fig, cap_x, y_top - 0.75, vertical=True)
        fig.add_annotation(x=cap_x + 0.45, y=y_top - 0.75,
                           text=f"C{i}", showarrow=False,
                           font=dict(color="#475569", size=9))
        draw_wire(fig, cap_x, y_top, cap_x, y_top - 0.55)
        draw_wire(fig, cap_x, y_top - 0.95, cap_x, y_bot)
        # Conectar al siguiente diodo si no es el último
        if i < 3:
            x_next = diode_positions[i][0]
            draw_wire(fig, x1 - 0.08, y_top, x_next, y_top)

    # Salida
    fig.add_annotation(x=3.3, y=y_top + 0.25, text="<b>V_DC</b>", showarrow=False,
                       font=dict(color="#34D399", size=11))
    draw_wire(fig, diode_positions[-1][1] - 0.08, y_top, 3.3, y_top)

    # GND rail
    draw_wire(fig, 0.0, y_top, 0.0, y_bot)
    draw_wire(fig, 0.0, y_bot, 3.3, y_bot)
    draw_gnd(fig, 1.5, y_bot)
    # Adapt the figure x range to fit Dickson (wider)
    fig.update_layout(xaxis=dict(visible=False, range=[-0.3, 3.6]))
    return fig


render()
