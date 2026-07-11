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
        "- La FLPDA Koch it. 2 es la que muestra mayor potencial para sostener transmisiones "
        "LoRa SF12 hasta ≈ 174 m de una torre TDT de alta potencia (criterio de consumo "
        "continuo del nodo, P_DC ≥ 438,5 µW); con el ciclo de trabajo regulatorio del 1 %, el "
        "alcance útil baja a ≈ 134 m. El caso de referencia a 100 m opera con amplio margen, "
        "bajo condiciones de propagación media estimada (corrección ITU-R P.1546, sin fading "
        "modelado).\n"
        "- A 100 m, P_DC = 1 335 µW, es decir un mensaje cada ≈ 158 s (unos 2,6 min). A 1 000 m "
        "la potencia cae a ≈ 16,4 µW; el V_DC ≈ 146 mV todavía supera los 130 mV que necesita el "
        "BQ25504 para arrancar, pero el período entre mensajes sube a ≈ 4,4 h.\n"
        "- La fase de transmisión se lleva casi toda la energía del ciclo: alrededor del 99,5 %.\n"
        "- El Sierpinski it. 3 sobre FR-4 resuena en solo 1 de las 7 bandas objetivo "
        "(5G-3,5 GHz, S₁₁ = −17,4 dB). Ese resultado pone en duda el fractal puro, sin "
        "elementos adicionales, para recolección multibanda.\n"
        "- El RMSE de 15,50 pp frente a Wang (2022) se explica sobre todo por la pérdida de "
        "adaptación fuera de resonancia, y en segundo lugar por la diferencia de sustrato y la "
        "ausencia de elementos adicionales.\n"
        "- Para RFEH en el Valle de Aburrá, la TDT del Cerro Nutibara es la fuente más "
        "adecuada. Las señales WiFi y celulares por encima de 1,8 GHz tienen densidades "
        "demasiado bajas para alimentar cargas reales."
    )

    _ref("§5.1 Conclusiones · §5.2 Aportaciones del trabajo")

    st.divider()

    st.subheader("Bajo qué condiciones se sostiene la conclusión")
    st.markdown(
        "El resultado positivo del trabajo es acotado, y conviene leerlo con sus "
        "condiciones explícitas:\n\n"
        "- Depende de una fuente potente y cercana. La operación autónoma se sostiene a "
        "≤ 100–200 m de un transmisor de alta potencia como la TDT del Cerro Nutibara. Lejos "
        "de una fuente así, las densidades de potencia ambientales (Wi-Fi, celular por "
        "encima de 1,8 GHz) son demasiado bajas. El nicho realista, entonces, es el despliegue "
        "próximo a infraestructura de radiodifusión, no la recolección urbana genérica.\n"
        "- El valor de referencia es una cota optimista. Los 1 335 µW de P_DC se obtienen con "
        "la PCE en el techo del modelo (0,85): es un mejor caso, no un valor esperado en "
        "operación real.\n"
        "- El Escenario A aporta un resultado en parte negativo, y honesto. El fractal de "
        "Sierpinski, por sí solo y sobre FR-4, no logra una adaptación multibanda "
        "aprovechable. Es evidencia de un límite, no una cifra de energía.\n"
        "- El contraste con Wang (2022) es una verificación de orden de magnitud, no una "
        "validación experimental. Difiere de sustrato (FR-4 frente a Duroid 5880) y arroja un "
        "RMSE de 15,50 pp. El trabajo es de modelado; no incluye un prototipo medido."
    )
    _ref("§1.3 Alcance y limitaciones del estudio · §4.5 Validación cruzada · "
         "§5.1 Conclusiones")

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
         "Tabla 13 (limitaciones y soluciones) · Tabla 14 (resumen estructural) · "
         "Apéndice E.11 Tabla canónica de limitaciones (L1–L8)")

    st.divider()
    st.page_link("pages/acerca.py",
                 label="Informacion del proyecto: metodologia y referencias →",
                 icon=":material/info:")


render()
