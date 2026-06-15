"""
utils/glosario.py — Patrones reutilizables de comprensión (guía UX, Oleada A).

Resuelve los problemas de interpretación con componentes de **fuente única**, no
con párrafos repetidos por pantalla. Respeta UX5 (economía de texto) y UX6 (no
ocultar lo esencial):

- Lo ESENCIAL (qué evalúa, criterio, conclusión, conexión con P_DC, interpretación
  de un KPI) va **visible** (`ficha_grafica`, `metrica`).
- La PROFUNDIDAD (definiciones completas) va **colapsable** y por página
  (`glosario_pagina`), nunca un popover global.

Las definiciones y criterios viven una sola vez en `GLOSARIO` / `CRITERIOS`.
"""

from __future__ import annotations

import streamlit as st


# ── Definiciones canónicas (una sola fuente) ────────────────────────────────
GLOSARIO: dict[str, str] = {
    "S11": "Coeficiente de reflexión: qué fracción de la potencia que llega a la antena "
           "se refleja en lugar de entrar. En dB, más negativo = mejor adaptación.",
    "adaptación": "Qué tan bien acopladas están dos etapas (antena–rectificador). Buena "
                  "adaptación = poca potencia reflejada = más energía aprovechada.",
    "ganancia": "Ganancia realizada (G), en dBi: cuánto concentra la antena la energía en "
                "la dirección útil. Ya incluye la eficiencia de radiación η_rad.",
    "impedancia": "Oposición compleja (parte real + reactiva) que la antena presenta a la "
                  "señal; determina cuánta potencia logra entrar al rectificador.",
    "η_total": "Eficiencia global del sistema: fracción de la energía captada que se "
               "conserva como potencia útil. Es el producto de las eficiencias de etapa.",
    "PCE": "Power Conversion Efficiency: eficiencia con que el rectificador convierte la "
           "señal de radiofrecuencia en corriente continua.",
    "P_DC": "Potencia continua útil que llega al nodo IoT tras toda la cadena RF→DC. Es el "
            "resultado central del proyecto.",
    "P_in": "Potencia de radiofrecuencia disponible en la antena; punto de partida de la "
            "cadena de conversión.",
    "IMN": "Red de adaptación de impedancias: acopla la antena con el rectificador para "
           "perder lo menos posible por desadaptación.",
    "RMSE": "Raíz del error cuadrático medio: error promedio del modelo frente a los datos "
            "de referencia (Wang 2022), en puntos porcentuales (pp).",
    "sesgo": "Error medio con signo: si es positivo, el modelo sobreestima en promedio.",
    "incertidumbre": "Rango en el que varía el resultado cuando el entorno (EIRP, "
                     "distancia, frecuencia) cambia respecto al caso de referencia.",
    "EIRP": "Potencia isotrópica radiada equivalente de la fuente: cuánta potencia emite la "
            "torre en la dirección útil.",
    "FSPL": "Pérdida de propagación en espacio libre: la atenuación natural de la onda al "
            "repartirse en una superficie cada vez mayor con la distancia.",
}

# ── Criterios visuales canónicos (una sola fuente) ──────────────────────────
CRITERIOS: dict[str, str] = {
    "−10 dB": "criterio convencional de adaptación aceptable: por debajo, la antena refleja "
              "menos del 10 % de la potencia incidente.",
    "banda de diseño": "el tramo de frecuencia para el que se diseñó la antena; dentro de "
                       "él deben cumplirse los criterios de adaptación y ganancia.",
    "V_cs 130 mV": "umbral de arranque en frío del PMIC BQ25504: por debajo, el gestor de "
                   "energía no logra encender el nodo.",
    "V_min cut-off": "tensión mínima de operación: si el supercondensador cae por debajo, "
                     "el nodo se apaga entre transmisiones.",
    "duty 1 %": "tope regulatorio del 1 % de ciclo de trabajo en la banda ISM 915 MHz "
                "(compatible ETSI).",
    "PCE cap 85 %": "techo de PCE del modelo: ningún doblador Greinacher reportado en la "
                    "literatura supera ~85 % en este rango de potencia.",
    "Q_L 40": "factor de calidad típico de un inductor SMD 0402/0603; valor de diseño del "
              "proyecto.",
}


# ── Glosario por página (colapsable, solo términos relevantes) ──────────────
def glosario_pagina(*claves: str):
    """Popover '📖 Definiciones' con SOLO los términos relevantes a esta página.
    Definición completa = profundidad colapsable (UX6). Fuente única: GLOSARIO."""
    defs = [(k, GLOSARIO[k]) for k in claves if k in GLOSARIO]
    if not defs:
        return
    with st.popover(":material/menu_book: Definiciones"):
        for k, v in defs:
            st.markdown(f"**{k}** — {v}")


# ── Ficha de gráfica: los esenciales, VISIBLES y compactos ──────────────────
def ficha_grafica(*, evalua: str, concluye: str, criterio: str | None = None,
                  contribuye: str | None = None):
    """Bloque VISIBLE (UX6) con lo mínimo para interpretar una gráfica:
        - Qué evalúa (y por qué existe).
        - Criterio principal (clave de CRITERIOS o texto libre).
        - Conclusión del trabajo de grado.
        - Cómo contribuye al resultado final (cadena hasta P_DC).
    Líneas cortas, no un bloque largo. Llamar justo debajo de la gráfica."""
    st.caption(f":material/quiz: **Qué evalúa:** {evalua}")
    if criterio:
        txt = CRITERIOS.get(criterio, criterio)
        st.caption(f":material/straighten: **Criterio:** {txt}")
    st.caption(f":material/lightbulb: **Concluye:** {concluye}")
    if contribuye:
        st.caption(f":material/link: **Aporta al resultado final:** {contribuye}")


# ── Criterio visual VISIBLE (1 línea, fuente única) ─────────────────────────
def criterio(clave: str):
    """Caption VISIBLE de 1 línea que explica un criterio/umbral.
    `clave` es una entrada de CRITERIOS (o texto libre). Para criterios sueltos
    que aparecen fuera de una `ficha_grafica` (líneas de referencia, cut-offs)."""
    txt = CRITERIOS.get(clave, clave)
    st.caption(f":material/straighten: **{clave}:** {txt}")


# ── Conexión con el resultado final VISIBLE (1 línea) ───────────────────────
def aporta(texto: str):
    """Línea VISIBLE que conecta la sección con el resultado final (cadena hasta
    P_DC). 1–2 frases, no un bloque. Usar cuando no hay `ficha_grafica`."""
    st.caption(f":material/link: **Aporta al resultado final:** {texto}")


# ── KPI con interpretación VISIBLE (una línea) ──────────────────────────────
def metrica(label: str, value: str, *, interpretacion: str,
            ayuda: str | None = None, border: bool = True):
    """st.metric con la interpretación en el delta VISIBLE (UX6: no solo hover).
    `interpretacion` = una línea: alto/bajo o qué concluye. `ayuda` = detalle
    ampliado opcional (colapsable, en el tooltip)."""
    st.metric(label, value, delta=interpretacion, delta_color="off",
              help=ayuda, border=border)
