"""
Sección 0 · Presentación del trabajo de grado.

Portada del recorrido. Arranca desde la PREGUNTA y la MOTIVACIÓN (no desde la
tecnología ni el método), en este orden:
    1. Cabecera institucional.
    2. Por qué este trabajo  — motivación: el problema, la oportunidad, el caso, la comparación.
    3. Objetivo general       — el enunciado formal del documento.
    4. El recorrido           — tabla-guía de lo que el lector encontrará y en qué orden.
    5. Cómo se abordó         — el enfoque a nivel marco + alcance y límites (condensado).
    6. Cierre                 — la pregunta abierta que invita a continuar.

La metodología *detallada* (cadena de cálculo, referencias por etapa, arquitectura)
vive en «Información del proyecto» (acerca.py). Esta página enmarca y motiva;
problema/contexto explican; acerca documenta.

Página de lectura. Narrativa derivada de §1.1 (motivación) y §1.2 (objetivos).
"""

import streamlit as st

from utils.pagina import donde_se_desarrolla as _ref


def render():
    # ════════════════════════════════════════════════════════════════════════
    # 1 · CABECERA INSTITUCIONAL
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

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 2 · POR QUÉ ESTE TRABAJO (motivación: arranca desde la pregunta)
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("Por qué este trabajo")
    st.markdown(
        "Los nodos IoT desplegados en campo dependen de baterías, y reemplazarlas a gran "
        "escala resulta costoso o inviable: la autonomía energética es hoy su principal "
        "límite. Al mismo tiempo, el entorno urbano está lleno de energía de "
        "radiofrecuencia —de televisión, telefonía móvil y Wi-Fi— que casi siempre se "
        "desaprovecha. Este trabajo estudia si esa energía, ya presente en el aire, puede "
        "aprovecharse para alimentar dispositivos IoT de bajo consumo."
    )
    st.markdown(
        "Para responder esta pregunta con cifras y no con suposiciones, el trabajo analiza "
        "un escenario real de radiodifusión presente en Medellín y estudia distintas "
        "alternativas de captura de energía. Los detalles técnicos de ese análisis se "
        "presentan en las siguientes secciones."
    )
    _ref("§1.1 Contexto y motivación")

    # ════════════════════════════════════════════════════════════════════════
    # 3 · OBJETIVO GENERAL (enunciado formal, visible)
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("Objetivo general")
    st.markdown(
        "Modelar y simular computacionalmente, con bibliotecas científicas de código "
        "abierto en Python, dos topologías de rectenas fractales multibanda —el "
        "**Triángulo de Sierpinski** (1,8–5,8 GHz) y la **FLPDA Koch** para UHF de TDT y "
        "LTE sub-GHz (470–900 MHz)— orientadas a la recolección de energía RF ambiental en "
        "dispositivos IoT de bajo consumo, evaluando su viabilidad técnica y económica en "
        "el contexto espectral colombiano."
    )
    _ref("§1.2.1 Objetivo general · §1.2.2 Objetivos específicos")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 4 · EL RECORRIDO (tabla-guía, no diagrama)
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("El recorrido")
    st.markdown(
        "La aplicación es una lectura guiada. Cada sección responde a una pregunta y "
        "prepara la siguiente:"
    )
    st.markdown(
        "| Paso | Pregunta |\n"
        "|---|---|\n"
        "| 1 | ¿Por qué la batería limita al IoT? |\n"
        "| 2 | ¿Qué es una rectena y cómo funciona? |\n"
        "| 3 | ¿Cómo se estudió el sistema? |\n"
        "| 4 | ¿Cuánta energía puede recuperarse? |\n"
        "| 5 | ¿Qué aplicaciones permitiría esa energía? |\n"
        "| 6 | ¿Qué tan confiables son los resultados? |\n"
        "| 7 | ¿Qué conclusiones deja el estudio? |\n"
    )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 5 · CÓMO SE ABORDÓ (enfoque a nivel marco + alcance, condensado)
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("Cómo se abordó")
    st.markdown(
        "El sistema se estudió con un modelo computacional en Python: un enfoque "
        "reproducible, que puede ejecutarse y revisarse sin software propietario ni "
        "instrumentación de laboratorio."
    )
    st.markdown(
        "Por esa misma razón, es un **estudio de modelado, no una medición**: permite "
        "estimar órdenes de magnitud y comparar alternativas de diseño, pero no sustituye "
        "una verificación experimental del dispositivo físico (los resultados conservan una "
        "incertidumbre no medida en la ganancia de las antenas, del orden de ±1,5 dBi). "
        "Sus conclusiones son, por tanto, de carácter comparativo y de viabilidad."
    )
    _ref("§2.9 Métodos de análisis electromagnético: enfoque adoptado · "
         "§3.2 Justificación del entorno Python · §1.3 Alcance y limitaciones · "
         "Apéndice E.11 Tabla de limitaciones (L1–L8) · "
         "Referencias y cadena de cálculo en «Información del proyecto»")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # 6 · CIERRE (pregunta abierta que invita a continuar)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(
        "El recorrido comienza con la pregunta que motiva todo el trabajo: *¿puede la "
        "energía de radiofrecuencia presente en el entorno convertirse en una fuente útil "
        "para alimentar nodos IoT de bajo consumo?*"
    )
    st.page_link("pages/problema.py",
                 label="Comenzar el recorrido — el problema del IoT →",
                 icon=":material/arrow_forward:")


render()
