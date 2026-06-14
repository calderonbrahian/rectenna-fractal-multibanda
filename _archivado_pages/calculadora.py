"""
Calculadora del modelo — Sandbox de exploración paramétrica.
NO contiene resultados de la tesis. Banner ámbar persistente.
Compara la exploración del usuario contra el valor canónico siempre visible.
"""

import math

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from configs.parametros import CANONICAL
from utils.pagina import encabezado, badge_exploracion, impacto_parametros, como_interpretar


def render():
    encabezado(
        ":material/calculate: Calculadora del modelo",
        "Sandbox: mueve los parámetros y observa cómo varía la cadena RF→DC.",
        que_es=("Una calculadora interactiva del modelo completo de la rectena. "
                "Tomando los mismos modelos que el pipeline canónico, recalcula "
                "P_in, P_DC, V_DC y el tiempo de carga del nodo IoT con los "
                "parámetros que decidas."),
        para_que_sirve=("Responder preguntas tipo *“¿y si el transmisor estuviera "
                         "a 200 m?”*, *“¿y si la antena tuviera 2 dBi menos por "
                         "errores de fabricación?”* o *“¿y si la red de adaptación "
                         "tuviera más pérdidas?”*. Todo sin tocar el resultado oficial."),
        entradas=("Sliders de EIRP, distancia, frecuencia, ganancia, η_IMN, PCE y "
                  "corrección urbana. Cada parámetro tiene un rango sugerido y un "
                  "valor por defecto coincidente con el canónico."),
        salidas=("Una tabla con tu exploración vs el valor canónico, una fila de "
                  "5 KPIs y una curva exploratoria P_DC vs distancia o vs EIRP "
                  "con un marcador azul en el equivalente al escenario de referencia."),
        como_leer=("Si una celda en la columna Δ es **positiva**, tu exploración "
                   "supera al canónico; si es **negativa**, lo subestima. El marcador "
                   "azul ★ en la gráfica te indica dónde caería el escenario de "
                   "referencia si dejaras los demás parámetros como están."),
    )

    badge_exploracion()

    # ── Controles ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("Parámetros del escenario")
        eirp_dbm  = st.slider("EIRP [dBm]", 40.0, 80.0, 70.0, 1.0,
                              help=("Potencia isotrópica radiada equivalente del "
                                    "transmisor. 70 dBm = 10 kW EIRP (TDT Nutibara). "
                                    "Rango razonable: 40 (estación pequeña) a 80 dBm "
                                    "(broadcast urbano de alta potencia)."))
        dist_m    = st.slider("Distancia [m]", 50, 2000, 100, 10,
                              help=("Distancia del nodo IoT al transmisor. "
                                    "P_DC cae como 1/d² (Friis). Rangos típicos: "
                                    "50–200 m en zonas urbanas densas, hasta 2 km "
                                    "en línea de vista directa al cerro."))
        freq_mhz  = st.select_slider("Frecuencia [MHz]",
                                      options=[470, 550, 700, 800, 900, 915],
                                      value=550,
                                      help=("Canal del transmisor. 550 MHz es el "
                                            "canónico (canal 30 UHF, RTVC). 915 MHz "
                                            "es ISM Colombia para LoRa."))
        st.caption("---")
        st.subheader("Parámetros de la antena/cadena")
        gain_dBi  = st.slider("Ganancia FLPDA [dBi]",
                              4.0, 10.0, float(CANONICAL['gain_dBi']), 0.1,
                              help="Canónico 7,10 dBi. Margen razonable ±2 dBi por errores de fabricación.")
        eta_imn   = st.slider("η_IMN red L", 0.85, 1.00,
                              float(CANONICAL['eta_imn']), 0.005,
                              help="Canónico 0,9484 con IL = 0,23 dB nominal.")
        pce       = st.slider("PCE rectificador", 0.20, 0.85,
                              float(CANONICAL['PCE']), 0.05,
                              help="Canónico 0,85 (cap del modelo). PCE reales: 0,55–0,75.")
        l_urb_dB  = st.slider("L_urb (corrección urbana) [dB]", 0.0, 12.0,
                              float(CANONICAL['L_urb_dB']), 0.5,
                              help="ITU-R P.1546: 0 (espacio libre), 6 (urbano), 10 (denso).")
        st.caption("---")
        st.button(":material/restart_alt: Restaurar valores canónicos",
                  on_click=_reset_to_canonical, width="stretch")

    # ── Bloque explicativo: significado físico de cada parámetro ─────────────
    impacto_parametros([
        {"nombre": "Potencia isotrópica radiada equivalente del transmisor",
         "simbolo": "EIRP [dBm]",
         "significado": ("Potencia que el transmisor *parece* radiar en todas las direcciones por igual. "
                          "Incluye la potencia eléctrica y la ganancia de la antena emisora."),
         "rango": "40–80 dBm. Canónico TDT Nutibara: 70 dBm.",
         "ecuacion": r"P_{in}\,[\mathrm{dBm}] = \mathrm{EIRP} - \mathrm{FSPL} - L_{urb} + G",
         "impacto": "+3 dB en EIRP → ×2 en P_in → ×2 en P_DC. Lineal en escala log."},
        {"nombre": "Distancia entre transmisor y receptor",
         "simbolo": "d [m]",
         "significado": ("Separación física entre la torre TDT y el nodo IoT. Determina la "
                          "dilución geométrica de la densidad de potencia (la sphera de radiación crece con d²)."),
         "rango": "50–2 000 m. Canónico: 100 m.",
         "ecuacion": r"\mathrm{FSPL} = 20\log_{10}(4\pi d / \lambda)",
         "impacto": "Doblar la distancia → −6 dB en P_in → ÷4 en P_DC."},
        {"nombre": "Frecuencia del canal de operación",
         "simbolo": "f [MHz]",
         "significado": ("Frecuencia central de la emisión RF. Afecta la longitud de onda (λ = c/f) "
                          "y por tanto la captación de la antena y las pérdidas de propagación."),
         "rango": "470–915 MHz (UHF + ISM Colombia).",
         "ecuacion": r"\lambda = c / f",
         "impacto": "A menor f → menor FSPL → más P_in (a igual G, η)."},
        {"nombre": "Ganancia realizada de la antena receptora",
         "simbolo": "G [dBi]",
         "significado": ("Cuántos dB la antena receptora concentra la potencia hacia la dirección del "
                          "transmisor en comparación con un isotrópico ideal. Incluye η_rad."),
         "rango": "5–10 dBi para una LPDA bien diseñada. Canónico: 7,10 dBi.",
         "ecuacion": r"P_{in} = \mathrm{EIRP}\cdot G\cdot(\lambda/4\pi d)^2",
         "impacto": "+1 dBi en G → +1 dB en P_in → +26 % en P_DC."},
        {"nombre": "Eficiencia de la red de adaptación L",
         "simbolo": "η_IMN",
         "significado": ("Fracción de la potencia disponible en la antena que pasa la red de adaptación "
                          "L sin disiparse en las resistencias parasíticas de L y C."),
         "rango": "0,85–1,00. Canónico: 0,9484 (IL = 0,23 dB).",
         "ecuacion": r"\eta_{IMN} = (1-|\Gamma|^2)\cdot 10^{-\mathrm{IL}/10}",
         "impacto": "Cada −1 % en η_IMN → −1 % aprox. en P_DC."},
        {"nombre": "Eficiencia de conversión RF→DC del rectificador",
         "simbolo": "PCE",
         "significado": ("Fracción de la potencia RF entregada al diodo que termina como corriente DC útil. "
                          "El modelo recorta a 0,85 como cota termodinámica del doblador."),
         "rango": "0,20–0,85. Canónico: 0,85 (cap activo en el escenario de referencia).",
         "ecuacion": r"\mathrm{PCE} = \min(P_{DC}/P_{in,rect}, 0{,}85)",
         "impacto": "PCE = 0,60 → P_DC ≈ 1 156 µW (70 % del canónico)."},
        {"nombre": "Corrección de propagación urbana ITU-R P.1546",
         "simbolo": "L_urb [dB]",
         "significado": ("Atenuación adicional por encima del espacio libre debida al entorno "
                          "(edificios, vegetación, multitrayectos). Es un valor estadístico mediano."),
         "rango": "0 (espacio libre), 6 (urbano denso), hasta 12 (muy denso).",
         "ecuacion": r"P_{in} = \mathrm{EIRP} - \mathrm{FSPL} - L_{urb} + G",
         "impacto": "+3 dB en L_urb → ÷2 en P_in → ÷2 en P_DC."},
    ])

    # ── Cálculo de la cadena con los valores del usuario ─────────────────────
    C0 = 3e8
    f_hz = freq_mhz * 1e6
    lam = C0 / f_hz
    FSPL = 20.0 * math.log10(4.0 * math.pi * dist_m / lam)
    P_in_dBm = eirp_dbm - FSPL - l_urb_dB + gain_dBi
    P_in_W = 10 ** ((P_in_dBm - 30.0) / 10.0)
    # Cadena de 4 factores sobre P_in (η_rad ya en G):
    eta_mm = CANONICAL['eta_mm']             # fijo al canónico (no es variable de despliegue)
    eta_pmic = CANONICAL['eta_pmic']
    P_dc_W = P_in_W * eta_mm * eta_imn * pce * eta_pmic
    P_dc_uW = P_dc_W * 1e6

    R_load = CANONICAL['R_load_ohm']
    V_dc_mV = (math.sqrt(max(P_dc_W * R_load, 0.0))) * 1000.0
    cold_ok = V_dc_mV >= CANONICAL['V_cs_mV']
    T_ciclo = CANONICAL['E_ciclo_mJ'] * 1e-3 / (P_dc_W + 1e-30)
    msg_dia = 86400.0 / T_ciclo if T_ciclo > 0 else 0.0

    # ── Comparación lado a lado: tu exploración vs canónico ──────────────────
    st.subheader("Tu exploración vs valor oficial de la tesis")
    def _delta_str(user, canon, unit="", decimals=1):
        d = user - canon
        sign = "+" if d > 0 else ("−" if d < 0 else "±")
        return f"{sign}{abs(d):.{decimals}f}{unit}"

    df_cmp = pd.DataFrame([
        ("P_in en antena",  f"+{P_in_dBm:.2f} dBm",  f"+{CANONICAL['P_in_dBm']:.2f} dBm",
         _delta_str(P_in_dBm, CANONICAL['P_in_dBm'], " dB", 2)),
        ("FSPL",            f"{FSPL:.2f} dB",        f"{CANONICAL['FSPL_dB']:.2f} dB",
         _delta_str(FSPL, CANONICAL['FSPL_dB'], " dB", 2)),
        ("P_DC",            f"{P_dc_uW:.1f} µW",     f"{CANONICAL['P_dc_uW']:.1f} µW",
         _delta_str(P_dc_uW, CANONICAL['P_dc_uW'], " µW", 0)),
        ("V_DC",            f"{V_dc_mV:.0f} mV",     f"{CANONICAL['V_dc_mV']:.0f} mV",
         _delta_str(V_dc_mV, CANONICAL['V_dc_mV'], " mV", 0)),
        ("Cold-start",      "✓ Viable" if cold_ok else "✗ NO", "✓ Viable",
         "—" if cold_ok else "✗"),
        ("T_ciclo SF12",    f"{T_ciclo:.0f} s" if T_ciclo < 86400 else "> 1 día",
                            f"{CANONICAL['T_ciclo_s']:.0f} s",
         _delta_str(T_ciclo, CANONICAL['T_ciclo_s'], " s", 0) if T_ciclo < 86400 else "—"),
        ("Mensajes / día",  f"≈ {msg_dia:.0f}" if msg_dia > 0 else "—",
                            f"≈ {86400/CANONICAL['T_ciclo_s']:.0f}",
         _delta_str(msg_dia, 86400/CANONICAL['T_ciclo_s'], "", 0) if msg_dia > 0 else "—"),
    ], columns=["Magnitud", "Exploración", "Tesis (canónico)", "Δ"])
    st.dataframe(df_cmp, hide_index=True, height=300,
                  column_config={
                      "Δ": st.column_config.TextColumn("Δ vs tesis", width="small",
                                                        help="Diferencia tu exploración − valor canónico"),
                  })

    st.divider()

    # ── KPIs grandes ─────────────────────────────────────────────────────────
    with st.container(horizontal=True):
        delta_pdc = P_dc_uW - CANONICAL['P_dc_uW']
        st.metric("P_DC", f"{P_dc_uW:.0f} µW",
                  delta=f"{delta_pdc:+.0f} µW vs canónico", delta_color="off", border=True)
        st.metric("V_DC", f"{V_dc_mV:.0f} mV",
                  delta=f"{V_dc_mV - CANONICAL['V_dc_mV']:+.0f} mV", delta_color="off", border=True)
        st.metric("Cold-start", "✓ Viable" if cold_ok else "✗ NO",
                  delta=f"V_DC vs umbral 130 mV", delta_color="off", border=True)
        st.metric("T_ciclo (SF12)",
                  f"{T_ciclo:.0f} s" if T_ciclo < 86400 else "> 24 h",
                  delta=f"{T_ciclo - CANONICAL['T_ciclo_s']:+.0f} s",
                  delta_color="inverse", border=True)
        st.metric("Mensajes / día", f"≈ {msg_dia:.0f}",
                  delta=f"{msg_dia - 86400/CANONICAL['T_ciclo_s']:+.0f}",
                  delta_color="normal", border=True)

    st.divider()

    # ── Curvas exploratorias: P_DC vs (distancia | EIRP) ─────────────────────
    st.subheader("Curva exploratoria")
    eje = st.segmented_control(
        "Eje a barrer", options=["P_DC vs distancia", "P_DC vs EIRP"],
        default="P_DC vs distancia", help="Mueve los sliders y la curva responde."
    ) or "P_DC vs distancia"

    R_load = CANONICAL['R_load_ohm']

    if eje == "P_DC vs distancia":
        x_arr = np.linspace(20, 2000, 300)
        y_arr = _pdc_curve_vs_d(x_arr, eirp_dbm, gain_dBi, l_urb_dB, lam,
                                 eta_mm, eta_imn, pce, eta_pmic)
        x_marker = 100.0
        y_marker = CANONICAL['P_dc_uW']
        x_title = 'Distancia [m]'
        x_tickvals = [20, 50, 100, 200, 500, 1000, 2000]
        xlogtype = 'log'
        sweep_label = (
            f"EIRP={eirp_dbm:.0f} dBm · G={gain_dBi:.2f} dBi · "
            f"L_urb={l_urb_dB:.1f} dB · η_IMN={eta_imn:.4f} · PCE={pce:.2f}"
        )
    else:
        x_arr = np.linspace(40, 80, 300)
        y_arr = _pdc_curve_vs_eirp(x_arr, dist_m, gain_dBi, l_urb_dB, lam,
                                    eta_mm, eta_imn, pce, eta_pmic)
        x_marker = 70.0
        # P_DC equivalente a EIRP=70 con la distancia actual del usuario:
        FSPL_user = 20.0 * math.log10(4.0 * math.pi * dist_m / lam)
        Pin_eq_dBm = 70.0 - FSPL_user - l_urb_dB + gain_dBi
        Pin_eq_W = 10 ** ((Pin_eq_dBm - 30.0) / 10.0)
        y_marker = (Pin_eq_W * eta_mm * eta_imn * pce * eta_pmic * 1e6)
        x_title = 'EIRP [dBm]'
        x_tickvals = [40, 50, 60, 70, 80]
        xlogtype = 'linear'
        sweep_label = (
            f"d={dist_m} m · G={gain_dBi:.2f} dBi · "
            f"L_urb={l_urb_dB:.1f} dB · η_IMN={eta_imn:.4f} · PCE={pce:.2f}"
        )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_arr, y=y_arr, mode='lines',
        line=dict(width=2.5, color='#FBBF24'),
        name='Tus parámetros',
        hovertemplate=f'{x_title}=%{{x}}<br>P_DC=%{{y:.1f}} µW<extra></extra>',
    ))
    if y_marker is not None:
        # Texto del marcador: el real de la tesis si el usuario está en (100 m, 70 dBm),
        # o el equivalente con los parámetros actuales en caso contrario.
        is_canonical_point = (eje == "P_DC vs distancia" and x_marker == 100.0) or \
                              (eje == "P_DC vs EIRP" and dist_m == 100)
        marker_label = (
            f"  Canónico: {CANONICAL['P_dc_uW']:.0f} µW"
            if is_canonical_point
            else f"  Eq. canónico (con tus parámetros): {y_marker:.0f} µW"
        )
        fig.add_trace(go.Scatter(
            x=[x_marker], y=[y_marker], mode='markers+text',
            marker=dict(size=14, color='#0077BB', symbol='star',
                         line=dict(color='white', width=1)),
            text=[marker_label],
            textposition='middle right',
            textfont=dict(color='#0077BB'),
            showlegend=False,
        ))
    fig.add_hline(y=13, line=dict(color='rgba(204,51,17,0.6)', dash='dash', width=1),
                  annotation_text='Umbral cold-start (≈ 13 µW)',
                  annotation_position='bottom right', annotation_font_size=10)
    fig.update_layout(
        template='simple_white', height=380,
        title=dict(text=f'{eje}  ·  {sweep_label}', font=dict(size=13)),
        xaxis=dict(title=x_title, type=xlogtype, tickvals=x_tickvals),
        yaxis=dict(title='P_DC [µW]', type='log'),
        margin=dict(l=70, r=20, t=55, b=60),
    )
    st.plotly_chart(fig, width="stretch")

    st.caption(
        ":material/info: La marca azul es el valor oficial de la tesis. "
        "La curva amarilla responde en vivo a los sliders de la barra lateral."
    )

    como_interpretar(
        titulo_grafica="la curva exploratoria",
        objetivo=("Comparar la potencia DC que tu configuración entrega en función de la "
                   "distancia (o la EIRP) contra el valor oficial del proyecto a 100 m."),
        ejes=("**Eje X** (logarítmico): distancia al transmisor en metros, o EIRP en dBm "
               "según el toggle. **Eje Y** (logarítmico): P_DC en µW."),
        tendencias=("La caída sigue la ley de Friis (1/d²). En escala log-log eso es una recta "
                     "con pendiente −2 (por cada década de distancia, dos décadas menos de potencia). "
                     "La línea roja de **13 µW** marca el umbral en el que la tensión rectificada "
                     "ya no permite el arranque en frío del PMIC."),
        si_sube_baja=("Si la curva queda **por encima** del marcador azul ★ en el punto de "
                       "referencia (100 m), tu configuración entrega más potencia que la canónica. "
                       "Si queda **por debajo**, entrega menos. Cuanto antes la curva cruza el umbral "
                       "rojo, menor el alcance autónomo de tu rectena."),
        impacto_parametros=("Subir EIRP, ganancia o frecuencia (baja en UHF) **eleva** toda la curva. "
                             "Subir L_urb o reducir η_IMN/PCE **baja** la curva. La forma de la "
                             "curva (pendiente) no cambia: solo se traslada arriba o abajo."),
    )


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _pdc_curve_vs_d(d_arr, eirp_dbm, gain_dBi, l_urb_dB, lam,
                     eta_mm, eta_imn, pce, eta_pmic):
    """P_DC [µW] en función de la distancia, con parámetros del usuario."""
    out = np.zeros_like(d_arr, dtype=float)
    for i, d in enumerate(d_arr):
        FSPLi = 20.0 * math.log10(4.0 * math.pi * d / lam)
        Pi_dBm = eirp_dbm - FSPLi - l_urb_dB + gain_dBi
        Pi_W = 10 ** ((Pi_dBm - 30.0) / 10.0)
        out[i] = Pi_W * eta_mm * eta_imn * pce * eta_pmic * 1e6
    return out


def _pdc_curve_vs_eirp(eirp_arr, dist_m, gain_dBi, l_urb_dB, lam,
                        eta_mm, eta_imn, pce, eta_pmic):
    """P_DC [µW] en función de la EIRP, a distancia fija."""
    FSPL_fixed = 20.0 * math.log10(4.0 * math.pi * dist_m / lam)
    out = np.zeros_like(eirp_arr, dtype=float)
    for i, eirp in enumerate(eirp_arr):
        Pi_dBm = eirp - FSPL_fixed - l_urb_dB + gain_dBi
        Pi_W = 10 ** ((Pi_dBm - 30.0) / 10.0)
        out[i] = Pi_W * eta_mm * eta_imn * pce * eta_pmic * 1e6
    return out


_CALC_KEYS = ['eirp_dbm', 'dist_m', 'freq_mhz', 'gain_dBi', 'eta_imn', 'pce', 'l_urb_dB']


def _reset_to_canonical():
    """Borra los widget keys de la calculadora para que Streamlit los repinte con
    los valores por defecto (canónicos). Robusto: ignora silenciosamente las
    claves que no existen aún."""
    for k in _CALC_KEYS:
        st.session_state.pop(k, None)


render()
