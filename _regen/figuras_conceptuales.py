"""
Figuras CONCEPTUALES y METODOLÓGICAS — sistema gráfico unificado.
================================================================================
Catálogo del pipeline por FAMILIAS (arquitectura maestra v2), todas con el mismo
lenguaje visual (estilo tipo paper, iconografía técnica de línea) definido en
estilo_figuras.py:

  · C5  Figura maestra   — la tesis completa en una figura   (Metodológica/síntesis)
  · C1  Fuentes → caso   — el porqué, con recorrido físico    (Conceptual)
  · C3  Anatomía rectena — qué ES una rectena (5 etapas)      (Conceptual)
  · C2  Flujo metodológico — el método como método            (Metodológica)
  · C4  Cadena reproducible — SSOT, un sistema, tres medios    (Metodológica)

No producen resultados nuevos: reusan CANONICAL/RF_UHF (SSOT) y nombres reales de
módulos. Deterministas. Regla tri-medio (documento / Streamlit / póster).

Ejecutar:  ./.venv/Scripts/python.exe _regen/figuras_conceptuales.py
"""

import os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
_HERE = os.path.dirname(os.path.abspath(__file__))
_DASH = os.path.dirname(_HERE)
if _DASH not in sys.path:
    sys.path.insert(0, _DASH)

import matplotlib.pyplot as plt
from configs.parametros import CANONICAL
import estilo as E

FIGS = os.path.join(_HERE, "out", "figuras")
os.makedirs(FIGS, exist_ok=True)


