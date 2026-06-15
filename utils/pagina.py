"""
utils/pagina.py — Patrones reutilizables para experiencia de usuario.

Estandariza el encabezado, los bloques de explicación, las cajas de interpretación
de gráficos y las cajas de impacto de parámetros. El objetivo es que **todas las
páginas se sientan iguales** y que un docente/jurado/profesional pueda usar la
plataforma sin necesidad de leer la tesis ni el código.
"""

from __future__ import annotations

import streamlit as st


# ── 1. Encabezado estandarizado ──────────────────────────────────────────────

def encabezado(
    titulo: str,
    subtitulo: str = "",
    *,
    que_es: str,
    para_que_sirve: str,
    entradas: str,
    salidas: str,
    como_leer: str = "",
    icono: str = ":material/info:",
):
    """Estructura uniforme arriba de cada página.

    Cualquier usuario que abra la página puede responder en 30 segundos:
        1. ¿Qué es esta página?
        2. ¿Para qué sirve?
        3. ¿Qué le doy de entrada?
        4. ¿Qué me devuelve?
        5. ¿Cómo se interpreta?
    """
    st.title(titulo)
    if subtitulo:
        st.caption(subtitulo)

    with st.expander(f"{icono}  Sobre esta página · *qué es, para qué sirve y cómo se usa*",
                     expanded=False):
        col_q, col_p = st.columns(2)
        with col_q:
            st.markdown(f"**:material/quiz: ¿Qué es esta página?**\n\n{que_es}")
            st.markdown(f"**:material/login: ¿Qué información recibe?**\n\n{entradas}")
        with col_p:
            st.markdown(f"**:material/track_changes: ¿Para qué sirve?**\n\n{para_que_sirve}")
            st.markdown(f"**:material/output: ¿Qué información entrega?**\n\n{salidas}")
        if como_leer:
            st.markdown("---")
            st.markdown(f"**:material/menu_book: ¿Cómo se interpreta?**  \n{como_leer}")


# ── 2. Caja "Cómo interpretar esta gráfica" ──────────────────────────────────

def como_interpretar(
    titulo_grafica: str = "esta gráfica",
    *,
    objetivo: str,
    ejes: str,
    tendencias: str,
    si_sube_baja: str = "",
    impacto_parametros: str = "",
):
    """Acompañar cada gráfica con una caja de interpretación uniforme.

    Llamar inmediatamente debajo de `st.plotly_chart(...)`."""
    with st.expander(f":material/visibility:  ¿Cómo interpretar {titulo_grafica}?",
                     expanded=False):
        st.markdown(f"**:material/track_changes: Objetivo de la gráfica**  \n{objetivo}")
        st.markdown(f"**:material/swap_horiz: Ejes y unidades**  \n{ejes}")
        st.markdown(f"**:material/trending_up: Lectura física de la tendencia**  \n{tendencias}")
        if si_sube_baja:
            st.markdown(f"**:material/arrow_upward: ¿Qué significa que la curva suba, baje o cambie?**  \n{si_sube_baja}")
        if impacto_parametros:
            st.markdown(f"**:material/tune: ¿Qué pasa si modifico los parámetros?**  \n{impacto_parametros}")


# ── 3. Caja de impacto de parámetros (para calculadoras) ─────────────────────

def impacto_parametros(parametros: list[dict]):
    """Llamar debajo de los sliders de una calculadora.

    Cada elemento del listado debe ser un dict con:
        nombre, simbolo, significado, rango, ecuacion, impacto

    Ejemplo:
        impacto_parametros([
            {"nombre": "EIRP", "simbolo": "EIRP [dBm]",
             "significado": "Potencia isotrópica radiada equivalente del transmisor.",
             "rango": "40–80 dBm. Canónico TDT Nutibara: 70 dBm.",
             "ecuacion": "P_in [dBm] = EIRP − FSPL − L_urb + G",
             "impacto": "+3 dB en EIRP → ×2 en P_in → ~×2 en P_DC."},
            ...
        ])
    """
    with st.expander(":material/tune:  Significado físico y rango de cada parámetro",
                     expanded=False):
        for p in parametros:
            with st.container(border=True):
                st.markdown(f"**{p['simbolo']}** — {p['nombre']}")
                cols = st.columns(2)
                with cols[0]:
                    st.markdown(f":material/info: **Significado físico**  \n{p['significado']}")
                    st.markdown(f":material/straighten: **Rango recomendado**  \n{p['rango']}")
                with cols[1]:
                    if p.get('ecuacion'):
                        st.markdown(f":material/function: **Ecuación afectada**")
                        st.latex(p['ecuacion'])
                    if p.get('impacto'):
                        st.markdown(f":material/leaderboard: **Impacto en los resultados**  \n{p['impacto']}")


