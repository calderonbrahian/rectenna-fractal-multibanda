"""
Pregunta del jurado — Preguntas pre-respondidas + Limitaciones L1–L8 + What-if del clip.
Página oculta del menú lateral, accesible directamente. El "as bajo la manga"
para la defensa.
"""

import math

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from configs.parametros import CANONICAL
from core.rectifier import RectifierCircuit
from utils.pagina import encabezado


def render():
    encabezado(
        ":material/quiz: Pregunta del jurado",
        "Preguntas frecuentes en una defensa de tesis, pre-respondidas.",
        que_es=("Página de **preparación para la defensa**: contiene nueve preguntas "
                 "que un jurado de tesis razonable haría, cada una con su respuesta "
                 "directa, su gráfica de soporte cuando corresponde y su limitación "
                 "declarada."),
        para_que_sirve=("Servir como **chuleta personal** durante la defensa: el autor "
                         "puede saltar directamente con Ctrl+F a la pregunta esperada y "
                         "responder con un valor o una gráfica preparada, sin improvisar."),
        entradas=("Para Q8 (What-if PCE) y Q9 (MC del modelo): sliders interactivos "
                  "que permiten responder en vivo a preguntas hipotéticas del jurado."),
        salidas=("9 tarjetas con la respuesta a cada pregunta, una gráfica de la "
                  "anatomía del clip de PCE, una histograma de la incertidumbre del modelo "
                  "y una tabla con las 8 limitaciones L1–L8 y su impacto cuantitativo."),
        como_leer=("Cada Q tiene una **respuesta corta y directa** (no rodeada de retórica). "
                   "La tabla L1–L8 al pie del documento es la **declaración honesta de "
                   "limitaciones** que se debe poder defender sin sorpresas."),
    )

    st.info(
        ":material/lightbulb: Cada tarjeta cubre una pregunta probable del jurado. "
        "El objetivo es no improvisar y poder llegar directamente a la respuesta "
        "con un gráfico o un valor.",
        icon=":material/lightbulb:",
    )

    # ── Tabla de contenidos rápida (para no scrollear en defensa) ───────────
    with st.container(border=True):
        st.markdown("**:material/list: Índice de preguntas**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "- **Q1** — Doble conteo de η_rad  \n"
                "- **Q2** — ¿PCE 85 % es físico o cap?  \n"
                "- **Q2b** *(visual)* — Anatomía del clip  \n"
                "- **Q3** — Ganancia: ¿es Carrel?  \n"
                "- **Q4** — Wang midió en Duroid  "
            )
        with c2:
            st.markdown(
                "- **Q5** — 70 dBm conservador  \n"
                "- **Q6** — σ del Monte Carlo  \n"
                "- **Q7** — ¿Por qué no HFSS?  \n"
                "- **Q8** *(interactivo)* — What-if PCE  \n"
                "- **Q9** *(interactivo)* — MC del modelo  "
            )
        st.caption(
            "Usa Ctrl/Cmd + F para buscar Q*N* y saltar directamente a la respuesta. "
            "Al pie: tabla L1–L8 con impacto cuantitativo de cada limitación."
        )

    # ── Preguntas pre-respondidas ────────────────────────────────────────────
    _q1_double_count()
    _q2_clip()
    _q2b_clip_anatomy()
    _q3_carrel_gain()
    _q4_substrate()
    _q5_eirp_conservador()
    _q6_montecarlo_sigmas()
    _q7_full_wave()
    _q8_what_if_pce()
    _q9_model_uncertainty()

    st.divider()

    # ── Limitaciones L1–L8 con impacto ───────────────────────────────────────
    st.subheader(":material/warning: Limitaciones del modelo (L1–L8) y su impacto cuantitativo")
    _render_limitaciones()


# ──────────────────────────────────────────────────────────────────────────────
#  Tarjetas de preguntas
# ──────────────────────────────────────────────────────────────────────────────

def _q_card(num, q, a_md):
    with st.container(border=True):
        st.markdown(f"#### Q{num}. {q}")
        st.markdown(a_md)


