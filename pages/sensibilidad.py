"""
Análisis de sensibilidad paramétrica.
Tabs: Q_L · R_load · τ–σ FLPDA
"""

import streamlit as st
import plotly.graph_objects as go

from analysis.sensibilidad import sweep_Q_L, sweep_R_load, sweep_tau_sigma
from plots.charts import fig_sweep_generic, fig_heatmap_tau_sigma
from utils.exportar import sweep_a_csv
from utils.pagina import (encabezado, badge_exploracion, correspondencia,
                          control_interactivo, donde_se_desarrolla as _ref)
from utils.glosario import criterio, aporta


def render():
    encabezado(
        "Sensibilidad paramétrica",
        "Barridos individuales sobre Q_L (inductor), R_load (PMIC) y mapa τ–σ del FLPDA.",
        que_es=("Página de **barridos individuales**: fija un parámetro como variable y "
                 "mantiene los demás canónicos. Sirve para entender la sensibilidad de la "
                 "PCE a un parámetro a la vez."),
        para_que_sirve=("Responder preguntas tipo *¿qué pasa si el inductor SMD tiene "
                         "Q = 25 en lugar de 40?*, *¿qué pasa si el PMIC presenta una R_load "
                         "distinta?* o *¿cuál sería el mapa de ganancia variando τ y σ "
                         "del FLPDA?*."),
        entradas=("Controles dentro de la página: frecuencia de evaluación y potencia de "
                  "entrada. Rectificación fija (doblador). Cada pestaña varía un parámetro "
                  "distinto."),
        salidas=("Tres tabs: curva PCE vs Q_L (inductor), curva PCE vs R_load (PMIC), y "
                  "mapa de calor de ganancia FLPDA en función de τ y σ con el punto de diseño "
                  "marcado con una estrella."),
        como_leer=("Una **pendiente fuerte** indica alta sensibilidad: pequeños cambios en "
                   "ese parámetro alteran la PCE. Una **curva plana** alrededor del punto "
                   "canónico indica robustez. El mapa τ–σ muestra las regiones de diseño "
                   "candidatas con su ganancia esperada."),
    )

    badge_exploracion()

    st.markdown(
        "Cada barrido fija un parámetro como variable y mantiene los demás en su valor "
        "de diseño, para ver **cuánto cambia el resultado** al moverlo. Una curva plana "
        "alrededor del punto canónico indica robustez; una pendiente fuerte, alta "
        "sensibilidad."
    )
    _ref("§4.3.2 Análisis de sensibilidad paramétrica y Monte Carlo")

    topology = 'doubler'  # fijo: topología canónica
    with st.container(border=True):
        st.markdown("**:material/tune: Controles de sensibilidad**")
        cs1, cs2, cs3 = st.columns([1, 1, 1.3])
        with cs1:
            f_GHz = st.select_slider(
                "Frecuencia [GHz]",
                options=[1.84, 2.04, 2.36, 2.54, 3.30, 4.76, 5.80],
                value=2.36,
                key='f_sens',
                help="Frecuencias canónicas de la validación Wang (2022).",
            )
        with cs2:
            Pin_dBm = st.slider(
                "Pin [dBm]",
                min_value=-30.0, max_value=0.0, value=-10.0, step=1.0,
                key='pin_sens',
                help="−10 dBm es el punto de comparación con Wang (régimen lineal).",
            )
        with cs3:
            st.caption(":material/lock: Rectificación: **doblador Greinacher** "
                       "(la del proyecto)")
    control_interactivo(
        magnitud="**Frecuencia** de evaluación (GHz, las 7 bandas canónicas de Wang) y "
                 "**Pin** (potencia de entrada al rectificador, dBm). Fijan el punto en el "
                 "que se barre cada parámetro de las pestañas.",
        referencia="f = 2,36 GHz y Pin = **−10 dBm** (el punto de comparación con Wang en "
                   "régimen lineal).",
        al_subir="Más Pin acerca la PCE a su techo y aplana las curvas; frecuencias más "
                 "altas penalizan por la capacitancia parásita del diodo.",
        al_bajar="Menos Pin → zona sub-umbral, donde la sensibilidad a Q_L y R_load se "
                 "acentúa.",
        limite="Fuera del rango de cosecha (Pin > 0 dBm) o de las bandas canónicas, la "
               "comparación con Wang deja de ser representativa.",
    )

    tab_ql, tab_rl, tab_ts = st.tabs([
        ":material/tune: Factor Q inductor (Q_L)",
        ":material/cable: Resistencia de carga (R_load)",
        ":material/grid_on: Mapa τ–σ FLPDA",
    ])

    # ── Factor Q inductor ─────────────────────────────────────────────────────
    with tab_ql:
        st.markdown(
            "Sensibilidad de la PCE y pérdida de inserción respecto al "
            "factor de calidad Q del inductor SMD. Valor de diseño: **Q_L = 40**."
        )
        with st.spinner("Barriendo Q_L..."):
            data = sweep_Q_L(topology=topology, f_GHz=f_GHz, Pin_dBm=Pin_dBm)
        col1, col2 = st.columns(2)
        with col1:
            fig = fig_sweep_generic(
                data['Q_L'], {'PCE [%]': data['PCE_pct']},
                'Q_L (inductor SMD)', 'PCE [%]',
                f'PCE vs Q_L — {f_GHz} GHz · {topology}',
            )
            fig.add_vline(x=40, line=dict(color='#B45309', dash='dash', width=1),
                          annotation_text='Q_L=40 (diseño)', annotation_position='top right')
            st.plotly_chart(fig)
        with col2:
            fig2 = fig_sweep_generic(
                data['Q_L'], {'IL [dB]': data['IL_dB']},
                'Q_L (inductor SMD)', 'IL [dB]',
                f'Pérdida de inserción vs Q_L — {f_GHz} GHz',
            )
            fig2.add_vline(x=40, line=dict(color='#B45309', dash='dash', width=1))
            st.plotly_chart(fig2)
        st.caption(
            "**R_L** = ω·L / Q_L. A mayor Q_L, menor pérdida óhmica → mayor PCE. "
            "Inductores SMD 0402/0603 típicos: Q_L = 30–60."
        )
        st.download_button(
            "Descargar CSV",
            sweep_a_csv(data, ['Q_L', 'PCE_pct', 'IL_dB']),
            file_name=f"sensibilidad_QL_{topology}_{f_GHz}GHz.csv",
            mime="text/csv",
        )
        correspondencia('complementaria',
                        "Barridos de sensibilidad del **Apéndice E.7**; no aparecen como "
                        "figura numerada en el documento.")
        criterio("Q_L 40")
        aporta("un Q_L bajo aumenta la pérdida de la red de adaptación (IL) → menor η_IMN → "
               "menos P_DC.")
        _ref("Apéndice E.7 Sensibilidad ante variación de Q_L y R_load · "
             "§2.8 Redes de adaptación de impedancias (IMN)")

    # ── R_load ────────────────────────────────────────────────────────────────
    with tab_rl:
        st.markdown(
            "Sensibilidad de PCE y Vdc respecto a la resistencia de carga equivalente. "
            "El BQ25504 presenta ~1300 Ω de entrada en condición nominal."
        )
        with st.spinner("Barriendo R_load..."):
            data_r = sweep_R_load(topology=topology, f_GHz=f_GHz, Pin_dBm=Pin_dBm)
        col1, col2 = st.columns(2)
        with col1:
            fig = fig_sweep_generic(
                data_r['R_load_ohm'], {'PCE [%]': data_r['PCE_pct']},
                'R_load [Ω]', 'PCE [%]',
                f'PCE vs R_load — {f_GHz} GHz · {topology}',
            )
            fig.add_vline(x=1300, line=dict(color='#B45309', dash='dash', width=1),
                          annotation_text='BQ25504 (1300 Ω)', annotation_position='top left')
            st.plotly_chart(fig)
        with col2:
            fig2 = fig_sweep_generic(
                data_r['R_load_ohm'], {'Vdc [mV]': data_r['Vdc_mV']},
                'R_load [Ω]', 'Vdc [mV]',
                f'Vdc vs R_load — {f_GHz} GHz · {topology}',
            )
            fig2.add_vline(x=1300, line=dict(color='#B45309', dash='dash', width=1))
            st.plotly_chart(fig2)
        st.download_button(
            "Descargar CSV",
            sweep_a_csv(data_r, ['R_load_ohm', 'PCE_pct', 'Vdc_mV']),
            file_name=f"sensibilidad_Rload_{topology}_{f_GHz}GHz.csv",
            mime="text/csv",
        )
        correspondencia('complementaria',
                        "Barridos de sensibilidad del **Apéndice E.7**; no aparecen como "
                        "figura numerada en el documento.")
        aporta("la R_load fija el punto de operación del rectificador; 1 300 Ω (entrada del "
               "BQ25504) es el valor de diseño que sostiene el P_DC de referencia.")
        _ref("Apéndice E.7 Sensibilidad ante variación de Q_L y R_load · "
             "§2.7 Física del diodo Schottky (carga del rectificador)")

    # ── Mapa τ–σ ──────────────────────────────────────────────────────────────
    with tab_ts:
        st.markdown(
            "Mapa de ganancia media de la FLPDA Koch en función de los parámetros "
            "de diseño τ (razón de escala) y σ (espaciado relativo) de Carrel (1961). "
            "El punto de diseño del Escenario B es **τ=0.90, σ=0.15**."
        )
        with st.spinner("Generando mapa τ–σ (puede tardar ~10 s)..."):
            data_ts = sweep_tau_sigma()
        fig = fig_heatmap_tau_sigma(data_ts)
        fig.add_trace(
            go.Scatter(x=[0.15], y=[0.90],
                       mode='markers',
                       marker=dict(symbol='star', size=14, color='#B45309'),
                       name='Diseño (τ=0.90, σ=0.15)',
                       showlegend=True)
        )
        st.plotly_chart(fig)
        st.caption(
            "**Eje Y** τ ∈ [0.80, 0.95] | **Eje X** σ ∈ [0.10, 0.22] | "
            "Ganancia promediada sobre 470–900 MHz | ⭐ = punto de diseño Escenario B"
        )
        correspondencia('complementaria',
                        "Mapa de diseño del **Apéndice E.4** (τ–σ del FLPDA), construido a "
                        "partir del barrido paramétrico; no es una figura numerada.")
        _ref("Apéndice E.4 Mapa de diseño τ–σ del FLPDA · "
             "§3.4.2 FLPDA Koch: método de Carrel y número de dipolos")


render()
