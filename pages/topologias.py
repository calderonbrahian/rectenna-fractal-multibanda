"""
Sección 3 · Topologías evaluadas.

Responde la pregunta que dejó abierta la página anterior: por qué se evalúan
precisamente estas dos antenas y qué espera aprender el estudio al compararlas.
El valor no está en que existan Sierpinski y Koch, sino en que representan dos
filosofías de diseño distintas (exploratoria vs cuantitativa).

Orden narrativo:
    Dos preguntas, dos diseños → Por qué geometría fractal →
    Dos estrategias (Sierpinski / Koch) → Qué se espera aprender al compararlas.

Página de lectura. Narrativa derivada de §2.3 y del objetivo general (§1.2.1).
"""

import streamlit as st
from utils.pagina import donde_se_desarrolla as _ref


def render():
    st.title(":material/category: Topologías evaluadas")
    st.markdown(
        "*Esta sección presenta las dos estrategias de diseño evaluadas en el estudio y "
        "explica por qué cada una responde a una pregunta diferente.*"
    )

    # ── La pregunta que abre la página ───────────────────────────────────────
    st.subheader("Dos preguntas, dos diseños")
    st.markdown(
        "Una vez entendido cómo una rectena convierte energía de radio en electricidad, "
        "surge una nueva pregunta: **¿qué tipo de antena conviene usar para capturar esa "
        "energía?**\n\n"
        "El estudio no evalúa muchas alternativas: se concentra en **dos diseños "
        "fractales** que representan enfoques diferentes y complementarios."
    )

    # ── Por qué fractal (contado desde la utilidad, no desde la teoría) ───────
    st.subheader("Por qué geometría fractal")
    st.markdown(
        "El estudio utiliza geometrías fractales porque permiten obtener comportamientos "
        "difíciles de lograr con antenas convencionales: **operar en varias bandas** o "
        "**reducir el tamaño físico** sin perder funcionalidad. Estas dos propiedades son "
        "justamente las que explora este trabajo, una en cada antena."
    )

    # ── Las dos estrategias, leídas como investigación (no como fichas) ───────
    st.subheader("Dos estrategias para resolver el problema")
    st.markdown(
        "Cada diseño lleva una de esas propiedades al extremo y responde a una pregunta "
        "distinta:"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### :material/cell_tower: Escenario A — Triángulo de Sierpinski")
            st.markdown(
                "**¿Qué se quiere investigar?**  \n"
                "Si una sola antena puede capturar energía procedente de varias fuentes "
                "urbanas al mismo tiempo.\n\n"
                "**¿Por qué esta geometría?**  \n"
                "Porque su estructura fractal genera resonancias en múltiples bandas "
                "(1,8–5,8 GHz).\n\n"
                "**¿Qué aporta al estudio?**  \n"
                "Representa el enfoque **exploratorio**: prioriza la cobertura espectral "
                "sobre una estimación precisa de energía.\n\n"
                "**Principal ventaja** · una única antena compacta puede operar en varias "
                "bandas de frecuencia.  \n"
                "**Principal limitación** · la energía capturada se reparte entre varias "
                "resonancias y no siempre se concentra donde más interesa."
            )
            st.page_link("pages/escenario_a.py",
                         label="Ver el Escenario A →", icon=":material/cell_tower:")
    with col_b:
        with st.container(border=True):
            st.markdown("#### :material/radio: Escenario B — FLPDA Koch")
            st.markdown(
                "**¿Qué se quiere investigar?**  \n"
                "Cuánta energía útil puede entregar una antena cuando apunta a una fuente "
                "concreta y bien conocida.\n\n"
                "**¿Por qué esta geometría?**  \n"
                "Porque la curva de Koch permite **miniaturizar** una antena dirigida de "
                "banda ancha y mantenerla compacta en la banda de televisión y telefonía "
                "baja (UHF, 470–900 MHz).\n\n"
                "**¿Qué aporta al estudio?**  \n"
                "Representa el enfoque **cuantitativo**: prioriza maximizar y cuantificar "
                "la energía capturada frente a la cobertura multibanda.\n\n"
                "**Principal ventaja** · al concentrar la energía en una dirección, permite "
                "estimar cifras concretas de energía recuperable.  \n"
                "**Principal limitación** · debe orientarse hacia la fuente y ocupa más "
                "espacio que una antena no dirigida."
            )
            st.page_link("pages/escenario_b.py",
                         label="Ver el Escenario B →", icon=":material/radio:")

    # ── Cierre: qué se espera aprender al compararlas (crea expectativa) ──────
    st.subheader("Qué se espera aprender al compararlas")
    st.markdown(
        "Ninguna de las dos antenas pretende ser «la mejor» en todos los escenarios. El "
        "interés del estudio es entender **qué se gana y qué se pierde con cada "
        "estrategia**: cobertura multibanda frente a captación dirigida de energía. Los "
        "resultados de los escenarios siguientes permitirán **cuantificar** esas "
        "diferencias."
    )
    _ref("§2.3 Geometría fractal aplicada a antenas · §2.3.2 Triángulo de Sierpinski · "
         "§2.3.3 Curva de Koch · §3.4 Módulo 1 — Geometrías fractales · "
         "Figura 4 (geometría del arreglo FLPDA Koch it. 2)")

    st.page_link("pages/escenario_a.py",
                 label="Siguiente — los escenarios estudiados →",
                 icon=":material/arrow_forward:")


render()
