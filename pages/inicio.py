"""
Página de inicio — Resultados de la tesis (read-only) y arquitectura del sistema.
Sin sliders. Sin Monte Carlo. Estos son los valores oficiales (auditoría 2026-05-28).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from configs.parametros import CANONICAL
from utils.pagina import encabezado, como_interpretar, badge_oficial


def render():
    encabezado(
        ":material/verified: Resultados de Referencia del Proyecto",
        "Valores oficiales del modelo bajo el escenario de referencia "
        "— d = 100 m · f = 550 MHz · EIRP = 70 dBm · TDT Cerro Nutibara",
        que_es=("Página de presentación oficial del proyecto: los valores que ves "
                "son los resultados que la tesis defiende. **No tiene sliders ni "
                "controles editables**; es una vista de lectura."),
        para_que_sirve=("Tener en un único lugar los valores definitivos de potencia "
                         "continua útil (P_DC), eficiencias por etapa, geometría de la "
                         "antena y comparación con la literatura. Útil al jurado para "
                         "verificar el resultado central del trabajo."),
        entradas=("Ninguna entrada por parte del usuario. Los valores provienen del "
                  "pipeline `rectenna_platform` y están sincronizados con los 51 tests "
                  "de regresión que protegen su integridad."),
        salidas=("Tres KPI grandes (P_DC, mensajes/día LoRa SF12, η_total), la "
                  "identidad correcta de la cadena RF→DC, un diagrama de bloques "
                  "físicos, un Sankey con caudales de potencia y una tabla con los "
                  "16 valores canónicos asociados a su test."),
        como_leer=("La cifra defendida del trabajo es **P_DC = 1 637,6 µW** a 100 m del "
                   "transmisor TDT del Cerro Nutibara. El resto de la página explica de "
                   "dónde sale, qué se pierde por el camino y cuánto le permite hacer "
                   "al nodo IoT en operación autónoma."),
    )

    badge_oficial()

    # ── KPIs principales (3 grandes) ─────────────────────────────────────────
    st.subheader("Lo que afirma la tesis")
    msg_dia = 86400.0 / CANONICAL['T_ciclo_s']
    with st.container(horizontal=True):
        st.metric(
            "Potencia DC útil",
            f"{CANONICAL['P_dc_uW']:.1f} µW",
            delta="test-protected · opera en cap PCE",
            delta_color="off",
            help="Potencia continua disponible para el nodo IoT tras toda la cadena RF→DC. "
                 "Bloqueado por test_cadena_potencia_canonica.",
            border=True,
        )
        st.metric(
            "Mensajes LoRa SF12 / día",
            f"≈ {msg_dia:.0f}",
            delta=f"T_ciclo ≈ {CANONICAL['T_ciclo_s']:.0f} s",
            delta_color="off",
            help="Cuántos mensajes puede transmitir el nodo en 24 h en modo autónomo "
                 "(recolección continua a 100 m del transmisor TDT).",
            border=True,
        )
        st.metric(
            "Eficiencia total η_total",
            f"{CANONICAL['eta_total']*100:.2f} %",
            delta="figura de mérito (5 factores)",
            delta_color="off",
            help="η_rad · η_mm · η_IMN · PCE · η_PMIC. NO se multiplica por P_in para obtener P_DC.",
            border=True,
        )

    st.divider()

    # ── Identidad correcta de la cadena ──────────────────────────────────────
    st.subheader("Cadena de conversión RF → DC")
    st.markdown(
        "La potencia DC se obtiene aplicando a **P_in** los cuatro factores de las "
        "etapas posteriores a la antena. **η_rad ya está embebida en la ganancia realizada G** "
        "que define P_in; por eso no se multiplica de nuevo."
    )
    st.markdown(
        r"$$P_{DC} = P_{in} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \text{PCE} \cdot \eta_{PMIC}$$"
    )
    st.markdown(
        f"$$= {CANONICAL['P_in_mW']:.3f}\\ \\text{{mW}} "
        f"\\cdot {CANONICAL['eta_mm']:.4f} "
        f"\\cdot {CANONICAL['eta_imn']:.4f} "
        f"\\cdot {CANONICAL['PCE']:.2f} "
        f"\\cdot {CANONICAL['eta_pmic']:.2f} "
        f"= {CANONICAL['P_dc_uW']:.1f}\\ \\mu\\text{{W}}$$"
    )

    with st.container(border=True):
        st.markdown(
            r"**Figura de mérito** (referida a la potencia interceptada *antes* de las "
            r"pérdidas de radiación, no a P_in):"
        )
        st.markdown(
            r"$$\eta_{total} = \eta_{rad} \cdot \eta_{mm} \cdot \eta_{IMN} "
            r"\cdot \text{PCE} \cdot \eta_{PMIC}"
            f" = {CANONICAL['eta_total']:.4f}$$"
        )
        st.caption(
            ":material/warning: **η_total no debe multiplicarse directamente por P_in** para recuperar "
            "P_DC: η_rad ya está contenida en la ganancia G que define P_in, por lo que "
            "hacerlo contabilizaría dos veces la pérdida de radiación."
        )

    st.divider()

    # ── Diagrama de bloques físico (lo primero que ve el jurado) ─────────────
    st.subheader("La rectena en una imagen")
    st.markdown(
        "De izquierda a derecha, los seis bloques físicos del sistema y los valores "
        "que el modelo entrega en cada interfaz para el escenario de referencia "
        "(100 m, 550 MHz, EIRP 70 dBm)."
    )
    st.plotly_chart(_render_block_diagram(), width="stretch")
    st.caption(
        ":material/info: Cada bloque es un componente físico real; las flechas etiquetadas "
        "son las **interfaces** del sistema con su potencia, eficiencia o tensión "
        "característica. El Sankey de abajo muestra estos mismos caudales en forma de flujo."
    )

    # ── Comparación de tamaño físico (referencia humana) ─────────────────────
    with st.expander(":material/straighten:  ¿Qué tan grande es la antena? (comparativa de tamaño)",
                      expanded=False):
        st.markdown(
            "Silueta del FLPDA Koch a escala real, junto a objetos cotidianos para que "
            "se vea sin ambigüedad en qué rango de tamaño está la antena del trabajo."
        )
        st.plotly_chart(_render_size_comparison(), width="stretch")
        st.caption(
            ":material/info: El FLPDA Koch mide aproximadamente **50 cm de boom × 32 cm "
            "de envergadura** (el doble de la longitud del dipolo más largo). Cabe en "
            "una caja del tamaño de una laptop, lo que la hace integrable como módulo "
            "IoT en pared. Sin Koch, la envergadura sería ≈ 57 cm para la misma f_low."
        )

    st.divider()

    # ── Sankey de la cadena (mW que entran, mW que salen) ────────────────────
    st.subheader("Diagrama de la cadena (caudales de potencia)")
    _render_sankey()

    st.divider()

    # ── Tabla completa de valores canónicos ──────────────────────────────────
    st.subheader("Tabla de valores canónicos (protegidos por test)")
    refs = [
        ("P_DC",          f"{CANONICAL['P_dc_uW']:.1f} µW",         "Potencia continua útil",                       "test_cadena_potencia_canonica · test_pdc_cadena_positivo"),
        ("V_DC",          f"{CANONICAL['V_dc_mV']:.0f} mV",          "Tensión continua de salida",                   "test_output_voltage_positivo"),
        ("P_in",          f"+{CANONICAL['P_in_dBm']:.2f} dBm",        "Potencia disponible en antena (100 m)",        "test_p_in_cerro_nutibara_100m"),
        ("FSPL",          f"{CANONICAL['FSPL_dB']:.2f} dB",          "Pérdida espacio libre (100 m, 550 MHz)",       "test_fspl_550mhz_100m"),
        ("L_urb",         f"{CANONICAL['L_urb_dB']:.1f} dB",         "Corrección urbana ITU-R P.1546",               "test_correccion_urbana_itu"),
        ("G",             f"{CANONICAL['gain_dBi']:.2f} dBi",        "Ganancia realizada @ 550 MHz",                 "test_flpda_ganancia_550mhz · test_ganancia_realizada_vs_directiva"),
        ("S₁₁",           f"{CANONICAL['S11_dB']:.2f} dB",           "Coef. reflexión @ 550 MHz",                    "test_s11_en_banda"),
        ("η_rad",         f"{CANONICAL['eta_rad']:.4f}",             "Eficiencia de radiación (embebida en G)",      "test_eta_rad_uhf · test_eta_rad_rango"),
        ("η_mm",          f"{CANONICAL['eta_mm']:.4f}",              "Eficiencia de adaptación (S₁₁→Γ)",             "test_eta_total_producto"),
        ("η_IMN",         f"{CANONICAL['eta_imn']:.4f}",             "Eficiencia red L (IL = 0,23 dB nominal)",      "test_il_razonable · test_vswr_razonable"),
        ("PCE",           f"{CANONICAL['PCE']:.2f}",                  "PCE doubler (cap del modelo)",                 "test_pce_clip_85pct · test_pce_rango_valido"),
        ("η_PMIC",        f"{CANONICAL['eta_pmic']:.2f}",            "Eficiencia BQ25504 (datasheet SLUSCY3)",       "test_eta_total_producto"),
        ("η_total",       f"{CANONICAL['eta_total']:.4f}",           "FOM de cinco factores",                        "test_eta_total_producto · test_cadena_potencia_canonica"),
        ("T_ciclo",       f"{CANONICAL['T_ciclo_s']:.1f} s",         "Período LoRa SF12 = E_ciclo/P_DC (derivado)",  "—  (consecuencia de P_DC)"),
        ("RMSE Wang",     f"{CANONICAL['RMSE_wang']:.2f} pp",        "Error vs Wang (2022), 7 frecuencias",          "test_validacion_wang2022_rmse · test_pce_wang2022_rmse"),
        ("f_c diodo",     "56,84 GHz",                                 "Frecuencia de corte SMS7630 = 1/(2π·R_S·C_j0)", "test_frecuencia_corte_sms7630"),
    ]
    df = pd.DataFrame(refs, columns=["Símbolo", "Valor", "Descripción", "Test(s) que lo bloquean"])
    st.dataframe(df, hide_index=True, height=560,
                  column_config={
                      "Test(s) que lo bloquean": st.column_config.TextColumn(
                          "Test(s) que lo bloquean",
                          width="large",
                          help="Tests reales presentes en rectenna_dashboard_st/tests/ (51 tests).",
                      ),
                  })

    st.divider()

    # ── Descripción de escenarios ─────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### :material/radio: Escenario B — Referencia cuantitativa")
            st.markdown(
                "- Antena log-periódica fractal **Koch it. 2** (FR-4, 8 dipolos, boom ≈ 50 cm)\n"
                "- Banda UHF: 470 – 900 MHz (TDT DVB-T2 Colombia + ISM 915 MHz)\n"
                "- Diseño Carrel (1961): τ = 0,90 · σ = 0,15 · κ = 43,75 %\n"
                "- Fuente: TDT Cerro Nutibara, EIRP = 70 dBm (conservador frente a 72,15 dBm reales)\n"
                "- Rectificador doubler SMS7630 · PMIC BQ25504 (cold-start 130 mV)\n"
                "- **Es el escenario que cuantifica P_DC y los resultados oficiales.**"
            )
    with col2:
        with st.container(border=True):
            st.markdown("#### :material/cell_tower: Escenario A — Exploración multibanda")
            st.markdown(
                "- Antena fractal **Sierpinski it. 3** (FR-4)\n"
                "- 7 bandas: 1,84 / 2,04 / 2,36 / 2,54 / 3,30 / 4,76 / 5,80 GHz\n"
                "- Modelo RLC paralelo (Puente-Baliarda et al., 1998)\n"
                "- :material/warning: No se cuantifica P_DC final: los EIRP de las fuentes urbanas "
                "  son variables y no están especificadas. Los resultados son **cota superior**."
            )

    st.caption(
        "Para responder \"¿Y si cambio EIRP, distancia, frecuencia…?\" usa la página "
        "**Calculadora del modelo** (sandbox). Para \"¿Por qué creerle al modelo?\" usa "
        "**Validación e incertidumbre**. Para \"¿Para qué sirve esto?\" usa **Viabilidad IoT**."
    )


def _render_sankey():
    """Sankey honesto: η_rad embebida en G; cadena de 4 factores sobre P_in."""
    # Caudales en µW para que la magnitud sea visible
    P_in_uW = CANONICAL['P_in_mW'] * 1000.0           # ≈ 2427 µW
    after_mm   = P_in_uW * CANONICAL['eta_mm']         # ≈ 2390
    after_imn  = after_mm * CANONICAL['eta_imn']       # ≈ 2267
    after_pce  = after_imn * CANONICAL['PCE']          # ≈ 1927
    after_pmic = after_pce * CANONICAL['eta_pmic']     # ≈ 1638  ≈ canonical

    loss_mm   = P_in_uW - after_mm
    loss_imn  = after_mm - after_imn
    loss_pce  = after_imn - after_pce
    loss_pmic = after_pce - after_pmic

    # Nodos: 0=P_in(G incl. η_rad), 1=tras η_mm, 2=tras η_IMN, 3=tras PCE, 4=P_DC útil,
    #         5=pérdida adaptación, 6=pérdida red L, 7=pérdida rectificación, 8=pérdida PMIC
    labels = [
        f"<b>P_in</b><br>{P_in_uW:,.0f} µW<br><i>η_rad ya en G</i>",
        f"tras η_mm<br>{after_mm:,.0f} µW",
        f"tras η_IMN<br>{after_imn:,.0f} µW",
        f"tras PCE<br>{after_pce:,.0f} µW",
        f"<b>P_DC</b><br>{after_pmic:,.0f} µW<br><i>al nodo IoT</i>",
        f"pérdida adaptación<br>{loss_mm:,.0f} µW",
        f"pérdida red L<br>{loss_imn:,.0f} µW",
        f"pérdida rectificación<br>{loss_pce:,.0f} µW",
        f"pérdida PMIC<br>{loss_pmic:,.0f} µW",
    ]
    node_colors = [
        "#0077BB", "#0077BB", "#0077BB", "#0077BB", "#009988",
        "#CC3311", "#CC3311", "#CC3311", "#CC3311",
    ]
    source = [0, 0, 1, 1, 2, 2, 3, 3]
    target = [1, 5, 2, 6, 3, 7, 4, 8]
    value  = [after_mm, loss_mm, after_imn, loss_imn, after_pce, loss_pce, after_pmic, loss_pmic]
    link_colors = [
        "rgba(0,119,187,0.35)", "rgba(204,51,17,0.35)",
        "rgba(0,119,187,0.35)", "rgba(204,51,17,0.35)",
        "rgba(0,119,187,0.35)", "rgba(204,51,17,0.35)",
        "rgba(0,153,136,0.55)", "rgba(204,51,17,0.35)",
    ]

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=labels, pad=24, thickness=22,
            color=node_colors,
            line=dict(color="rgba(255,255,255,0.15)", width=0.5),
        ),
        link=dict(
            source=source, target=target, value=value,
            color=link_colors,
            hovertemplate="%{value:.0f} µW<extra></extra>",
        ),
    ))
    fig.update_layout(
        template="simple_white", height=420,
        title=dict(text="Caudales de potencia en la cadena RF → DC", font=dict(size=14)),
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(size=11),
    )
    st.plotly_chart(fig)
    st.caption(
        f"Lectura: en azul lo que avanza a la siguiente etapa, en rojo lo que se disipa. "
        f"El cuello de botella son las dos eficiencias del 85 % (rectificación y PMIC). "
        f"Total disipado: {(P_in_uW - after_pmic):,.0f} µW · "
        f"Total útil: {after_pmic:,.0f} µW · "
        f"Eficiencia operativa sobre P_in: {after_pmic/P_in_uW*100:.2f} % "
        f"(= η_mm·η_IMN·PCE·η_PMIC, NO η_total)."
    )


def _render_size_comparison():
    """Comparativa visual: silueta del FLPDA Koch contra objetos cotidianos a escala real."""
    fig = go.Figure()

    # Objeto: (nombre, ancho_cm, alto_cm, color, y_offset)
    items = [
        ("Moneda 1 €",       2.3,   2.3,  "#94A3B8",   0),
        ("Tarjeta crédito",  8.6,   5.4,  "#94A3B8",   0),
        ("Smartphone",       7.5,  16.0,  "#94A3B8",   0),
        ("Cuaderno A5",     14.8,  21.0,  "#94A3B8",   0),
        ("Laptop 13''",     30.0,  21.0,  "#94A3B8",   0),
        ("FLPDA Koch (tesis)", 50.0, 32.0, "#FBBF24",  0),
    ]

    # Posicionar uno tras otro con un pequeño gap
    x_cursor = 0.0
    gap = 4.0
    for nombre, w, h, color, _ in items:
        # Caja del objeto (con esquinas redondeadas via line+rectangle)
        fill = "rgba(251,191,36,0.18)" if "FLPDA" in nombre else "rgba(148,163,184,0.10)"
        fig.add_shape(type="rect",
                      x0=x_cursor, y0=0, x1=x_cursor + w, y1=h,
                      line=dict(color=color, width=2),
                      fillcolor=fill)
        # Nombre arriba
        fig.add_annotation(
            x=x_cursor + w / 2, y=h + 3,
            text=f"<b>{nombre}</b><br>{w:.1f} × {h:.1f} cm",
            showarrow=False, font=dict(color=color, size=10),
        )
        x_cursor += w + gap

    # Línea de referencia 1 m
    fig.add_shape(type="line",
                  x0=0, y0=-4, x1=100, y1=-4,
                  line=dict(color="#34D399", width=2))
    fig.add_shape(type="line", x0=0, y0=-5, x1=0, y1=-3,
                  line=dict(color="#34D399", width=2))
    fig.add_shape(type="line", x0=100, y0=-5, x1=100, y1=-3,
                  line=dict(color="#34D399", width=2))
    fig.add_annotation(x=50, y=-7, text="<b>1 metro de referencia</b>",
                       showarrow=False, font=dict(color="#34D399", size=11))

    # Anotación destacando el FLPDA
    flpda_x_center = x_cursor - 50.0 / 2 - gap
    fig.add_annotation(
        x=flpda_x_center, y=42,
        text="★ Antena del trabajo<br><i>cabe sobre un escritorio</i>",
        showarrow=True, arrowhead=2, ax=0, ay=-25,
        font=dict(color="#FBBF24", size=11),
        bgcolor="rgba(15,23,42,0.6)",
        bordercolor="#FBBF24", borderwidth=1, borderpad=5,
    )

    fig.update_layout(
        template='simple_white',
        height=320,
        showlegend=False,
        xaxis=dict(visible=False, range=[-2, x_cursor + 2]),
        yaxis=dict(visible=False, range=[-10, 55], scaleanchor='x', scaleratio=1),
        margin=dict(l=10, r=10, t=20, b=20),
    )
    return fig


def _render_block_diagram():
    """Diagrama de bloques físico de la rectena completa.
    Seis bloques en horizontal con flechas etiquetadas en cada interfaz."""
    fig = go.Figure()

    # Bloques: (x_center, label_top, label_bottom, color, icon)
    blocks = [
        (1.0,  "Torre TDT",       "Cerro Nutibara<br>EIRP = 70 dBm",      "#0EA5E9", "📡"),
        (3.7,  "Antena FLPDA Koch", "8 dipolos · Carrel<br>G = 7,10 dBi · η_mm = 0,9847", "#60A5FA", "📶"),
        (6.4,  "Red de adaptación L", "Q_L = 40 · Q_C = 80<br>η_IMN = 0,9484",  "#A78BFA", "⚙️"),
        (9.1,  "Doblador Greinacher", "2× SMS7630<br>PCE = 0,85 (cap)",     "#FBBF24", "▷|"),
        (11.8, "PMIC BQ25504",    "Boost converter<br>η_PMIC = 0,85",     "#34D399", "🔋"),
        (14.5, "Nodo LoRa SX1276", "SF12 BW125<br>R_load ≈ 1 300 Ω",      "#F87171", "📨"),
    ]

    # Anotaciones de interfaz (entre bloques): (x, top_text, bottom_text)
    interfaces = [
        (2.35, "↓ 67,25 dB",  "FSPL + 6 dB urb."),
        (5.05, "↓ 2,43 mW", "P_in en antena"),
        (7.75, "↓ × η_IMN",   "potencia al diodo"),
        (10.45,"↓ × PCE",     "V_DC ≈ 1 460 mV"),
        (13.15,"↓ × η_PMIC",  "P_DC = 1 638 µW"),
    ]

    # Dibujar cada bloque
    for x, top, bottom, color, icon in blocks:
        # caja
        fig.add_shape(type="rect",
                      x0=x - 1.15, y0=-0.65, x1=x + 1.15, y1=0.65,
                      line=dict(color=color, width=2),
                      fillcolor="rgba(248, 250, 252, 0.95)",
                      layer="below")
        # icono y título arriba
        fig.add_annotation(
            x=x, y=0.45, xref="x", yref="y",
            text=f"<span style='font-size:18px'>{icon}</span><br><b>{top}</b>",
            showarrow=False, font=dict(color=color, size=11),
        )
        # detalle abajo
        fig.add_annotation(
            x=x, y=-0.3, xref="x", yref="y",
            text=bottom,
            showarrow=False, font=dict(color="#334155", size=10),
        )

    # Dibujar flechas e interfaces
    for x_arrow, top_text, bottom_text in interfaces:
        fig.add_annotation(
            x=x_arrow + 0.6, y=0,
            ax=x_arrow - 0.6, ay=0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.4,
            arrowwidth=2.3, arrowcolor="#475569",
        )
        # etiqueta superior
        fig.add_annotation(
            x=x_arrow, y=1.0,
            text=f"<b>{top_text}</b>",
            showarrow=False, font=dict(color="#FBBF24", size=10),
        )
        # etiqueta inferior
        fig.add_annotation(
            x=x_arrow, y=-1.05,
            text=f"<i>{bottom_text}</i>",
            showarrow=False, font=dict(color="#475569", size=9),
        )

    # Resaltar la salida final
    fig.add_annotation(
        x=14.5, y=1.4,
        text="<b>P_DC ≈ 1 638 µW</b><br><i>545 mensajes SF12 / día</i>",
        showarrow=False, font=dict(color="#34D399", size=12),
        bgcolor="rgba(52, 211, 153, 0.12)",
        bordercolor="#34D399", borderwidth=1, borderpad=6,
    )

    # Etiqueta de entrada
    fig.add_annotation(
        x=1.0, y=1.4,
        text="<b>Energía de la radio TV</b><br><i>presente en el aire</i>",
        showarrow=False, font=dict(color="#0EA5E9", size=11),
        bgcolor="rgba(14, 165, 233, 0.10)",
        bordercolor="#0EA5E9", borderwidth=1, borderpad=6,
    )

    fig.update_layout(
        template="simple_white",
        height=300,
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.3, 15.8]),
        yaxis=dict(visible=False, range=[-1.5, 1.9], scaleanchor="x", scaleratio=0.4),
        margin=dict(l=10, r=10, t=20, b=20),
    )
    return fig


render()
