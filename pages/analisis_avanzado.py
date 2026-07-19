"""
Análisis avanzado — Sensibilidad · Monte Carlo · Supercondensador · Presupuesto · Arte
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from analysis.avanzado import (
    run_tornado, run_monte_carlo, run_rectifier_bw,
    run_link_budget, run_supercap, run_state_of_art,
)
from plots.charts import fig_tornado, fig_mc_histogram, fig_rectifier_bw, COLORS
from configs.parametros import CANONICAL
from utils.pagina import (encabezado, badge_exploracion,
                          control_interactivo, donde_se_desarrolla as _ref)


def render():
    encabezado(
        "Análisis avanzado",
        "Sensibilidad · Monte Carlo · Supercondensador · Presupuesto · Estado del arte",
        que_es=("Página de **herramientas avanzadas** para analizar incertidumbre, "
                 "sensibilidad y comparativa con literatura. Reúne 6 herramientas "
                 "técnicas en tabs separados."),
        para_que_sirve=("Cuantificar **qué tan sensible** es el resultado a cada parámetro "
                         "(tornado), **qué incertidumbre** introduce el entorno (Monte Carlo), "
                         "**cómo dimensionar** el supercondensador, ver el **presupuesto "
                         "de enlace** detallado y comparar con el **estado del arte**."),
        entradas=("Controles en la parte superior de la página: EIRP, distancia, "
                  "frecuencia, R_load y número de muestras Monte Carlo. Cada pestaña tiene "
                  "además sus propios controles."),
        salidas=("6 tabs con tornado, histograma MC, curva BW del rectificador, waterfall "
                  "de presupuesto de enlace, métricas del supercap y tabla comparativa "
                  "con publicaciones recientes."),
        como_leer=("**Tornado**: la barra más larga arriba es el parámetro **dominante** "
                   "(el que más cambia P_DC al variar en ±Δ). **Monte Carlo**: el IC 95 % "
                   "te dice en qué rango cae P_DC el 95 % de las veces si EIRP/dist/freq "
                   "varían con la incertidumbre del entorno. **Estado del arte**: ojo, "
                   "el 85 % de este trabajo es el cap del modelo, no una medida."),
    )

    badge_exploracion()

    st.markdown(
        "Estas herramientas examinan **cuán robusto** es el resultado de referencia: "
        "qué parámetro pesa más, qué incertidumbre añade el entorno, cómo se dimensiona "
        "el almacenamiento y cómo se sitúa el trabajo frente a la literatura."
    )
    _ref("§5.3.2 Robustez del resultado: incertidumbre, sensibilidad y Monte Carlo")

    with st.container(border=True):
        st.markdown("**:material/tune: Parámetros de análisis** "
                    "*(afectan a varias pestañas)*")
        cc1, cc2, cc3, cc4, cc5 = st.columns(5)
        with cc1:
            eirp_dbm = st.slider("EIRP [dBm]", 40.0, 80.0, 72.15, 1.0)
        with cc2:
            dist_m = st.slider("Distancia [m]", 50.0, 500.0, 100.0, 10.0)
        with cc3:
            freq_ghz = st.select_slider("Frecuencia [GHz]",
                                        options=[0.470, 0.550, 0.700, 0.900, 0.915],
                                        value=0.550)
        with cc4:
            R_load = st.select_slider("R_load [Ω]",
                                      options=[500, 700, 1000, 1300, 2000, 3000],
                                      value=1300)
        with cc5:
            n_mc = st.select_slider("N muestras MC",
                                    options=[500, 1000, 2000, 5000, 10000],
                                    value=10000)
    control_interactivo(
        magnitud="**EIRP** (potencia de la fuente, dBm), **distancia** (m), **frecuencia** "
                 "(GHz), **R_load** (carga del rectificador, Ω) y **N** (muestras del Monte "
                 "Carlo). Definen el punto de operación que se analiza.",
        referencia="Escenario de referencia: EIRP = 72,15 dBm · d = 100 m · f = 550 MHz · "
                   "R_load = 1 300 Ω · N = 10 000.",
        al_subir="Más EIRP o menor distancia → más P_DC. Más N → estimación Monte Carlo más "
                 "estable (pero más lenta).",
        al_bajar="Menos EIRP o más distancia → menos P_DC; pocas muestras → histograma "
                 "ruidoso; R_load muy lejos de 1 300 Ω desadapta el diodo.",
        limite="Fuera de EIRP 40–80 dBm o d 50–500 m se sale del rango analizado; el modelo "
               "es válido en el régimen de cosecha (P_in baja), no para fuentes dedicadas.",
    )

    tab_tornado, tab_mc, tab_bw, tab_link, tab_sc, tab_art = st.tabs([
        ":material/bar_chart: Sensibilidad (tornado)",
        ":material/casino: Monte Carlo",
        ":material/bandwidth: Ancho de banda rectificador",
        ":material/receipt_long: Presupuesto de enlace",
        ":material/battery_charging_full: Supercondensador",
        ":material/leaderboard: Estado del arte",
    ])

    # ── Tornado ──────────────────────────────────────────────────────────────
    with tab_tornado:
        st.markdown(
            "Variación de cada parámetro en ±Δ manteniendo los demás fijos. "
            "El ancho de la barra indica el impacto sobre P_DC [µW]."
        )
        with st.spinner("Calculando sensibilidad..."):
            sens = run_tornado(eirp_dbm=eirp_dbm, dist_m=dist_m,
                               freq_ghz=freq_ghz, R_load=float(R_load))

        with st.container(horizontal=True):
            st.metric("P_DC base",      f"{sens['baseline']:.1f} µW",   border=True)
            st.metric("Parámetro dominante",
                      sens['results'][0]['param'] if sens['results'] else "—", border=True)
            if sens['results']:
                st.metric("Impacto máx.",
                          f"{sens['results'][0]['pct_change']:.0f}%", border=True)

        st.plotly_chart(fig_tornado(sens))

        st.markdown("#### Tabla de sensibilidad")
        df_s = pd.DataFrame([{
            'Parámetro':    r['param'],
            'Base':         r['base'],
            'Δ':            r['delta'],
            'P_DC bajo [µW]':  f"{r['val_low']:.2f}",
            'P_DC alto [µW]':  f"{r['val_high']:.2f}",
            'Impacto [%]':     f"{r['pct_change']:.1f}",
        } for r in sens['results']])
        st.dataframe(df_s, hide_index=True)
        st.caption(
            "Δ EIRP = ±3 dB · Δ dist = ±20 m · Δ freq = ±0.05 GHz · Δ R_load = ±300 Ω"
        )
        _ref("§5.3.2 Robustez del resultado: incertidumbre, sensibilidad y Monte Carlo · "
             "Anexo B.7 Sensibilidad ante variación de Q_L y R_load")

    # ── Monte Carlo ───────────────────────────────────────────────────────────
    with tab_mc:
        st.markdown(
            r"""
