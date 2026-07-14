"""
Página de Resultados — el resultado de referencia del proyecto.

Esta página muestra ÚNICAMENTE resultados: el resultado central (P_DC), los
indicadores que lo resumen, el recorrido de la energía hasta obtenerlo y el
detalle técnico (cómo se calcula, dónde se pierde, parámetros). El planteamiento
del problema, el contexto y los escenarios viven en sus propias secciones
narrativas (Introducción, Diseño y metodología, Escenarios estudiados); aquí no
se repiten. Es una vista de lectura, sin controles.

Orden: resultado → cómo fluye la energía → detalle técnico.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from configs.parametros import CANONICAL
from utils.pagina import (encabezado, badge_oficial,
                          donde_se_desarrolla as _ref)
from utils.glosario import metrica, glosario_pagina


def render():
    encabezado(
        ":material/verified: Resultado de referencia del proyecto",
        "La potencia útil que entrega la rectena bajo el escenario base, y cómo se obtiene",
        que_es=("Página de resultados: presenta el resultado central del proyecto (la "
                "potencia continua útil que entrega la rectena bajo el escenario de "
                "referencia) y cómo se obtiene a lo largo de la cadena. Es una vista de "
                "lectura, sin controles editables."),
        para_que_sirve=("Ver en un solo lugar el resultado principal, los indicadores que "
                        "lo resumen, el recorrido de la energía y los parámetros del "
                        "escenario de referencia."),
        entradas=("Ninguna entrada por parte del lector. Los valores corresponden al "
                  "escenario de referencia (transmisor TDT del Cerro Nutibara, 100 m, "
                  "550 MHz)."),
        salidas=("El resultado principal (P_DC), los tres indicadores clave, el diagrama de "
                 "bloques con los caudales de potencia, la identidad de cálculo, el Sankey "
                 "de pérdidas y la tabla de parámetros."),
        como_leer=("Primero el resultado y sus indicadores; después cómo fluye la energía "
                   "hasta obtenerlo; al final, el detalle técnico de cómo se calcula y "
                   "dónde se pierde."),
    )

    badge_oficial()
    st.caption(
        ":material/radio: Estos valores corresponden al **Escenario B** (antena FLPDA Koch "
        "apuntando a la TDT del Cerro Nutibara), el escenario cuantitativo del proyecto. "
        "El planteamiento y la comparación de escenarios están en las secciones "
        "*Introducción* y *Escenarios estudiados*."
    )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 1 · EL RESULTADO PRINCIPAL
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("El resultado principal")
    st.markdown(
        "Bajo el escenario de referencia, el modelo estima que la rectena entrega cerca "
        "de **1 335 µW** (alrededor de 1,6 milivatios) de potencia continua útil a 100 m "
        "del transmisor del Cerro Nutibara.\n\n"
        "Es una potencia pequeña, del orden de la milésima de vatio, pero ese es "
        "justamente el rango en el que trabaja un nodo IoT de bajo consumo. Un sensor de "
        "este tipo no necesita energía de forma continua: pasa la mayor parte del tiempo "
        "en reposo, acumulando la energía recolectada, y la gasta en ráfagas muy breves "
        "para tomar una medida y transmitirla. El interés del resultado no es encender un "
        "equipo grande, sino mostrar que, bajo las hipótesis asumidas, la energía de "
        "radiofrecuencia del entorno podría sostener la operación periódica de un sensor "
        "inalámbrico."
    )
    _ref("§5.3 Caso de estudio: Cerro Nutibara · §5.3.1 Cálculo de la cadena de potencia · "
         "Anexo B.16 (presupuesto de enlace) · Anexo B.17 (cadena de potencia completa)")

    # ── Indicadores: qué pregunta responde cada uno, antes de la cifra ───────
    st.markdown("##### Los tres indicadores que resumen ese resultado")
    st.markdown(
        "Para evaluar si el sistema es viable, el proyecto se apoya en tres indicadores. "
        "Cada uno responde una pregunta distinta:"
    )
    st.markdown(
        "- **Potencia DC útil** — *¿cuánta energía realmente aprovechable entrega la "
        "rectena?* Es lo que queda tras todas las pérdidas de la cadena, disponible para "
        "el dispositivo.\n"
        "- **Mensajes LoRa por día** — *¿alcanza esa energía para una función IoT real?* "
        "Traduce la potencia a algo tangible. El nodo del proyecto usa **LoRa**, una "
        "tecnología de radio de bajo consumo y largo alcance habitual en sensores; "
        "acumula la energía captada y la gasta en envíos breves. Este indicador estima "
        "cuántos mensajes podría enviar en un día alimentándose solo de lo recolectado.\n"
        "- **Eficiencia total** — *¿qué fracción de la energía captada se conserva como "
        "útil?* Resume el desempeño global del sistema y permite compararlo con otros "
        "trabajos publicados."
    )

    msg_dia = 86400.0 / CANONICAL['T_ciclo_s']
    with st.container(horizontal=True):
        metrica(
            "Potencia DC útil",
            f"{CANONICAL['P_dc_uW']:.1f} µW",
            interpretacion="suficiente para el nodo IoT de referencia",
            ayuda="Potencia continua disponible para el nodo IoT tras toda la cadena RF→DC. "
                  "Opera con la PCE en el techo del modelo.",
        )
        metrica(
            "Mensajes LoRa SF12 / día",
            f"≈ {int(msg_dia)}",
            interpretacion="viable para monitoreo periódico (no baja latencia)",
            ayuda=f"Un mensaje cada ≈ {CANONICAL['T_ciclo_s']:.0f} s en operación autónoma "
                  "(recolección continua a 100 m del transmisor TDT).",
        )
        metrica(
            "Eficiencia total η_total",
            f"{CANONICAL['eta_total']*100:.2f} %",
            interpretacion="alta: el escenario opera con la PCE en su techo",
            ayuda="η_rad · η_mm · η_IMN · PCE · η_PMIC. Figura de mérito de reporte; NO se "
                  "multiplica por P_in para obtener P_DC.",
        )
    glosario_pagina("P_DC", "η_total", "PCE", "ganancia")
    _ref("Potencia y eficiencia: §5.3.1 y Anexo B.2 (identidades de cadena, 4 vs 5 "
         "factores) · Mensajes LoRa por día: §4.6 Etapa 3: Presupuesto energético del nodo IoT")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 2 · CÓMO FLUYE LA ENERGÍA HASTA EL RESULTADO
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("Cómo fluye la energía hasta el resultado")
    st.markdown(
        "El diagrama muestra el recorrido de la energía con los valores que el modelo "
        "entrega en cada paso del escenario de referencia. Las etiquetas técnicas se "
        "resumen en la tabla del final; aquí basta con seguir el flujo de izquierda a "
        "derecha. *(Qué es cada etapa de la rectena se explica en la sección "
        "**Introducción → Qué es una rectena**.)*"
    )
    st.plotly_chart(_render_block_diagram(), width="stretch")

    st.markdown(
        "**Leyendo el diagrama de izquierda a derecha:**\n\n"
        "- La señal sale de la torre TDT y viaja por el aire. En esos 100 m la pérdida de "
        "propagación suma **73,25 dB**: la mayor parte es la atenuación natural del espacio "
        "libre (FSPL = 67,25 dB, porque la onda se reparte en una superficie cada vez mayor "
        "al alejarse), y a eso el modelo añade una corrección urbana de 6 dB para representar "
        "obstáculos y reflexiones de un entorno real.\n"
        "- La antena recupera una fracción de lo que queda gracias a su ganancia, que "
        "concentra la energía que recibe. Tras este paso, la potencia disponible a la "
        "entrada del sistema es de unos **2,43 mW**.\n"
        "- La red de adaptación acopla la antena con el rectificador para que casi "
        "toda esa potencia pase a la siguiente etapa, en lugar de reflejarse.\n"
        "- El rectificador transforma la señal de radio en tensión continua, y la "
        "gestión de energía (PMIC) la estabiliza y eleva hasta dejarla lista para "
        "usarse.\n"
        "- Al final de la cadena quedan los **1 335 µW** de potencia útil que recibe el "
        "nodo IoT, que son el resultado principal de esta página."
    )
    _ref("Propagación y la pérdida de 67,25 dB: §3.5 Propagación RF y modelo de Friis · "
         "Parámetros de la antena: §3.4 · FLPDA Koch: §4.4.2 y §5.2 · "
         "Cálculo de la cadena: §5.3.1 · Figura 11 (cascada de eslabones de la cadena RF→DC)")

    with st.expander(":material/straighten:  ¿Qué tan grande es la antena? (comparativa de tamaño)",
                      expanded=False):
        st.markdown(
            "Silueta del FLPDA Koch a escala real, junto a objetos cotidianos para que "
            "se vea sin ambigüedad en qué rango de tamaño está la antena del trabajo."
        )
        st.plotly_chart(_render_size_comparison(), width="stretch")
        st.caption(
            ":material/info: El FLPDA Koch mide aproximadamente **66 cm de boom × 32 cm "
            "de envergadura** (el doble de la longitud del dipolo más largo). Cabe en "
            "una caja del tamaño de una laptop, lo que la hace integrable como módulo "
            "IoT en pared. Sin Koch, la envergadura sería ≈ 57 cm para la misma f_low."
        )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 3 · DETALLE TÉCNICO
    # ════════════════════════════════════════════════════════════════════════
    st.header("Detalle técnico")
    st.caption("Cómo se calcula el resultado y dónde se pierde la energía, "
               "con toda la profundidad del modelo.")

    # ── 3a · Cómo se calcula la potencia útil ────────────────────────────────
    st.subheader("Cómo se calcula la potencia útil")
    st.markdown(
        "La potencia continua útil se obtiene aplicando a **P_in** (la potencia "
        "disponible en la antena) los cuatro factores de las etapas posteriores. "
        "**η_rad ya está incluida en la ganancia realizada G** que define P_in; por eso "
        "no se vuelve a multiplicar."
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
            ":material/warning: **η_total no debe multiplicarse directamente por P_in** para "
            "recuperar P_DC: η_rad ya está contenida en la ganancia G que define P_in, por "
            "lo que hacerlo contabilizaría dos veces la pérdida de radiación."
        )

    _ref("§5.3.1 Cálculo de la cadena de potencia · "
         "Anexo B.2 Identidades de cadena (4 vs 5 factores)")

    st.divider()

    # ── 3b · Dónde se pierde la energía ──────────────────────────────────────
    st.subheader("¿Por dónde se pierde la energía?")
    st.markdown(
        "De los **{p_in:,.0f} µW** que capta la antena, solo **{p_dc:,.0f} µW** "
        "llegan al nodo IoT. El siguiente diagrama de flujo (Sankey) separa, en cada "
        "etapa, lo que avanza (azul) de lo que se disipa (rojo), para ver dónde se "
        "pierde más.".format(
            p_in=CANONICAL['P_in_mW'] * 1000.0,
            p_dc=CANONICAL['P_dc_uW'],
        )
    )

    _render_sankey()

    with st.container(border=True):
        st.markdown(
            "**Qué dice este diagrama** — esta descomposición de la cadena de potencia "
            "corresponde al análisis desarrollado en el proyecto (Anexo B.12)."
        )
        st.markdown(
            "- La pérdida más importante es la rectificación (RF→DC): se lleva unos "
            "**340 µW (≈ 14 %)** de la energía inicial. Le sigue de cerca la gestión de "
            "energía del PMIC, con unos **289 µW (≈ 12 %)**.\n"
            "- Esas dos conversiones del 85 % son, entonces, las que más limitan el "
            "desempeño. Son pérdidas intrínsecas a la electrónica de conversión con esta "
            "tecnología: en el modelo operan en su techo y son las más difíciles de "
            "reducir.\n"
            "- Las pérdidas que dependen del diseño, la adaptación de la antena "
            "(≈ 37 µW, 1,5 %) y la red de adaptación (≈ 123 µW, 5 %), ya son pequeñas, "
            "porque sus eficiencias se mantienen altas.\n"
            "- En el balance final, de la energía que capta la antena, alrededor del "
            "**67 %** llega como potencia útil al nodo IoT; el 33 % restante se disipa, "
            "sobre todo en la conversión de potencia."
        )

    _ref("§3.1 El sistema rectenna: arquitectura y eficiencia · "
         "Anexo B.12 Anatomía de la cadena de potencia (descomposición Sankey)")

    with st.expander(":material/visibility:  Cómo leer este diagrama (colores y anchos)",
                      expanded=False):
        st.markdown(
            "- **Azul:** potencia que avanza a la siguiente etapa. **Rojo:** potencia "
            "que se disipa (se pierde como calor) en esa etapa.\n"
            "- **El ancho de cada flujo es proporcional a los µW.** Cuanto más gruesa "
            "la banda roja, más energía se pierde ahí.\n"
            "- **El cuello de botella son las dos conversiones del 85 %** "
            "(rectificación RF→DC y gestión de energía del PMIC): juntas explican la "
            "mayor parte de la pérdida.\n"
            "- Las eficiencias de antena y de adaptación (η_mm, η_IMN) son altas, así que "
            "sus pérdidas son comparativamente pequeñas."
        )

    st.divider()

    # ── 3c · Tabla de parámetros del escenario de referencia ─────────────────
    st.subheader("Resumen de parámetros del escenario de referencia")
    st.caption("Variables principales del modelo bajo el escenario base. "
               "El significado físico de las más importantes se detalla más abajo.")
    refs = [
        ("P_DC",      f"{CANONICAL['P_dc_uW']:.1f} µW",   "Potencia continua útil que llega al nodo IoT tras toda la cadena."),
        ("V_DC",      f"{CANONICAL['V_dc_mV']:.0f} mV",   "Tensión continua de salida del sistema."),
        ("P_in",      f"+{CANONICAL['P_in_dBm']:.2f} dBm", "Potencia de RF disponible en la antena (a 100 m del transmisor)."),
        ("FSPL",      f"{CANONICAL['FSPL_dB']:.2f} dB",   "Pérdida por propagación en espacio libre (100 m, 550 MHz)."),
        ("L_urb",     f"{CANONICAL['L_urb_dB']:.1f} dB",  "Corrección adicional por entorno urbano (ITU-R P.1546)."),
        ("G",         f"{CANONICAL['gain_dBi']:.2f} dBi", "Ganancia realizada de la antena a 550 MHz."),
        ("S₁₁",       f"{CANONICAL['S11_dB']:.2f} dB",    "Reflexión a la entrada: qué tan bien adaptada está la antena."),
        ("η_rad",     f"{CANONICAL['eta_rad']:.4f}",      "Eficiencia de radiación de la antena (ya incluida en G)."),
        ("η_mm",      f"{CANONICAL['eta_mm']:.4f}",       "Eficiencia por adaptación de impedancia (derivada de S₁₁)."),
        ("η_IMN",     f"{CANONICAL['eta_imn']:.4f}",      "Eficiencia de la red de adaptación L (IL ≈ 0,23 dB)."),
        ("PCE",       f"{CANONICAL['PCE']:.2f}",          "Eficiencia de conversión RF→DC del rectificador (techo del modelo)."),
        ("η_PMIC",    f"{CANONICAL['eta_pmic']:.2f}",     "Eficiencia del gestor de energía BQ25504."),
        ("η_total",   f"{CANONICAL['eta_total']:.4f}",    "Eficiencia global del sistema (figura de mérito de 5 factores)."),
        ("T_ciclo",   f"{CANONICAL['T_ciclo_s']:.1f} s",  "Tiempo entre mensajes LoRa SF12 en operación autónoma."),
        ("RMSE Wang", f"{CANONICAL['RMSE_wang']:.2f} pp", "Error del modelo frente a los datos de Wang (2022)."),
        ("f_c diodo", "56,84 GHz",                         "Frecuencia de corte del diodo SMS7630 = 1/(2π·R_S·C_j0)."),
    ]
    df = pd.DataFrame(refs, columns=["Símbolo", "Valor", "Qué representa"])
    st.dataframe(df, hide_index=True, height=560,
                  column_config={
                      "Símbolo": st.column_config.TextColumn("Símbolo", width="small"),
                      "Valor": st.column_config.TextColumn("Valor", width="small"),
                      "Qué representa": st.column_config.TextColumn("Qué representa", width="large"),
                  })

    with st.expander(":material/menu_book:  ¿Qué significan las variables principales?",
                      expanded=False):
        st.markdown(
            "- **P_DC** — Potencia continua útil disponible a la salida del sistema. "
            "Es la energía que finalmente podría aprovechar un dispositivo IoT.\n"
            "- **P_in** — Potencia de radiofrecuencia que la antena logra captar del "
            "entorno; es el punto de partida de toda la cadena.\n"
            "- **G** — Ganancia de la antena: cuánto concentra la energía recibida en "
            "la dirección útil. Ya incorpora la eficiencia de radiación η_rad.\n"
            "- **η_IMN** — Eficiencia de la red de adaptación. Indica qué porcentaje de "
            "la potencia captada logra transferirse hacia el rectificador.\n"
            "- **PCE** — Eficiencia de conversión RF→DC. Mide qué tan bien el "
            "rectificador transforma energía de radiofrecuencia en energía continua. "
            "En el escenario base opera en el techo del modelo (0,85).\n"
            "- **η_total** — Eficiencia global del sistema, usada como figura de mérito "
            "para comparar con la literatura. No se multiplica por P_in para obtener P_DC."
        )

    _ref("Reporte canónico de magnitudes: Anexo B.1 · "
         "Definición de cada parámetro: §3.4 Parámetros fundamentales de antenas y rectenas")

    st.divider()
    st.page_link("pages/viabilidad_iot.py",
                 label="Siguiente — ¿qué se puede hacer con esta energía? →",
                 icon=":material/sensors:")


def _render_sankey():
    """Sankey honesto: η_rad embebida en G; cadena de 4 factores sobre P_in."""
    # Caudales en µW para que la magnitud sea visible
    P_in_uW = CANONICAL['P_in_mW'] * 1000.0           # ≈ 2427 µW
    after_mm   = P_in_uW * CANONICAL['eta_mm']         # ≈ 2390
    after_imn  = after_mm * CANONICAL['eta_imn']       # ≈ 2267
    after_pce  = after_imn * CANONICAL['PCE']          # ≈ 1927
    after_pmic = after_pce * CANONICAL['eta_pmic']     # ≈ 1335  ≈ canonical

    loss_mm   = P_in_uW - after_mm
    loss_imn  = after_mm - after_imn
    loss_pce  = after_imn - after_pce
    loss_pmic = after_pce - after_pmic

    def pct(x):
        return f"{x / P_in_uW * 100:.0f} %"

    # Nodos: 0=P_in(G incl. η_rad), 1=tras η_mm, 2=tras η_IMN, 3=tras PCE, 4=P_DC útil,
    #         5=pérdida adaptación, 6=pérdida red L, 7=pérdida rectificación, 8=pérdida PMIC
    labels = [
        f"<b>P_in</b><br>{P_in_uW:,.0f} µW (100 %)<br><i>η_rad ya en G</i>",
        f"tras η_mm<br>{after_mm:,.0f} µW",
        f"tras η_IMN<br>{after_imn:,.0f} µW",
        f"tras PCE<br>{after_pce:,.0f} µW",
        f"<b>P_DC</b><br>{after_pmic:,.0f} µW ({pct(after_pmic)})<br><i>al nodo IoT</i>",
        f"pérdida adaptación<br>{loss_mm:,.0f} µW ({pct(loss_mm)})",
        f"pérdida red L<br>{loss_imn:,.0f} µW ({pct(loss_imn)})",
        f"pérdida rectificación<br>{loss_pce:,.0f} µW ({pct(loss_pce)})",
        f"pérdida PMIC<br>{loss_pmic:,.0f} µW ({pct(loss_pmic)})",
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
        textfont=dict(color="#0f172a", size=12),
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
        title=dict(text="Diagrama de flujo · azul = avanza · rojo = se pierde",
                   font=dict(size=14)),
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(size=11),
    )
    st.plotly_chart(fig)
    st.caption(
        f"Total disipado: {(P_in_uW - after_pmic):,.0f} µW · "
        f"Total útil: {after_pmic:,.0f} µW · "
        f"Eficiencia operativa sobre P_in: {after_pmic/P_in_uW*100:.2f} % "
        f"(= η_mm·η_IMN·PCE·η_PMIC, distinta de η_total)."
    )


def _render_size_comparison():
    """Comparativa visual: silueta del FLPDA Koch contra objetos cotidianos a escala real."""
    fig = go.Figure()

    # Objeto: (nombre, ancho_cm, alto_cm, color, y_offset)
    items = [
        ("Moneda 1 €",       2.3,   2.3,  "#475569",   0),
        ("Tarjeta crédito",  8.6,   5.4,  "#475569",   0),
        ("Smartphone",       7.5,  16.0,  "#475569",   0),
        ("Cuaderno A5",     14.8,  21.0,  "#475569",   0),
        ("Laptop 13''",     30.0,  21.0,  "#475569",   0),
        ("FLPDA Koch (proyecto)", 50.0, 32.0, "#B45309",  0),
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
                  line=dict(color="#059669", width=2))
    fig.add_shape(type="line", x0=0, y0=-5, x1=0, y1=-3,
                  line=dict(color="#059669", width=2))
    fig.add_shape(type="line", x0=100, y0=-5, x1=100, y1=-3,
                  line=dict(color="#059669", width=2))
    fig.add_annotation(x=50, y=-7, text="<b>1 metro de referencia</b>",
                       showarrow=False, font=dict(color="#059669", size=11))

    # Anotación destacando el FLPDA
    flpda_x_center = x_cursor - 50.0 / 2 - gap
    fig.add_annotation(
        x=flpda_x_center, y=42,
        text="★ Antena del trabajo<br><i>cabe sobre un escritorio</i>",
        showarrow=True, arrowhead=2, ax=0, ay=-25,
        font=dict(color="#B45309", size=11),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#B45309", borderwidth=1, borderpad=5,
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
        (1.0,  "Torre TDT",       "Cerro Nutibara<br>EIRP = 72,15 dBm",   "#0369A1", "📡"),
        (3.7,  "Antena FLPDA Koch", "12 dipolos · Carrel<br>G = 4,97 dBi · η_mm = 0,983", "#2563EB", "📶"),
        (6.4,  "Red de adaptación L", "Q_L = 40 · Q_C = 80<br>η_IMN = 0,9484",  "#7C3AED", "⚙️"),
        (9.1,  "Doblador Greinacher", "2× SMS7630<br>PCE = 0,85 (cap)",     "#B45309", "▷|"),
        (11.8, "PMIC BQ25504",    "Boost converter<br>η_PMIC = 0,85",     "#059669", "🔋"),
        (14.5, "Nodo LoRa SX1276", "SF12 BW125<br>R_load ≈ 1 300 Ω",      "#DC2626", "📨"),
    ]

    # Anotaciones de interfaz (entre bloques): (x, top_text, bottom_text)
    interfaces = [
        (2.35, "↓ 73,25 dB",  "FSPL 67,25 + 6 urb."),
        (5.05, "↓ 2,43 mW", "P_in en antena"),
        (7.75, "↓ × η_IMN",   "potencia al diodo"),
        (10.45,"↓ × PCE",     "V_DC ≈ 1 460 mV"),
        (13.15,"↓ × η_PMIC",  "P_DC = 1 335 µW"),
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
            showarrow=False, font=dict(color="#B45309", size=10),
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
        text="<b>P_DC ≈ 1 335 µW</b><br><i>545 mensajes SF12 / día</i>",
        showarrow=False, font=dict(color="#047857", size=12),
        bgcolor="rgba(5, 150, 105, 0.12)",
        bordercolor="#059669", borderwidth=1, borderpad=6,
    )

    # Etiqueta de entrada
    fig.add_annotation(
        x=1.0, y=1.4,
        text="<b>Energía de la radio TV</b><br><i>presente en el aire</i>",
        showarrow=False, font=dict(color="#0369A1", size=11),
        bgcolor="rgba(3, 105, 161, 0.10)",
        bordercolor="#0369A1", borderwidth=1, borderpad=6,
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
