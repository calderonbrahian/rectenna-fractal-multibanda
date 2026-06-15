"""
Sección 2 · Contexto: el sistema rectena.
Narrativa derivada de §2.1 (El sistema rectenna: arquitectura y eficiencia).
Página de lectura; sin controles ni cálculos.
"""

import streamlit as st
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/bolt: Contexto: qué es una rectena",
        "El sistema de recolección de energía RF, bloque por bloque",
        que_es=("Explica qué es una rectena y cómo se encadenan las eficiencias de sus "
                "etapas, para tener el vocabulario antes de ver los escenarios y resultados."),
        para_que_sirve=("Comprender el sistema completo —de la antena a la carga— y por qué "
                        "la eficiencia total es siempre el producto de varias etapas."),
        entradas="Ninguna; es una página de lectura.",
        salidas=("La definición de rectena, sus cinco bloques en serie y la expresión de la "
                 "eficiencia total del sistema."),
    )

    st.subheader("Una rectena = antena + rectificador")
    st.markdown(
        "Una **rectena** (de *rectifying antenna*) convierte directamente las ondas de "
        "radiofrecuencia en tensión continua, sin etapas intermedias de conversión. La "
        "cadena completa comprende **cinco bloques en serie**:"
    )
    st.markdown(
        "**Antena receptora → red de adaptación de impedancias (IMN) → circuito "
        "rectificador → filtro DC → carga.**"
    )

    st.subheader("La eficiencia total es el producto de las etapas")
    st.markdown(
        "Cada bloque conserva solo una fracción de la energía, así que la eficiencia total "
        "del sistema es el **producto** de las eficiencias de etapa:"
    )
    st.latex(
        r"\eta_{total} = \eta_{rad} \cdot \eta_{mm} \cdot \eta_{IMN} \cdot \text{PCE} \cdot \eta_{PMIC}"
    )
    st.markdown(
        "**Qué significa cada término.** Todos son eficiencias: fracciones entre 0 y 1 "
        "(sin unidades), que indican qué parte de la energía sobrevive a cada etapa.\n"
        "- **η_rad** — eficiencia de radiación de la antena: qué fracción capta/radia en "
        "lugar de disiparse como calor en el conductor.\n"
        "- **η_mm** — eficiencia de adaptación (*mismatch*): qué fracción entra realmente "
        "a la antena en vez de reflejarse por desajuste de impedancia.\n"
        "- **η_IMN** — eficiencia de la red de adaptación que conecta la antena con el "
        "rectificador.\n"
        "- **PCE** — eficiencia de conversión RF→DC del rectificador (la etapa que "
        "transforma la radio en corriente continua).\n"
        "- **η_PMIC** — eficiencia del gestor de energía que acondiciona y entrega la "
        "potencia a la carga.\n\n"
        "**Por qué se multiplican:** cada etapa conserva solo una parte de lo que recibe, "
        "así que el rendimiento global es el producto de todas. Basta con que una etapa sea "
        "baja para que η_total caiga: es una cadena, no una suma."
    )
    st.markdown(
        "En sustratos de baja pérdida (Duroid 5880) las eficiencias totales típicas son del "
        "**28–50 % a −10 dBm**. **Sobre FR-4** —el sustrato económico que adopta este "
        "proyecto— se ubican entre el **30 % y el 40 %**."
    )

    st.info(
        "El recorrido detallado de la energía por estos bloques, con las cifras del "
        "escenario de referencia, se presenta en la sección **Energía capturada "
        "(resultado de referencia)**.",
        icon=":material/info:",
    )

    _ref("§2.1 El sistema rectenna: arquitectura y eficiencia · "
         "§2.4 Parámetros fundamentales de antenas y rectenas")

    st.page_link("pages/topologias.py",
                 label="Siguiente — las dos topologías evaluadas →",
                 icon=":material/arrow_forward:")


render()