def _save(fig, name):
    path = os.path.join(FIGS, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _hflow(nodes, accent, w=0.92, h=1.3, title_fs=8.4, sub_fs=6.6,
           numbered=False, cap=None):
    """Construye un flujo horizontal de nodos [(title, sub, icon)]. Devuelve fig.
    Nodos anchos (1.5 in/unidad) para que el texto quepa sin desbordar."""
    n = len(nodes)
    fig, ax = E.canvas(n * 1.5, 2.8, (0, n), (0, 2))
    for i, (title, sub, icon) in enumerate(nodes):
        cx = i + 0.5
        E.node(ax, cx, 1.28, w, h, title, sub=sub, icon=icon, accent=accent,
               idx=(i + 1) if numbered else None, title_fs=title_fs, sub_fs=sub_fs)
        if i < n - 1:
            E.flow(ax, cx + w/2, 1.28, cx + 1 - w/2, 1.28, accent=E.RAIL)
    if cap:
        E.caption(ax, n/2, 0.30, cap)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
def figC5_maestra():
    """C5 · La tesis en una figura (graphical abstract) — cuadrícula 2×4."""
    stages = [
        ("Problema", "energía IoT", E.ic_alert),
        ("Pregunta", "¿RF viable?", E.ic_question),
        ("Hipótesis", "sí, y medible", E.ic_bulb),
        ("Metodología", "modelo + código", E.ic_code),
        ("Dos topologías", "Sierpinski · FLPDA", E.ic_branch),
        ("Simulación", "cadena RF→DC", E.ic_waves),
        ("Resultados", "viabilidad", E.ic_chart),
        ("Conclusiones", "método reusable", E.ic_check),
    ]
    fig, ax = E.canvas(9.2, 5.0, (0, 4.4), (0, 2.7))
    top_y, bot_y = 1.85, 0.72
    xs_top = [0.55, 1.5, 2.45, 3.4]      # 1-4 izq→der
    xs_bot = [3.4, 2.45, 1.5, 0.55]      # 5-8 der→izq (boustrofedón)
    W, H = 0.92, 1.02
    for k in range(4):
        t, s, ic = stages[k]
        E.node(ax, xs_top[k], top_y, W, H, t, sub=s, icon=ic, accent=E.AC_METHOD,
               idx=k + 1, title_fs=8.0, sub_fs=6.2)
        if k < 3:
            E.flow(ax, xs_top[k] + W/2, top_y, xs_top[k + 1] - W/2, top_y, accent=E.RAIL)
    E.flow(ax, xs_top[3], top_y - H/2, xs_bot[0], bot_y + H/2, accent=E.RAIL)  # baja 4→5
    for k in range(4):
        t, s, ic = stages[4 + k]
        E.node(ax, xs_bot[k], bot_y, W, H, t, sub=s, icon=ic, accent=E.AC_METHOD,
               idx=5 + k, title_fs=8.0, sub_fs=6.2)
        if k < 3:
            E.flow(ax, xs_bot[k] - W/2, bot_y, xs_bot[k + 1] + W/2, bot_y, accent=E.RAIL)
    return _save(fig, "FigC5_maestra.png"), "C5 · 8 etapas (2×4 graphical abstract)"


def figC1_fuentes_a_caso():
    """C1 · Del entorno urbano al caso — recorrido físico con iconos (Q2)."""
    n = 5
    fig, ax = E.canvas(n * 1.5, 3.1, (0, n), (0, 2.5))
    etapas = [
        ("Entorno urbano", "AM·FM·TDT·LTE·5G", E.ic_city),
        ("Campo EM", "densidad RF", E.ic_waves),
        ("Rectena", "antena + diodo", E.ic_antenna),
        ("Modelo", "reproducible", E.ic_code),
        ("Viabilidad", "energía útil", E.ic_chart),
    ]
    for i, (t, s, ic) in enumerate(etapas):
        cx = i + 0.5
        E.node(ax, cx, 1.45, 0.92, 1.3, t, sub=s, icon=ic, accent=E.AC_CONCEPT,
               title_fs=8.4, sub_fs=6.4)
        if i < n - 1:
            E.flow(ax, cx + 0.46, 1.45, cx + 0.54, 1.45, accent=E.RAIL)
    # marca de caso sobre la primera etapa
    E.ic_pin(ax, 0.5, 2.24, 0.13, E.AC_A)
    ax.text(0.5, 2.42, "Caso: TDT (Colombia)", ha="center", fontsize=6.8,
            color=E.INK, fontweight="bold", family=E.FONT)
    return _save(fig, "FigC1_fuentes_a_caso.png"), "C1 · recorrido físico + caso"


def figC3_anatomia_rectena():
    """C3 · Qué ES una rectena — cinco etapas conceptuales, sin números (Q3, obs.8).
    Cadena CONCEPTUAL (bloques). La cadena CUANTITATIVA vive en la cascada (Cap. 4)."""
    nodes = [
        ("Antena", "capta la onda", E.ic_antenna),
        ("Adaptación\n(IMN)", "transfiere P", E.ic_match),
        ("Rectificador", "RF → DC", E.ic_diode),
        ("Gestor\n(PMIC)", "acondiciona", E.ic_chip),
        ("Carga IoT", "consume", E.ic_battery),
    ]
    fig = _hflow(nodes, E.AC_CONCEPT, w=0.9, h=1.15, title_fs=8.4, sub_fs=6.6)
    return _save(fig, "FigC3_anatomia_rectena.png"), "C3 · anatomía (5 etapas, conceptual)"


def figC2_flujo_metodologico():
    """C2 · Flujo metodológico — el método como método (Q4)."""
    nodes = [
        ("Pregunta", "¿RF viable?", E.ic_question),
        ("Escenario", "fuente · f", E.ic_pin),
        ("Modelado", "antena · diodo", E.ic_code),
        ("Validación", "Wang · P-B.", E.ic_check),
        ("Resultados", "P_DC · η · T", E.ic_chart),
        ("Criterios", "topología", E.ic_branch),
    ]
    fig = _hflow(nodes, E.AC_METHOD, w=0.9, h=1.15, title_fs=8.4, sub_fs=6.4,
                 numbered=True)
    return _save(fig, "FigC2_flujo_metodologico.png"), "C2 · 6 etapas numeradas"


def figC4_cadena_reproducible():
    """C4 · Cadena de reproducibilidad — un sistema, tres medios (Q10)."""
    fig, ax = E.canvas(9.0, 3.6, (0, 10), (0, 5))
    cad = [("Modelo", "físico", E.ic_waves), ("Código", "core/·simulation/", E.ic_code),
           ("Pipeline", "_regen/", E.ic_chip), ("Artefactos", "figuras·tablas", E.ic_chart)]
    xs = [1.15, 3.15, 5.15, 7.15]
    for (t, s, ic), x in zip(cad, xs):
        E.node(ax, x, 3.7, 1.55, 1.2, t, sub=s, icon=ic, accent=E.AC_REPRO,
               title_fs=8.6, sub_fs=6.6)
    for i in range(len(xs) - 1):
        E.flow(ax, xs[i] + 0.78, 3.7, xs[i + 1] - 0.78, 3.7, accent=E.RAIL)
    medios = [("Documento", 4.35), ("Streamlit", 3.7), ("Póster", 3.05)]
    for txt, y in medios:
        E.node(ax, 9.05, y, 1.5, 0.55, txt, accent=E.AC_REPRO, title_fs=8.0)
        E.flow(ax, 7.95, 3.7, 8.32, y, accent=E.RAIL, lw=1.3)
    E.node(ax, 4.0, 1.35, 5.2, 0.8,
           "Repositorio público · SSOT · 51 pruebas de regresión",
           accent=E.INK, title_fs=8.4)
    E.flow(ax, 3.15, 3.1, 3.6, 1.78, accent=E.RAIL, lw=1.2)
    ax.text(9.05, 2.15, "un sistema,\ntres medios", ha="center", fontsize=6.8,
            style="italic", color=E.MUTE, family=E.FONT)
    return _save(fig, "FigC4_cadena_reproducible.png"), "C4 · pipeline → 3 medios → repo"


if __name__ == "__main__":
    print("=" * 70)
    print("FIGURAS CONCEPTUALES/METODOLÓGICAS — sistema gráfico unificado")
    print("=" * 70)
    for label, fn in [
        ("C5 · Figura maestra", figC5_maestra),
        ("C1 · Fuentes → caso", figC1_fuentes_a_caso),
        ("C3 · Anatomía rectena", figC3_anatomia_rectena),
        ("C2 · Flujo metodológico", figC2_flujo_metodologico),
        ("C4 · Cadena reproducible", figC4_cadena_reproducible),
    ]:
        try:
            path, det = fn()
            print(f"[OK ] {label}  {det}")
        except Exception as e:
            import traceback
            print(f"[ERR] {label}  {type(e).__name__}: {e}")
            traceback.print_exc()
    print(f"\nSalida: {FIGS}")