# ── 4. Distintivo visual: Resultado Oficial vs Exploración ──────────────────

def badge_oficial():
    """Banner verde que presenta la página como los resultados de referencia
    del proyecto de grado (vista de lectura, sin controles editables)."""
    st.success(
        ":material/verified: **Resultados de referencia del proyecto de grado.** "
        "Esta sección presenta los resultados obtenidos para el escenario principal "
        "estudiado. Estos valores sirven como punto de comparación para comprender el "
        "comportamiento del sistema y, después, explorar distintos escenarios y "
        "parámetros en las demás secciones de la aplicación.",
        icon=":material/verified:",
    )


def donde_se_desarrolla(seccion: str):
    """Ancla de *guía de lectura*: indica en qué sección del informe de grado se
    desarrolla el tema que el lector tiene delante. La narrativa de la aplicación
    no inventa contenido; remite al documento donde el concepto se trabaja en
    detalle. Llamar inmediatamente debajo del contenido al que se refiere.

    Patrón uniforme en toda la app:
        1. Se muestra el contenido (texto, métrica, gráfica).
        2. Debajo, este bloque indica dónde profundizar en el proyecto.
    """
    st.caption(f":material/menu_book: **Dónde se desarrolla en el proyecto:** {seccion}")


def correspondencia(tipo: str, detalle: str):
    """Declara la correspondencia de una gráfica con el trabajo de grado.

    tipo:
        'directa'        → reproduce una figura del documento.
        'derivada'       → construida a partir de datos/ecuaciones de una figura/tabla.
        'complementaria' → no aparece literal; creada para facilitar la interpretación.
    Llamar inmediatamente debajo de `st.plotly_chart(...)`.
    """
    iconos = {
        'directa':        (":material/content_copy:", "Reproducción directa"),
        'derivada':       (":material/insights:",     "Visualización interactiva derivada"),
        'complementaria': (":material/add_chart:",    "Visualización complementaria"),
    }
    ic, label = iconos.get(tipo, (":material/image:", "Visualización"))
    st.caption(f"{ic} **{label}.** {detalle}")


def control_interactivo(*, magnitud: str, referencia: str, al_subir: str,
                        al_bajar: str, limite: str):
    """Bloque de contexto para un control interactivo (slider/selector).

    Responde, para cualquier parámetro editable: qué magnitud física representa,
    cuál es el valor de referencia del trabajo, qué pasa al subirlo/bajarlo y
    cuándo deja de ser razonable. Llamar junto al control.
    """
    with st.expander(":material/tune:  ¿Qué hace este control y hasta dónde tiene sentido?",
                     expanded=False):
        st.markdown(f"**Qué representa.** {magnitud}")
        st.markdown(f"**Valor de referencia del trabajo.** {referencia}")
        st.markdown(f"**Si aumenta.** {al_subir}")
        st.markdown(f"**Si disminuye.** {al_bajar}")
        st.markdown(f"**Cuándo deja de ser representativo.** {limite}")


def badge_exploracion(detalle: str = ""):
    """Banner ámbar indicando que los valores producidos dependen de los
    sliders del usuario y NO son resultados oficiales del proyecto."""
    base = ("**Sección de exploración paramétrica.** Los valores presentados "
            "dependen de los parámetros seleccionados y **no corresponden a los "
            "resultados de referencia del informe**, que se reportan en la sección "
            "de inicio.")
    if detalle:
        base += f"\n\n{detalle}"
    st.warning(":material/science:  " + base, icon=":material/science:")
