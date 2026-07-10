# AUDITORÍA DE ARQUITECTURA DEL CÓDIGO — Plan maestro y ejecución
**Fecha:** 2026-07-10 · **SSOT del proyecto:** el documento final (`...FINAL_09072026`). El código debe contar la misma historia: **la metodología es el aporte; el caso colombiano la demuestra.**

## Veredicto de la Fase 0 (sin complacencia)

Estudié el sistema como si fuera a construirlo hoy desde cero. **Lo construiría casi igual.** La arquitectura ya está bien estratificada y cada capa justifica su existencia:

```
configs/         SSOT (parámetros, canónicos, estilo)
   ↓
core/            modelos físicos puros (antenna·flpda·rectifier·matching·comparacion·lora_budget·analysis)
   ↓
simulation/      runners de escenario (A/B) → dicts
analysis/        wrappers de análisis avanzado (avanzado envuelve core/analysis; sensibilidad para UI)
   ↓
plots/  _regen/  visualización UI (plotly)  ·  pipeline de artefactos (figuras/tablas del documento)
   ↓
pages/           UI Streamlit (NO se toca en esta fase)
```

`analysis/avanzado.py` **envuelve** `core/analysis.py` sin duplicar lógica; `simulation/` produce dicts serializables; el pipeline consume modelos, no reimplementa. No hay responsabilidades mezcladas graves, ni módulos monolíticos, ni capas inventadas. **Por tanto esto NO es una reestructuración: es una limpieza y una alineación.** Manufacturar cambios estructurales aquí sería justo lo que el usuario pidió no hacer («no optimizar por optimizar»).

## Hallazgos reales (lo que sí justifica un cambio)

| # | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| H1 | **Código muerto trackeado**: `experimental/` (10 archivos, ~1245 líneas de prototipos) | `git ls-files` lo lista; ningún módulo lo importa | Eliminar |
| H2 | **Scripts sueltos muertos**: `gen_donut*.py` (4 archivos) | untracked, no importados, iteraciones de dónut del póster | Eliminar |
| H3 | **Función muerta**: `core/analysis.py::smith_chart_data()` | único «uso» es su propio docstring; 0 llamadores, 0 tests | Eliminar |
| H4 | **Artefacto obsoleto**: `_regen/out/figuras/FigC3_cadena_fisica.png` | quedó de una versión previa (renombrada a `FigC3_anatomia_rectena.png`) | Eliminar |
| H5 | **SSOT de color duplicada**: `_regen/generate_artifacts.py` fija `C_AZUL="#0077BB"…` duplicando `configs.COLORS` | 13+ usos de constantes locales | Importar de `configs.COLORS` |
| H6 | **Comentario obsoleto**: `parametros.py` cita `rectenna_platform/config/variables.yaml` (externo, defunct) | 1 comentario | Reescribir: el SSOT es este archivo |
| H7 | **Dependencia innecesaria**: `pyyaml` en requirements | `yaml` no se importa en ningún módulo | Quitar de requirements |
| H8 | **Pipeline desalineado con el documento nuevo**: los generadores conceptuales (`figuras_conceptuales.py`) viven aparte del entry-point (`generate_artifacts.py`) | dos comandos separados | Un solo comando regenera TODO el material del documento |
| H9 | **Cobertura**: los artefactos nuevos (5 figuras conceptuales) no tienen prueba | no hay smoke test del pipeline | Añadir smoke test |

## Sobre las 51 pruebas (cuestionadas explícitamente)

Las leí una por una. **Ninguna sobra.** `test_regression_canonical.py` (11) bloquea cada valor canónico (SMS7630, f_c, diseño/ganancia FLPDA, FSPL, P_in, cadena de potencia, RMSE Wang, resonancias Sierpinski, clip PCE) — es la **garantía de reproducibilidad** que sostiene los números del documento. `test_models.py` (~40, en 7 clases) valida cada modelo físico. No hay redundancia dañina ni pruebas heredadas de módulos difuntos. **Conservo las 51 y añado 1** (smoke del pipeline, H9). Reducir por reducir debilitaría la reproducibilidad, que es el aporte.

## Plan de ejecución (orden óptimo, con checkpoint git por fase)

- **Fase A — Muerte al código muerto** (H1–H4): eliminar `experimental/`, `gen_donut*`, `smith_chart_data`, PNG obsoleto. Verificar imports + tests.
- **Fase B — SSOT de color** (H5, H6): `generate_artifacts` importa `configs.COLORS`; corregir comentario. Regenerar artefactos idénticos (verificación byte-diferencial de valores, no de píxeles).
- **Fase C — Higiene de dependencias** (H7): quitar `pyyaml`.
- **Fase D — Pipeline unificado** (H8): un runner regenera datos + conceptuales.
- **Fase E — Prueba nueva** (H9): smoke test del pipeline conceptual.
- **Fase F — Auditoría final + push**: suite completa verde, import-check de la API que consume Streamlit, checkpoint, changelog, commit y push.

Cada fase: analizar → modificar → verificar → pytest → commit (checkpoint). Rollback = rama `backup-pre-code-audit` + historial git.

## Decisiones deliberadamente NO tomadas

1. **No reestructurar capas** — la estratificación es correcta; cambiarla sería riesgo sin beneficio.
2. **No fusionar ni partir módulos de `core/`** — cada uno posee un dominio claro y un tamaño razonable; `analysis.py` (552 líneas) es cohesivo (todo es «análisis»).
3. **No tocar `pages/` ni `app.py`** — UI Streamlit, restringido; además preservo la API pública que importan.
4. **No tocar `poster_figures.py`** — póster, restringido.
5. **No eliminar figuras de datos «extra»** (fig02/04/06/07/08) — no están muertas: alimentan Streamlit y los apéndices.
6. **No recortar pruebas** — son la garantía de reproducibilidad.
7. **No sacar los artefactos generados del git** — snapshot de reproducibilidad intencional.
8. **No cambiar `WANG2022_FREQS` (2,36) frente a `BANDS_A` (2,45)** — es dato externo citado, legítimamente distinto del centro de banda.
