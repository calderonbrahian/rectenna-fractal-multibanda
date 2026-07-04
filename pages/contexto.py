"""
Sección 2 · Contexto: cómo una onda de radio se convierte en electricidad útil.

La idea principal de la página es la TRANSFORMACIÓN de energía (la rectena es el
medio, no el tema). Orden narrativo: fenómeno físico primero, formalización después.
    1. Una rectena = antena + rectificador.
    2. El recorrido de la energía (alto nivel) → diagrama (detalle visual).
    3. Por qué no toda la energía llega (fenómeno) → ecuación como evidencia.
    4. Cierre: pregunta-puente hacia las topologías que se evaluarán.

Sin jerga temprana (IMN, Z₀, LoRa, FR-4, Duroid quedan en niveles posteriores o en
el popover). Narrativa derivada de §2.1.
"""

import streamlit as st
import plotly.graph_objects as go

from utils.pagina import donde_se_desarrolla as _ref


def render():
    st.title(":material/bolt: ¿Cómo una onda de radio se convierte en electricidad útil?")
    st.markdown(
        "*Además de información, las ondas de radio transportan energía electromagnética. "
        "Esta sección explica cómo un dispositivo llamado rectena la captura y la convierte "
        "en electricidad capaz de alimentar un sensor.*"
    )

    # ── Definición mínima ────────────────────────────────────────────────────
    st.subheader("Una rectena = antena + rectificador")
    st.markdown(
        "Una **rectena** es la unión de dos piezas: una antena, que capta las ondas de "
        "radio del aire, y un rectificador, que convierte esa señal en corriente "
        "continua aprovechable. En una sola pieza reúne las dos funciones clave: capturar "
        "la energía y transformarla en electricidad utilizable."
    )

    # ── El recorrido de la energía (alto nivel) + diagrama (detalle visual) ───
    st.subheader("El recorrido de la energía")
    st.markdown(
        "Entre captar la onda y alimentar el sensor, la energía hace un recorrido. Empieza "
        "en el aire como una onda de radio y, para poder usarse, atraviesa varias etapas: "
        "primero se capta, luego se acondiciona para que no se pierda, después se convierte "
        "en corriente continua y por fin se entrega al dispositivo que la usa. La rectena es "
        "el sistema que realiza ese recorrido completo, de izquierda (entra como radio) a "
        "derecha (sale como electricidad):"
    )
    st.plotly_chart(_fig_rectena(), width="stretch")

    st.divider()

    # ── Por qué no toda la energía llega: fenómeno primero, ecuación después ──
    st.subheader("Por qué no toda la energía llega")
    st.markdown(
        "Ese recorrido tiene un precio. Ninguna etapa es perfecta: cada bloque conserva "
        "solo una parte de la energía que recibe y pierde el resto, sea por reflexión, por "
        "calor o por una conversión incompleta. Si la antena y el rectificador no están bien "
        "acoplados, por ejemplo, parte de la energía rebota y se pierde antes de avanzar."
    )
    st.markdown(
        "Y como las etapas van en cadena, esas pérdidas se acumulan: la eficiencia total "
        "depende de todas a la vez, y **la etapa más débil marca el techo** de todo el "
        "sistema. Basta con que un bloque rinda poco para que caiga el conjunto."
    )
    st.markdown(
        "Matemáticamente, esa idea se expresa como el producto de las eficiencias de "
        "cada etapa:"
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

    _ref("§2.1 El sistema rectenna: arquitectura y eficiencia · "
         "§2.4 Parámetros fundamentales de antenas y rectenas")

    st.divider()

    # ── Cierre: pregunta-puente hacia las topologías ─────────────────────────
    st.markdown(
        "Ya sabemos cómo una rectena transforma energía de radio en electricidad. La "
        "siguiente pregunta es **qué diseños de antena se evaluarán** para realizar esa "
        "tarea."
    )
    st.page_link("pages/topologias.py",
                 label="Siguiente — las topologías que se evalúan →",
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
