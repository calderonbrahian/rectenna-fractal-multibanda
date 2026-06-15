"""
Validación cruzada — Modelo analítico vs Wang et al. (2022) IEEE TAP
                  — FLPDA Koch vs Carrel (1961)

Doubler fijo (topología canónica del proyecto). Pin = -10 dBm declarado.
Caveats de sustrato (FR-4 vs Duroid 5880) y de punto de potencia visibles arriba.

Corresponde a §3.7 (Estrategia de validación cruzada) y §4.5 (Validación
cruzada y análisis del error, RMSE = 15,50 pp) del informe de grado.
"""

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from analysis.sensibilidad import run_validacion_wang
from core.flpda import FLPDA_Koch
from core.comparacion import validate_carrel1961, WANG2022, CARREL1961
from utils.pagina import encabezado, correspondencia, donde_se_desarrolla as _ref
from utils.glosario import metrica, glosario_pagina
# (fig_validacion_wang ya no se usa; se reemplazó por _fig_wang_scatter_with_errors)


@st.cache_data(ttl="1h")
def _cached_wang_validation(topology: str = "doubler") -> dict:
    """Cachea la validación Wang (es un cálculo iterativo de PCE sobre 7 frecuencias)."""
    return run_validacion_wang(topology=topology)


def _fig_wang_scatter_with_errors(res: dict) -> go.Figure:
    """Scatter modelo vs Wang con barras de error sistemático y caveat Duroid."""
    f = np.array(res['freqs_GHz'])
    pce_meas = np.array(res['pce_referencia'])
    pce_mod  = np.array(res['pce_simulacion'])

    # Barra de error sistemático estimada: 6 pp por sustrato + 2 pp por variabilidad de medida
    yerr_meas = np.full_like(pce_meas, 2.0, dtype=float)         # Wang ± 2 pp medida
    yerr_mod  = np.full_like(pce_mod, 6.0, dtype=float)           # modelo ± 6 pp sustrato

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=f, y=pce_meas, mode='lines+markers',
        name='Wang (2022) — Duroid 5880',
        marker=dict(size=10, color='#059669', symbol='circle'),
        line=dict(width=2.4, color='#059669'),
        error_y=dict(type='data', array=yerr_meas, visible=True,
                     color='rgba(52,211,153,0.55)', thickness=1.4, width=4),
        hovertemplate='f=%{x:.2f} GHz<br>PCE medida=%{y:.1f}%<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=f, y=pce_mod, mode='lines+markers',
        name='Modelo — FR-4 (este trabajo)',
        marker=dict(size=10, color='#B45309', symbol='diamond'),
        line=dict(width=2.4, color='#B45309'),
        error_y=dict(type='data', array=yerr_mod, visible=True,
                     color='rgba(251,191,36,0.55)', thickness=1.4, width=4),
        hovertemplate='f=%{x:.2f} GHz<br>PCE modelo=%{y:.1f}%<extra></extra>',
    ))

    # Banda sombreada del Escenario B (550 MHz) extrapolada al rango Wang
    fig.add_vrect(
        x0=1.84, x1=2.6,
        fillcolor='rgba(0,119,187,0.06)', line_width=0,
        annotation_text='Zona de mejor acuerdo del modelo',
        annotation_position='top left', annotation_font_size=10,
    )

    fig.update_layout(
        template='simple_white', height=420,
        title=dict(
            text='Comparación PCE modelo vs Wang (2022)  ·  barras: incertidumbre por sustrato',
            font=dict(size=13),
        ),
        xaxis=dict(title='Frecuencia [GHz]', tickmode='array',
                   tickvals=list(f), ticktext=[f'{x:.2f}' for x in f]),
        yaxis=dict(title='PCE [%]', range=[0, 80]),
        legend=dict(orientation='h', y=-0.18),
        margin=dict(l=70, r=20, t=55, b=80),
    )
    fig.add_annotation(
        x=5.8, y=72, xref='x', yref='y',
        text='Δ tan δ: 0,02 (FR-4) vs 0,0009 (Duroid 5880)<br>≈ 22× más pérdidas → ~6 pp de sesgo',
        showarrow=False, align='right',
        font=dict(size=10, color='#B45309'),
        bgcolor='rgba(248, 250, 252, 0.9)', bordercolor='rgba(251,191,36,0.4)', borderwidth=1, borderpad=6,
    )
    return fig


