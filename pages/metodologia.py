"""
Sección 4 · Metodología de simulación.
Narrativa derivada de §2.9 (Métodos de análisis electromagnético) y del Capítulo 3
(Metodología computacional). Página de lectura; sin controles ni cálculos.
"""

import streamlit as st
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/build: Metodología de simulación",
        "Cómo se obtienen los resultados: modelado analítico circuital en Python",
        que_es=("Explica el enfoque de modelado del proyecto y por qué se eligió, para que "
                "los resultados de las demás secciones se interpreten en su contexto."),
        para_que_sirve=("Saber qué tipo de afirmaciones permite el modelo —y cuáles no— "
                        "antes de leer las cifras."),
        entradas="Ninguna; es una página de lectura.",
        salidas="El enfoque metodológico, su alcance y su justificación.",
    )

    st.subheader("Modelado analítico circuital, no onda completa")
    st.markdown(
        "El proyecto modela cada etapa del sistema con **ecuaciones analíticas y de circuito "
        "equivalente** implementadas en Python (NumPy/SciPy), no con simulación "
        "electromagnética de onda completa (HFSS, CST) ni con mediciones de laboratorio. "
        "Es un alcance **exploratorio-comparativo**: evalúa la viabilidad de dos topologías "
        "en un contexto espectral específico, no diseña un producto físico."
    )
    st.markdown(
        "El modelo encadena referencias primarias: **Carrel (1961)** para el arreglo "
        "log-periódico, la **curva de Koch** para la miniaturización, **Friis + ITU-R "
        "P.1546** para la propagación, **Shockley** para el diodo y el **datasheet del "
        "BQ25504** para la gestión de energía."
    )

    with st.container(border=True):
        st.markdown(
            "**Qué permite y qué no.** El enfoque permite **estimar** órdenes de magnitud y "
            "**comparar** topologías de forma reproducible y sin herramientas propietarias. "
            "No sustituye una validación experimental: los patrones de radiación y las "
            "eficiencias llevan una incertidumbre que el propio trabajo documenta como "
            "limitaciones (sección **Conclusiones**)."
        )

    st.info(
        "La reproducibilidad y la trazabilidad teoría↔código del modelo se detallan en la "
        "sección **Información del proyecto**.",
        icon=":material/info:",
    )

    _ref("§2.9 Métodos de análisis electromagnético: enfoque adoptado y alternativas · "
         "§3.1 Enfoque metodológico · §3.3 Arquitectura del pipeline de simulación")

    st.page_link("pages/escenario_a.py",
                 label="Siguiente — los escenarios estudiados →",
                 icon=":material/arrow_forward:")


render()
