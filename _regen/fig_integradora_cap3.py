# -*- coding: utf-8 -*-
"""
FigT4 · Figura integradora del Capítulo 3 (cierre del marco teórico).
Diagrama de flujo vertical: Escenario RF → Captación electromagnética →
Conversión RF-DC → Gestión y almacenamiento → Alimentación del dispositivo →
Validación del modelo. Estilo IEEE del proyecto (estilo.py), sin cifras.
Puente hacia la metodología: el Capítulo 4 implementa cada bloque como una fase.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import estilo as E

OUT_F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)

BLOQUES = [
    ("Escenario RF",               "fuentes urbanas disponibles",   E.ic_waves),
    ("Captación electromagnética", "antena fractal y propagación",  E.ic_antenna_lp),
    ("Conversión RF-DC",           "adaptación y rectificación",    E.ic_diode),
    ("Gestión y almacenamiento",   "PMIC y supercondensador",       E.ic_battery),
    ("Alimentación del dispositivo", "nodo IoT autónomo",           E.ic_chip),
    ("Validación del modelo",      "contraste con la literatura",   E.ic_check),
]

n = len(BLOQUES)
BW, BH, GAP = 3.55, 0.66, 0.34
H = n * BH + (n - 1) * GAP
fig, ax = E.canvas(5.4, H + 0.5, (0.0, 5.4), (-0.25, H + 0.25))

cx = 3.05           # centro de las cajas (desplazado a la derecha del icono)
ix = 0.78           # columna de iconos
E.rail(ax, ix, ix, 0.0, lw=0.0)   # no-op para mantener orden z

ys = []
for k, (titulo, sub, icono) in enumerate(BLOQUES):
    cy = H - BH / 2 - k * (BH + GAP)
    ys.append(cy)
    E.node_ieee(ax, cx, cy, BW, BH, titulo, sub=sub, title_fs=9.6, sub_fs=7.0)
    icono(ax, ix, cy, 0.21, E.INK)
    # conector fino icono→caja
    ax.plot([ix + 0.30, cx - BW / 2], [cy, cy], color=E.RAIL, lw=0.7, zorder=0)

for k in range(n - 1):
    E.flow_ieee(ax, cx, ys[k] - BH / 2, cx, ys[k + 1] + BH / 2, lw=1.0, ms=9)

E.label_ieee(ax, cx, -0.16,
             "cada bloque del flujo se implementa como una fase de la metodología",
             fs=7.0, style="italic", color=E.MUTE)

path = os.path.join(OUT_F, "FigT4_flujo_integrador.png")
fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK:", path)
