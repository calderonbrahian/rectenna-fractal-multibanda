"""
Viabilidad IoT — la conclusión operativa del proyecto.
Pregunta: ¿Para qué sirve realmente esto?

Cadena:  P_DC  →  E_ciclo  →  T_ciclo  →  mensajes/día
         + cold-start del PMIC
         + dimensionamiento del supercondensador
         + modo autónomo vs asistido

Corresponde a §3.6 (Presupuesto energético del nodo IoT) y §4.3 (caso Cerro
Nutibara) del informe de grado.
"""

import math
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from configs.parametros import CANONICAL
from utils.pagina import (encabezado, correspondencia, control_interactivo,
                          donde_se_desarrolla as _ref)


# ── Perfiles LoRa (energía por ciclo TX+RX+sleep) ───────────────────────────
# Valores típicos para mensaje LoRa de ~10 bytes en banda 915 MHz Colombia.
LORA_SF = {
    "SF7  (rápido, corto alcance)":  {"E_mJ":  47.0,  "ToA_s": 0.051, "color": "#00BFA6"},
    "SF9  (intermedio)":             {"E_mJ": 110.0,  "ToA_s": 0.226, "color": "#B45309"},
    "SF12 (máximo alcance)":         {"E_mJ": CANONICAL["E_ciclo_mJ"], "ToA_s": 1.155, "color": "#DC2626"},
}