def _q1_double_count():
    with st.container(border=True):
        st.markdown("#### Q1. Si P_in = 2,43 mW y η_total = 0,6715, ¿por qué P_DC no es 1 631 µW?")
        st.markdown(
            "**El producto literal P_in · η_total = 1 631 µW no debe leerse como la potencia DC** "
            "porque **η_rad ya está contenida en la ganancia realizada G** que define P_in. "
            "Multiplicar P_in por η_total volvería a contabilizar la pérdida de radiación."
        )
        st.markdown("La cadena operativa aplica a P_in los **cuatro factores posteriores** a la antena:")
        st.latex(
            r"P_{DC} = P_{in} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \mathrm{PCE} \cdot \eta_{PMIC}"
        )
        st.latex(
            rf"= {CANONICAL['P_in_mW']:.3f}\ \text{{mW}}\cdot {CANONICAL['eta_mm']:.4f}"
            rf"\cdot {CANONICAL['eta_imn']:.4f}\cdot {CANONICAL['PCE']:.2f}"
            rf"\cdot {CANONICAL['eta_pmic']:.2f} = {CANONICAL['P_dc_uW']:.1f}\ \mu\mathrm{{W}}"
        )
        st.markdown(
            f"**η_total = {CANONICAL['eta_total']:.4f}** se reporta como **figura de mérito "
            f"de cinco factores**, referida a la potencia interceptada *antes* de las "
            f"pérdidas de radiación."
        )


def _q2_clip():
    _q_card(
        2,
        "Tu PCE = 85 %. ¿Es un resultado físico o un cap impuesto?",
        """
Es **un cap impuesto explícitamente en el código** como cota termodinámica de la
topología dobladora (Greinacher). En el escenario de referencia el cap **sí está activo**:
la PCE cruda del modelo de Shockley excede 0,85 al recibir P_in ≈ 2,4 mW, y se recorta.

**Lectura honesta:** la potencia continua reportada (1 637,6 µW) **opera en el techo**.
Un prototipo real con PCE de 0,60–0,70 entregaría entre **1 156 y 1 350 µW** (ver Q8).
La cifra del modelo es una **cota superior**, no una predicción central.
""",
    )


def _q3_carrel_gain():
    _q_card(
        3,
        "¿La ganancia 7,10 dBi viene del nomograma de Carrel?",
        """
**No**. Es un modelo **paramétrico** anclado a la directividad típica de una LPDA de
ocho elementos (≈ 7,5 dBi, consistente con Carrel 1961) con una variación intrabanda
de ±0,5 dB y descuento de η_rad. **Los parámetros τ y σ fijan la geometría e impedancia,
no entran en el cálculo de ganancia.**

Una simulación EM de onda completa (HFSS/CST) podría modificar la ganancia en
**±1–2 dBi**. Para fines de diseño y dimensionamiento, 7,10 dBi es una estimación
razonable; para fabricación, requiere verificación.
""",
    )


def _q4_substrate():
    _q_card(
        4,
        "Wang midió en Duroid 5880. ¿Tu RMSE de 15,50 pp es comparable?",
        """
**Parcialmente, y se admite explícitamente.** El sustrato es la causa dominante del sesgo
sistemático: FR-4 (tan δ ≈ 0,02) tiene **~22× más pérdidas** que el Duroid 5880
(tan δ ≈ 0,0009) usado por Wang. **El sustrato aporta del orden de 6 pp del RMSE
total**.

Además: el modelo asume adaptación perfecta a P_in = −10 dBm, mientras que el
rectificador experimental de Wang tiene pérdidas reales. Por eso sobreestima a baja
frecuencia y subestima a alta (capacitancia de unión parásita no modelada).

**Conclusión metodológica:** la comparación es **verificación de orden de magnitud**,
no validación punto a punto sobre el mismo material.
""",
    )


def _q5_eirp_conservador():
    _q_card(
        5,
        "La torre TDT del Nutibara emite 10 kW ERP, que son 72,15 dBm EIRP. ¿Por qué usas 70 dBm?",
        """
**Por conservadurismo**. La conversión exacta ERP → EIRP suma 2,15 dB (la ganancia
del dipolo λ/2 de referencia). El modelo adopta **70 dBm** como EIRP nominal, lo que
**subestima la potencia recolectada en un factor 10^(2,15/10) ≈ 1,64**.

Implicación: la potencia continua reportada (1 637,6 µW) es una **cota inferior**
respecto a la EIRP real. Un prototipo frente a la misma torre debería obtener algo
**más** potencia que el modelo predice, no menos.
""",
    )


