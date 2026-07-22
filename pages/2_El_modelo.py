"""
PÁGINA 2 · ¿Cómo funciona el modelo?
================================================================================
La cadena energética explorable, contada desde el punto de vista del PROYECTO
(no de la electrónica de detalle). Seis eslabones, cada uno con 2-3 frases y su
apoyo visual. Un único control interactivo simple —el nivel de potencia de
entrada frente a la eficiencia de conversión— muestra la TENDENCIA del modelo
llamando en vivo a `core.rectifier.PCE`, no números aislados.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core.rectifier import RectifierCircuit
from utils.ui import css, cabecera, figura, A_ORO, B_VERDE, TEAL, MUTE, INK

css()

cabecera(
    kicker="El modelo",
    pregunta="¿Cómo se convierte una onda en energía útil?",
    bajada="El modelo sigue la energía por seis eslabones, desde la torre emisora "
           "hasta el sensor. Cada eslabón resta una parte; entender dónde se pierde "
           "explica por qué una estrategia rinde más que otra.",
)

figura(
    "R3_camino_energia.png",
    "El camino de la energía: qué fracción sobrevive en cada paso de la cadena RF-DC.",
)

st.markdown("### Recorre la cadena, eslabón por eslabón")
st.caption("Despliega cada etapa. Todo lo que se muestra proviene del modelo, no de valores fijos.")

with st.expander("1 · Fuentes RF — de dónde viene la energía", expanded=True):
    st.write(
        "El aire urbano tiene decenas de emisores: televisión digital, celular, "
        "WiFi. No todos aportan igual. Una torre de televisión concentra mucha "
        "potencia en una banda; el celular y el WiFi reparten poca en muchas. "
        "Esa asimetría es la que decide la estrategia."
    )
    figura("FigC1_fuentes_a_caso.png",
           "Del universo de fuentes ambientales al caso concreto de la demostración.")

with st.expander("2 · Captación — la antena fractal"):
    st.write(
        "La antena recoge la onda. Una geometría **fractal** (Sierpinski, Koch) "
        "permite resonar en varias frecuencias con un tamaño compacto. Aquí se "
        "pierde por radiación imperfecta y por desajuste de impedancia: solo una "
        "fracción de lo que llega entra al circuito."
    )
    figura("FigC3_anatomia_rectena.png",
           "Anatomía de la rectena: antena, red de adaptación y rectificador.")

with st.expander("3 · Conversión RF-DC — el rectificador (control en vivo)"):
    st.write(
        "El diodo Schottky convierte la onda de RF en corriente continua. Su "
        "eficiencia (**PCE**) no es constante: crece con la potencia de entrada y "
        "se satura. Mueve el control y observa la **tendencia** —el punto marcado "
        "es tu nivel; la curva completa la calcula el modelo de Shockley en vivo."
    )
    p_in = st.slider("Potencia de entrada al rectificador [dBm]",
                     min_value=-30, max_value=5, value=-10, step=1,
                     help="Nivel disponible en la antena. A más potencia, mejor conversión, hasta saturar.")

    rect = RectifierCircuit(topology="doubler", R_load=1300.0)
    barrido = np.arange(-30, 6, 1.0)
    pce_curva = [rect.PCE(float(p), 700e6) * 100 for p in barrido]
    pce_pt = rect.PCE(float(p_in), 700e6) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=barrido, y=pce_curva, mode="lines",
                             line=dict(color=TEAL, width=3), name="PCE(Shockley)"))
    fig.add_trace(go.Scatter(x=[p_in], y=[pce_pt], mode="markers",
                             marker=dict(color=A_ORO, size=14, line=dict(color="white", width=2)),
                             name="tu nivel"))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
        xaxis_title="Potencia de entrada [dBm]", yaxis_title="Eficiencia de conversión [%]",
        plot_bgcolor="white", font=dict(color=INK),
    )
    fig.update_yaxes(gridcolor="#eceff3", range=[0, 90])
    fig.update_xaxes(gridcolor="#eceff3")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"A {p_in} dBm el modelo entrega una PCE de **{pce_pt:.0f} %**. "
        "La curva satura en el 85 % (límite físico del diodo SMS7630)."
    )

with st.expander("4 · Gestión — el conversor de arranque (PMIC)"):
    st.write(
        "La corriente continua cruda es demasiado débil e inestable para un chip. "
        "Un conversor *boost* (BQ25504) la eleva y estabiliza, con la condición de "
        "arrancar en frío por encima de 130 mV. Añade su propia eficiencia (~85 %) "
        "a la cadena."
    )

with st.expander("5 · Almacenamiento — el tampón de energía"):
    st.write(
        "La energía llega en un goteo continuo, pero el sensor la gasta a ráfagas "
        "(cada transmisión consume mucho durante poco tiempo). Un supercondensador "
        "o una batería pequeña acumula el goteo y libera la ráfaga cuando toca "
        "transmitir."
    )

with st.expander("6 · Dispositivo — el nodo IoT"):
    st.write(
        "Al final está el sensor LoRa: lee un dato y lo transmite cada cierto "
        "tiempo. Si la energía media cosechada supera su consumo medio, el nodo "
        "opera indefinidamente. La pregunta de viabilidad es exactamente esa "
        "comparación, y se responde en «Los hallazgos»."
    )

st.divider()
st.markdown(
    f"<p class='lead'>Cada eslabón multiplica una eficiencia. El producto de todas "
    f"—de la antena al PMIC— es la <b>figura de mérito</b> de la cadena. Dónde se "
    f"pierde más depende del <span style='color:{A_ORO};font-weight:600'>escenario A</span> "
    f"o <span style='color:{B_VERDE};font-weight:600'>escenario B</span>, y eso es "
    f"lo que la investigación mide.</p>",
    unsafe_allow_html=True,
)
