"""
Utilidades de presentación compartidas por los prototipos (experimentales).

Centraliza la estética "grado póster / defensa proyectada":
  - poster_style():  CSS global (tipografía legible a distancia, tarjetas de
                     métricas, oculta el chrome de Streamlit para un panel limpio).

Cada prototipo añade además, inline en su canvas, un botón "⬇ PNG" para exportar
la lámina al póster o a las diapositivas. No forma parte de la app oficial.
"""

import streamlit as st

ACCENT = "#7C3AED"   # violeta de marca (fractal)
ACCENT2 = "#16A34A"  # verde (energía útil)


def poster_style():
    """Inyecta el CSS de presentación. Idempotente (Streamlit reescribe el DOM)."""
    st.markdown(
        """
        <style>
          /* — panel limpio para proyección / convención — */
          #MainMenu {visibility:hidden;}
          [data-testid="stToolbar"] {display:none;}
          footer {visibility:hidden;}
          [data-testid="stDecoration"] {background:linear-gradient(90deg,#7C3AED,#16A34A);}

          /* — tipografía más legible a distancia — */
          .block-container {padding-top:2.2rem;}
          h1 {font-weight:800; letter-spacing:-0.5px;}

          /* — tarjetas de métricas (KPI) — */
          [data-testid="stMetric"] {
            background:linear-gradient(180deg,#ffffff,#f8fafc);
            border:1px solid #E2E8F0; border-left:4px solid #7C3AED;
            border-radius:12px; padding:12px 16px;
            box-shadow:0 1px 3px rgba(15,23,42,0.06);
          }
          [data-testid="stMetricValue"] {font-size:1.7rem; font-weight:700;}
          [data-testid="stMetricLabel"] {font-size:0.95rem; color:#475569;}
          [data-testid="stMetricLabel"] p {font-size:0.95rem;}

          /* — caja de "pregunta que responde" más marcada — */
          [data-testid="stAlert"] {border-radius:12px;}
        </style>
        """,
        unsafe_allow_html=True,
    )