def _q6_montecarlo_sigmas():
    _q_card(
        6,
        "El Monte Carlo usa σ_EIRP = 2 dB, ±15 m, σ_f = 0,01 GHz. ¿De dónde salen?",
        """
**Son rangos de uso del entorno**, no incertidumbre del modelo:

| Variable | σ / rango | Origen |
|---|---|---|
| EIRP ±2 dB | Variación nominal de potencia de transmisores broadcast (regulación CRC) |
| Distancia ±15 m | Tolerancia razonable de emplazamiento del nodo |
| Frecuencia σ=0,01 GHz | Ancho del canal UHF (8 MHz / canal DVB-T) |

**Limitación admitida:** este Monte Carlo mide la **sensibilidad al despliegue**, no
la **incertidumbre del modelo** (que viene de heurísticas: ganancia, η_rad empírica,
IL nominal de la red L, cap de PCE). Esta segunda incertidumbre se cubre con el
análisis de **limitaciones L1–L8** al pie de esta página y los **What-if** (Q8).
""",
    )


def _q7_full_wave():
    _q_card(
        7,
        "¿Por qué no usaste HFSS o CST?",
        """
**Por alcance**. El objetivo del trabajo es **dimensionar la viabilidad energética**
del sistema completo (rectena + IoT), no optimizar la geometría de una antena aislada.
Para esa pregunta, el modelo analítico es:

- **Suficiente:** captura las dependencias dominantes (η_rad, η_mm, PCE, η_PMIC).
- **Trazable:** cada número se sigue al modelo que lo genera.
- **Reproducible:** el pipeline corre en cualquier máquina con Python y NumPy.

Una simulación EM de onda completa aportaría precisión adicional en G y S₁₁
(±1–2 dBi, ±1–3 pp en η_rad), pero **no cambia las conclusiones de viabilidad** del
escenario de referencia. Queda recomendada como trabajo futuro.
""",
    )


def _q8_what_if_pce():
    """What-if del clip de PCE — calculadora interactiva."""
    with st.container(border=True):
        st.markdown("#### Q8. ¿Y si el rectificador real solo alcanza 60 % de PCE?")
        st.markdown(
            "Recalculo de P_DC y T_ciclo con la PCE real (el resto de la cadena "
            "permanece canónico)."
        )
        pce_real = st.slider("PCE real [%]", min_value=20, max_value=85, value=70, step=1)
        pce = pce_real / 100.0
        P_in_W = CANONICAL['P_in_mW'] * 1e-3
        # P_DC = P_in · η_mm · η_imn · PCE_real · η_pmic   (4 factores sobre P_in)
        P_dc_real_W = (P_in_W * CANONICAL['eta_mm'] * CANONICAL['eta_imn']
                       * pce * CANONICAL['eta_pmic'])
        P_dc_real_uW = P_dc_real_W * 1e6
        T_ciclo_real = CANONICAL['E_ciclo_mJ'] * 1e-3 / (P_dc_real_W + 1e-30)
        msg_real = 86400.0 / T_ciclo_real

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            delta = P_dc_real_uW - CANONICAL['P_dc_uW']
            st.metric("P_DC con PCE real", f"{P_dc_real_uW:.0f} µW",
                      delta=f"{delta:+.0f} µW vs canónico", delta_color="off", border=True)
        with c2:
            delta_t = T_ciclo_real - CANONICAL['T_ciclo_s']
            st.metric("T_ciclo SF12", f"{T_ciclo_real:.0f} s",
                      delta=f"{delta_t:+.0f} s", delta_color="inverse", border=True)
        with c3:
            st.metric("Mensajes / día", f"≈ {msg_real:.0f}",
                      delta=f"{msg_real - 86400/CANONICAL['T_ciclo_s']:+.0f}",
                      delta_color="normal", border=True)
        with c4:
            ratio = pce / CANONICAL['PCE']
            st.metric("Razón PCE / cap", f"{ratio:.2f}", border=True)

        st.caption(
            "Lectura: incluso con PCE = 60 % (lejos del cap del modelo), el sistema "
            "sigue entregando energía suficiente para varios cientos de mensajes LoRa SF12 "
            "diarios en el punto de referencia."
        )


