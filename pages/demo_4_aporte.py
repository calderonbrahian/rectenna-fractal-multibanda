"""NIVEL 1 · Demostración — 4/4 · El aporte y su alcance."""
import streamlit as st
from utils.figuras import figura, FIG

st.title("El aporte")
st.subheader("Queda un método, no solo un número.")

figura(FIG["maestra"], "El trabajo completo en una figura: del problema a las conclusiones.")

st.markdown(
    "El resultado central no es que la TDT del Cerro Nutibara alimente un nodo IoT. Ese fue el "
    "**caso demostrador**. El aporte es una **metodología analítica, computacional y reproducible** "
    "para estudiar el aprovechamiento de energía de RF ambiental —de cualquier fuente—, validada "
    "contra literatura y disponible como código abierto."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Verificable**")
    st.caption("56 pruebas automáticas fijan cada valor canónico; el código es público.")
with col2:
    st.markdown("**Transferible**")
    st.caption("Otras fuentes (FM, telefonía) se estudian re-escalando la misma geometría.")
with col3:
    st.markdown("**Honesto**")
    st.caption("Es modelado, no medición: sus límites están declarados y cuantificados.")

st.info(
    "El caso colombiano demuestra la aplicación; no define el alcance. "
    "¿Quiere ver el detalle técnico? Pase al **Laboratorio** en el menú lateral."
)
st.caption("Nivel 1 · Demostración — 4/4 · Fin del recorrido de 3 minutos.")
