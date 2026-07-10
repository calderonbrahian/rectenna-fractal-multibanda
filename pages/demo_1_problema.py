"""NIVEL 1 · Demostración — 1/4 · El problema y la pregunta."""
import streamlit as st
from utils.figuras import figura, FIG

st.title("El problema")
st.subheader("Los nodos IoT mueren por su batería; alrededor sobra energía de radio.")

st.markdown(
    "Las ciudades están atravesadas de forma permanente por emisiones de radiofrecuencia "
    "—radio, televisión digital, telefonía móvil—. Se diseñaron para transportar información, "
    "pero son también **una infraestructura energética invisible**. Un nodo IoT de bajo consumo "
    "podría, en principio, tomar algo de esa energía y aliviar su mayor limitación: la batería."
)

figura(FIG["fuentes"],
       "De muchas fuentes de RF ambiental a un caso demostrador (TDT). El método no depende de la fuente elegida.")

st.divider()
st.markdown("#### La pregunta de investigación")
st.info(
    "¿Es viable recuperar energía de radiofrecuencia ambiental para alimentar dispositivos IoT "
    "de bajo consumo, y puede demostrarse mediante un modelo analítico **reproducible**?"
)
st.caption("Nivel 1 · Demostración — 1/4 · Continúa en «La metodología».")