Propagación de incertidumbre mediante Monte Carlo (N muestras). Este Monte Carlo mide la
sensibilidad al despliegue (entorno y emplazamiento), no la incertidumbre del modelo en
sí; esa segunda parte se trata en las limitaciones L1–L8.

| Parámetro | Distribución | σ / rango | Justificación |
|-----------|-------------|-----------|---------------|
| EIRP [dBm] | Normal | σ = 2 dB | Tolerancia de potencia de transmisores broadcast (regulación CRC) |
| Distancia [m] | Uniforme | ± 15 m | Imprecisión razonable de emplazamiento del nodo |
| Frecuencia [GHz] | Normal | σ = 0.01 GHz | Ancho del canal UHF (8 MHz / canal DVB-T) |

:material/info: **No incluido** en este MC (por estar declarado como hipótesis del modelo):
ganancia G (modelo paramétrico), η_rad (expresión empírica), IL nominal de la red L,
cap de PCE = 0,85.
"""
        )
        with st.spinner(f"Monte Carlo N={n_mc}... (puede tardar ~{n_mc//200} s)"):
            mc = run_monte_carlo(eirp_dbm=eirp_dbm, dist_m=dist_m,
                                 freq_ghz=freq_ghz, R_load=float(R_load),
                                 n_samples=n_mc)

        with st.container(horizontal=True):
            st.metric("Media P_DC",   f"{mc['mean']:.1f} µW",  border=True)
            st.metric("Std",          f"{mc['std']:.1f} µW",   border=True)
            st.metric("CV",           f"{mc['cv_pct']:.0f}%",  border=True)
            st.metric("IC 95%",
                      f"[{mc['ci_95'][0]:.0f}, {mc['ci_95'][1]:.0f}] µW", border=True)
            st.metric("P5 / P95",
                      f"[{mc['p5']:.0f}, {mc['p95']:.0f}] µW", border=True)

        st.plotly_chart(fig_mc_histogram(mc))
        st.caption(f"Muestras válidas (P_DC > 0): {mc['n_valid']}/{mc['n_total']}")
        _ref("§5.3.2 Robustez del resultado: incertidumbre, sensibilidad y Monte Carlo · "
             "§6.3 Limitaciones del estudio (L1–L8) · Figura 14 (Monte Carlo de P_DC)")

    # ── Ancho de banda rectificador ───────────────────────────────────────────
    with tab_bw:
        st.markdown(
            "Ancho de banda a **−3 dB de PCE** del rectificador doubler SMS7630. "
            "Se barre la frecuencia alrededor del centro de la banda UHF."
        )
        st.info(
            ":material/info: **No es una afirmación del proyecto.** Es una propiedad "
            "derivada del modelo del rectificador. Se incluye para mostrar que el "
            "doubler opera en una banda amplia, no para sustentar un valor "
            "específico.",
            icon=":material/info:",
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            pin_bw = st.slider("Pin [dBm]", -25.0, 0.0, -10.0, 1.0, key='pin_bw')
        with col2:
            fc_mhz = st.select_slider("Centro [MHz]",
                                       options=[470, 550, 700, 900, 2450],
                                       value=550, key='fc_bw')
        with col3:
            span_mhz = st.select_slider("Span [MHz]",
                                         options=[500, 800, 1000, 1500, 2000],
                                         value=1000, key='span_bw')
        control_interactivo(
            magnitud="**Pin** (potencia de entrada, dBm), **Centro** (frecuencia central "
                     "del barrido, MHz) y **Span** (anchura del barrido, MHz). Definen "
                     "sobre qué tramo se mide el ancho de banda a −3 dB de PCE.",
            referencia="Pin = −10 dBm, centro = 550 MHz (banda del Escenario B).",
            al_subir="Más Pin → la PCE sube hacia su techo y la curva se ensancha; más "
                     "Span muestra un tramo de frecuencia mayor.",
            al_bajar="Menos Pin → la PCE cae y el pico se estrecha; Span pequeño hace zoom "
                     "alrededor del centro.",
            limite="Es una propiedad **exploratoria** del modelo, no un resultado del "
                   "informe; fuera del régimen de cosecha (Pin > 0 dBm) deja de ser "
                   "representativa.",
        )
        with st.spinner("Calculando BW..."):
            bw = run_rectifier_bw(Pin_dBm=pin_bw,
                                   freq_center_mhz=float(fc_mhz),
                                   freq_span_mhz=float(span_mhz))

        with st.container(horizontal=True):
            st.metric("PCE máx.",   f"{bw['pce_max']*100:.1f}%",            border=True)
            st.metric("f @ PCE máx.", f"{bw['freq_max_hz']/1e6:.0f} MHz",   border=True)
            st.metric("BW −3 dB",   f"{bw['bw_3dB_hz']/1e6:.0f} MHz",      border=True)
            st.metric("f_low",      f"{bw['f_low_3dB']/1e6:.0f} MHz",       border=True)
            st.metric("f_high",     f"{bw['f_high_3dB']/1e6:.0f} MHz",      border=True)
            st.metric("BW fraccional", f"{bw['fractional_bw']*100:.0f}%",   border=True)

        st.plotly_chart(fig_rectifier_bw(bw))
        _ref("§3.7 Física del diodo Schottky · §3.7.2 Frecuencia de corte del SMS7630")

    # ── Presupuesto de enlace ─────────────────────────────────────────────────
    with tab_link:
        st.markdown(
            "Presupuesto de enlace RF→DC formal. "
            "Los valores de ganancia, η_mm, η_IMN y PCE son los canónicos del Escenario B."
        )
        with st.spinner("Generando presupuesto..."):
            lb = run_link_budget(eirp_dbm=eirp_dbm, dist_m=dist_m, freq_ghz=freq_ghz)

        df_lb = pd.DataFrame(lb).rename(columns={
            'parameter':      'Parámetro',
            'value':          'Valor',
            'unit':           'Unidad',
            'cumulative_dBm': 'Acumulado [dBm]',
        })
        st.dataframe(df_lb, hide_index=True)

        # Waterfall chart
        cum_vals = [float(r['cumulative_dBm']) for r in lb]
        fig_wf   = go.Figure(go.Scatter(
            x=list(range(len(cum_vals))), y=cum_vals,
            mode='lines+markers',
            line=dict(color=COLORS[0], width=2),
            marker=dict(size=8),
            text=[r['parameter'] for r in lb],
            hovertemplate='%{text}<br>Acumulado: %{y:.1f} dBm',
        ))
        fig_wf.update_layout(
            template='simple_white', height=350,
            title={'text': 'Waterfall — Potencia acumulada en la cadena', 'font': {'size': 13}},
            xaxis=dict(tickvals=list(range(len(lb))),
                       ticktext=[r['parameter'][:20] for r in lb],
                       tickangle=-40),
            yaxis_title='Potencia acumulada [dBm]',
            margin=dict(l=60, r=20, t=45, b=120),
        )
        st.plotly_chart(fig_wf)
        st.caption(
            f"Ganancia: {CANONICAL['gain_dBi']:.2f} dBi · "
            f"η_mm: {CANONICAL['eta_mm']:.4f} · "
            f"η_IMN: {CANONICAL['eta_imn']:.4f} · "
            f"PCE: {CANONICAL['PCE']*100:.0f}% · "
            f"η_PMIC: {CANONICAL['eta_pmic']*100:.0f}%"
        )
        _ref("§3.5 Propagación RF y modelo de Friis · "
             "§5.3.1 Cálculo de la cadena de potencia · "
             "Anexo B.16 (presupuesto de enlace RF→DC)")

    # ── Supercondensador ──────────────────────────────────────────────────────
    with tab_sc:
        st.markdown(
            "Dimensionamiento del supercondensador para almacenamiento de energía. "
            "Referencia: ciclo LoRa SF12 con 1% DC (E_ciclo ≈ 259 mJ)."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            P_dc_input = st.number_input("P_DC entrada [µW]",
                                          min_value=1.0, max_value=50000.0,
                                          value=float(CANONICAL['P_dc_uW']), step=10.0)
            E_ciclo_mj = st.number_input("E_ciclo [mJ]",
                                          min_value=1.0, max_value=5000.0,
                                          value=float(CANONICAL['E_ciclo_mJ']), step=1.0)
        with col2:
            C_mf = st.select_slider("Capacitancia [mF]",
                                     options=[100, 220, 330, 470, 1000, 4700],
                                     value=330)
            V_max_sc = st.number_input("V_max [V]", 1.5, 5.5, 3.3, 0.1)
        with col3:
            V_min_sc = st.number_input("V_min [V]", 0.5, 3.0, 1.8, 0.1)
            ESR_sc   = st.number_input("ESR [Ω]", 0.0, 500.0, 0.0, 5.0,
                                       help="0 Ω reproduce el Anexo B.9 del documento "
                                            "(sin pérdidas óhmicas de carga).")

        with st.spinner("Calculando supercondensador..."):
            sc = run_supercap(P_dc_uW=P_dc_input, E_ciclo_mJ=E_ciclo_mj,
                              C_mF=float(C_mf), V_max=V_max_sc,
                              V_min=V_min_sc, ESR_ohm=ESR_sc)

        with st.container(horizontal=True):
            st.metric("C",            f"{sc['C_mF']:.0f} mF",          border=True)
            st.metric("E_útil",       f"{sc['E_useful_mJ']:.0f} mJ",   border=True)
            st.metric("Ciclos / carga", f"{sc['n_ciclos']:.1f}",        border=True)
            st.metric("T_carga",      f"{sc['t_charge_min']:.1f} min",  border=True)
            st.metric("η_storage",    f"{sc['eta_storage']*100:.1f}%",  border=True)
            st.metric("P_leak",       f"{sc['P_leak_uW']:.2f} µW",      border=True)

        st.markdown(f"""
