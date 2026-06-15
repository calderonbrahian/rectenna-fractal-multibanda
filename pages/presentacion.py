"""
Sección 0 · Presentación del trabajo de grado.

Es la portada del recorrido y fija el marco desde el primer segundo:
    Bloque 1 — Cabecera institucional (título, autor, director, programa, etc.).
    Bloque 2 — Enfoque metodológico: cómo se hizo, por qué así y qué límites tiene.

Página de lectura. Narrativa derivada de §1.2 (objetivos), §2.9 y Capítulo 3.
"""

import streamlit as st
from utils.pagina import donde_se_desarrolla as _ref


def render():
    # ════════════════════════════════════════════════════════════════════════
    # BLOQUE 1 · CABECERA INSTITUCIONAL
    # ════════════════════════════════════════════════════════════════════════
    st.caption("TRABAJO DE GRADO")
    st.title("Diseño y simulación computacional de rectenas fractales multibanda "
             "para recolección de energía RF en entornos IoT")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Autor**  \nBrahian Calderón Múnera")
    with c2:
        st.markdown("**Director**  \nLuis Alberto Flórez Serna, M.Sc.")
    with c3:
        st.markdown("**Programa**  \nIngeniería de Telecomunicaciones")
    st.markdown(
        "**Universidad de Antioquia** · Facultad de Ingeniería · Medellín, Colombia · 2026"
    )
    with st.expander("Objetivo general del trabajo"):
        st.markdown(
            "Modelar y simular computacionalmente, con bibliotecas científicas de código "
            "abierto en Python, dos topologías de rectenas fractales multibanda —el "
            "**Triángulo de Sierpinski** (1,8–5,8 GHz) y la **FLPDA Koch** para UHF de TDT "
            "y LTE sub-GHz (470–900 MHz)— orientadas a la recolección de energía RF "
            "ambiental en dispositivos IoT de bajo consumo, evaluando su viabilidad técnica "
            "y económica en el contexto espectral colombiano."
        )
        _ref("§1.2.1 Objetivo general · §1.2.2 Objetivos específicos")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # BLOQUE 2 · ENFOQUE METODOLÓGICO (cómo se hizo)
    # ════════════════════════════════════════════════════════════════════════
    st.header(":material/build: Cómo se hizo: el enfoque metodológico")
    st.markdown(
        "Antes de entrar en materia conviene saber **cómo está construido este trabajo**, "
        "porque eso define qué tipo de conclusiones permite sacar."
    )

    st.subheader("Un modelo analítico en Python, no un simulador ni un prototipo")
    st.markdown(
        "Todo el sistema se modela con **ecuaciones analíticas y de circuito equivalente** "
        "implementadas en **Python** (NumPy/SciPy). **No** es un simulador electromagnético "
        "de onda completa (HFSS, CST) ni un montaje de laboratorio físico: es un **modelo "
        "matemático reproducible** que sigue la cadena de la rectena etapa por etapa."
    )

    st.subheader("Por qué este enfoque")
    st.markdown(
        "El objetivo del trabajo es **metodológico y accesible**: cualquier estudiante "
        "puede reproducirlo **sin licencias de software propietario ni instrumentación de "
        "RF costosa**. Su alcance es **exploratorio-comparativo** —evalúa y compara la "
        "viabilidad de dos topologías de antena en un contexto espectral concreto (el "
        "colombiano)—, no diseña un producto físico para fabricar."
    )

    st.subheader("Sobre qué bases matemáticas se apoya")
    st.markdown(
        "El modelo no inventa fórmulas: **encadena referencias clásicas y bien "
        "establecidas**.\n"
        "- **Carrel (1961)** — diseño del arreglo log-periódico (número de dipolos, escala).\n"
        "- **Curva de Koch** — miniaturización fractal de los dipolos.\n"
        "- **Friis + ITU-R P.1546** — propagación de la señal y corrección urbana.\n"
        "- **Shockley** — comportamiento del diodo rectificador."
    )

    st.warning(
        "**Qué permite y qué no.**  \n"
        "✅ **Permite** estimar órdenes de magnitud y **comparar** topologías de forma "
        "reproducible y sin herramientas propietarias.  \n"
        "⚠️ **No sustituye** una validación experimental: los patrones de radiación y las "
        "eficiencias llevan una **incertidumbre no medida** (≈ ±1,5 dBi en ganancia), que "
        "el propio trabajo documenta como limitación.",
        icon=":material/warning:",
    )

    _ref("§2.9 Métodos de análisis electromagnético: enfoque adoptado y alternativas · "
         "§3.1 Enfoque metodológico · §3.3 Arquitectura del pipeline de simulación · "
         "Tabla 4 (arquitectura del pipeline de simulación)")

    st.page_link("pages/problema.py",
                 label="Comenzar el recorrido — el problema del IoT →",
                 icon=":material/arrow_forward:")


render()
