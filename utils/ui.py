"""
Identidad visual y helpers de la aplicación (versión narrativa).
================================================================================
La app dejó de ser una plataforma de simulación: ahora es una herramienta para
COMPRENDER el modelo y REPRODUCIR la investigación. Este módulo concentra el
lenguaje visual único (paleta oro/verde/teal del proyecto, tomada tal cual de
`_regen/estilo.py`), la resolución de figuras del pipeline y unos pocos
primitivos de maquetación con baja carga cognitiva.

Regla dura del proyecto: la app solo CONSUME el modelo (core/, configs/) y las
figuras del pipeline (_regen/out). No define números ni colores propios.

    from utils.ui import COL, css, cabecera, figura, dato

Autor: Brahian Calderón Múnera · UdeA · 2026
"""

import os
import sys

import streamlit as st

# ── Paleta SSOT: se importa TAL CUAL de _regen/estilo.py ──────────────────────
_DASH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REGEN = os.path.join(_DASH, "_regen")
for _p in (_DASH, _REGEN):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from estilo import COL  # noqa: E402  (oro A / verde B / teal accent — SSOT)

A_ORO = COL["A"]        # Escenario A · concentrar en una fuente dominante (oro)
B_VERDE = COL["B"]      # Escenario B · acumular energía distribuida (verde)
TEAL = COL["accent"]    # serie neutra / conceptual
INK = COL["ink"]
MUTE = COL["mute"]

# ── Directorios de figuras del pipeline (única fuente gráfica) ────────────────
_DIRS = [
    os.path.join(_DASH, "_regen", "out", "figuras"),
    os.path.join(_DASH, "_regen", "out", "research"),
]


def ruta_figura(nombre: str):
    """Devuelve la ruta del PNG en cualquiera de los directorios del pipeline."""
    for d in _DIRS:
        p = os.path.join(d, nombre)
        if os.path.exists(p):
            return p
    return None


def figura(nombre: str, caption: str = None, ancho: bool = True):
    """Muestra una figura del pipeline (nunca se generan gráficos nuevos aquí)."""
    p = ruta_figura(nombre)
    if p:
        st.image(p, caption=caption, width="stretch" if ancho else "content")
    else:
        st.info(
            f"Figura «{nombre}» no encontrada. Regenera el sistema gráfico con "
            "`python _regen/generate_artifacts.py`."
        )


# ── CSS mínimo y coherente (sin gradientes estridentes) ───────────────────────
def css():
    st.markdown(
        f"""
        <style>
          :root {{
            --oro: {A_ORO}; --verde: {B_VERDE}; --teal: {TEAL};
            --ink: {INK}; --mute: {MUTE};
          }}
          .block-container {{ max-width: 1060px; padding-top: 2.4rem; }}

          /* Cabecera de página: la pregunta ES el título */
          .kicker {{
            font-size: .78rem; letter-spacing: .14em; text-transform: uppercase;
            font-weight: 600; color: var(--mute); margin-bottom: .35rem;
          }}
          .pregunta {{
            font-size: 2.05rem; line-height: 1.15; font-weight: 700;
            color: var(--ink); margin: 0 0 .35rem 0;
          }}
          .bajada {{ font-size: 1.02rem; color: var(--mute); max-width: 60ch; margin-bottom: .4rem; }}
          .rule {{ height: 3px; width: 62px; border-radius: 3px;
                   background: var(--teal); margin: .3rem 0 1.4rem 0; }}
          .rule.a {{ background: var(--oro); }}
          .rule.b {{ background: var(--verde); }}

          /* Tarjetas A / B — el hilo conductor concentrar vs acumular */
          .ab {{ border: 1px solid #e4e7ec; border-radius: 12px; padding: 1.1rem 1.2rem;
                 background: #fff; height: 100%; }}
          .ab.a {{ border-top: 4px solid var(--oro); }}
          .ab.b {{ border-top: 4px solid var(--verde); }}
          .ab h4 {{ margin: 0 0 .4rem 0; font-size: 1.05rem; }}
          .ab.a h4 {{ color: var(--oro); }}
          .ab.b h4 {{ color: var(--verde); }}
          .ab p {{ color: var(--mute); font-size: .93rem; margin: 0; }}

          /* Dato en vivo (proviene de core/ o de los JSON del pipeline) */
          .dato {{ border-left: 4px solid var(--teal); padding: .1rem 0 .1rem .9rem; margin: .2rem 0; }}
          .dato.a {{ border-color: var(--oro); }}
          .dato.b {{ border-color: var(--verde); }}
          .dato .v {{ font-size: 1.7rem; font-weight: 700; color: var(--ink); line-height: 1; }}
          .dato .l {{ font-size: .84rem; color: var(--mute); }}

          .lead {{ font-size: 1.14rem; line-height: 1.5; color: var(--ink); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecera(kicker: str, pregunta: str, bajada: str = "", acento: str = "teal"):
    """Encabezado consistente: la pregunta de la página como título."""
    clase = {"a": "a", "b": "b", "teal": ""}.get(acento, "")
    st.markdown(f'<div class="kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pregunta">{pregunta}</div>', unsafe_allow_html=True)
    if bajada:
        st.markdown(f'<div class="bajada">{bajada}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rule {clase}"></div>', unsafe_allow_html=True)


def dato(valor: str, etiqueta: str, acento: str = "teal"):
    """Cifra en vivo con su etiqueta. `acento` ∈ {'a','b','teal'}."""
    clase = {"a": "a", "b": "b"}.get(acento, "")
    st.markdown(
        f'<div class="dato {clase}"><div class="v">{valor}</div>'
        f'<div class="l">{etiqueta}</div></div>',
        unsafe_allow_html=True,
    )


def tarjeta_ab(lado: str, titulo: str, texto: str):
    """Tarjeta del contraste A (concentrar) vs B (acumular)."""
    st.markdown(
        f'<div class="ab {lado}"><h4>{titulo}</h4><p>{texto}</p></div>',
        unsafe_allow_html=True,
    )