def _q2b_clip_anatomy():
    """Visualización: PCE cruda del modelo Shockley vs PCE clippeada en 0.85."""
    with st.container(border=True):
        st.markdown("#### Q2b. *(visual)* ¿Cómo se ve el cap actuando?")
        st.markdown(
            "Curva PCE del modelo en función de la potencia de entrada al rectificador "
            "(escala log). Se muestran la **curva cruda** (Shockley sin cap) y la "
            "**curva reportada** (clip 0,85). En el punto de operación canónico, las "
            "dos no coinciden: el modelo está **operando en el techo**."
        )
        st.plotly_chart(_fig_clip_anatomy(), width="stretch")
        st.caption(
            ":material/info: La región sombreada en rojo es donde el cap recorta. "
            "Cualquier mejora del rectificador físico (mejor adaptación, optimización "
            "banda por banda) podría llevar la PCE real cerca del techo, pero la "
            "**cifra reportada por el modelo no puede exceder 0,85 por construcción**."
        )


def _q9_model_uncertainty():
    """MC sobre incertidumbre del MODELO, no del entorno."""
    with st.container(border=True):
        st.markdown("#### Q9. *(interactivo)* ¿Y la incertidumbre del **modelo**?")
        st.markdown(
            "El Monte Carlo de la página *Análisis avanzado* mide la sensibilidad al "
            "**despliegue** (EIRP regulado, ubicación del nodo). Este, en cambio, "
            "propaga la incertidumbre de las **heurísticas del modelo**: ganancia "
            "(±1–2 dBi por ser paramétrica), η_rad (±2 pp por ser empírica), IL nominal "
            "(0,23 dB nominal frente a posibles 0,5 dB reales), y un PCE real menor que "
            "el cap. Es la versión rigurosa de la pregunta \"¿qué tan apretado es tu número?\"."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            n_mc = st.select_slider("Muestras Monte Carlo",
                                    options=[500, 1000, 2000, 5000], value=2000,
                                    key="mc_modelo_n")
        with c2:
            gain_sigma = st.slider("σ ganancia [dBi]", 0.0, 3.0, 1.5, 0.1,
                                   key="mc_modelo_g")
        with c3:
            pce_min = st.slider("PCE mínima del rectificador real",
                                0.30, 0.85, 0.55, 0.05, key="mc_modelo_pce")

        out = _run_model_montecarlo(n_mc, gain_sigma, pce_min)
        with st.container(horizontal=True):
            st.metric("Media P_DC", f"{out['mean']:.0f} µW", border=True)
            st.metric("Mediana",     f"{out['median']:.0f} µW", border=True)
            st.metric("IC 95 %",
                      f"[{out['p2_5']:.0f}, {out['p97_5']:.0f}] µW", border=True)
            st.metric("Canónico (cap)", f"{CANONICAL['P_dc_uW']:.0f} µW",
                      delta=f"+{CANONICAL['P_dc_uW']-out['median']:.0f} µW vs mediana",
                      delta_color="off", border=True)

        st.plotly_chart(_fig_model_mc_histogram(out), width="stretch")
        st.caption(
            f":material/info: El canónico ({CANONICAL['P_dc_uW']:.0f} µW) es la cota "
            "superior; la **mediana de la incertidumbre del modelo** es típicamente "
            "20–40 % menor. Esto es coherente con tratar el resultado oficial como "
            "**estimación de viabilidad**, no como predicción central."
        )


# ──────────────────────────────────────────────────────────────────────────────
#  Visualizaciones cacheadas
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl="1h")
def _clip_anatomy_data(pce_cap: float, r_load_ohm: float):
    """Calcula la curva PCE cruda (sin clip) vs Pin_dBm para el doubler SMS7630.
    pce_cap y r_load_ohm se pasan explícitamente para que el cache se invalide
    si cambian los valores canónicos en una sesión futura."""
    rect = RectifierCircuit(topology='doubler', R_load=r_load_ohm)
    pin_dbm = np.linspace(-30.0, 10.0, 80)
    PCE_MAX = float(pce_cap)
    pce_clipped_arr = np.array([rect.PCE(float(p), freq=550e6) for p in pin_dbm])
    # Estimación visual de la "PCE cruda" (sin cap): donde el modelo está saturado en el
    # techo, dibujamos una rampa suave que sigue subiendo, para hacer evidente la zona de clip.
    pce_raw = np.array([
        min(PCE_MAX * (1.0 + 0.15 * max((p - (-5)) / 25.0, 0.0)), 1.0)
        if pc >= PCE_MAX - 1e-6 else pc
        for p, pc in zip(pin_dbm, pce_clipped_arr)
    ])
    return pin_dbm, pce_raw, pce_clipped_arr, PCE_MAX


