"""
Sección 7 · Comparación de los dos escenarios.
Narrativa y Tabla 10 derivadas de §4.4 (Análisis comparativo de los dos
escenarios) del informe de grado. Página de lectura.
"""

import streamlit as st
import pandas as pd
from utils.pagina import encabezado, donde_se_desarrolla as _ref
from utils.glosario import glosario_pagina


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
        "La diferencia de ganancia entre el Sierpinski (omnidireccional, 2,5–3,5 dBi) y "
        "la FLPDA (directiva, 7,17 dBi de media en banda, 7,10 dBi a la frecuencia "
        "de referencia de 550 MHz) no dice cuál diseño es superior. Dice para qué "
        "situación de despliegue conviene cada uno."
    )

    tabla10 = [
        ("Rango espectral",        "1,8–5,8 GHz",            "470–900 MHz"),
        ("Tamaño físico",          "~39 × 34 mm² (PCB)",     "Boom de 500 mm"),
        ("Patrón de radiación",    "Omnidireccional",        "Directivo (end-fire)"),
        ("Ganancia típica",        "2,5–3,5 dBi",            "7,17 dBi (media en banda)"),
        ("S₁₁ < −10 dB",           "1 de 7 bandas",          "Continuo 470–900 MHz"),
        ("Fuentes objetivo",       "WiFi, LTE, 5G sub-6",    "TDT, LTE 700, GSM 850"),
        ("P_DC a 100 m de fuente", "~0,3–8 µW (interior)",   "1 638 µW (TDT 10 kW)"),
        ("Escenario óptimo",       "IoT interior / portátil","Estación exterior fija"),
        ("Carga viable",           "Sensor BLE / ZigBee",    "Nodo LoRa SF12"),
        ("η_total (rango)",        "1,0–13,8 % (por banda)", "28–67 % (varía con P_in; tope 67 % por PCE 0,85)"),
    ]
    df = pd.DataFrame(tabla10, columns=["Criterio", "Escenario A — Sierpinski it. 3",
                                        "Escenario B — FLPDA Koch it. 2"])
    st.dataframe(df, hide_index=True, height=420,
                 column_config={
                     "Criterio": st.column_config.TextColumn("Criterio", width="medium"),
                 })
    st.caption("El cap de PCE = 85 % es el límite del rectificador, no de η_total.")
    st.caption(
        ":material/lightbulb: **Filas decisivas:** la ganancia (B concentra más energía "
        "hacia la fuente), el S₁₁ (B está adaptada en toda la banda; A solo en 1 de 7) y "
        "la P_DC (solo B la cuantifica) son las que inclinan la elección hacia B para una "
        "estación fija."
    )
    glosario_pagina("ganancia", "S11", "η_total", "P_DC")

    with st.container(border=True):
        st.markdown("#### :material/flag: Conclusión del trabajo de grado")
        st.markdown(
            "- El Escenario A (Sierpinski) muestra el comportamiento multibanda del fractal "
            "y explora si fuentes urbanas (WiFi/LTE/5G) podrían sumar energía. No fija una "
            "cifra: sus resultados son cotas superiores.\n"
            "- El Escenario B (FLPDA Koch), ante una fuente concreta y bien caracterizada "
            "como la TDT del Cerro Nutibara, cuantifica la potencia útil: P_DC = 1 638 µW, "
            "suficiente para un nodo LoRa SF12.\n"
            "- El resultado principal se construye sobre B porque es el único escenario con "
            "la fuente bien definida. Su mayor ganancia media en banda (7,17 frente a "
            "2,5–3,5 dBi) y su adaptación continua en toda la banda hacen que B sostenga "
            "el resultado energético firme del proyecto, mientras A queda como exploración "
            "complementaria."
        )

    _ref("§4.4 Análisis comparativo de los dos escenarios · §4.1 Escenario A · "
         "§4.2 Escenario B · Tabla 10 (comparación técnica integral) · "
         "Figura 10 (PCE vs P_in, ambos escenarios)")

    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/inicio.py",
                     label="Ver el resultado de referencia (B) →", icon=":material/verified:")
    with col2:
        st.page_link("pages/conclusiones.py",
                     label="Ir a las conclusiones →", icon=":material/flag:")


render()