def render():
    encabezado(
        ":material/cell_tower: Viabilidad energética del nodo IoT",
        "Lo que la potencia recolectada permite en la práctica: "
        "qué transmite, con qué cadencia, durante cuánto tiempo.",
        que_es=("Página de **aplicación operativa**: traduce la potencia continua "
                 "estimada por el modelo (microvatios) en métricas que un ingeniero "
                 "IoT entiende: tiempo de carga, tamaño del supercondensador, "
                 "mensajes LoRa por día y modo de operación viable."),
        para_que_sirve=("Responder si la rectena puede sostener un nodo LoRa **sin "
                         "batería primaria**, hasta qué distancia, con qué cadencia y "
                         "respetando las restricciones regulatorias de duty cycle del "
                         "1 % en la banda ISM 915 MHz."),
        entradas=("Para algunas vistas: selector de perfil LoRa (SF7 / SF9 / SF12), "
                  "ventana de tiempo del diente de sierra del supercap y los parámetros "
                  "del supercondensador (capacitancia, V_max, V_min)."),
        salidas=("KPIs del nodo (P_DC, T_ciclo, mensajes/día, V_DC), tabla compacta "
                  "mensajes/día × SF × distancia con tope regulatorio, mapa de viabilidad "
                  "EIRP × distancia, curva T_ciclo vs distancia, línea de tiempo del "
                  "ciclo LoRa y diente de sierra de la tensión del supercap."),
        como_leer=("**Modo autónomo**: el nodo se alimenta sólo de la cosecha RF. La tabla "
                   "indica cuántos mensajes/día puede transmitir. Si la celda muestra un "
                   "asterisco (*), el tope lo manda la regulación, no la energía. "
                   "**Modo asistido**: si la cosecha no alcanza para el ciclo deseado, "
                   "se requiere una batería primaria que se prolonga gracias a la cosecha."),
    )

    # ── Índice rápido (TOC para defensa) ────────────────────────────────────
    with st.container(border=True):
        st.markdown("**:material/list: En esta página**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "1. KPIs en el punto de referencia (100 m)  \n"
                "2. Cadena energética operativa (4 tarjetas)  \n"
                "3. Mensajes/día × SF × distancia *(la tabla clave)*  \n"
                "4. Mapa de viabilidad EIRP × distancia"
            )
        with c2:
            st.markdown(
                "5. Hasta dónde alcanza la operación autónoma  \n"
                "6. Anatomía energética de un mensaje LoRa  \n"
                "7. Dimensionamiento del supercondensador  \n"
                "8. Modos de operación (autónomo vs asistido)"
            )

    st.markdown(
        "Esta página traduce la potencia continua del escenario de referencia "
        "(P_DC ≈ 1 638 µW) en algo tangible para un nodo IoT: cuánta energía necesita "
        "cada mensaje, cuánto tarda en acumularla, cuántos mensajes puede enviar al día "
        "y hasta qué distancia la operación se sostiene por sí sola."
    )
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
         "§4.3 Caso de estudio: Cerro Nutibara")

    # ── KPIs operativos ──────────────────────────────────────────────────────
    P_DC_uW = CANONICAL['P_dc_uW']
    E_ciclo_mJ = CANONICAL['E_ciclo_mJ']
    T_ciclo_s = CANONICAL['T_ciclo_s']
    msg_per_day = 86400.0 / T_ciclo_s

    st.subheader("Lo que el modelo permite en el punto de referencia (100 m)")
    with st.container(horizontal=True):
        st.metric("Potencia continua", f"{P_DC_uW:.1f} µW", border=True)
        st.metric("Energía por mensaje SF12", f"{E_ciclo_mJ:.1f} mJ", border=True)
        st.metric("Período entre mensajes", f"≈ {T_ciclo_s:.0f} s",
                  help="Tiempo necesario para recolectar la energía de un ciclo.", border=True)
        st.metric("Mensajes / día (SF12)", f"≈ {msg_per_day:.0f}",
                  delta="modo autónomo (sin batería primaria)", delta_color="off", border=True)
        st.metric("Tensión continua", f"{CANONICAL['V_dc_mV']:.0f} mV",
                  delta=f"+{CANONICAL['V_dc_mV']-CANONICAL['V_cs_mV']:.0f} mV vs cold-start",
                  delta_color="normal", border=True)

    st.divider()

    # ── Cadena propagación → rectificación → almacenamiento → transmisión ───
    st.subheader("Cadena energética operativa")
    _render_energy_chain(P_DC_uW, T_ciclo_s, E_ciclo_mJ, msg_per_day)
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
         "§4.3.1 Cálculo de la cadena de potencia")

    st.divider()

    # ── T_ciclo vs distancia, por SF ────────────────────────────────────────
    st.subheader("¿Hasta dónde alcanza la operación autónoma?")
    st.markdown(
        "Para cada distancia, la potencia recolectada cambia como 1/d² (Friis). "
        "Cada perfil LoRa (SF) requiere una energía distinta por mensaje. "
        "El cruce define el período entre transmisiones."
    )
    _render_t_ciclo_vs_d()
    correspondencia('directa',
                    "Reproduce la **Figura 7** del trabajo (intervalo entre transmisiones "
                    "T_ciclo vs distancia, LoRa SF12).")
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
         "§2.5 Propagación RF y modelo de Friis · "
         "Figura 6 (P_DC vs distancia) · Figura 7 (T_ciclo vs distancia)")

    st.divider()

    # ── Dimensionamiento de supercondensador ────────────────────────────────
    st.subheader("Dimensionamiento del supercondensador")
    st.markdown(
        "El supercap acumula la energía entre transmisiones. Capacidad típica "
        "para almacenar ≥ 1 ciclo SF12 está en el rango de **100–470 mF**."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        C_mF = st.select_slider("Capacitancia [mF]",
                                 options=[47, 100, 220, 330, 470, 1000, 4700],
                                 value=330)
    with c2:
        V_max = st.number_input("V_max [V]", 1.5, 5.5, 3.3, 0.1)
    with c3:
        V_min = st.number_input("V_min [V]", 0.5, 3.0, 1.8, 0.1)

    control_interactivo(
        magnitud="**Capacitancia C** del supercondensador [mF] y las tensiones de "
                 "operación **V_max / V_min** [V]. La energía útil almacenada es "
                 "E = ½·C·(V_max² − V_min²).",
        referencia="C = **330 mF**, V_max = **3,3 V**, V_min = **1,8 V** (consistente con "
                   "§5.1 y el Apéndice E.9: almacena ≥ 1 ciclo SF12).",
        al_subir="Más C o mayor ventana V_max−V_min → más energía almacenada y más ciclos "
                 "por carga, pero el tiempo de carga completa crece y el supercap ocupa más.",
        al_bajar="Menos C → carga más rápido pero almacena menos; si no cubre un ciclo "
                 "SF12, la tensión cae por debajo de V_min y el nodo se apaga entre envíos.",
        limite="Por debajo del **mínimo C** que cubre un ciclo deja de ser viable; V_min no "
               "debe bajar de los 130 mV de arranque del PMIC ni V_max superar la tensión "
               "nominal del componente.",
    )

    E_buffer_J = 0.5 * (C_mF * 1e-3) * (V_max**2 - V_min**2)
    E_buffer_mJ = E_buffer_J * 1000.0
    n_ciclos_SF12 = E_buffer_mJ / E_ciclo_mJ
    t_carga_s = E_buffer_J / (P_DC_uW * 1e-6)   # P_DC en W; resultado en s

    with st.container(horizontal=True):
        st.metric("Energía útil del supercap", f"{E_buffer_mJ:.0f} mJ", border=True)
        st.metric("Ciclos SF12 almacenados", f"{n_ciclos_SF12:.1f}",
                  help="Cuántos mensajes LoRa SF12 puede sostener desde plena carga.",
                  border=True)
        st.metric("Tiempo de carga completa",
                  f"{t_carga_s:.0f} s ({t_carga_s/60:.1f} min)", border=True)
        st.metric("Cold-start BQ25504",
                  "Viable ✓" if CANONICAL['V_dc_mV'] >= CANONICAL['V_cs_mV'] else "NO ✗",
                  delta=f"V_DC = {CANONICAL['V_dc_mV']:.0f} mV vs umbral 130 mV",
                  delta_color="off", border=True)

    # ── Carga y descarga del supercap en el tiempo ──────────────────────────
    st.markdown("**:material/show_chart: Carga y descarga del supercap en el tiempo**")
    st.markdown(
        "El supercap **se carga lentamente** con la potencia continua P_DC y se "
        "**descarga en saltos** cada vez que el nodo transmite. En régimen permanente "
        "la tensión oscila como diente de sierra entre un valle (justo después del TX) "
        "y un techo (justo antes del siguiente)."
    )
    csf, cdur = st.columns(2)
    with csf:
        sf_temporal_key = st.segmented_control(
            "Perfil LoRa",
            options=list(LORA_SF.keys()),
            default="SF12 (máximo alcance)",
            key="sf_temporal",
        ) or "SF12 (máximo alcance)"
    with cdur:
        duracion_min = st.select_slider(
            "Ventana de tiempo a visualizar",
            options=[2, 5, 10, 20, 30, 60],
            value=10,
            format_func=lambda v: f"{v} min",
            key="dur_temporal",
        )

    E_ciclo_temporal_mJ = LORA_SF[sf_temporal_key]['E_mJ']
    st.plotly_chart(
        _fig_supercap_temporal(P_DC_uW, E_ciclo_temporal_mJ, C_mF, V_max, V_min, duracion_min),
        width="stretch",
    )
    correspondencia('complementaria',
                    "No aparece literal en la tesis; modela el diente de sierra del "
                    "supercondensador descrito en el **Apéndice E.9**.")
    st.caption(
        ":material/info: Esta es la **firma temporal** del nodo IoT alimentado por "
        "recolección RF: una rampa lenta de carga (decenas de segundos a minutos) "
        "interrumpida por una caída instantánea en cada transmisión. Si la curva "
        "amarilla queda por encima de V_min en todo momento, la operación es "
        "sostenible; si toca V_min o menos, el supercap es demasiado pequeño y el "
        "nodo se apaga entre transmisiones."
    )
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
         "Apéndice E.9 Caracterización temporal del supercondensador")

    st.divider()

    # ── Tabla compacta: mensajes/día por SF × distancia ──────────────────────
    st.subheader("Mensajes por día — SF × distancia (modo autónomo)")
    st.markdown(
        "Para cada celda, el modelo calcula la potencia continua recolectada a esa "
        "distancia y la divide por la energía por ciclo del perfil LoRa correspondiente. "
        "El resultado es el número de mensajes que el nodo puede transmitir en 24 horas "
        "sin batería de cebado."
    )
    st.caption(
        ":material/push_pin: **Tabla de referencia fija** — calculada con la fuente "
        "canónica del proyecto (TDT, EIRP 70 dBm, 550 MHz). *No* depende de los "
        "controles del supercondensador de arriba: el número de mensajes/día lo fija "
        "la potencia cosechada y la energía por mensaje, no el tamaño del buffer. "
        "Otras fuentes y EIRP se exploran en el **mapa de viabilidad** más abajo."
    )
    st.dataframe(_messages_per_day_table(),
                 hide_index=True, height=290,
                 column_config={
                     "Distancia": st.column_config.TextColumn("Distancia", width="small"),
                     "P_DC": st.column_config.TextColumn("P_DC", width="small"),
                     "Cold-start": st.column_config.TextColumn("Cold-start", width="small"),
                     "SF7":  st.column_config.TextColumn("SF7 (msj/día)",  help="Mínimo entre cota por energía y duty cycle 1 %"),
                     "SF9":  st.column_config.TextColumn("SF9 (msj/día)",  help="Mínimo entre cota por energía y duty cycle 1 %"),
                     "SF12": st.column_config.TextColumn("SF12 (msj/día)", help="Mínimo entre cota por energía y duty cycle 1 %"),
                 })
    st.caption(
        ":material/info: Cada celda muestra el **mínimo** entre dos topes: la cota por "
        "**energía** (lo que da el modelo de la cadena RF→DC) y la cota por **duty cycle "
        "regulatorio** del 1 % aplicable a la banda ISM 915 MHz (ETSI-compatible). "
        "El asterisco (*) indica que en esa celda **manda la regulación**, no la energía. "
        "Topes regulatorios absolutos por SF: "
        f"SF7 ≈ {86400*0.01/LORA_SF['SF7  (rápido, corto alcance)']['ToA_s']:.0f} · "
        f"SF9 ≈ {86400*0.01/LORA_SF['SF9  (intermedio)']['ToA_s']:.0f} · "
        f"SF12 ≈ {86400*0.01/LORA_SF['SF12 (máximo alcance)']['ToA_s']:.0f} mensajes/día. "
        "“—” = cold-start no asegurado."
    )
    correspondencia('derivada',
                    "Tabla calculada con el modelo de la cadena RF→DC; el desglose "
                    "energético por ciclo del nodo es la **Tabla 5**.")
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
         "§4.3.1 Cálculo de la cadena de potencia · "
         "Tabla 5 (desglose energético por ciclo del nodo IoT)")

    st.divider()

    # ── Mapa de viabilidad (EIRP × distancia) por SF ─────────────────────────
    st.subheader("Mapa de viabilidad — EIRP × distancia, por SF")
    st.markdown(
        "Para cada celda (EIRP, distancia), el color indica el período entre "
        "transmisiones del nodo en operación autónoma. Útil para juzgar si una "
        "fuente RF cualquiera (no solo TDT) habilita el caso de uso."
    )
    sf_sel = st.segmented_control(
        "Factor de ensanchamiento (SF)", options=list(LORA_SF.keys()),
        default=list(LORA_SF.keys())[-1],   # SF12 por defecto
    ) or list(LORA_SF.keys())[-1]
    st.plotly_chart(_heatmap_t_ciclo(sf_sel), width="stretch")
    correspondencia('complementaria',
                    "No aparece literal en la tesis; generaliza el caso a una rejilla "
                    "EIRP × distancia, según el **Apéndice E.10**.")
    _ref("Apéndice E.10 Operación fuera del caso canónico — mapa EIRP × distancia · "
         "§4.3 Caso de estudio: Cerro Nutibara")

    st.divider()

    # ── Línea de tiempo de un mensaje LoRa ───────────────────────────────────
    st.subheader("Anatomía energética de un mensaje LoRa")
    st.markdown(
        "Perfil de corriente del nodo durante un ciclo: despertar → transmisión → "
        "ventana de recepción → reposo. Casi toda la energía se gasta en la "
        "transmisión (la barra roja); el reposo es <10 µA, dominado por la fuga "
        "del supercondensador."
    )
    st.plotly_chart(_lora_tx_timeline(), width="stretch")
    correspondencia('derivada',
                    "Construida a partir del desglose energético por ciclo del nodo "
                    "(**Tabla 5**, perfiles LoRa SX1276).")
    _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT (perfiles LoRa SX1276) · "
         "Tabla 5 (desglose energético por ciclo)")

    st.divider()

    # ── Modo autónomo vs asistido ────────────────────────────────────────────
    st.subheader("Modos de operación")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### :material/eco: Modo autónomo (sin batería)")
            st.markdown(
                f"- Se alimenta **exclusivamente** de la recolección RF.\n"
                f"- Cadencia limitada por T_ciclo ≈ **{T_ciclo_s:.0f} s** (SF12).\n"
                f"- ≈ **{msg_per_day:.0f} mensajes/día** a 100 m del transmisor TDT.\n"
                f"- Arranca en frío desde V_DC = {CANONICAL['V_dc_mV']:.0f} mV "
                f"(umbral 130 mV).\n"
                f"- :material/check: Ideal para **monitoreo ambiental** de baja frecuencia.\n"
                f"- :material/warning: NO ideal para aplicaciones con baja latencia."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("#### :material/battery_charging_full: Modo asistido (batería primaria)")
            st.markdown(
                "- Batería primaria complementa la recolección.\n"
                "- La recolección **no elimina** la batería: prolonga su vida útil.\n"
                "- Cadencia limitada por la **aplicación**, no por la energía.\n"
                "- Útil cuando la densidad de potencia ambiental cae (movilidad, "
                "obstáculos, cambio de emplazamiento).\n"
                "- :material/check: Ideal cuando hay requisitos de latencia o "
                "tasas de transmisión mayores."
            )

    st.caption(
        ":material/info: El presupuesto energético supone recolección continua a 100 m "
        "del transmisor TDT. En condiciones reales, la potencia varía con la geometría "
        "urbana (±10–15 dB según ITU-R P.1546); la cadencia operativa debe reevaluarse "
        "por emplazamiento."
    )
    _ref("§5.1 Conclusiones · §1.3 Alcance y limitaciones del estudio")


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _render_energy_chain(P_DC_uW, T_ciclo_s, E_ciclo_mJ, msg_per_day):
    """Cuatro tarjetas encadenadas: propagación → rectificación → almacenamiento → TX."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.markdown("#### :material/cell_tower: 1. Propagación")
            st.markdown(
                f"EIRP = **70 dBm**  \n"
                f"d = **100 m**  \n"
                f"FSPL = {CANONICAL['FSPL_dB']:.1f} dB  \n"
                f"L_urb = {CANONICAL['L_urb_dB']:.0f} dB  \n"
                f":material/arrow_forward: **P_in = +{CANONICAL['P_in_dBm']:.2f} dBm**"
            )
    with c2:
        with st.container(border=True):
            st.markdown("#### :material/bolt: 2. Rectificación")
            st.markdown(
                f"Doubler SMS7630  \n"
                f"η_mm = {CANONICAL['eta_mm']:.4f}  \n"
                f"η_IMN = {CANONICAL['eta_imn']:.4f}  \n"
                f"PCE = {CANONICAL['PCE']:.2f} (cap)  \n"
                f":material/arrow_forward: **P_DC = {P_DC_uW:.0f} µW**"
            )
    with c3:
        with st.container(border=True):
            st.markdown("#### :material/battery_charging_full: 3. Almacenamiento")
            st.markdown(
                f"PMIC BQ25504, η = 0.85  \n"
                f"Cold-start ≥ 130 mV  \n"
                f"V_DC modelo = {CANONICAL['V_dc_mV']:.0f} mV ✓  \n"
                f"E_ciclo = {E_ciclo_mJ:.0f} mJ  \n"
                f":material/arrow_forward: T_carga = {T_ciclo_s:.0f} s"
            )
    with c4:
        with st.container(border=True):
            st.markdown("#### :material/radio: 4. Transmisión")
            st.markdown(
                f"LoRa SF12, BW 125 kHz  \n"
                f"Sensibilidad −137 dBm  \n"
                f"ToA ≈ 1,15 s  \n"
                f"DC activo < 1 %  \n"
                f":material/arrow_forward: **~{msg_per_day:.0f} mensajes/día**"
            )


def _render_t_ciclo_vs_d():
    """T_ciclo (s) vs distancia para SF7, SF9, SF12. Sombreado cold-start OK."""
    d = np.linspace(20, 2000, 400)
    # P_DC escala con (100/d)^2 desde el canónico:
    P_DC_d_uW = CANONICAL['P_dc_uW'] * (100.0 / d) ** 2

    # Cold-start: V_DC = √(P_DC · R_load).  V_cs = 130 mV → P_DC_cs = 0.130²/1300 ≈ 13 µW
    R_load = CANONICAL['R_load_ohm']
    V_cs = CANONICAL['V_cs_mV'] / 1000.0
    P_DC_cs_uW = (V_cs ** 2 / R_load) * 1e6
    d_cs = 100.0 * math.sqrt(CANONICAL['P_dc_uW'] / P_DC_cs_uW)

    fig = go.Figure()

    # Sombreado cold-start OK
    fig.add_vrect(
        x0=20, x1=d_cs,
        fillcolor='rgba(0, 153, 136, 0.10)',
        line_width=0,
        annotation_text=f"Cold-start OK (d ≤ {d_cs:.0f} m)",
        annotation_position='top left',
        annotation_font_size=11,
    )
    fig.add_vrect(
        x0=d_cs, x1=2000,
        fillcolor='rgba(204, 51, 17, 0.08)',
        line_width=0,
        annotation_text=f"Cold-start no asegurado (d > {d_cs:.0f} m)",
        annotation_position='top right',
        annotation_font_size=11,
    )

    # Curvas T_ciclo(d) por SF
    for nombre, cfg in LORA_SF.items():
        # P_DC en W para obtener T en s
        T_s = (cfg["E_mJ"] * 1e-3) / (P_DC_d_uW * 1e-6 + 1e-30)
        fig.add_trace(go.Scatter(
            x=d, y=T_s, mode='lines',
            name=nombre,
            line=dict(width=2.5, color=cfg["color"]),
            hovertemplate="d=%{x:.0f} m<br>T=%{y:.0f} s<extra>" + nombre + "</extra>",
        ))

    # Marca del punto canónico (100 m, T_ciclo SF12)
    fig.add_trace(go.Scatter(
        x=[100], y=[CANONICAL['T_ciclo_s']],
        mode='markers+text',
        marker=dict(size=14, color='#B45309', symbol='star',
                    line=dict(color='white', width=1)),
        text=[f"  Canónico: {CANONICAL['T_ciclo_s']:.0f} s @ 100 m (SF12)"],
        textposition='middle right',
        textfont=dict(size=11, color='#B45309'),
        showlegend=False,
        hoverinfo='skip',
    ))

    # Línea horizontal a 1 hora y 1 día como referencia
    fig.add_hline(y=3600, line=dict(color='rgba(200,200,200,0.35)', dash='dot', width=1),
                  annotation_text='1 h', annotation_position='top left',
                  annotation_font_size=10)
    fig.add_hline(y=86400, line=dict(color='rgba(200,200,200,0.35)', dash='dot', width=1),
                  annotation_text='1 día', annotation_position='top left',
                  annotation_font_size=10)

    fig.update_layout(
        template='simple_white', height=440,
        title=dict(text='Período entre transmisiones vs. distancia (modo autónomo)',
                   font=dict(size=14)),
        xaxis=dict(title='Distancia al transmisor TDT [m]', type='log',
                    tickvals=[20, 50, 100, 200, 500, 1000, 2000]),
        yaxis=dict(title='Tiempo de recolección por mensaje [s]', type='log',
                    tickvals=[1, 10, 60, 300, 600, 3600, 86400],
                    ticktext=['1 s', '10 s', '1 min', '5 min', '10 min', '1 h', '1 día']),
        legend=dict(orientation='h', y=-0.18),
        margin=dict(l=70, r=20, t=50, b=80),
    )
    st.plotly_chart(fig)
    st.caption(
        f":material/info: A 100 m el modelo entrega 1 mensaje SF12 cada **{CANONICAL['T_ciclo_s']:.0f} s** "
        f"(≈ 545/día). Más allá de **{d_cs:.0f} m** el cold-start del PMIC ya no está asegurado "
        f"con la antena de referencia."
    )


def _messages_per_day_table():
    """Tabla compacta: mensajes/día × SF × distancia, EIRP 70 dBm.
    Por celda muestra el MÍNIMO entre la cota por energía y la cota por duty cycle
    regulatorio (1 % ISM 915 MHz Colombia). Marca con * cuando manda regulación."""
    # (math en top-level)
    # (pandas en top-level)

    distancias = [50, 100, 200, 300, 500, 750, 1000, 1500]
    G = CANONICAL['gain_dBi']
    L_urb = CANONICAL['L_urb_dB']
    eta = CANONICAL['eta_mm'] * CANONICAL['eta_imn'] * CANONICAL['PCE'] * CANONICAL['eta_pmic']
    R_load = CANONICAL['R_load_ohm']
    V_cs = CANONICAL['V_cs_mV'] / 1000.0
    lam = 3e8 / 550e6
    DUTY_CYCLE = 0.01   # 1 %  (ISM 915 MHz Colombia, ETSI-compatible)

    rows = []
    for d in distancias:
        FSPL = 20.0 * math.log10(4.0 * math.pi * d / lam)
        P_in_dBm = 70.0 - FSPL - L_urb + G
        P_in_W = 10 ** ((P_in_dBm - 30.0) / 10.0)
        P_dc_W = P_in_W * eta
        V_dc = math.sqrt(max(P_dc_W * R_load, 0.0))
        cold_ok = V_dc >= V_cs

        row = {
            "Distancia": f"{d} m",
            "P_DC": f"{P_dc_W*1e6:.0f} µW" if P_dc_W*1e6 >= 1 else f"{P_dc_W*1e9:.1f} nW",
            "Cold-start": "✓" if cold_ok else "✗",
        }
        for sf_key, cfg in LORA_SF.items():
            sf_label = sf_key.split()[0]   # "SF7", "SF9", "SF12"
            E_J = cfg["E_mJ"] * 1e-3
            T_energy = E_J / max(P_dc_W, 1e-30)
            n_energy = 86400.0 / T_energy
            ToA = cfg["ToA_s"]
            # Cota regulatoria: el ToA solo puede ocupar 1% del tiempo del aire.
            n_reg = 86400.0 * DUTY_CYCLE / ToA
            n_eff = min(n_energy, n_reg)

            if not cold_ok:
                row[f"{sf_label}"] = "—"
            elif n_eff < 1:
                row[f"{sf_label}"] = "< 1"
            else:
                bind = "*" if n_reg < n_energy else ""
                v = f"{n_eff:,.0f}".replace(",", " ") if n_eff >= 1000 else f"{n_eff:.0f}"
                row[f"{sf_label}"] = f"{v}{bind}"
        rows.append(row)

    return pd.DataFrame(rows)


@st.cache_data(ttl="1h")
def _heatmap_t_ciclo_data(sf_key: str):
    """Calcula T_ciclo (s) en una rejilla EIRP × distancia para un SF dado."""
    # (numpy en top-level)
    # (math en top-level)
    eirp = np.arange(40.0, 81.0, 2.0)
    dist = np.array([50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000])
    E_mJ = LORA_SF[sf_key]["E_mJ"]

    G = CANONICAL['gain_dBi']
    L_urb = CANONICAL['L_urb_dB']
    eta = CANONICAL['eta_mm'] * CANONICAL['eta_imn'] * CANONICAL['PCE'] * CANONICAL['eta_pmic']
    lam = 3e8 / 550e6
    Z = np.zeros((len(dist), len(eirp)), dtype=float)
    for j, e in enumerate(eirp):
        for i, d in enumerate(dist):
            FSPL = 20.0 * math.log10(4.0 * math.pi * d / lam)
            P_in_dBm = e - FSPL - L_urb + G
            P_in_W = 10 ** ((P_in_dBm - 30.0) / 10.0)
            P_dc_W = P_in_W * eta
            T = (E_mJ * 1e-3) / max(P_dc_W, 1e-30)
            Z[i, j] = T
    return eirp, dist, Z


def _fmt_time(s: float) -> str:
    if s < 60: return f"{s:.0f} s"
    if s < 3600: return f"{s/60:.1f} min"
    if s < 86400: return f"{s/3600:.1f} h"
    return f"{s/86400:.1f} d"


def _heatmap_t_ciclo(sf_key: str):
    """Heatmap T_ciclo (s) sobre rejilla EIRP × d."""
    # (numpy en top-level)
    eirp, dist, Z = _heatmap_t_ciclo_data(sf_key)

    Z_clip = np.clip(Z, 1, 86400 * 30)
    Zlog = np.log10(Z_clip)

    fig = go.Figure(go.Heatmap(
        z=Zlog, x=eirp, y=dist,
        colorscale='Viridis_r',
        colorbar=dict(
            title=dict(text='T_ciclo', font=dict(size=11)),
            tickvals=[0, 1, float(np.log10(60)), float(np.log10(3600)),
                       float(np.log10(86400)), float(np.log10(86400 * 7))],
            ticktext=['1 s', '10 s', '1 min', '1 h', '1 día', '1 semana'],
        ),
        hovertemplate='EIRP=%{x:.0f} dBm<br>d=%{y:.0f} m<br>T_ciclo=%{customdata}<extra></extra>',
        customdata=np.array([[_fmt_time(t) for t in row] for row in Z]),
    ))
    fig.add_trace(go.Scatter(
        x=[70], y=[100],
        mode='markers+text',
        marker=dict(size=14, color='#B45309', symbol='star',
                    line=dict(color='white', width=1)),
        text=[f"  Canónico: {CANONICAL['T_ciclo_s']:.0f} s"],
        textposition='middle right',
        textfont=dict(color='#B45309', size=11),
        showlegend=False,
    ))
    fig.update_layout(
        template='simple_white', height=380,
        title=dict(text=f'Período entre transmisiones [escala log]  ·  {sf_key}',
                   font=dict(size=13)),
        xaxis=dict(title='EIRP de la fuente RF [dBm]'),
        yaxis=dict(title='Distancia [m]', type='log',
                    tickvals=[50, 100, 200, 500, 1000, 2000]),
        margin=dict(l=70, r=20, t=50, b=60),
    )
    return fig


def _lora_tx_timeline():
    """Perfil de corriente típico de un nodo LoRa SF12 durante un ciclo.
    Eje lineal con segunda traza opaca en las fases de reposo, para que
    se distinga el reposo (~5 µA) del consumo activo (15–120 mA)."""
    fases = [
        ("Reposo",       6.0,   0.005, '#475569'),
        ("Wake/Boot",    0.05,  15.0,  '#B45309'),
        ("TX SF12",      1.15,  120.0, '#DC2626'),
        ("Reposo TX→RX", 1.0,   0.005, '#475569'),
        ("RX1 window",   0.25,  12.0,  '#059669'),
        ("Reposo RX",    1.0,   0.005, '#475569'),
        ("RX2 window",   0.25,  12.0,  '#059669'),
        ("Reposo final", 5.0,   0.005, '#475569'),
    ]
    fig = go.Figure()
    t_cur = 0.0
    for nombre, dt, I_mA, color in fases:
        t_start = t_cur
        t_end = t_cur + dt
        ts = [t_start, t_start + 1e-4, t_end - 1e-4, t_end]
        Is = [0.0,     I_mA,           I_mA,           0.0]
        fig.add_trace(go.Scatter(
            x=ts, y=Is, mode='lines', fill='tozeroy',
            line=dict(color=color, width=1.5),
            name=nombre,
            hovertemplate=f'{nombre}<br>I={I_mA} mA · Δt={dt:.2f} s<extra></extra>',
            showlegend=True,
        ))
        t_cur = t_end

    # Energía total y porcentual de cada fase
    E_total_mJ = sum(dt * I_mA * 3.3 for _, dt, I_mA, _ in fases)
    E_tx_mJ = 1.15 * 120.0 * 3.3        # solo la fase TX
    pct_tx = E_tx_mJ / E_total_mJ * 100

    fig.add_annotation(
        x=6.6, y=120, xref='x', yref='y',
        text=f"TX SF12 concentra {pct_tx:.0f}% de la energía<br>en {1.15:.2f}s",
        showarrow=True, arrowhead=2, ax=80, ay=-10,
        font=dict(size=10, color='#DC2626'),
        bgcolor='rgba(248, 250, 252, 0.9)', bordercolor='rgba(248,113,113,0.6)',
        borderwidth=1, borderpad=5,
    )

    fig.update_layout(
        template='simple_white', height=340,
        title=dict(text=f'Perfil de corriente en un ciclo LoRa SF12  ·  E ≈ {E_total_mJ:.0f} mJ a 3,3 V',
                   font=dict(size=13)),
        xaxis=dict(title='Tiempo dentro del ciclo activo [s]', range=[0, 14.7]),
        yaxis=dict(title='Corriente del nodo [mA]', range=[0, 140]),
        legend=dict(orientation='h', y=-0.22),
        margin=dict(l=70, r=20, t=50, b=80),
    )
    return fig


def _fig_supercap_temporal(P_DC_uW, E_ciclo_mJ, C_mF, V_max, V_min, T_show_min):
    """Diente de sierra de V(t) del supercap: carga continua P_DC + descarga
    instantánea por cada TX LoRa que extrae E_ciclo del condensador."""
    C = C_mF * 1e-3        # F
    P = P_DC_uW * 1e-6     # W
    E_TX = E_ciclo_mJ * 1e-3   # J
    T_cycle = E_TX / max(P, 1e-30)
    T_total = T_show_min * 60.0

    # V_bot estable suponiendo V_top = V_max y régimen permanente
    V_bot_sq = V_max ** 2 - 2 * E_TX / C
    if V_bot_sq <= 0:
        V_bot = 0.0
        feasible = False
        reason = "el supercap se descarga totalmente en una sola TX"
    elif V_bot_sq < V_min ** 2:
        V_bot = float(np.sqrt(V_bot_sq))
        feasible = False
        reason = f"V cae a {V_bot:.2f} V, por debajo de V_min = {V_min:.2f} V"
    else:
        V_bot = float(np.sqrt(V_bot_sq))
        feasible = True
        reason = ""

    # Generar el diente de sierra: arrancamos en V_max, TX → V_bot → carga → V_max
    times = [0.0]
    voltages = [V_max]
    t = 0.0
    while t < T_total:
        # Descarga instantánea por TX
        V_after = float(np.sqrt(max(voltages[-1] ** 2 - 2 * E_TX / C, 0.0)))
        times.append(t); voltages.append(V_after)

        # Carga durante T_cycle (o lo que reste hasta T_total)
        dt_charge = min(T_cycle, T_total - t)
        n = max(int(dt_charge / 1.0), 30)   # >=30 puntos para curva suave
        for tt in np.linspace(t, t + dt_charge, n)[1:]:
            V_t = float(np.sqrt(V_after ** 2 + 2 * P * (tt - t) / C))
            V_t = min(V_t, V_max)
            times.append(tt); voltages.append(V_t)
        t += dt_charge

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=voltages, mode='lines',
        line=dict(color='#B45309' if feasible else '#DC2626', width=2.2),
        name='V_supercap(t)',
        hovertemplate='t=%{x:.1f} s<br>V=%{y:.3f} V<extra></extra>',
        fill='tozeroy', fillcolor='rgba(251,191,36,0.08)' if feasible else 'rgba(248,113,113,0.08)',
    ))

    # Líneas horizontales de referencia
    fig.add_hline(y=V_max, line=dict(color='#059669', dash='dot', width=1.2),
                  annotation_text=f'V_max = {V_max:.2f} V',
                  annotation_position='top right', annotation_font_size=10)
    fig.add_hline(y=V_min, line=dict(color='#DC2626', dash='dash', width=1.2),
                  annotation_text=f'V_min = {V_min:.2f} V (cut-off)',
                  annotation_position='bottom right', annotation_font_size=10)
    fig.add_hline(y=0.130, line=dict(color='rgba(248,113,113,0.40)', dash='dot', width=1),
                  annotation_text='V_cs = 130 mV (cold-start BQ25504)',
                  annotation_position='bottom left', annotation_font_size=9)

    # Etiquetar la primera TX para que el jurado vea el "salto"
    if len(times) > 2:
        fig.add_annotation(
            x=times[1], y=voltages[1],
            text=f"  TX consume E = {E_ciclo_mJ:.0f} mJ",
            showarrow=True, arrowhead=2, ax=80, ay=-30,
            font=dict(size=10, color='#DC2626'),
        )

    # Caja informativa
    n_tx_window = int(T_total / T_cycle)
    if feasible:
        info_text = (f"<b>Operación sostenible</b><br>"
                     f"V oscila entre {V_bot:.2f} V y {V_max:.2f} V<br>"
                     f"T_ciclo ≈ {T_cycle:.0f} s · {n_tx_window} TX en {T_show_min} min")
        info_color = '#059669'; info_bg = 'rgba(52,211,153,0.10)'
    else:
        C_min = 2 * E_TX / max(V_max ** 2 - V_min ** 2, 1e-9) * 1000  # mF
        info_text = (f"<b>⚠ Capacitancia insuficiente</b><br>"
                     f"{reason}.<br>"
                     f"Mínimo necesario: C ≥ {C_min:.0f} mF")
        info_color = '#DC2626'; info_bg = 'rgba(248,113,113,0.10)'

    fig.add_annotation(
        x=0.02, y=0.97, xref='paper', yref='paper', xanchor='left', yanchor='top',
        text=info_text, showarrow=False, align='left',
        font=dict(size=11, color=info_color),
        bgcolor=info_bg,
        bordercolor=info_color, borderwidth=1, borderpad=8,
    )

    fig.update_layout(
        template='simple_white',
        title=dict(
            text=f"Tensión del supercap · C = {C_mF:.0f} mF · {sf_label_for_title(E_ciclo_mJ)}",
            font=dict(size=13)),
        xaxis=dict(title='Tiempo [s]', range=[0, T_total]),
        yaxis=dict(title='V_supercap [V]', range=[0, V_max * 1.12]),
        height=400, showlegend=False,
        margin=dict(l=70, r=20, t=50, b=60),
    )
    return fig


def sf_label_for_title(E_mJ):
    """Devuelve el label corto del perfil LoRa según la energía por ciclo."""
    for sf_key, cfg in LORA_SF.items():
        if abs(cfg["E_mJ"] - E_mJ) < 0.5:
            return sf_key.split()[0]
    return "LoRa"


render()