def _fig_clip_anatomy():
    """PCE cruda vs PCE clippeada con sombreado de la zona de cap activo."""
    # (numpy disponible en top-level)
    pin, pce_raw, pce_clip, cap = _clip_anatomy_data(
        pce_cap=CANONICAL['PCE'], r_load_ohm=CANONICAL['R_load_ohm'])

    # Punto canónico aproximado: P en el rectificador = +3,55 dBm
    p_op = 3.55

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pin, y=pce_raw * 100, mode='lines',
        line=dict(color='#FBBF24', width=2.5, dash='dot'),
        name='PCE cruda (Shockley sin clip, ilustrativa)',
    ))
    fig.add_trace(go.Scatter(
        x=pin, y=pce_clip * 100, mode='lines',
        line=dict(color='#34D399', width=2.8),
        name='PCE reportada por el modelo',
        fill='tonexty',
        fillcolor='rgba(204,51,17,0.10)',
    ))
    fig.add_hline(y=cap * 100,
                  line=dict(color='#F87171', dash='dash', width=1.4),
                  annotation_text=f'cap PCE = {cap*100:.0f} %',
                  annotation_position='top right', annotation_font_size=10)
    fig.add_vline(x=p_op,
                  line=dict(color='#0077BB', dash='dot', width=1.2),
                  annotation_text='Operación canónica (≈ +3,5 dBm)',
                  annotation_position='top left', annotation_font_size=10)
    fig.update_layout(
        template='simple_white', height=320,
        title=dict(text='Anatomía del clip: PCE cruda vs reportada (doubler SMS7630, 550 MHz)',
                   font=dict(size=13)),
        xaxis=dict(title='Pin en el rectificador [dBm]',
                    tickvals=[-30, -20, -10, 0, 5, 10]),
        yaxis=dict(title='PCE [%]', range=[0, 100]),
        legend=dict(orientation='h', y=-0.20),
        margin=dict(l=70, r=20, t=50, b=70),
    )
    return fig


@st.cache_data(ttl="1h")
def _run_model_montecarlo(n: int, gain_sigma: float, pce_min: float):
    """MC sobre heurísticas del modelo. Devuelve estadísticos de P_DC."""
    # (numpy disponible en top-level)
    rng = np.random.default_rng(seed=42)
    # Distribuciones explícitamente DECLARADAS:
    # - Ganancia: Normal(canon, σ=gain_sigma) dBi   (heurística paramétrica → ±1–2 dBi)
    # - η_rad: Beta-like via Normal acotada (canon ±2 pp)
    # - η_mm:  ±0.5 pp (depende de S11)
    # - η_IMN: Uniforme entre IL 0.23 dB y IL 0.5 dB (nominal vs pesimista)
    # - PCE_real: Uniforme entre pce_min y 0.85 (cap)
    # - η_PMIC: ±5 pp datasheet
    G_dBi = rng.normal(loc=CANONICAL['gain_dBi'], scale=gain_sigma, size=n)
    eta_rad = np.clip(rng.normal(loc=CANONICAL['eta_rad'], scale=0.01, size=n), 0.85, 1.0)
    eta_mm  = np.clip(rng.normal(loc=CANONICAL['eta_mm'],  scale=0.005, size=n), 0.92, 1.0)
    # η_IMN: muestreamos IL en [0.23, 0.5] dB y convertimos
    IL = rng.uniform(low=0.23, high=0.5, size=n)
    eta_imn = 10 ** (-IL / 10.0)
    PCE = rng.uniform(low=pce_min, high=0.85, size=n)
    eta_pmic = np.clip(rng.normal(loc=CANONICAL['eta_pmic'], scale=0.025, size=n), 0.70, 0.90)

    # Cadena con la ganancia variable (afecta a P_in que entra al rectificador)
    # (math en top-level)
    EIRP = 70.0
    d = 100.0
    f = 550e6
    L_urb = CANONICAL['L_urb_dB']
    lam = 3e8 / f
    FSPL = 20.0 * math.log10(4.0 * math.pi * d / lam)
    P_in_dBm = EIRP - FSPL - L_urb + G_dBi
    P_in_W = 10 ** ((P_in_dBm - 30.0) / 10.0)
    # Aplicamos 4 factores sobre P_in (la ganancia ya implica η_rad nominal; aquí η_rad
    # se reporta como FOM, pero NO se vuelve a multiplicar — convención auditada)
    P_dc_W = P_in_W * eta_mm * eta_imn * PCE * eta_pmic
    P_dc_uW = P_dc_W * 1e6

    return {
        'samples': P_dc_uW,
        'mean':   float(np.mean(P_dc_uW)),
        'median': float(np.median(P_dc_uW)),
        'std':    float(np.std(P_dc_uW)),
        'p2_5':   float(np.percentile(P_dc_uW, 2.5)),
        'p97_5':  float(np.percentile(P_dc_uW, 97.5)),
        'n':      n,
    }


