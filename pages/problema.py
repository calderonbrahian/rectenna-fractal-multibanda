"""
Sección 1 · Portada e introducción del trabajo de grado.

Es el arranque del recorrido. Estructura:
    Portada (identidad del trabajo, separada del contenido)
    → El problema → La oportunidad → Caso de estudio → Transición hacia la rectena.

Página de lectura narrativa; sin controles ni cálculos. Las definiciones de los
términos técnicos aparecen en hover (no en un glosario aparte). Narrativa
derivada de §1.1 (Contexto y motivación) del informe de grado.
"""

import streamlit as st
from utils.pagina import donde_se_desarrolla as _ref
from utils.glosario import termino


def render():
    # ════════════════════════════════════════════════════════════════════════
    # PORTADA — identidad del trabajo, claramente separada del contenido
    # ════════════════════════════════════════════════════════════════════════
    with st.container(border=True):
        st.caption("TRABAJO DE GRADO · INGENIERÍA DE TELECOMUNICACIONES · "
                   "UNIVERSIDAD DE ANTIOQUIA")
        st.markdown(
            "## Diseño y simulación computacional de rectenas fractales multibanda "
            "para recolección de energía RF en entornos IoT"
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Autor**  \nBrahian Calderón Múnera")
            st.markdown("**Director**  \nLuis Alberto Flórez Serna, M.Sc.")
        with c2:
            st.markdown("**Programa**  \nIngeniería de Telecomunicaciones")
            st.markdown("**Institución**  \nUniversidad de Antioquia · Medellín · 2026")
        with st.expander("Objetivo general del trabajo"):
            st.markdown(
                "Modelar y simular computacionalmente, con bibliotecas científicas de "
                "código abierto en Python, dos topologías de rectenas fractales multibanda "
                "—el **Triángulo de Sierpinski** (1,8–5,8 GHz) y la **FLPDA Koch** para UHF "
                "de TDT y LTE sub-GHz (470–900 MHz)— orientadas a la recolección de energía "
                "RF ambiental en dispositivos IoT de bajo consumo, evaluando su viabilidad "
                "técnica y económica en el contexto espectral colombiano."
            )
            _ref("§1.2.1 Objetivo general · §1.2.2 Objetivos específicos")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # INTRODUCCIÓN — la narrativa empieza directamente con el problema
    # ════════════════════════════════════════════════════════════════════════
    st.title(":material/battery_alert: El problema: la batería como límite del IoT")
    st.markdown(
        "*Esta sección abre el recorrido del trabajo. Plantea por qué la batería limita a "
        "los nodos IoT y qué oportunidad ofrece la energía que ya viaja por el aire; al "
        "final, una pregunta conducirá hacia la solución que estudia el proyecto.*"
    )

    st.subheader("La batería: el límite práctico de la autonomía")
    st.markdown(
        "Un nodo IoT —un pequeño sensor inalámbrico desplegado en campo— suele alimentarse "
        "con una batería, y ahí está su talón de Aquiles: la batería **se agota**. En "
        "despliegues a gran escala (subestaciones eléctricas, estructuras de altura, zonas "
        "industriales remotas, infraestructura agrícola), cada visita para reemplazarla "
        "tiene un costo logístico que, cuando supera al del propio sensor, **vuelve "
        "inviable el despliegue**. La batería deja de ser un detalle y se convierte en el "
        "**límite real de la autonomía** del sistema."
    )

    st.subheader("La oportunidad: energía que ya viaja por el aire")
    st.markdown(
        "En cualquier ciudad hay señales de radio —de televisión, telefonía móvil, "
        "Wi-Fi— que **ya están presentes en el entorno** y que, además de información, "
        "transportan **pequeñas cantidades de energía**. Casi siempre esa energía se "
        "desaprovecha.\n\n"
        "La pregunta de fondo del trabajo es sencilla: **¿se puede recoger una parte de "
        "esa energía y usarla para que un sensor funcione por sí mismo?** No es una idea "
        "nueva —ya en los años ochenta se demostró que las microondas podían alimentar "
        "dispositivos a distancia—; lo que cambió es que hoy esas señales urbanas son "
        "**persistentes** y la electrónica de muy bajo consumo vuelve la idea plausible."
    )

    st.subheader("El caso de estudio: una fuente concreta para poder cuantificar")
    st.markdown(
        "Para pasar de la idea a un **número**, el trabajo necesita una fuente de radio "
        "concreta y bien conocida: solo si la fuente está caracterizada se puede calcular "
        "cuánta energía llega a la antena y cuánta se aprovecha. Por eso el estudio se "
        "sitúa en **Medellín (Colombia)** y toma como caso de estudio el transmisor de "
        f"{termino('TDT')} del **Cerro Nutibara**.",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(
            "**Por qué se eligió esta fuente.** El transmisor del Cerro Nutibara se "
            f"seleccionó como caso de estudio porque es una fuente {termino('RF')} "
            f"**potente y estable** ({termino('EIRP')} de 2 a 10 kW), emite de forma "
            "continua y está **bien caracterizada**. Eso permite construir un **escenario "
            "cuantitativo realista** para evaluar la viabilidad del sistema —en lugar de "
            "quedarse en una estimación vaga— y sirve de referencia para todo el trabajo. "
            "Sus densidades de potencia en UHF superan en uno o dos órdenes de magnitud "
            "las de una red Wi-Fi doméstica.",
            unsafe_allow_html=True,
        )
        st.caption(":material/info: Pasa el cursor sobre los términos subrayados "
                   "(TDT, RF, EIRP) para ver su definición.")
    _ref("§1.1 Contexto y motivación · §1.3 Alcance y limitaciones del estudio · "
         "Tabla 1 (densidades de potencia RF típicas en entornos urbanos)")

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # TRANSICIÓN + CONCLUSIÓN — puente hacia la rectena
    # ════════════════════════════════════════════════════════════════════════
    st.subheader("Del problema a la solución")
    st.markdown(
        "Si esa energía está disponible en el entorno, surge la pregunta que guía el "
        "resto del recorrido:"
    )
    st.info(
        "**Si hay energía de radio en el aire, ¿cómo se captura y se convierte en "
        "electricidad útil para un dispositivo IoT?**",
        icon=":material/help:",
    )
    st.markdown(
        "La dependencia de baterías sigue siendo una limitación importante para muchos "
        "nodos IoT. Este trabajo explora si la energía de radiofrecuencia del entorno "
        "puede aprovecharse como **fuente complementaria** de alimentación. Para entender "
        "cómo hacerlo, primero hay que conocer el dispositivo encargado de capturar esa "
        "energía: la **rectena**."
    )

    st.page_link("pages/contexto.py",
                 label="Siguiente — ¿qué es una rectena? →",
                 icon=":material/arrow_forward:")


render()
