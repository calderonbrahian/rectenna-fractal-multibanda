"""
Sección 7 · Comparación de los dos escenarios.
Narrativa y Tabla 10 derivadas de §4.4 (Análisis comparativo de los dos
escenarios) del informe de grado. Página de lectura.
"""

import streamlit as st
import pandas as pd
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/compare: Comparación de los dos escenarios",
        "Sierpinski (A) frente a FLPDA Koch (B): no cuál es mejor, sino para qué",
        que_es=("Sintetiza la comparación técnica entre las dos topologías estudiadas, "
                "criterio por criterio."),
        para_que_sirve=("Ver lado a lado las diferencias y entender que cada topología "
                        "encaja en un escenario de despliegue distinto."),
        entradas="Ninguna; es una página de lectura.",
        salidas="La tabla comparativa integral (Tabla 10 del informe) y su lectura.",
    )

    st.markdown(
        "La diferencia de ganancia entre el **Sierpinski** (omnidireccional, 2,5–3,5 dBi) y "
        "la **FLPDA** (directiva, 7,17 dBi) **no determina cuál diseño es superior**: "
        "determina **para qué situación de despliegue** es adecuado cada uno."
    )

    tabla10 = [
        ("Rango espectral",        "1,8–5,8 GHz",            "470–900 MHz"),
        ("Tamaño físico",          "~39 × 34 mm² (PCB)",     "Boom de 500 mm"),
        ("Patrón de radiación",    "Omnidireccional",        "Directivo (end-fire)"),
        ("Ganancia típica",        "2,5–3,5 dBi",            "7,17 dBi"),
        ("S₁₁ < −10 dB",           "1 de 7 bandas",          "Continuo 470–900 MHz"),
        ("Fuentes objetivo",       "WiFi, LTE, 5G sub-6",    "TDT, LTE 700, GSM 850"),
        ("P_DC a 100 m de fuente", "~0,3–8 µW (interior)",   "1 638 µW (TDT 10 kW)"),
        ("Escenario óptimo",       "IoT interior / portátil","Estación exterior fija"),
        ("Carga viable",           "Sensor BLE / ZigBee",    "Nodo LoRa SF12"),
        ("η_total (rango)",        "0,1–25,0 % (por banda)", "28–72 % (varía con P_in)"),
    ]
    df = pd.DataFrame(tabla10, columns=["Criterio", "Escenario A — Sierpinski it. 3",
                                        "Escenario B — FLPDA Koch it. 2"])
    st.dataframe(df, hide_index=True, height=420,
                 column_config={
                     "Criterio": st.column_config.TextColumn("Criterio", width="medium"),
                 })
    st.caption("Tabla 10 del informe — Comparación técnica integral. "
               "El cap de PCE = 85 % es el límite del rectificador, no de η_total.")

    with st.container(border=True):
        st.markdown(
            "**Lectura.** El Sierpinski es **omnidireccional y compacto**: encaja en un nodo "
            "IoT interior o portátil que capta de varias fuentes débiles. La FLPDA es "
            "**directiva y de mayor ganancia**: encaja en una estación exterior fija "
            "apuntando a una fuente potente y conocida (la TDT). Por eso el resultado "
            "energético firme del proyecto proviene del **Escenario B**."
        )

    _ref("§4.4 Análisis comparativo de los dos escenarios · §4.1 Escenario A · §4.2 Escenario B")

    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/inicio.py",
                     label="Ver el resultado de referencia (B) →", icon=":material/verified:")
    with col2:
        st.page_link("pages/conclusiones.py",
                     label="Ir a las conclusiones →", icon=":material/flag:")


render()