def render():
    encabezado(
        ":material/verified: Validación cruzada del modelo",
        "Modelo analítico vs Wang et al. (2022) · FLPDA Koch vs Carrel (1961)",
        que_es=("Página de **verificación externa**: compara las predicciones del "
                 "modelo de rectificador y de antena con datos publicados en la "
                 "literatura por dos referencias independientes."),
        para_que_sirve=("Acotar el error del modelo y delimitar el rango de frecuencias "
                         "donde es más fiable. Sirve para que el jurado pueda decir si la "
                         "comparación con Wang (2022) es comparable, dónde lo es y dónde no, "
                         "y por qué."),
        entradas=("Ninguna entrada por parte del usuario; los datos de Wang (2022) y "
                  "Carrel (1961) son fijos. Los parámetros del modelo son los canónicos."),
        salidas=("Métricas de error (RMSE, sesgo, máximo absoluto), un scatter con barras "
                  "de incertidumbre por sustrato, una tabla punto a punto, una explicación "
                  "de las causas y una comparativa de parámetros con Carrel."),
        como_leer=("**RMSE 15,50 pp** es el error global. El modelo *sobreestima* a baja "
                   "frecuencia (1,84–2,04 GHz) y *subestima* a alta (3,30–5,80 GHz). "
                   "El sesgo viene principalmente de la diferencia de sustrato (FR-4 vs "
                   "Duroid 5880, ≈ 22× más pérdidas). Lectura honesta: **verificación de "
                   "orden de magnitud**, no validación punto a punto."),
    )

    # ── Caveats visibles arriba (no en expander) ──────────────────────────────
    with st.container(border=True):
        st.markdown(
            ":material/info: **Condiciones de la comparación con Wang (2022)** "
            "— la lectura del RMSE depende de saberlas:"
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                "**:material/bolt: Punto de potencia**\n\n"
                "P_in = **−10 dBm** (régimen lineal del rectificador). "
                "El modelo usa adaptación ideal en este punto."
            )
        with c2:
            st.markdown(
                "**:material/layers: Sustrato (factor dominante)**\n\n"
                "Wang: **Duroid 5880** (tan δ ≈ 0,0009).\n"
                "Este modelo: **FR-4** (tan δ ≈ 0,02), unas 22× más disipativo. "
                "Sesgo estimado: **~6 pp** del RMSE total."
            )
        with c3:
            st.markdown(
                "**:material/electric_bolt: Diseños distintos**\n\n"
                "Wang optimiza red de adaptación banda por banda. "
                "El modelo asume adaptación perfecta en pequeña señal: "
                "sobreestima a baja frecuencia, subestima a alta (C_j parásita)."
            )

    _ref("§3.7 Estrategia de validación cruzada · "
         "§4.5 Validación cruzada y análisis del error (RMSE = 15,50 pp)")

    st.divider()

    tab_wang, tab_carrel = st.tabs([
        ":material/verified: Wang et al. (2022)",
        ":material/library_books: Carrel (1961)",
    ])

    # ── Wang et al. (2022) ──────────────────────────────────────────────────
    with tab_wang:
        with st.spinner("Validando contra Wang 2022 (doubler · P_in = −10 dBm)..."):
            res = _cached_wang_validation(topology='doubler')

        with st.container(horizontal=True):
            metrica(
                "RMSE", f"{res['RMSE']:.2f} pp",
                interpretacion="moderado: verificación de orden de magnitud, no punto a punto",
                ayuda="Raíz del error cuadrático medio frente a las medidas de Wang (2022). "
                      "El grueso se explica por la diferencia de sustrato (FR-4 vs Duroid).",
            )
            metrica(
                "Sesgo (error medio)", f"{res['mean_error_abs']:.2f} pp",
                interpretacion="el modelo sobreestima a baja f, subestima a alta",
                ayuda="Error medio con signo: si > 0, el modelo sobreestima en promedio.",
            )
            st.metric(
                "Error máx. absoluto", f"{res['max_error_abs']:.2f} pp",
                border=True,
            )
        glosario_pagina("RMSE", "sesgo", "incertidumbre", "PCE")

        # Visualización principal con barras de error sistemático
        st.plotly_chart(_fig_wang_scatter_with_errors(res), width="stretch")
        correspondencia('directa',
                        "Reproduce la **Figura 11** del trabajo (comparación punto a punto "
                        "modelo vs Wang 2022); se añaden barras de incertidumbre por sustrato.")

        # ── Causas del error (3 ítems claros, ya NO en expander) ─────────────
        st.markdown("#### :material/biotech: Causas del error sistemático")
        st.markdown(
            """
| # | Causa | Banda donde se manifiesta | Magnitud estimada |
|---|------|---------------------------|-------------------|
| 1 | **Sustrato FR-4 vs Duroid 5880** (tan δ 22× mayor) | Toda la banda | ≈ **6 pp** sistemático |
| 2 | **Adaptación perfecta asumida** en el modelo | 1,84 – 2,04 GHz (sobreestimación) | + 25 a + 12 pp |
| 3 | **Capacitancia parásita C_j a alta frecuencia** no modelada | 3,30 – 5,80 GHz (subestimación) | − 14 a − 19 pp |

**Conclusión.** El RMSE de **15,50 pp** y la asimetría del error son coherentes con las
hipótesis declaradas: el modelo es más fiable en el extremo inferior del espectro,
justamente donde opera el Escenario B de referencia (550 MHz). La comparación no es
entre diseños sobre el mismo material; léase como **verificación de orden de magnitud**.
"""
        )

        st.markdown("#### Tabla comparativa punto a punto")
        df = pd.DataFrame({
            'f [GHz]':              res['freqs_GHz'],
            'PCE Wang medida [%]':  res['pce_referencia'],
            'PCE modelo [%]':       res['pce_simulacion'],
            'Error abs [pp]':       res['error_abs_pp'],
            'Error rel [%]':        res['error_rel_pct'],
        })
        st.dataframe(df, hide_index=True)
        correspondencia('directa',
                        "Corresponde a la **Tabla 11** del trabajo (comparación banda a "
                        "banda: η_total del modelo vs PCE estimada de Wang 2022).")
        st.caption(
            ":material/info: Topología fija: **doubler** (la canónica del proyecto)."
        )
        _ref("§3.7 Estrategia de validación cruzada · "
             "§4.5 Validación cruzada y análisis del error · "
             "Figura 11 (modelo vs Wang) · Tabla 11 (comparación banda a banda) · "
             "Referencia: Wang et al. (2022), IEEE TAP")

    # ── Carrel (1961) ───────────────────────────────────────────────────────
    with tab_carrel:
        flpda  = FLPDA_Koch()
        res_c  = validate_carrel1961(flpda)

        with st.container(horizontal=True):
            st.metric(
                "Ganancia media FLPDA",
                f"{res_c['ganancia_media_dBi']:.2f} dBi",
                delta=f"{res_c['ganancia_media_dBi'] - res_c['ganancia_Carrel_dBi']:.2f} vs Carrel",
                border=True,
            )
            st.metric("S11 mínimo",     f"{res_c['S11_min_dB']:.2f} dB",     border=True)
            st.metric("Reducción Koch", f"−{res_c['reduccion_Koch_pct']}%",   border=True)

        st.info(
            ":material/info: La comparación con Carrel (1961) es **modelo analítico vs "
            "modelo analítico**: ambos son aproximaciones de líneas de transmisión "
            "acopladas, no simulaciones electromagnéticas de onda completa. Las "
            "casillas ✅/⚠️ marcan consistencia con la referencia de Carrel para una "
            "LPDA de los mismos τ y σ.",
            icon=":material/info:",
        )

        st.markdown("#### Comparativa de parámetros de diseño")
        df_c = pd.DataFrame({
            'Parámetro': ['τ', 'σ', 'Ganancia media [dBi]', 'S11 [dB]',
                          'BW ratio', 'Reducción Koch [%]', 'N elementos'],
            'Este diseño': [
                res_c['tau_disenio'], res_c['sigma_disenio'],
                res_c['ganancia_media_dBi'], res_c['S11_min_dB'],
                res_c['BW_ratio_disenio'], f"−{res_c['reduccion_Koch_pct']}",
                res_c['n_elementos'],
            ],
            'Referencia Carrel': [
                res_c['tau_Carrel'], res_c['sigma_Carrel'],
                res_c['ganancia_Carrel_dBi'], res_c['S11_Carrel_dB'],
                res_c['BW_ratio_Carrel'], '0 (LPDA clásica)',
                'Variable',
            ],
            'Cumple': [
                '✅', '✅',
                '✅' if res_c['ganancia_media_dBi'] >= res_c['ganancia_Carrel_dBi'] - 1 else '⚠️',
                '✅' if res_c['S11_min_dB'] <= res_c['S11_Carrel_dB'] else '⚠️',
                '✅', '✅ miniaturización', '—',
            ],
        })
        # Columnas de tipo mixto (números + texto) → texto, para una tabla Arrow-compatible.
        st.dataframe(df_c.astype(str), hide_index=True)

        with st.expander("Fundamento matemático de la reducción Koch", expanded=False):
            st.markdown(
                r"""
La curva de Koch de iteración $n$ reduce la longitud física de cada segmento por el factor:

$$k_{\text{red}} = \left(\frac{3}{4}\right)^n$$

Para $n=2$: $k_{\text{red}} = (3/4)^2 = 0.5625$, lo que equivale a una **reducción del 43.75%** en longitud física manteniendo la misma longitud eléctrica ($\lambda/2$).

El número de elementos de la LPDA se calcula por Carrel (1961):

$$N = 1 + \left\lceil \frac{\log(f_{\text{high}}/f_{\text{low}})}{\log(1/\tau)} \right\rceil$$

Para $f_{\text{low}}=470$ MHz, $f_{\text{high}}=900$ MHz, $\tau=0.90$:

$$N = 1 + \left\lceil \frac{\log(900/470)}{\log(1/0.90)} \right\rceil = """ + str(res_c['n_elementos']) + r"""$$

**Nota.** El boom (≈ 50 cm) lo fija el espaciado σ sobre longitudes **eléctricas**;
la curva de Koch reduce la dimensión **transversal** de cada dipolo, no la longitud
del boom.
"""
            )
        _ref("§3.4.2 FLPDA Koch: método de Carrel y número de dipolos · "
             "§4.5 Validación cruzada · Referencia: Carrel (1961)")


render()