| Parámetro | Valor |
|-----------|-------|
| Capacitancia | {sc['C_mF']:.0f} mF ({sc['C_mF']*1e-3:.3f} F) |
| V_max / V_min | {sc['V_max']:.2f} V / {sc['V_min']:.2f} V |
| E_total almacenada | {sc['E_stored_mJ']:.1f} mJ |
| E_útil (V_max→V_min) | {sc['E_useful_mJ']:.1f} mJ |
| E_ciclo LoRa | {sc['E_ciclo_mJ']:.2f} mJ |
| Ciclos por carga completa | {sc['n_ciclos']:.1f} |
| Tiempo de carga | {sc['t_charge_s']:.0f} s = **{sc['t_charge_min']:.1f} min** |
| ESR | {sc['ESR_ohm']:.1f} Ω |
| P_auto-descarga | {sc['P_leak_uW']:.2f} µW |
| η_almacenamiento | {sc['eta_storage']*100:.1f}% |
""")
        _ref("Anexo B.9 Caracterización temporal del supercondensador · "
             "§4.6 Etapa 3: Presupuesto energético del nodo IoT")

    # ── Estado del arte ───────────────────────────────────────────────────────
    with tab_art:
        st.markdown(
            "Comparativa del sistema propuesto con el estado del arte en rectenas fractales y multi-banda."
        )
        st.warning(
            ":material/warning: **Cuidado al leer la comparación.** El valor de PCE "
            "de \"Este trabajo\" (85 %) corresponde al **cap del modelo**, no a una "
            "medición experimental. Los demás trabajos reportan valores **medidos** "
            "en prototipos físicos. No es una comparación entre iguales. El proyecto lo "
            "declara explícitamente como limitación L6.",
            icon=":material/warning:",
        )
        with st.spinner("Cargando tabla..."):
            pce_max_val = CANONICAL['PCE'] * 100
            art = run_state_of_art(pce_max_pct=pce_max_val, pdc_uw=CANONICAL['P_dc_uW'])

        df_art = pd.DataFrame(art).rename(columns={
            'reference':  'Referencia',
            'journal':    'Revista',
            'antenna':    'Antena',
            'substrate':  'Sustrato',
            'freq_range': 'Rango f',
            'bands':      'Bandas',
            'gain_dBi':   'G [dBi]',
            'PCE_max':    'PCE máx.',
            'Pin_dBm':    'Pin [dBm]',
            'P_dc_uW':    'P_DC [µW]',
            'rectifier':  'Rectificador',
            'notes':      'Notas',
        })
        cols_show = ['Referencia', 'Rango f', 'Bandas', 'G [dBi]', 'PCE máx.',
                     'Pin [dBm]', 'P_DC [µW]', 'Sustrato', 'Notas']
        # Columnas de tipo mixto (p. ej. 'Bandas' con 'UWB') → texto, para Arrow.
        st.dataframe(df_art[cols_show].astype(str), hide_index=True)

        # Gráfico comparativo PCE máx.
        refs_with_pce = [r for r in art if isinstance(r['PCE_max'], str) and '%' in str(r['PCE_max'])]
        if refs_with_pce:
            labels = [r['reference'].split('(')[0].strip() for r in refs_with_pce]
            pces   = [float(str(r['PCE_max']).replace('%', '')) for r in refs_with_pce]
            colors = [COLORS[4] if 'Este trabajo' in r['reference'] else COLORS[0]
                      for r in refs_with_pce]
            fig_cmp = go.Figure(go.Bar(
                x=labels, y=pces,
                marker_color=colors,
                text=[f"{p:.1f}%" for p in pces], textposition='outside',
            ))
            fig_cmp.update_layout(
                template='simple_white', height=360,
                title={'text': 'PCE máxima — comparativa estado del arte', 'font': {'size': 13}},
                xaxis_tickangle=-30,
                yaxis_title='PCE [%]',
                margin=dict(l=60, r=20, t=45, b=120),
            )
            st.plotly_chart(fig_cmp)
            st.caption(":material/star: Este trabajo destacado en amarillo")

        _ref("§3.2 Estado del arte en rectenas fractales · "
             "§6.3 Limitaciones del estudio (L6: PCE = 0,85 es cap del modelo) · "
             "Anexo B.20 (resumen estructural por subsistema)")

    st.divider()
    st.page_link("pages/sensibilidad.py",
                 label="Siguiente - sensibilidad parametrica →",
                 icon=":material/tune:")


render()
