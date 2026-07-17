# Fase 0 — Factibilidad del rediseño multibanda (Sierpinski)

**Fecha:** 2026-07-17 · **Autor del análisis:** spike `_regen/_spike_multibanda.py`
**Pregunta:** ¿hasta dónde se puede llevar la cobertura multibanda del Sierpinski
sin romper la fidelidad del modelo analítico (no full-wave)?

## Resultado del spike (7 bandas objetivo BANDS_A)

| Ruta | Arquitectura | Bandas útiles | η por banda |
|------|--------------|:-------------:|-------------|
| **Baseline** | Modular, antena referida a 50 Ω (S11 antena sola) | **1/7** | solo 5G-3,5 (−17,4 dB) |
| **Ruta A** | Afinar el peine (barrer f₀ y factor de escala) | **3/7** | GSM1800, WiFi-2,4, 5G-2,6 |
| **Ruta B** | Rectena integrada, co-diseño conjugado Za→Z_diodo | **6/7** | η_match 0,43–0,74 |

Detalle Ruta B (η_match rigurosa, red L con Q finito, potencia entregada real):

```
GSM1800  1.84 GHz  0.52   LTE      2.04 GHz  0.43  (única < 0.5)
WiFi_2.4 2.45 GHz  0.57   5G_2.6   2.54 GHz  0.57
5G_3.5   3.30 GHz  0.61   5G_4.9   4.76 GHz  0.72
WiFi_5.8 5.80 GHz  0.74
```

## Interpretación (el hallazgo clave)

El **"1/7" original es en gran parte un artefacto de modelado**, no un límite físico
del fractal. El modelo actual penaliza a la antena con η_mm = 1−|Γ|² **referida a
50 Ω** (la antena "sola" debe presentar ~50 Ω), y por separado adapta 50 Ω→diodo.
Eso es correcto para una arquitectura **modular con línea de 50 Ω** (conectorizada),
pero **no** para una rectena **integrada**, donde la antena se conecta directamente
a la red de adaptación y al diodo. En la rectena integrada no hay interfaz de 50 Ω:
se hace **adaptación conjugada Za(f)→Z_diodo** en cada banda, y la "reflexión de la
antena" deja de ser una pérdida. Solo queda la pérdida por Q finito de la red.

Con esa arquitectura (la estándar en cosechadores RF reales), **6 de 7 bandas**
entregan η_match ≥ 0,5. La eficiencia por banda (0,43–0,74) es menor que el acople
limpio monobanda de la dirigida — coherente con la reactancia grande del diodo
(−200 a −600 Ω) que hay que sintonizar con componentes de Q finito.

## Decisión de ruta

**Ruta B (co-diseño conjugado integrado) como eje, con Ruta A como afinamiento
complementario del peine.** Es la ruta físicamente honesta y la que convierte el
resultado de "el fractal no sirve" en "el fractal sirve bajo una arquitectura
integrada, con eficiencia modesta por banda".

### Caveats que deben quedar declarados en el documento (integridad científica)
1. **Bode-Fano / ancho de banda:** una sola red pasiva no adapta las 6 bandas a la
   vez. La arquitectura implícita es un **rectificador multibanda** (una rama
   adaptada por banda, combinada en DC) o una red reconfigurable — arquitectura
   conocida en la literatura de RF harvesting. Hay que modelarla y nombrarla así.
2. **η_rad de FR-4 (0,32–0,61)** sigue aplicando encima → la eficiencia total por
   banda es modesta y la potencia total cosechada en un entorno urbano disperso es
   pequeña (decenas de µW). Esto **exige** el criterio energía-asistido (ciclo de
   trabajo bajo + batería/supercap tampón) para que el caso multibanda sea viable.
3. El número η_match del spike es una estimación de factibilidad; los canónicos
   finales salen de implementar el co-diseño conjugado en `core/matching.py` +
   `core/lora_budget.py` y regenerar (Fase 4–5).

## Encaje con el marco de dos modos
- **Modo 1 (sin batería, autonomía continua):** FLPDA dirigida, fuente fuerte y
  conocida (torre TDT), banda estrecha, arquitectura de 50 Ω. Ya validado (1.335 µW).
- **Modo 2 (energía-asistido):** Sierpinski multibanda integrada, entorno urbano
  denso con fuentes dispersas, ciclo de trabajo bajo, batería tampón que se rellena.
  Este spike lo habilita cuantitativamente.
