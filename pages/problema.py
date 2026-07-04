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
    # La narrativa empieza directamente con el problema. La cabecera institucional
    # y el enfoque metodológico viven en la sección "Presentación", antes de esta.
    st.title(":material/battery_alert: El problema: la batería como límite del IoT")
    st.markdown(
        "*Esta sección abre el recorrido del trabajo. Plantea por qué la batería limita a "
        "los nodos IoT y qué oportunidad ofrece la energía que ya viaja por el aire; al "
        "final, una pregunta conducirá hacia la solución que estudia el proyecto.*"
    )

    st.subheader("La batería: el límite práctico de la autonomía")
    st.markdown(
        "Un nodo IoT (un pequeño sensor inalámbrico desplegado en campo) suele alimentarse "
        "con una batería, y ahí está su talón de Aquiles: la batería **se agota**. Imagina "
        "miles de sensores repartidos por una subestación eléctrica, en lo alto de una "
        "torre o en una zona rural de difícil acceso. Mantenerlos vivos significa ir hasta "
        "cada uno a cambiarle la batería. Cuando ese costo supera al del propio sensor, el "
        "despliegue deja de ser viable. La batería ya no es un detalle: se vuelve el límite "
        "real de la autonomía del sistema."
    )

    st.subheader("La oportunidad: energía que ya viaja por el aire")
    st.markdown(
        "En cualquier ciudad hay señales de radio (de televisión, telefonía móvil, "
        "Wi-Fi) que ya circulan por el entorno y que, además de información, transportan "
        "pequeñas cantidades de energía. Casi siempre esa energía se desaprovecha.\n\n"
        "La pregunta de fondo del trabajo es sencilla: **¿se puede recoger una parte de "
        "esa energía y usarla para que un sensor funcione por sí mismo?** Dos cosas la "
        "vuelven plausible hoy: esas señales urbanas son persistentes y la electrónica de "
        "muy bajo consumo necesita cada vez menos para arrancar."
    )

    st.subheader("El caso de estudio: una fuente real y conocida")
    st.markdown(
        "Para responder la pregunta con números reales, y no con suposiciones, hace falta "
        "una fuente de radio concreta y bien caracterizada: solo así se puede calcular "
        "cuánta energía llega y cuánta se aprovecha. En este trabajo se eligió el "
        f"transmisor de {termino('TDT', 'televisión digital')} del **Cerro Nutibara**, en "
        "Medellín.",
        unsafe_allow_html=True,
    )
    st.markdown(
        "¿Por qué esa fuente? Porque es potente, permanente y conocida: emite de forma "
        "continua y sus características están documentadas. Eso permite apoyar todo el "
        "estudio sobre un escenario real en lugar de una estimación vaga."
    )
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
        "puede aprovecharse como fuente complementaria de alimentación. Para entender "
        "cómo hacerlo, primero hay que conocer el dispositivo encargado de capturar esa "
        "energía: la **rectena**."
    )

    st.page_link("pages/contexto.py",
                 label="Siguiente — ¿qué es una rectena? →",
                 icon=":material/arrow_forward:")


render()
