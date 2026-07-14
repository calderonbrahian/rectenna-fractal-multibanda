"""NIVEL 1 · Demostración — 3/4 · Qué se demostró."""
import streamlit as st
from configs.parametros import CANONICAL
from utils.figuras import figura, FIG

st.title("Qué se demostró")
st.subheader("Caso de estudio: la TDT del Cerro Nutibara (Valle de Aburrá).")

c1, c2, c3 = st.columns(3)
c1.metric("Potencia DC útil @ 100 m", "1 335 µW")
c2.metric("Eficiencia total (5 factores)", "40,23 %")
c3.metric("Error vs. Wang (2022)", "15,50 pp")

st.markdown(
    "Con la antena dirigida (Escenario B) frente al transmisor de TDT, el modelo estima **1 335 µW** "
    "de potencia útil a 100 m: suficiente para sostener un nodo IoT de bajo consumo. La difusa "
    "multibanda (Escenario A) queda como límite ilustrativo: adapta solo 1 de 7 bandas sobre FR-4."
)

figura(FIG["cascada"], "¿Dónde se va la energía? La cascada de eficiencia de la cadena RF→DC (Escenario B).")

col1, col2 = st.columns(2)
with col1:
    figura(FIG["pce_ambos"], "Los dos escenarios comparados: B (verde) llega al techo del rectificador; A (oro), no.")
with col2:
    figura(FIG["wang"], "Credibilidad: el modelo contrastado punto a punto con mediciones publicadas (Wang, 2022).")

st.success(
    "**Es viable.** Y la comparación deja criterios: A, omnidireccional y compacto, para IoT interior; "
    "B, directivo, para un nodo exterior fijo frente a una fuente firme."
)
st.caption("Nivel 1 · Demostración — 3/4 · Continúa en «El estudio y su alcance».")
