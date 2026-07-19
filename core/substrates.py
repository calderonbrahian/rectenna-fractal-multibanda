"""
================================================================================
MÓDULO: Sustratos dieléctricos — capa de estudio comparativo (F0)
================================================================================
Catálogo de sustratos de microondas para el estudio comparativo de antenas ×
sustratos. Cada sustrato expone una interfaz uniforme:

    sub.er(f_hz)         permitividad relativa εr(f)   [adimensional]
    sub.tan_delta(f_hz)  tangente de pérdidas tan δ(f) [adimensional]
    sub.h                espesor del dieléctrico h      [m]
    sub.name             nombre para figuras/tablas     [str]

El FR-4 es DISPERSIVO: delega en configs.parametros.fr4_er y fr4_tan_delta
(única fuente de verdad de esos números — NO se duplican aquí). Los sustratos
de bajo perdidas (RT/duroid 5880, RO4003C) son prácticamente no dispersivos en
la banda de interés y se modelan con εr y tan δ constantes de datasheet.

Referencias de datasheet:
    Rogers RT/duroid 5880 — εr=2,20 (±0,02), tan δ=0,0009 @ 10 GHz, h=1,575 mm.
    Rogers RO4003C        — εr=3,55, tan δ=0,0027 @ 10 GHz, h=1,524 mm.
    FR-4 (Isola/Shengyi)  — εr≈4,4 @ 1 GHz (dispersivo), tan δ≈0,02.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

from dataclasses import dataclass, field
from typing import Callable

from configs.parametros import fr4_er, fr4_tan_delta, FR4_H_M


@dataclass(frozen=True)
class Substrate:
    """
    Sustrato dieléctrico de microondas con interfaz uniforme.

    Atributos
    ---------
    name       : nombre de presentación (figuras/tablas)
    h          : espesor del dieléctrico [m]
    _er_fn     : función εr(f_hz) — permite modelar dispersión (FR-4)
    _tan_fn    : función tan δ(f_hz)
    er_ref     : εr nominal de referencia (para etiquetas rápidas)
    tan_ref    : tan δ nominal de referencia (para etiquetas rápidas)
    """
    name:    str
    h:       float
    _er_fn:  Callable[[float], float] = field(repr=False)
    _tan_fn: Callable[[float], float] = field(repr=False)
    er_ref:  float = 0.0
    tan_ref: float = 0.0

    def er(self, f_hz: float) -> float:
        """Permitividad relativa εr a la frecuencia f_hz [Hz]."""
        return float(self._er_fn(f_hz))

    def tan_delta(self, f_hz: float) -> float:
        """Tangente de pérdidas tan δ a la frecuencia f_hz [Hz]."""
        return float(self._tan_fn(f_hz))


def _const(value: float) -> Callable[[float], float]:
    """Devuelve una función f(f_hz)->value constante (sustrato no dispersivo)."""
    return lambda _f_hz: value


# ── Catálogo de sustratos ─────────────────────────────────────────────────────
# FR-4: DISPERSIVO — delega en configs.parametros (SSOT). er_ref/tan_ref son solo
# etiquetas @ 1 GHz para tablas; el cálculo físico usa .er(f)/.tan_delta(f).
SUBSTRATES = {
    'FR4': Substrate(
        name='FR-4',
        h=FR4_H_M,
        _er_fn=fr4_er,
        _tan_fn=fr4_tan_delta,
        er_ref=4.4,
        tan_ref=0.02,
    ),
    'RT5880': Substrate(
        name='RT/duroid 5880',
        h=1.575e-3,
        _er_fn=_const(2.2),
        _tan_fn=_const(0.0009),
        er_ref=2.2,
        tan_ref=0.0009,
    ),
    'RO4003C': Substrate(
        name='RO4003C',
        h=1.524e-3,
        _er_fn=_const(3.55),
        _tan_fn=_const(0.0027),
        er_ref=3.55,
        tan_ref=0.0027,
    ),
}


def get_substrate(name: str) -> Substrate:
    """
    Devuelve el objeto Substrate para 'name' ('FR4', 'RT5880', 'RO4003C').

    Acepta también un objeto Substrate ya construido (idempotente), para que las
    clases de antena admitan indistintamente el nombre o el objeto.
    """
    if isinstance(name, Substrate):
        return name
    try:
        return SUBSTRATES[name]
    except KeyError:
        disponibles = ', '.join(SUBSTRATES)
        raise KeyError(f"Sustrato '{name}' no reconocido. Disponibles: {disponibles}.")
