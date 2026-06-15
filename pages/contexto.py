"""
Sección 2 · Contexto: el sistema rectena.
Explica, con un diagrama conceptual y definiciones en hover, qué es una rectena y
cómo se encadenan sus etapas. La ecuación de eficiencia lleva el desglose de
términos en un popover (no como bloque). Narrativa derivada de §2.1.
"""

import streamlit as st
import plotly.graph_objects as go

from utils.pagina import encabezado, donde_se_desarrolla as _ref
from utils.glosario import termino


def render():
    encabezado(
        ":material/bolt: Contexto: qué es una rectena",
        "El sistema de recolección de energía RF, bloque por bloque",
        que_es=("Explica qué es una rectena y cómo se encadenan sus etapas, para tener el "
                "vocabulario antes de ver los escenarios y los resultados."),
        para_que_sirve=("Comprender el sistema completo —de la antena a la carga— y por qué "
                        "la eficiencia total es siempre el producto de varias etapas."),
        entradas="Ninguna; es una página de lectura.",
        salidas=("Un diagrama de la cadena de la rectena, la definición de cada etapa y la "
                 "expresión de la eficiencia total del sistema."),
    )

    # ── Qué es + diagrama conceptual de la cadena ────────────────────────────
    st.subheader("Una rectena = antena + rectificador")
    st.markdown(
        f"Una {termino('rectena')} es la unión de dos piezas: una **antena**, que capta las "
        "ondas de radio presentes en el aire, y un **rectificador**, que convierte esa "
        "señal en corriente continua aprovechable. Lo hace **directamente**, sin etapas "
        "intermedias de conversión.\n\n"
        "Entre la antena y el dispositivo final hay unos bloques de apoyo. Este es el "
        "recorrido completo de la energía, de izquierda (entra como radio) a derecha (sale "
        "como corriente continua):",
        unsafe_allow_html=True,
    )
    st.plotly_chart(_fig_rectena(), width="stretch")
    st.markdown(
        f"En palabras: la **antena** capta, la {termino('IMN')} **acopla**, el "
        f"{termino('rectificador')} **convierte** la radio en continua, el "
        f"{termino('filtro DC')} la **alisa** y la {termino('carga')} —aquí, el **nodo "
        "IoT**— la **usa**. "
        ":material/info: *Pasa el cursor sobre los términos subrayados para ver su definición.*",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Eficiencia total: ecuación + desglose en popover ─────────────────────
    st.subheader("Por qué la eficiencia total es un producto, no una suma")
    st.markdown(
        "**Ninguna etapa es perfecta:** cada bloque conserva solo una parte de la energía "
        "que recibe y pierde el resto (como calor, reflexión o conversión incompleta). Por "
        "eso la **eficiencia total** del sistema es el **producto** de las eficiencias de "
        "todas las etapas:"
    )
    st.latex(
        r"\eta_{total} = \eta_{rad} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \text{PCE} \cdot \eta_{PMIC}"
    )
    with st.popover(":material/help: ¿Qué significa cada término?"):
        st.markdown(
            "Todos son **eficiencias**: fracciones entre 0 y 1 (sin unidades), la parte de "
            "la energía que **sobrevive** a cada etapa.\n"
            "- **η_rad** — eficiencia de radiación de la antena (qué fracción capta en lugar "
            "de disiparse como calor).\n"
            "- **η_mm** — eficiencia de adaptación (*mismatch*): qué fracción entra a la "
            "antena en vez de reflejarse.\n"
            "- **η_IMN** — eficiencia de la red de adaptación entre antena y rectificador.\n"
            "- **PCE** — eficiencia de conversión RF→DC del rectificador.\n"
            "- **η_PMIC** — eficiencia del gestor de energía que entrega la potencia a la carga."
        )

    st.markdown(
        "**Cómo se lee físicamente:** al multiplicarse, **basta con que una etapa sea baja "
        "para que toda la eficiencia caiga** —es una cadena, no una suma—. La etapa con "
        "menor eficiencia es la que **domina las pérdidas** y marca el techo de todo el "
        "sistema. Por eso conviene que cada bloque rinda lo más alto posible."
    )
    st.caption(
        "Orden de magnitud: en sustratos de baja pérdida (Duroid 5880) las eficiencias "
        "totales típicas son del **28–50 % a −10 dBm**; sobre **FR-4** —el sustrato "
        "económico que adopta este proyecto— se ubican entre el **30 % y el 40 %**."
    )

    _ref("§2.1 El sistema rectenna: arquitectura y eficiencia · "
         "§2.4 Parámetros fundamentales de antenas y rectenas")

    st.page_link("pages/topologias.py",
                 label="Siguiente — las dos topologías evaluadas →",
                 icon=":material/arrow_forward:")


def _fig_rectena():
    """Diagrama conceptual de la cadena de la rectena (sin cifras): cinco bloques
    en serie con su función, de RF (izquierda) a corriente continua (derecha)."""
    fig = go.Figure()

    # (x_centro, nombre, función, color, icono)
    blocks = [
        (1.0,  "Antena",            "capta las<br>ondas de radio",   "#0369A1", "📡"),
        (3.6,  "Red de adaptación", "acopla antena<br>y rectificador", "#7C3AED", "⚙️"),
        (6.2,  "Rectificador",      "convierte RF<br>en continua",   "#B45309", "▷|"),
        (8.8,  "Filtro DC",         "alisa la<br>tensión",           "#2563EB", "〜"),
        (11.4, "Carga · nodo IoT",  "usa la<br>energía",             "#059669", "🔋"),
    ]

    for x, nombre, funcion, color, icono in blocks:
        fig.add_shape(type="rect", x0=x - 1.05, y0=-0.62, x1=x + 1.05, y1=0.62,
                      line=dict(color=color, width=2),
                      fillcolor="rgba(248, 250, 252, 0.95)", layer="below")
        fig.add_annotation(x=x, y=0.30, xref="x", yref="y",
                           text=f"<span style='font-size:18px'>{icono}</span><br><b>{nombre}</b>",
                           showarrow=False, font=dict(color=color, size=11))
        fig.add_annotation(x=x, y=-0.34, xref="x", yref="y", text=f"<i>{funcion}</i>",
                           showarrow=False, font=dict(color="#334155", size=9))

    # Flechas entre bloques
    for i in range(len(blocks) - 1):
        x0 = blocks[i][0] + 1.05
        x1 = blocks[i + 1][0] - 1.05
        fig.add_annotation(x=x1, y=0, ax=x0, ay=0,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=3, arrowsize=1.3,
                           arrowwidth=2.2, arrowcolor="#475569")

    # Etiquetas de entrada/salida
    fig.add_annotation(x=1.0, y=1.15, text="<b>Entra:</b> energía de radio (RF)",
                       showarrow=False, font=dict(color="#0369A1", size=11),
                       bgcolor="rgba(3,105,161,0.10)", bordercolor="#0369A1",
                       borderwidth=1, borderpad=5)
    fig.add_annotation(x=11.4, y=1.15, text="<b>Sale:</b> corriente continua",
                       showarrow=False, font=dict(color="#047857", size=11),
                       bgcolor="rgba(5,150,105,0.12)", bordercolor="#059669",
                       borderwidth=1, borderpad=5)

    fig.update_layout(
        template="simple_white", height=260, showlegend=False,
        xaxis=dict(visible=False, range=[-0.4, 12.8]),
        yaxis=dict(visible=False, range=[-1.0, 1.6], scaleanchor="x", scaleratio=0.45),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


render()