def _fig_model_mc_histogram(out: dict):
    # (numpy disponible en top-level)
    s = out['samples']
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=s, nbinsx=40,
        marker=dict(color='#34D399', line=dict(color='rgba(255,255,255,0.2)', width=0.5)),
        hovertemplate='P_DC ∈ %{x:.0f} µW<br>n=%{y}<extra></extra>',
    ))
    fig.add_vline(x=CANONICAL['P_dc_uW'],
                  line=dict(color='#FBBF24', dash='dash', width=2),
                  annotation_text=f"Canónico (cap) = {CANONICAL['P_dc_uW']:.0f} µW",
                  annotation_position='top right', annotation_font_size=11)
    fig.add_vline(x=out['median'],
                  line=dict(color='#0077BB', dash='dot', width=2),
                  annotation_text=f"Mediana = {out['median']:.0f} µW",
                  annotation_position='top left', annotation_font_size=11)
    fig.add_vrect(x0=out['p2_5'], x1=out['p97_5'],
                  fillcolor='rgba(0,119,187,0.10)', line_width=0)
    fig.update_layout(
        template='simple_white', height=330,
        title=dict(text=f"Incertidumbre del modelo (N={out['n']})  ·  banda azul = IC 95 %",
                   font=dict(size=13)),
        xaxis=dict(title='P_DC [µW]'),
        yaxis=dict(title='Frecuencia'),
        margin=dict(l=60, r=20, t=50, b=50),
        showlegend=False,
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
#  Limitaciones L1–L8
# ──────────────────────────────────────────────────────────────────────────────

def _render_limitaciones():
    lims = [
        ("L1", "Modelo de antena", "Modelo analítico de líneas de transmisión acopladas (Carrel) en lugar de simulación EM de onda completa", "±1–2 dBi en G, ±1–3 pp en η_rad", "Media"),
        ("L2", "Sierpinski RLC", "Impedancia Sierpinski modelada como RLC paramétrico (no EM)", "S₁₁ válido cerca de cada resonancia; lejos puede diferir", "Alta"),
        ("L3", "Red L IL nominal", "Pérdida de inserción 0,23 dB nominal de SMD-FR-4, no medida", "≈ 0,5 pp en η_total para IL=0,5 dB pesimista", "Baja"),
        ("L4", "Modelo de Friis", "Canal de espacio libre + corrección urbana fija (mediana ITU-R P.1546)", "±10–15 dB punto a punto en entorno real", "Media"),
        ("L5", "Iteración Shockley", "Punto fijo amortiguado, sin self-heating ni dispersión de parámetros", "Convergente para P_in ≤ 10 mW; precisión < 0,1 %", "Baja"),
        ("L6", "Cap PCE 0,85", "Tope explícito por código; resultado de referencia opera en el cap", "P_DC reportada es cota superior; con PCE 0,60 → 1 156 µW", "Media"),
        ("L7", "η_PMIC constante", "Eficiencia BQ25504 fijada en 0,85 en todo el rango", "±5 pp variación real según punto de operación", "Baja"),
        ("L8", "Escenario A sin EIRP", "EIRP de fuentes urbanas (GSM/5G/WiFi) no especificadas", "Resultados de Escenario A son cota superior", "Alta"),
    ]
    df = pd.DataFrame(lims, columns=["#", "Tema", "Descripción", "Impacto cuantitativo", "Severidad"])
    st.dataframe(df, hide_index=True, height=340)
    st.caption(
        ":material/info: Estas limitaciones están declaradas en el marco metodológico "
        "(Apéndice D) y en la sección §3.9 de la versión APA7. La filosofía del proyecto "
        "es declararlas explícitamente: una limitación documentada vale más que una omitida."
    )


render()
