"""
PÁGINA 1 · ¿Qué problema resuelve la investigación?
================================================================================
La historia de entrada. Sin gráficos técnicos: solo la tensión que motiva el
trabajo (dispositivos limitados por energía frente a RF ambiental disponible
día y noche), la pregunta de investigación textual y el mensaje principal.
Las figuras narrativas del pipeline (C1 / R1) hacen el apoyo visual.
"""

import streamlit as st

from utils.ui import css, cabecera, figura, tarjeta_ab, dato

css()

cabecera(
    kicker="La pregunta",
    pregunta="¿Puede la radiación de fondo alimentar un sensor?",
    bajada="Miles de millones de dispositivos de bajo consumo dependen de baterías "
           "que hay que cambiar. Mientras tanto, el aire de una ciudad está lleno de "
           "energía de radiofrecuencia —televisión, celular, WiFi— que radia día y noche.",
)

st.markdown(
    '<p class="lead">Este trabajo estudia si una antena impresa de geometría '
    '<b>fractal</b>, acoplada a un rectificador, puede recoger esa energía y '
    'sostener un nodo de Internet de las Cosas. No busca una cifra de récord: '
    'busca entender <b>cuánta energía hay realmente disponible</b> y <b>qué '
    'estrategia de captación</b> conviene según la fuente.</p>',
    unsafe_allow_html=True,
)

st.write("")
figura(
    "C1_por_que_rf.png",
    "Por qué la RF ambiental: energía disponible de forma continua, sin sol ni "
    "vibración, complementando el almacenamiento del nodo.",
)

# ── El hilo conductor de toda la app: dos estrategias ─────────────────────────
st.markdown("### Dos formas de captar la misma energía")
st.write(
    "Toda la investigación se organiza en torno a un contraste. Recorre la app "
    "con esta pregunta en mente:"
)
c1, c2 = st.columns(2)
with c1:
    tarjeta_ab(
        "a", "A · Concentrar",
        "Apuntar a una única fuente dominante (una torre de televisión) y "
        "extraer de ella todo lo posible con una rectena difusa multibanda.",
    )
with c2:
    tarjeta_ab(
        "b", "B · Acumular",
        "Sumar la energía repartida en muchas bandas débiles con una antena "
        "dirigida de banda ancha (FLPDA Koch) hacia el emisor más fuerte.",
    )

st.write("")
st.divider()

# ── El mensaje principal, anticipado ──────────────────────────────────────────
st.markdown("### El mensaje, en una frase")
st.markdown(
    '<p class="lead">Cuando existe una fuente dominante, <b>concentrarse en ella '
    'gana</b>; cuando la energía está repartida, <b>acumular muchas bandas</b> es '
    'lo que rinde. El caso colombiano (televisión digital en Medellín) es solo la '
    '<b>demostración</b> de un método general.</p>',
    unsafe_allow_html=True,
)

col = st.columns(3)
with col[0]:
    dato("día y noche", "la RF ambiental no depende del clima", "teal")
with col[1]:
    dato("2 estrategias", "concentrar (A) vs acumular (B)", "a")
with col[2]:
    dato("1 método", "reproducible y validado", "b")

st.write("")
st.caption(
    "Continúa en «El modelo» para ver cómo se calcula la energía, o salta directo "
    "a «Los hallazgos» para el resultado."
)
