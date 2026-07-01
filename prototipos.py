"""
HUB de prototipos animados (experimentales).

Reúne las simulaciones de canvas en una sola app con selector lateral.
NO forma parte de la aplicación oficial del trabajo de grado.

Ejecutar:  .venv/Scripts/streamlit run prototipos.py
"""

import streamlit as st

st.set_page_config(page_title="Prototipos · Rectena fractal",
                   page_icon=":material/animation:", layout="wide")

pg = st.navigation(
    {
        "Inicio": [
            st.Page("prototipo_portada.py", title="Portada", icon=":material/home:",
                    default=True),
        ],
        "Simulaciones (prototipos)": [
            st.Page("prototipo_dia_sensor.py", title="Cómo funciona la rectena",
                    icon=":material/sensors:"),
            st.Page("prototipo_doblador.py", title="Doblador Greinacher",
                    icon=":material/bolt:"),
            st.Page("prototipo_cascada.py", title="Cascada de energía",
                    icon=":material/water_drop:"),
            st.Page("prototipo_espectro.py", title="Espectro urbano",
                    icon=":material/cell_tower:"),
            st.Page("prototipo_avsb.py", title="Escenario A vs B",
                    icon=":material/compare:"),
            st.Page("prototipo_patron.py", title="Patrón de radiación",
                    icon=":material/wifi_tethering:"),
        ],
    },
    position="sidebar",
)
st.sidebar.divider()
st.sidebar.caption(
    "💡 Cada lámina tiene un botón **⬇ PNG** para exportar la imagen al póster o a las "
    "diapositivas."
)
st.sidebar.caption("Prototipos experimentales — no forman parte de la app oficial.")
pg.run()
