"""
Sección 1 · El problema de investigación.
Narrativa derivada de §1.1 (Contexto y motivación) del informe de grado.
Página de lectura; sin controles ni cálculos.
"""

import streamlit as st
from utils.pagina import encabezado, donde_se_desarrolla as _ref


def render():
    encabezado(
        ":material/battery_alert: El problema: la batería como límite del IoT",
        "Por qué tiene sentido recolectar energía de radiofrecuencia ambiental",
        que_es=("Primera parada del recorrido: plantea el problema que motiva el proyecto "
                "de grado, antes de entrar en antenas, circuitos o resultados."),
        para_que_sirve=("Entender qué limita hoy a los nodos IoT desplegados en campo y qué "
                        "oportunidad abre aprovechar la energía de radio que ya existe en el "
                        "entorno."),
        entradas="Ninguna; es una página de lectura.",
        salidas=("El planteamiento del problema (la batería) y la oportunidad (la energía "
                 "de radiofrecuencia ambiental)."),
    )

    # ── Portada del trabajo de grado (identidad del proyecto en la entrada) ──
    with st.container(border=True):
        st.markdown(
            "**Trabajo de grado para optar al título de Ingeniero de Telecomunicaciones "
            "· Universidad de Antioquia**"
        )
        st.markdown(
            "### Diseño y simulación computacional de rectenas fractales multibanda "
            "para recolección de energía RF en entornos IoT"
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Autor**  \nBrahian Calderón Múnera")
            st.markdown("**Director**  \nLuis Alberto Flórez Serna, M.Sc.")
        with c2:
            st.markdown("**Programa**  \nIngeniería de Telecomunicaciones")
            st.markdown("**Institución**  \nUniversidad de Antioquia · Medellín · 2026")
        st.markdown(
            "**Objetivo general**  \n"
            "Modelar y simular computacionalmente, con bibliotecas científicas de código "
            "abierto en Python, dos topologías de rectenas fractales multibanda —el "
            "**Triángulo de Sierpinski** (1,8–5,8 GHz) y la **FLPDA Koch** para UHF de TDT "
            "y LTE sub-GHz (470–900 MHz)— orientadas a la recolección de energía RF "
            "ambiental en dispositivos IoT de bajo consumo, evaluando su viabilidad "
            "técnica y económica en el contexto espectral colombiano."
        )
        _ref("§1.2.1 Objetivo general · §1.2.2 Objetivos específicos")

    st.subheader("La batería es el límite práctico de la autonomía")
    st.markdown(
        "En un nodo IoT desplegado en campo, la batería no es un componente más: es el "
        "**límite práctico de la autonomía** del sistema. En despliegues a gran escala "
        "—subestaciones eléctricas, estructuras de altura, zonas industriales remotas, "
        "infraestructura agrícola— cada visita de mantenimiento para reemplazar una "
        "batería implica un costo logístico que, cuando supera al del propio sensor, "
        "**compromete la viabilidad del despliegue**."
    )

    st.subheader("La oportunidad: energía que ya viaja por el aire")
    st.markdown(
        "La **recolección de energía de radiofrecuencia ambiental** (RF Energy Harvesting, "
        "RFEH) aprovecha las señales que ya viajan por el espectro para alimentar nodos con "
        "consumos en el rango de los microvatios a milivatios. No es una idea nueva "
        "—Brown (1984) hizo volar un helicóptero en miniatura propulsado por microondas "
        "captadas en vuelo—; lo que cambió en las últimas décadas es la disponibilidad de "
        "**señales urbanas persistentes** (TDT, LTE, WiFi) y la aparición de circuitos de "
        "gestión de energía con umbrales de activación por debajo de 330 mV (por ejemplo, "
        "el BQ25504 de Texas Instruments)."
    )

    with st.container(border=True):
        st.markdown(
            "**¿Por qué la TDT del Cerro Nutibara?** Los transmisores de televisión digital "
            "del Cerro Nutibara (~1 550 m s. n. m.) operan con potencias isotrópicas "
            "radiadas equivalentes (EIRP) de **2 a 10 kW**, con densidades de potencia en "
            "las bandas UHF (470–698 MHz TDT DVB-T2 y 758–803 MHz LTE Band 28) que superan "
            "en **uno a dos órdenes de magnitud** las de los puntos de acceso WiFi "
            "domésticos. Esa disparidad es la que el proyecto explota."
        )

    _ref("§1.1 Contexto y motivación · §1.3 Alcance y limitaciones del estudio · "
         "Tabla 1 (densidades de potencia RF típicas en entornos urbanos)")

    st.page_link("pages/contexto.py",
                 label="Siguiente — ¿qué es una rectena? →",
                 icon=":material/arrow_forward:")


render()
