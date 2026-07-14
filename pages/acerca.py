"""Página Acerca — Metodología, referencias y arquitectura del proyecto."""

import streamlit as st
import pandas as pd

from configs.parametros import CANONICAL
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        "Información del proyecto",
        "Metodología · Referencias bibliográficas · Arquitectura de la simulación",
        que_es=("Página de **información de referencia** sobre el proyecto de grado. "
                 "Reúne la metodología completa del cálculo, las referencias "
                 "bibliográficas con su uso específico en el modelo y la arquitectura "
                 "de la simulación."),
        para_que_sirve=("Que un docente, investigador o profesional pueda **reproducir el "
                         "trabajo** o entender cómo se conectan los conceptos teóricos con "
                         "su implementación. Sirve también como punto de partida para "
                         "extender el modelo en trabajo futuro."),
        entradas=("Ninguna; es una página de lectura."),
        salidas=("Cadena de cálculo del Escenario B (Carrel + Koch + Friis + Shockley + "
                  "PMIC), modelo RLC del Escenario A (Sierpinski), 10 referencias "
                  "bibliográficas con su uso específico y la arquitectura de la simulación."),
        como_leer=("Empieza por la sección de **metodología** para entender la cadena de "
                   "cálculo. La tabla de **referencias** indica dónde se usa cada una en "
                   "el modelo. La arquitectura final muestra cómo está organizada la "
                   "simulación."),
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            "**Trabajo de grado:** Diseño y simulación computacional de rectenas "
            "fractales multibanda para recolección de energía RF en entornos IoT  \n"
            "**Programa:** Ingeniería de Telecomunicaciones · Universidad de Antioquia  \n"
            "**Autor:** Brahian Calderón Múnera  \n"
            "**Director:** Luis Alberto Flórez Serna, M.Sc. · 2026"
        )
    with col2:
        with st.container(border=True):
            st.markdown("**Modelo físico:** Shockley + Carrel + Friis")
            st.markdown("**Enfoque:** analítico circuital (no onda completa)")
            st.markdown(":material/menu_book: Metodología en §3.9 y Capítulo 4")

    st.divider()

    # ── Metodología ───────────────────────────────────────────────────────────
    st.subheader(":material/build: Metodología de simulación")
    with st.expander("Ver cadena de cálculo completa", expanded=True):
        st.markdown("### Escenario B — FLPDA Koch (470–900 MHz) · escenario cuantitativo")
        st.markdown(
            "Carrel (1961) establece el número de elementos del arreglo log-periódico "
            "a partir de la razón de escala τ y de las frecuencias extremas:"
        )
        st.latex(r"N \;=\; 1 + \left\lceil \frac{\log(f_H/f_L)}{\log(1/\tau)} \right\rceil")
        st.markdown(
            "Con τ = 0,90, σ = 0,15 y banda 470–900 MHz se obtiene **N = 12** dipolos. "
            "La modificación fractal de Koch de orden 2 reduce la dimensión transversal "
            "del dipolo:"
        )
        st.latex(r"k_{\mathrm{red}} \;=\; (3/4)^2 = 0{,}5625 \quad\Longrightarrow\quad \text{reducción física } 43{,}75\%")

        st.markdown("Modelo de propagación (Friis + ITU-R P.1546):")
        st.latex(
            r"P_{\mathrm{in}} \;=\; \mathrm{EIRP} \;-\; \mathrm{FSPL}(f,d) \;-\; L_{\mathrm{urb}} \;+\; G_{\mathrm{ant}}"
        )
        st.markdown(
            f"En el escenario de referencia (EIRP = 72,15 dBm, d = 100 m, f = 550 MHz, "
            f"G = {CANONICAL['gain_dBi']:.2f} dBi, L_urb = {CANONICAL['L_urb_dB']:.0f} dB) "
            f"da **P_in = {CANONICAL['P_in_dBm']:.2f} dBm = {CANONICAL['P_in_mW']:.3f} mW**."
        )

        st.markdown("Cadena de potencia: la potencia continua se obtiene aplicando a P_in "
                    "los cuatro factores de las etapas posteriores a la antena. Aquí η_rad "
                    "ya está embebida en la ganancia realizada G que define P_in, así que "
                    "no se vuelve a multiplicar.")
        st.latex(
            r"P_{DC} \;=\; P_{\mathrm{in}} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \mathrm{PCE} \cdot \eta_{PMIC}"
        )

        st.markdown("Figura de mérito global (cinco factores, referida a la potencia "
                    "interceptada antes de las pérdidas de radiación). "
                    ":material/warning: No se multiplica por P_in para recuperar P_DC, "
                    "porque eso contabilizaría dos veces η_rad:")
        st.latex(
            r"\eta_{\mathrm{total}} \;=\; \eta_{\mathrm{rad}} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \mathrm{PCE} \cdot \eta_{PMIC}"
            r"\;=\; " + f"{CANONICAL['eta_total']:.4f}"
        )

        st.markdown("Rectificador SMS7630: modelo iterativo de Shockley con amortiguación "
                    "0,4/0,6, 80 iteraciones máximo. El resultado se recorta a un techo "
                    "PCE = 0,85 (cap explícito del modelo, no de medición):")
        st.latex(
            r"V_{DC} \;=\; N\,(V_{\mathrm{oc,pk}} - V_f), \quad "
            r"V_f \;=\; n\,V_T\,\ln\!\Big(\tfrac{I_d}{I_s} + 1\Big), \quad "
            r"\mathrm{PCE} \;\in\; [0,\;0{,}85]"
        )

        st.markdown("PMIC BQ25504: convertidor elevador con arranque en frío para "
                    "V_in ≥ 130 mV y eficiencia η_PMIC = 0,85 (datasheet SLUSCY3).")

        st.divider()

        st.markdown("### Escenario A — Sierpinski Gasket (1,84–7,36 GHz) · exploratorio")
        st.markdown(
            "Resonancias log-periódicas del fractal de Sierpinski iteración 3:"
        )
        st.latex(r"f_k \;=\; f_0 \cdot 2^k, \quad k = 0, 1, 2 \;\;\Rightarrow\;\; 1{,}84\,/\,3{,}68\,/\,7{,}36\;\mathrm{GHz}")
        st.markdown(
            "Impedancia de entrada modelada por combinación en admitancia de resonadores "
            "RLC, uno por banda (Puente-Baliarda et al., 1998), con un fondo inductivo y "
            "Q ≈ 8,5 sobre FR-4 (dominado por tan δ). Cerca de cada resonancia el resonador "
            "asociado domina; lejos, el sumatorio en admitancia produce alta impedancia. "
            ":material/warning: El escenario A no cuantifica P_DC final porque los EIRP de "
            "fuentes urbanas (GSM/5G/WiFi) son variables y no están especificados."
        )
    _ref("§3.9 Métodos de análisis electromagnético: enfoque adoptado · "
         "§4.3 Estructura del modelo de simulación · §4.4–§4.6 Etapas del modelo")

    st.divider()

    # ── Referencias bibliográficas ────────────────────────────────────────────
    st.subheader(":material/menu_book: Referencias bibliográficas")
    refs = [
        {"Clave": "Wang2022",  "Referencia": "Y. Wang et al., 'A Seven-Band Rectenna for RF Energy Harvesting from Low-Power Ambient RF Sources,' IEEE Trans. Antennas Propag., 70(2), 1283–1295, 2022.", "Uso": "Datos experimentales de PCE (Duroid 5880), validación cruzada del rectificador"},
        {"Clave": "Carrel1961","Referencia": "R. L. Carrel, 'Analysis and Design of the Log-Periodic Dipole Antenna,' Ph.D. dissertation, Univ. of Illinois, Urbana, 1961.", "Uso": "Diseño LPDA: τ, σ, N (anclaje paramétrico de la ganancia base)"},
        {"Clave": "Puente1998","Referencia": "C. Puente-Baliarda et al., 'On the behavior of the Sierpinski multiband fractal antenna,' IEEE TAP, 46(4), 517–524, 1998.", "Uso": "Modelo RLC paralelo del Sierpinski (Escenario A)"},
        {"Clave": "Pozar2012", "Referencia": "D. M. Pozar, Microwave Engineering, 4th ed., Wiley, 2012.", "Uso": "Potencia disponible (§2), red de adaptación L (§5.1), parámetros S"},
        {"Clave": "Bahl1977",  "Referencia": "I. J. Bahl and D. K. Trivedi, 'A designer's guide to microstrip line,' Microwaves, 16(5), 174–182, 1977.", "Uso": "Permitividad efectiva dinámica de FR-4"},
        {"Clave": "SMS7630",   "Referencia": "Skyworks Solutions, SMS7630 datasheet + AN-4003, 2019.", "Uso": "Parámetros SPICE: Is=5 µA, n=1,05, Rs=20 Ω, Cj0=0,14 pF, Vj=0,34 V, M=0,40"},
        {"Clave": "BQ25504",   "Referencia": "Texas Instruments, BQ25504 datasheet SLUSCY3, 2019.", "Uso": "Cold-start 130 mV, η_PMIC=85 %, R_load ≈ 1300 Ω"},
        {"Clave": "SX1276",    "Referencia": "Semtech, SX1276/77/78/79 LoRa Transceiver datasheet, 2019.", "Uso": "Consumo Tx/Rx/Sleep — perfiles SF7/SF9/SF12"},
        {"Clave": "ITUR1546",  "Referencia": "ITU-R Recommendation P.1546-6, 2019.", "Uso": "Corrección de propagación urbana: +6 dB sobre FSPL"},
        {"Clave": "Friis1946", "Referencia": "H. T. Friis, 'A Note on a Simple Transmission Formula,' Proc. IRE, 34(5), 254–256, 1946.", "Uso": "Ecuación de transmisión base del modelo de propagación"},
    ]
    df = pd.DataFrame(refs)
    st.dataframe(df, hide_index=True, column_config={
        "Clave":      st.column_config.TextColumn("Clave", width="small"),
        "Referencia": st.column_config.TextColumn("Referencia APA7", width="large"),
        "Uso":        st.column_config.TextColumn("Uso en el modelo", width="medium"),
    })
    _ref("Referencias del informe de grado · §3.2 Estado del arte en rectenas fractales")

    st.divider()

    # ── Arquitectura de la simulación ─────────────────────────────────────────
    st.subheader(":material/folder_open: Arquitectura de la simulación")
    st.code(
        """rectenna_dashboard_st/
├── app.py                       # Entrada: navegación multipágina
├── .streamlit/config.toml       # Tema claro institucional UdeA
├── pages/                       # Dos niveles: Demostración + Laboratorio
│   ├── demo_1_problema.py       # N1 · El problema y la pregunta
│   ├── demo_2_metodo.py         # N1 · La metodología del estudio
│   ├── demo_3_resultados.py     # N1 · Qué se demostró
│   ├── demo_4_aporte.py         # N1 · El estudio y su alcance
│   ├── escenario_a.py           # N2 · Escenario A — Sierpinski · 1,8–5,8 GHz
│   ├── escenario_b.py           # N2 · Escenario B — FLPDA Koch · 470–900 MHz
│   ├── comparacion.py           # N2 · Comparación de los dos escenarios
│   ├── inicio.py                # N2 · Resultado de referencia (P_DC)
│   ├── viabilidad_iot.py        # N2 · Aplicación al nodo IoT
│   ├── validacion.py            # N2 · Validación con literatura (Wang 2022)
│   ├── analisis_avanzado.py     # N2 · Análisis de incertidumbre (tornado, MC)
│   ├── sensibilidad.py          # N2 · Sensibilidad paramétrica (Q_L, R_load, τ–σ)
│   ├── conclusiones.py          # N2 · Conclusiones y limitaciones
│   └── acerca.py                # N2 · Esta página (metodología y referencias)
├── core/                        # Implementaciones físicas (fuente de verdad)
│   ├── antenna.py               # FractalAntenna (Sierpinski)
│   ├── flpda.py                 # FLPDA_Koch (Carrel + Koch)
│   ├── matching.py              # LMatchNetwork (red L, Nelder-Mead)
│   ├── rectifier.py             # SchottkyDiode_SMS7630, RectifierCircuit
│   ├── lora_budget.py           # Friis, BQ25504, perfiles LoRa
│   ├── comparacion.py           # Validación Wang2022, Carrel1961
│   └── analysis.py              # MC, BW, LinkBudget, Supercap
├── simulation/                  # Runners cacheados (@st.cache_data) — Esc A/B
├── analysis/                    # Runners cacheados — análisis avanzado
├── plots/charts.py              # Funciones Plotly reutilizables
├── configs/parametros.py        # CANONICAL (auditado 2026-05-28) + constantes
├── utils/exportar.py            # CSV export
└── tests/                       # Pruebas de regresión del modelo
    ├── test_regression_canonical.py
    └── test_models.py""",
        language="",
    )
    _ref("§4.2 Justificación del entorno Python de código abierto · "
         "§4.3 Estructura del modelo de simulación · "
         "Tabla 2 (etapas del modelo de simulación)")

    st.divider()

    # ── Limitaciones y alcance ──────────────────────────────────────────────
    st.subheader(":material/rule: Limitaciones y alcance del estudio")
    with st.container(border=True):
        st.markdown(
            """
Este es un trabajo de modelado, no una medición. Los resultados estiman órdenes de magnitud y permiten comparar diseños, pero no reemplazan la caracterización experimental de un prototipo. Conviene leerlos junto con las limitaciones que el propio informe declara:

- El sustrato modelado es FR-4 (tan δ ≈ 0,02), bastante más disipativo que un laminado de microondas. Frente a un Duroid 5880, esto resta del orden de 10–12 puntos a la η_total.
- La ganancia de las antenas proviene de un modelo analítico, no de una simulación de onda completa; arrastra una incertidumbre de ±1,5 dBi que no se midió.
- La propagación usa Friis con una corrección urbana fija de +6 dB y no modela el desvanecimiento; en un emplazamiento real el error local puede llegar a ±10–20 dB.
- No se fabricaron prototipos. La comparación con Wang (2022) es una verificación de orden de magnitud, no una validación punto a punto (RMSE = 15,50 pp), y además contrasta diseños sobre sustratos distintos.
- La PCE = 0,85 es el techo del modelo del rectificador, no un valor medido. El resultado de referencia opera justo en ese máximo, así que es un mejor caso, no un valor esperado en campo.
- El η_total = 0,4023 es una figura de mérito de cinco factores. La potencia útil se obtiene aplicando solo cuatro factores sobre P_in, porque η_rad ya está contenida en la ganancia G; multiplicar η_total por P_in contaría dos veces la pérdida de radiación.

La tabla completa de limitaciones (L1–L8), con el impacto cuantitativo de cada una y su posible mitigación, está en el Anexo B del informe de grado.
"""
        )
    _ref("§1.2 Alcance y limitaciones del estudio · §6.3 Limitaciones del estudio · "
         "§5.5 Validación cruzada y análisis del error · "
         "Anexo B.11 Tabla canónica de limitaciones del estudio (L1–L8)")

    st.caption(
        "Esta aplicación es la capa de presentación interactiva del trabajo de grado. "
        "El modelo físico es la fuente única de los valores presentados; los detalles "
        "de reproducibilidad se documentan en el §4.2 del informe de grado."
    )


render()
