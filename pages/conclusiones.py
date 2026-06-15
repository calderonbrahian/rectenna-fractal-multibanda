"""
Sección 11 · Conclusiones.
Narrativa derivada de §5.1 (Conclusiones) y §5.3 / Tabla 13 (Limitaciones) del
informe de grado. Página de lectura.
"""

import streamlit as st
import pandas as pd
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/flag: Conclusiones",
        "Qué sugiere el modelo y qué hay que tener en cuenta al leerlo",
        que_es=("Cierra el recorrido con los hallazgos principales del proyecto y sus "
                "limitaciones declaradas."),
        para_que_sirve=("Quedarse con las conclusiones de fondo y con la lectura honesta de "
                        "su alcance."),
        entradas="Ninguna; es una página de lectura.",
        salidas="Los hallazgos principales (§5.1) y la tabla de limitaciones (Tabla 13).",
    )

    st.subheader("Hallazgos principales")
    st.markdown(
        "- La **FLPDA Koch it. 2** presenta el mayor potencial para sostener transmisiones "
        "**LoRa SF12 a ≤ 100 m** de una torre TDT de alta potencia, bajo condiciones de "
        "propagación media estimada (corrección ITU-R P.1546, sin fading modelado).\n"
        "- **A 100 m:** P_DC = 1 638 µW → un mensaje cada ≈ 158 s (≈ 2,6 min). "
        "**A 1 000 m:** P_DC ≈ 16,4 µW, con V_DC ≈ 146 mV > 130 mV (arranca el BQ25504), "
        "pero el período sube a ≈ 4,4 h.\n"
        "- La **fase de transmisión domina el ~99,5 %** de la energía por ciclo.\n"
        "- El **Sierpinski it. 3 sobre FR-4** resuena solo en **1 de 7** bandas objetivo "
        "(5G-3,5 GHz, S₁₁ = −16,4 dB), lo que cuestiona el valor del fractal puro —sin "
        "elementos adicionales— para recolección multibanda.\n"
        "- El **RMSE de 15,50 pp** frente a Wang (2022) se explica sobre todo por la "
        "pérdida de adaptación fuera de resonancia; secundariamente, por la diferencia de "
        "sustrato y la ausencia de elementos adicionales.\n"
        "- La **TDT del Cerro Nutibara es la fuente RF más adecuada** para RFEH en el Valle "
        "de Aburrá; las señales WiFi y celulares por encima de 1,8 GHz tienen densidades "
        "demasiado bajas para alimentar cargas reales."
    )

    _ref("§5.1 Conclusiones · §5.2 Aportaciones del trabajo")

    st.divider()

    st.subheader("Limitaciones del estudio (Tabla 13)")
    st.markdown(
        "Los resultados deben leerse junto con sus limitaciones declaradas. El trabajo es "
        "**de modelado**, no experimental:"
    )
    tabla13 = [
        ("Sustrato FR-4 (tan δ = 0,020)",   "10–12 pp en η_total",            "Migrar a RO4003 / Rogers 4350"),
        ("Modelo analítico (±1,5 dBi)",     "8–12 pp en η_total",            "Integrar PyNEC (Método de Momentos)"),
        ("Friis sin fading",                "Error ±10–20 dB local",         "Site survey con analizador de espectro"),
        ("Sin prototipos físicos",          "Sin validación experimental",   "Fabricar prototipo y medir con VNA"),
        ("Modelo lineal del diodo",         "Sin distorsión armónica",       "Análisis de balance armónico"),
        ("εᵣ del FR-4 variable con f",      "Corrimiento 3–8 % en bandas altas", "Medir εᵣ por lote con VNA"),
    ]
    df = pd.DataFrame(tabla13, columns=["Limitación", "Impacto cuantificado", "Solución propuesta"])
    st.dataframe(df, hide_index=True, height=250,
                 column_config={
                     "Limitación": st.column_config.TextColumn("Limitación", width="medium"),
                     "Impacto cuantificado": st.column_config.TextColumn("Impacto cuantificado", width="medium"),
                     "Solución propuesta": st.column_config.TextColumn("Solución propuesta", width="medium"),
                 })
    st.caption(
        "Todos los modelos son circuitales y analíticos; no se realizaron simulaciones "
        "full-wave ni mediciones experimentales. La interpretación adecuada de los "
        "resultados es la de un trabajo de modelado reproducible, no de medición."
    )

    _ref("§5.3 Limitaciones del estudio · §5.4 Trabajo futuro · "
         "Apéndice E.11 Tabla canónica de limitaciones (L1–L8)")


render()
