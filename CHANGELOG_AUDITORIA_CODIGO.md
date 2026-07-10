# CHANGELOG — Auditoría de arquitectura del código (2026-07-10)

Auditoría de ingeniería sobre el código/pipeline con el **documento final como SSOT**.
Veredicto: la arquitectura ya se justifica a sí misma (capas correctas). El trabajo fue
**limpieza y alineación**, no reestructuración. Rollback: rama `backup-pre-code-audit`.

## Commits (checkpoints por fase)

| Commit | Fase | Qué |
|---|---|---|
| `c42b9e7` | Baseline | Sistema gráfico unificado de figuras conceptuales (`estilo_figuras.py`, `figuras_conceptuales.py`, C1–C5) |
| `3b2d58d` | A · código muerto | −`experimental/` (10 arch., ~1245 líneas), −`gen_donut*.py` (4), −`smith_chart_data()` (0 llamadores), −PNG obsoleto |
| `d6ccfc6` | B · SSOT color | `generate_artifacts` toma la paleta de `configs.COLORS` (sin duplicar hex); comentario canónicos corregido |
| `394c3dc` | C+D · pipeline | Entry-point único regenera TODO (datos+conceptuales+tablas); −`pyyaml` (no usado) |
| `07b3768` | E · pruebas | +5 smoke tests de figuras conceptuales (51 → 56) |
| `c68eed1` | F · docs | README/NOTICE al día |

## Resultados

- **Menos superficie muerta:** −14 archivos, ~−1360 líneas de código no usado, 0 referencias colgantes.
- **SSOT reforzada:** una sola definición de la paleta; el pipeline no duplica constantes.
- **Reproducibilidad de un comando:** `python _regen/generate_artifacts.py` regenera datos + conceptuales + tablas + verificación (14 artefactos, deltas canónicos ≈ 0).
- **Cobertura alineada:** las 5 figuras nuevas del documento ahora tienen prueba.
- **API intacta:** todo lo que importan `pages/` resuelve; Streamlit no se tocó.
- **56/56 pruebas verdes.**

## Decisiones deliberadamente NO tomadas

1. No reestructurar capas (`configs→core→{simulation,analysis}→{plots,_regen}→pages`): es correcta.
2. No fusionar/partir módulos de `core/` (cada uno posee un dominio claro; `analysis.py` es cohesivo).
3. No tocar `pages/`, `app.py` ni `poster_figures.py` (UI/póster, restringido).
4. No borrar figuras de datos «extra» (alimentan Streamlit/apéndices; no están muertas).
5. No recortar pruebas (son la garantía de reproducibilidad — el aporte).
6. No sacar artefactos generados de git (snapshot de reproducibilidad intencional).
7. No cambiar `WANG2022_FREQS` (2,36 vs banda 2,45): dato externo citado, legítimo.

## Riesgos residuales

- El `estilo_figuras.py` mantiene su propia paleta «paper» (distinta de `configs.COLORS`) — es intencional (dos sistemas: gráficas de datos vs diagramas conceptuales), no deuda.
- El root del proyecto (fuera del repo) tiene un `_regen/` duplicado antiguo — fuera del alcance del repo; no afecta.

## Iteración de unificación total (2026-07-10)

| Commit | Qué |
|---|---|
| `9268dac` | Identidad visual ÚNICA: `estilo.py` (paleta semántica A=oro/B=verde + rcParams sans + helpers) es la fuente única; `generate_artifacts` la consume; corregida la semántica de color (Sierpinski verde→oro). |
| `c1f75b5` | Streamlit en dos niveles: N1 Demostración (4 páginas visuales con figuras del pipeline) + N2 Laboratorio (detalle regrupado). `utils/figuras.py` = fuente gráfica única en la app. |
| `4833037` | Eliminadas 4 páginas superseded por la Demostración; árbol de `acerca.py` y README al día. |

**Fuente gráfica única confirmada:** documento, Streamlit (N1) y póster consumen los mismos PNG de `_regen/out/figuras/`. Un comando (`python _regen/generate_artifacts.py`) regenera las 16 figuras (11 datos + 5 conceptuales) con una identidad. Las figuras de datos del documento se re-embebieron para compartir esa identidad (doc CHECKPOINT_v5). SSOT y 56/56 pruebas intactas.

**Frontera deliberada:** el Nivel 2 (Laboratorio) mantiene gráficas interactivas (plotly) para la *exploración* de parámetros (barridos, sensibilidades) — no son artefactos estáticos y responden a la entrada del usuario; la regla «Streamlit no genera gráficos propios» aplica a las figuras canónicas/estáticas, que sí salen todas del pipeline.
