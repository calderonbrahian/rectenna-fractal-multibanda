"""NIVEL 1 · Demostración — 2/4 · La metodología (el aporte)."""
import streamlit as st
from utils.figuras import figura, FIG

st.title("La metodología")
st.subheader("El aporte no es un dispositivo: es un método reproducible para estudiar el aprovechamiento de RF.")

st.markdown(
    "Toda la cadena de cálculo está implementada en **Python con bibliotecas de código abierto**, "
    "sin software electromagnético comercial ni prototipos físicos. Cada etapa deja código y datos "
    "que cualquiera puede reejecutar."
)

figura(FIG["flujo"], "El método en seis pasos, de la pregunta a los criterios de selección de topología.")

st.divider()
st.markdown("#### Qué es una rectena")
figura(FIG["anatomia"], "Las cinco etapas de la cadena RF→DC, de la onda captada a la energía utilizable.")

st.markdown(
    "**¿Por qué dos topologías?** Para aprender *cuándo* sirve cada geometría: una difusa multibanda "
    "(Sierpinski) y una dirigida de banda ancha (FLPDA Koch). No se busca coronar una, sino dejar "
    "criterios de diseño transferibles."
)
st.caption("Nivel 1 · Demostración — 2/4 · Continúa en «La demostración».")
