"""
Sección 3 · Topologías evaluadas.
Narrativa derivada de §2.3 (Geometría fractal aplicada a antenas) y del objetivo
general (§1.2.1). Página de lectura; sin controles ni cálculos.
"""

import streamlit as st
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/category: Topologías evaluadas",
        "Dos antenas fractales para dos preguntas distintas",
        que_es=("Presenta las dos topologías fractales que estudia el proyecto y por qué se "
                "eligieron estas dos, antes de entrar al detalle de cada escenario."),
        para_que_sirve=("Entender la lógica del trabajo: una antena para explorar el "
                        "comportamiento multibanda y otra para cuantificar energía útil ante "
                        "una fuente concreta."),
        entradas="Ninguna; es una página de lectura.",
        salidas="La descripción de las dos topologías y el papel de cada una en el proyecto.",
    )

    st.subheader("Por qué geometría fractal")
    st.markdown(
        "Las geometrías fractales (autosimilares) permiten que una misma antena resuene en "
        "**varias bandas** o que un dipolo se **miniaturice** sin cambiar su frecuencia de "
        "operación. El proyecto aprovecha ambas propiedades, una en cada topología."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### :material/cell_tower: Triángulo de Sierpinski (Escenario A)")
            st.markdown(
                "- **Banda:** 1,8–5,8 GHz · **patrón:** omnidireccional.\n"
                "- Aprovecha la **autosimilitud** para resonar en varias bandas a la vez.\n"
                "- Pregunta que aborda: *¿puede una sola antena captar energía de varias "
                "fuentes urbanas (WiFi, LTE, 5G) a la vez?*\n"
                "- Es **exploratorio**: no fija una cifra de energía final.\n"
                "- **Ventaja:** una sola antena multibanda y muy compacta. "
                "**Limitación:** sobre FR-4 solo resuena bien en 1 de 7 bandas, por lo que "
                "no aporta energía firme."
            )
            st.page_link("pages/escenario_a.py",
                         label="Ver el Escenario A →", icon=":material/cell_tower:")
    with col_b:
        with st.container(border=True):
            st.markdown("#### :material/radio: FLPDA Koch (Escenario B)")
            st.markdown(
                "- **Banda:** 470–900 MHz (UHF) · **patrón:** directivo (end-fire).\n"
                "- Usa la **curva de Koch** para miniaturizar los dipolos del arreglo "
                "log-periódico.\n"
                "- Pregunta que aborda: *¿cuánta energía útil entrega ante una fuente "
                "concreta y bien caracterizada (la TDT del Cerro Nutibara)?*\n"
                "- Es el escenario **cuantitativo** del proyecto.\n"
                "- **Ventaja:** adaptada en toda la banda UHF y de mayor ganancia → "
                "cuantifica energía útil. **Limitación:** directiva y de mayor tamaño "
                "(boom ~50 cm); requiere apuntar a la fuente."
            )
            st.page_link("pages/escenario_b.py",
                         label="Ver el Escenario B →", icon=":material/radio:")

    st.markdown(
        "Las dos existen porque el trabajo busca **comparar** ambas topologías y establecer "
        "criterios de selección según el entorno de despliegue; esa comparación se presenta "
        "en la sección **Comparación de los dos escenarios**."
    )

    _ref("§2.3 Geometría fractal aplicada a antenas · §2.3.2 Triángulo de Sierpinski · "
         "§2.3.3 Curva de Koch · §3.4 Módulo 1 — Geometrías fractales · "
         "Figura 4 (geometría del arreglo FLPDA Koch it. 2)")

    st.page_link("pages/escenario_a.py",
                 label="Siguiente — los escenarios estudiados →",
                 icon=":material/arrow_forward:")


render()
