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
    """Banner verde indicando que los valores de la página son resultados de
    referencia oficiales del proyecto (read-only, protegidos por test)."""
    st.success(
        ":material/verified: **Resultados de Referencia del Proyecto.** "
        "Los valores que se muestran aquí son los reportados en la tesis y están "
        "**protegidos por la suite de 51 tests del pipeline** (auditoría 2026-05-28). "
        "Para explorar cómo cambian al modificar parámetros, ve a la página "
        "**Calculadora del modelo**.",
        icon=":material/verified:",
    )


def badge_exploracion(detalle: str = ""):
    """Banner ámbar indicando que los valores producidos dependen de los
    sliders del usuario y NO son resultados oficiales del proyecto."""
    base = ("**Página de exploración paramétrica.** Los valores que produzcas "
            "aquí dependen de los parámetros que muevas; **no son los resultados "
            "oficiales del proyecto**. Para ver los resultados oficiales ve a "
            "**Resultados de Referencia del Proyecto** (página de inicio).")
    if detalle:
        base += f"\n\n{detalle}"
    st.warning(":material/science:  " + base, icon=":material/science:")
