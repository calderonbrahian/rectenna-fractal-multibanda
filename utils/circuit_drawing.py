"""
utils/circuit_drawing.py — Primitivas para esquemáticos de circuitos en Plotly.

Se usan tanto en pages/escenario_a.py (topologías comparativas) como en
pages/escenario_b.py (doblador Greinacher con conducción interactiva). Centralizar
estas primitivas evita duplicar la lógica de dibujo.

Convenciones
------------
- Colores por defecto: cable gris #94A3B8, diodo amarillo #FBBF24, GND gris.
- Coordenadas: cualquier sistema; el caller debe ajustar xaxis/yaxis a su escala.
- Las funciones modifican `fig` en sitio y no devuelven nada.
"""

from __future__ import annotations


# ── Componentes pasivos ───────────────────────────────────────────────────────

def draw_capacitor(fig, x: float, y: float, *, vertical: bool = False,
                    color: str = "#94A3B8") -> None:
    """Capacitor = dos líneas paralelas. (x, y) es el centro del componente.
    vertical=True dibuja el cap entre dos puntos verticales (placas horizontales)."""
    if vertical:
        fig.add_shape(type="line", x0=x - 0.25, y0=y, x1=x + 0.25, y1=y,
                      line=dict(color=color, width=3))
        fig.add_shape(type="line", x0=x - 0.25, y0=y - 0.2, x1=x + 0.25, y1=y - 0.2,
                      line=dict(color=color, width=3))
    else:
        fig.add_shape(type="line", x0=x, y0=y - 0.25, x1=x, y1=y + 0.25,
                      line=dict(color=color, width=3))
        fig.add_shape(type="line", x0=x + 0.2, y0=y - 0.25, x1=x + 0.2, y1=y + 0.25,
                      line=dict(color=color, width=3))


def draw_wire(fig, x0: float, y0: float, x1: float, y1: float,
               *, color: str = "#94A3B8", width: float = 2) -> None:
    """Cable recto entre dos puntos."""
    fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                  line=dict(color=color, width=width))


def draw_gnd(fig, x: float, y: float, *, color: str = "#94A3B8") -> None:
    """Símbolo de tierra: tres líneas paralelas decrecientes."""
    for i, frac in enumerate([0.20, 0.13, 0.07]):
        fig.add_shape(type="line",
                      x0=x - frac, y0=y - i * 0.06, x1=x + frac, y1=y - i * 0.06,
                      line=dict(color=color, width=1.5))


# ── Diodos (Schottky) ────────────────────────────────────────────────────────

def draw_diode_right(fig, x0: float, x1: float, y: float,
                      *, color: str = "#FBBF24") -> None:
    """Diodo apuntando a la derecha: ánodo en x0, cátodo en x1. Triángulo
    relleno + barra del cátodo. x1 − x0 ≈ longitud del símbolo."""
    fig.add_shape(type="path",
                  path=f"M {x0},{y - 0.22} L {x0},{y + 0.22} L {x1 - 0.08},{y} Z",
                  fillcolor=color, line_color=color)
    fig.add_shape(type="line", x0=x1 - 0.08, y0=y - 0.25, x1=x1 - 0.08, y1=y + 0.25,
                  line=dict(color=color, width=3))


def draw_diode_up(fig, x: float, y0: float, y1: float,
                   *, color: str = "#FBBF24") -> None:
    """Diodo apuntando hacia arriba: ánodo en y0, cátodo en y1."""
    fig.add_shape(type="path",
                  path=f"M {x - 0.22},{y0} L {x + 0.22},{y0} L {x},{y1 - 0.08} Z",
                  fillcolor=color, line_color=color)
    fig.add_shape(type="line", x0=x - 0.25, y0=y1 - 0.08, x1=x + 0.25, y1=y1 - 0.08,
                  line=dict(color=color, width=3))
