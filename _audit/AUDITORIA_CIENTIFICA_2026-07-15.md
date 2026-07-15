# Auditoría científica, técnica y de ingeniería — `rectenna_dashboard_st`

**Fecha:** 2026-07-15 · **Alcance:** Fase 13 (informe previo a modificar). Auditoría de re-derivación del núcleo físico, coherencia con el documento v5 y propuesta de reorganización.
**Método:** lectura y re-derivación manual de los 7 módulos de `core/` + `configs/parametros.py`, verificación numérica con el intérprete real (`.venv`), y cruce contra el documento `Calderon_Munera_B_TG_UdeA_APA7_FINAL_13072026_v5.docx`.
**Regla aplicada:** nada se asume correcto por funcionar. Cada resultado se re-derivó.

> **Veredicto global:** el núcleo físico (`lora_budget`, `rectifier`, `flpda`, `matching`) es **dimensionalmente correcto y la cadena canónica cierra numéricamente** (1.335 µW y η_total 0,4023 reproducidos exactamente). Los problemas serios NO están en la cadena principal sino en **módulos periféricos que contradicen o adelantan a la cadena canónica** (tabla de estado del arte, presupuesto de enlace formal) y en **hipótesis físicas que el dashboard no expone con la transparencia que exige el nuevo alcance**.

---

## 1. HALLAZGOS CRÍTICOS

### C1 — Referencia fabricada visible en el dashboard (integridad científica)
**Archivo:** `core/analysis.py:467-480` (`STATE_OF_ART`), renderizada vía `analysis/avanzado.py:132` → páginas.
`STATE_OF_ART` incluye **`Shen et al. (2019), IEEE Access, "Koch fractal dipolo, triple banda"`**. Esta referencia fue **verificada como inexistente y retirada del documento** (auditoría v31). Sigue mostrándose en el dashboard como estado del arte.
- **Verificación:** `Shen` aparece **0 veces** en el documento v5; sí en `analysis.py`.
- **Impacto:** el dashboard cita una fuente fabricada que el documento ya repudió. Riesgo de integridad ante un jurado.
- **Acción:** eliminar la entrada Shen del `STATE_OF_ART`.

### C2 — El presupuesto de enlace del dashboard NO reproduce el valor canónico
**Archivo:** `core/analysis.py:221-295` (`link_budget_table`), usado en `analysis/avanzado.py:84-96` (`run_link_budget`).
La función **omite las pérdidas de polarización (0,5 dB) y de armónicos (0,4 dB)** que sí están en la cadena canónica (`lora_budget.harvested_uw_full`, líneas 239-240).
- **Verificación (ejecutada):** la tabla de link budget del dashboard reporta **P_DC = 1.642,4 µW**, no 1.335,0 µW. La diferencia (0,9 dB → ×1,23) reintroduce **casi exactamente el valor pre-revisión (1.637,6 µW)**.
- **Impacto:** contradicción interna del 23 %. Un jurado que siga el presupuesto de enlace paso a paso obtiene un número distinto (y mayor) que el titular. Rompe la trazabilidad (Fase 8) y la coherencia (Fase 6). Es el hallazgo más grave porque *parece* riguroso.
- **Acción:** añadir las filas de pérdida por polarización y por armónicos a `link_budget_table` (o parametrizarlas), de modo que la última fila dé 1.335,0 µW. Idealmente, `link_budget_table` debería derivar cada eslabón de la MISMA función que la cadena canónica, no reimplementarla.

---

## 2. HALLAZGOS IMPORTANTES

### I1 — El resultado estrella opera en el *clip* de PCE, lejos del punto de validación
- **Dónde:** `rectifier.py:225` (`np.clip(..., 0, 0.85)`); validación en `comparacion.py:54` (`PCE(-10.0, f)`).
- La validación cruzada con Wang (RMSE 15,50 pp) se hace a **Pin = −10 dBm**. El punto canónico entrega **+2,67 dBm** al rectificador — 12 dB más alto, en el régimen donde la PCE está **saturada al tope de 0,85**. Es decir, el 1.335 µW titular depende de un valor de PCE (0,85) que **no está validado experimentalmente**; solo el régimen de baja potencia lo está.
- **Impacto:** la fortaleza de la validación no cubre el punto de operación reportado. Es una limitación real (el documento la declara como limitación L-*, pero el dashboard no la hace visible).
- **Acción:** exponer explícitamente en la página de validación que el punto canónico está en saturación y que la validación es a −10 dBm; mostrar la curva PCE(Pin) marcando ambos puntos.

### I2 — Dos modelos distintos de η_rad para la misma física
- **Dónde:** `antenna.py:229-253` vs `flpda.py:231-250`.
- Misma magnitud (eficiencia de radiación en FR-4), **dos fórmulas y calibraciones distintas**: factor 30 vs 8; `tanδ` constante (0,02) vs dispersivo `fr4_tan_delta(f)`; con/sin `√εr`; clips [0,30–0,85] vs [0,20–0,85].
- **Impacto:** inconsistencia física; el mismo sustrato se modela de dos maneras. Viola "si dos ecuaciones hacen lo mismo, unifícalas".
- **Acción:** un único modelo `eta_rad(f, substrate)` en `configs/` o `core/`, parametrizado, usado por ambas antenas.

### I3 — η_rad es una calibración, no una derivación, y es el driver dominante
- **Dónde:** `flpda.py:231-250`.
- η_rad ≈ 0,60 @550 MHz se obtiene con constantes **ajustadas para caer en el rango de literatura (0,50–0,70)**, no derivadas de primeros principios. Es el parámetro que bajó P_dc de 1.637 a 1.335 y η_total de 0,67 a 0,40.
- **Impacto:** el número más importante del trabajo descansa en una estimación calibrada. Es honesto (mejor que el 0,9952 previo), pero su incertidumbre domina todo el resultado.
- **Acción:** en "Detrás del modelo", presentar η_rad como **la hipótesis clave**, con su rango (0,50–0,70), su origen (literatura FR-4 UHF) y su propagación al resultado (un slider η_rad→P_dc sería pedagógicamente ideal).

### I4 — La directividad es heurística; el rizo es decorativo
- **Dónde:** `flpda.py:150-181` (`gain_dBi`, `directivity_dBi`).
- G0 = 7,5 dBi es una **constante asumida** ("LPDA clásica 7–9 dBi"), con corrección ad-hoc `0,5·log10(N/8)` y un rizo `−0,5·|sin(3·phase)|` **sin base física** (el "3" y el "0,5" son decorativos).
- **Impacto:** la mitad de la ganancia canónica (4,97 = 7,21 directiva − 2,24 por η_rad) es una directividad asumida, no calculada de la geometría. Coherente con "no full-wave", pero el rizo simula una precisión que no existe.
- **Acción:** eliminar el rizo decorativo (o justificarlo); declarar la directividad como valor de referencia de Carrel, no como cálculo.

### I5 — Miniaturización Koch idealizada
- **Dónde:** `flpda.py:47` (`_KOCH_REDUCTION`).
- Se asume que la longitud eléctrica gana el factor geométrico completo `(4/3)^n`, dando reducción física `(3/4)^n = 0,5625` (43,75 %). El Koch real miniaturiza **menos** (la ganancia de longitud eléctrica es incompleta y degrada η_rad).
- **Acción:** declarar como cota superior de miniaturización; citar literatura (Vinoy, Gianvittorio).

### I6 — Tabla de estado del arte sin respaldo documental (Fase 2)
- **Dónde:** `core/analysis.py:396-495`.
- De 7 entradas, solo **Wang y Pinuela** aparecen en el documento. `Sun (2013)`, `Hagerty (2004)`, `Olgun (2011)` y `Shen (2019)` **no están en la tesis** (0 ocurrencias verificadas).
- **Impacto:** el dashboard presenta una comparación que el documento no respalda — excede el alcance del documento (viola el principio "ni más ni menos").
- **Acción:** o se añade la tabla comparativa al documento (con referencias reales verificadas), o se elimina/reduce a las fuentes citadas. Shen se elimina en cualquier caso (C1).

### I7 — Ganancia stale en la fila "Este trabajo" del estado del arte
- **Dónde:** `core/analysis.py:488` (`'gain_dBi': '7.1-7.5'`).
- Es la directividad pre-revisión; la ganancia **realizada** canónica es 4,83–4,97 dBi.
- **Acción:** corregir a `'4.8-5.0'` (realizada) o etiquetar explícitamente "directiva".

### I8 — Monte Carlo reporta media condicional
- **Dónde:** `core/analysis.py:139` (`valid = samples[samples > 0]`).
- Los estadísticos (media 1.511, IC95, etc.) se calculan **excluyendo las realizaciones que fallan cold-start** (P=0). Es una media *condicionada a viabilidad*, no incondicional.
- **Acción:** divulgar explícitamente, o reportar también la fracción de fallos (`n_valid/n_total`, que ya se calcula pero no se destaca).

### I9 — Dualidad de modelos de conversión (PCE) y de cosecha
- **Dónde:** `lora_budget.py` — `pce_uhf()` (tanh, PCE_max 55 %) + `harvested_uw()` vs `rectifier.PCE()` (Shockley) + `harvested_uw_full()`.
- Coexisten dos modelos de PCE y dos funciones de cosecha. El canónico usa las segundas; las primeras (tanh) son "conservadoras para diseño rápido".
- **Impacto:** dos verdades para la misma magnitud confunden y contradicen el objetivo de transparencia.
- **Acción:** verificar si `pce_uhf`/`harvested_uw` se usan en alguna página; si son solo-display, etiquetarlas claramente como "estimación conservadora alternativa"; si están muertas, eliminarlas (ver Fase 9).

### I10 — Monte Carlo: nº de muestras y semilla redundante
- **Dónde:** `analysis/avanzado.py:48-65`.
- `run_monte_carlo` usa `n_samples=2000` por defecto, mientras la corrección documentada fue **10.000**. Además `np.random.seed(MC_SEED)` (línea 64) es redundante: `monte_carlo_pdc` ya usa `np.random.default_rng(42)` internamente.
- **Acción:** unificar a 10.000 (o pasar el valor desde la página), eliminar la semilla legacy redundante.

---

## 3. HALLAZGOS MENORES

- **M1 — FSPL duplicado.** `link_budget_table` (`analysis.py:234-236`) reimplementa FSPL con `c0=3e8` **hardcodeado**, en vez de usar `lora_budget.fspl_dB` y `configs.C0`.
- **M2 — Sustrato tratado de 3 formas.** `flpda.py` usa `tanδ=0,02` constante; `antenna.py`/`parametros.py` usan `fr4_tan_delta(f)` dispersivo; `antenna.get_er` (`antenna.py:116`) duplica `parametros.fr4_er`.
- **M3 — Números mágicos sin documentar** en los modelos de impedancia: `flpda.py` (Q=4,5; peso `(δ·8)²`; `0,97^k`; R_dip=73); `antenna.py` (R=60; `0,85^k`; `L_bg=45/ω0`; Rbg=8; Q=8,5).
- **M4 — Defaults stale.** `received_power_dBm` default `ant_gain_dBi=4.9` (vs canónico 4,97; `lora_budget.py:133`); `harvested_uw` default `7.5` y docstrings citan 7,5 dBi (valor pre-revisión; `lora_budget.py:39-44,167`).
- **M5 — Comentario físico impreciso.** `flpda.py:202`: R_dip=73 Ω rotulado "medio dipolo"; 73 Ω es la resistencia de radiación del dipolo **λ/2 completo**.

### Fase 9 — Higiene de código (barrido verificado con grep en todo el repo)

**Código muerto (borrado seguro, 0 llamadas confirmadas):**
- `utils/glosario.py`: `ficha_grafica()` (:102), `aporta()` (:129)
- `utils/pagina.py`: `correspondencia()` (:118), `impacto_parametros()` (:57)
- `core/antenna.py`: `eta_sys()` (:329), `IEEE_RCPARAMS` (:46)
- `configs/parametros.py`: `WANG2022_FREQS_GHZ/_PCE_PCT/_S11_DB/_GAIN_DBI` (:144-147) — además duplican el dict `WANG2022` de `comparacion.py`
- `plots/charts.py`: `fig_validacion_wang()` (:123, reemplazada por `_fig_wang_scatter_with_errors`); y **bloque muerto dentro de `fig_tornado()` (:214-233)** — construye una figura `fig` completa y luego retorna `fig2`, descartándola
- `_regen/estilo.py`: `caption()` (:116), `ic_pin()` (:293); `_regen/figuras_conceptuales.py`: `_hflow()` (:45)

**Imports sin usar:** solo en `_regen/` — `estilo.py:18` (`numpy`), `:22` (`PathPatch`), `:23` (`Path`); `figuras_conceptuales.py:31` (`CANONICAL`). El resto del repo (core, pages, etc.) tiene todos sus imports en uso.

**Solo usados por tests (no muertos, pero señalar):** `pce_uhf()` y `harvested_uw()` (`lora_budget.py:146,166`) y `directivity_dBi()` (`flpda.py:170`) — corrobora I9.

**Duplicación (SSOT) — corrobora y extiende M1/M2/I2:**
- `RF_UHF` (`parametros.py:97`) ≡ `RF_SOURCES_UHF` (`lora_budget.py:73`): dos fuentes de verdad para el mismo dato (solo cambian colores).
- Γ/S11 con cuerpo idéntico en `antenna.S11_dB`, `flpda.S11_dB` y `matching._gamma`.
- Patrón VSWR→|Γ| repetido en 6 sitios; dBm→W en 3; η_match en 3.
- Constantes hardcodeadas que existen en `configs/`: `3e8` (antena, flpda, analysis), `50.0` Z0 (antena, flpda, matching), `1300.0` R_load (rectifier + 7 sitios), `72.15`, `0.02`, `4.4`, `300.0`, `259.25`.

**Sin archivos huérfanos** (las 14 páginas de `app.py` coinciden con `pages/`; los scripts `_regen/*` son entradas de pipeline).

**Figuras generadas pero no consumidas por la app** (7 PNG en `_regen/out/figuras/`: `Fig12_geom_sierpinski`, `Fig13_sierpinski_iteraciones`, `Fig14_koch_geometria`, `Fig15_flpda_completa`, `FigC6_koch_resonancia`, `FigC7_fractal_a_iot`) — son deliverables del documento/póster, no del dashboard. `assets/` y `data/` solo tienen `.gitkeep`.

---

## 4. PROPUESTA DE REORGANIZACIÓN (Fases 3–8, 10)

**Identidad:** dejar la estética de "software técnico" (paneles de métricas) por una **narrativa guiada tipo póster**: cada pantalla responde UNA pregunta y enlaza a la siguiente. Fondo limpio, una idea por vista, la matemática disponible en capas expandibles (no oculta, no impuesta).

**Navegación en 7 capas, cada resultado trazable hacia atrás:**

| Nivel | Pregunta que responde | Contenido |
|---|---|---|
| 1 · Historia | ¿Qué problema existe y por qué? | Baterías→RFEH→IoT; el caso colombiano. Sin números todavía. |
| 2 · Resultados | ¿Qué se obtuvo? | Los 3–4 números titulares (1.335 µW, 174 m, 40,23 %) **con interpretación física**, cada uno enlazando a su ecuación. |
| 3 · Modelo | ¿Cómo funciona la rectena? | Cadena RF→DC etapa por etapa (antena→adaptación→rectificador→PMIC→IoT), con hipótesis de cada eslabón. |
| 4 · Ecuaciones | ¿Con qué matemática? | **Fichas de ecuación** (ver abajo). |
| 5 · Código | ¿Cómo se resolvió? | Bloque expandible con la implementación real + resultado + test que lo bloquea. |
| 6 · Constantes | ¿Con qué valores y de dónde? | "Detrás del modelo": diccionario de constantes y variables (ver Fase 4/5). |
| 7 · Validación | ¿Cómo sé que es creíble? | Wang (a −10 dBm, con la limitación I1 visible), Carrel, límites físicos, Monte Carlo con su media condicional (I8). |

**Ficha de ecuación (Nivel 4), una por cada ecuación del documento:** ecuación renderizada · significado físico · variables y unidades · supuestos · limitaciones · referencia bibliográfica · capítulo del documento · archivo Python + línea. Ejemplo para Friis: `P_r = EIRP − FSPL − L_urb − L_pol − L_arm + G_r` → §4.3.1 doc → `lora_budget.py:239`.

**Cadena de trazabilidad (Nivel 2→6, Fase 8):** cada número titular despliega `resultado → ecuación → variables → constantes → dato/fuente → archivo:línea → test`. Ejemplo: `1.335 µW → P_DC=P_in·η_mm·η_imn·PCE·η_pmic → parametros.CANONICAL → test_regression_canonical.py:136`.

**"Detrás del modelo" (Fases 4–5), sección nueva:** diccionario navegable de **constantes** (c, ε₀, μ₀, η₀, k_B, q, V_t, εr(f), tanδ(f), Z0, EIRP, V_cs…) y **variables** (P_in, P_dc, η_rad, η_mm, η_imn, PCE, η_pmic, Za, Γ, S11, G, FSPL, d, f…), cada una con: qué representa · origen · unidades · dónde/en qué ecuaciones se usa. Es la pieza que convierte el dashboard en "laboratorio abierto".

**Consolidación de páginas:** hoy hay 14 páginas + 4 `demo_*` sueltas. Varias son "aplicación comercial" (métricas por llenar). Propuesta: mapear las 14 a los 7 niveles, fusionar las `demo_*` (probablemente muertas, ver Fase 9), y que ninguna página exista si no responde una pregunta en una frase (Fase 10).

**Rigor de lenguaje (Fase 12):** barrer y eliminar "demuestra/prueba/garantiza/aporte/revoluciona/pipeline/framework/estado del arte" en textos de cara al usuario; mantener el alcance de trabajo de grado.

---

## 5. LISTA EXACTA DE CAMBIOS PROPUESTOS

| # | Archivo · función | Cambio | Justificación | Impacto |
|---|---|---|---|---|
| C1 | `core/analysis.py:467-480` `STATE_OF_ART` | Eliminar entrada `Shen et al. (2019)` | Referencia fabricada, ya retirada del documento | Integridad; el dashboard deja de citar una fuente inexistente |
| C2 | `core/analysis.py:221-295` `link_budget_table` | Añadir filas de pérdida de polarización (0,5 dB) y armónicos (0,4 dB); o derivar de `harvested_uw_full` | Hoy da 1.642 µW ≠ 1.335 canónico | La tabla de enlace reproduce el titular; se elimina la contradicción del 23 % |
| I1 | `pages/validacion.py` (UI) | Marcar que el punto canónico opera en saturación de PCE y que la validación es a −10 dBm | La validación no cubre el punto de operación | Transparencia; el jurado ve la limitación real |
| I2 | `antenna.py:229` + `flpda.py:231` | Unificar en un único `eta_rad(f, substrate)` | Misma física, dos modelos | Coherencia; una sola verdad para η_rad |
| I3 | "Detrás del modelo" (nuevo) | Exponer η_rad como hipótesis clave con rango y propagación | Es el driver dominante | Pedagogía y honestidad |
| I4 | `flpda.py:166,180` | Eliminar rizo `0,5·|sin(3·phase)|` o justificarlo | Decorativo, simula precisión inexistente | Rigor |
| I6 | `core/analysis.py:396-495` + documento | Recortar `STATE_OF_ART` a fuentes citadas en la tesis, o añadir la tabla al documento | Sin respaldo documental | Coherencia doc↔dashboard |
| I7 | `core/analysis.py:488` | `'7.1-7.5'` → `'4.8-5.0'` (realizada) | Valor stale pre-revisión | Coherencia con el SSOT |
| I8 | `core/analysis.py:143-156` (UI) | Divulgar media condicional; destacar `n_valid/n_total` | Sesgo por exclusión de fallos | Rigor estadístico |
| I9 | `lora_budget.py:146-201` | Etiquetar o eliminar `pce_uhf`/`harvested_uw` según uso real | Dualidad de PCE | Claridad; menos superficie de confusión |
| I10 | `analysis/avanzado.py:48-65` | `n_samples` 2000→10000; quitar `np.random.seed` redundante | Coherencia con corrección documentada | Reproducibilidad |
| M1 | `core/analysis.py:234-236` | Usar `fspl_dB` y `configs.C0` | FSPL duplicado, c0 hardcodeado | DRY / SSOT |
| M2 | `flpda.py:73` | Usar `fr4_tan_delta(f)` dispersivo como `antenna.py` | Sustrato inconsistente | Coherencia física |
| M4 | `lora_budget.py:133,167` | Defaults 4,9/7,5 → 4,97 / documentar | Valores pre-revisión | Evita confusión |
| M5 | `flpda.py:202` | Corregir comentario "medio dipolo" | Impreciso | Claridad |

---

**Nota de método:** este informe se emitió primero (Fase 13). La adenda abajo registra lo ya ejecutado.

---

## ADENDA — Cambios aplicados (2026-07-15)

Ejecutados y verificados (56/56 tests, todos los módulos importan, canónicos intactos):

| Hallazgo | Acción aplicada | Estado |
|---|---|---|
| C1 | Eliminada referencia fabricada `Shen et al. (2019)` de `STATE_OF_ART` | ✅ |
| C2 | `link_budget_table` ahora incluye pérdidas polarización+armónicos y reutiliza `fspl_dB` → reproduce **1.335,0 µW** (antes 1.642) | ✅ |
| I7 | `STATE_OF_ART` "Este trabajo" ganancia `7.1-7.5`→`4.8-5.0` (realizada) | ✅ |
| I10 | `run_monte_carlo` default 2000→10000 (coincide con el documento: media 1.510≈1.511); eliminada semilla legacy redundante | ✅ |
| M1 | `link_budget_table` usa `fspl_dB`/`C0` en vez de FSPL inline con `c0=3e8` | ✅ |
| M4 | `received_power_dBm` default 4.9→4.97 dBi | ✅ |
| M5 | Comentario "medio dipolo λ/2"→"un dipolo λ/2" | ✅ |
| Fase 9 | Eliminados: `WANG2022_*` (configs, duplicado+muerto), `IEEE_RCPARAMS`, `eta_sys` (antenna), bloque muerto en `fig_tornado` | ✅ |
| Fases 4-8 | **Nueva página `Detrás del modelo`** (`pages/detras_del_modelo.py`): diccionario de constantes+variables (valores en vivo del SSOT), 7 fichas de ecuación con referencia+§documento+archivo:línea, y cadena de trazabilidad de 1.335 µW. Registrada en `app.py`. | ✅ |

**Documento:** verificado — **no requiere cambios**. Los defectos C1/C2 y demás son exclusivos del dashboard. El documento v5 ya incluye las pérdidas pol/armónicos en su presupuesto de enlace, no contiene la referencia Shen ni la tabla de estado del arte, y sus valores de Monte Carlo corresponden a n=10.000. La única corrección documental (frontera cold-start 1 200→1 013 m) se aplicó en la ronda anterior. Por tanto **no se creó copia nueva**.

**Deliberadamente NO modificado (rompería el canónico congelado en el documento evaluado):**
- I4 (rizo de ganancia) — el término `sin(3·phase)` es *load-bearing* del valor canónico 4,97 dBi; quitarlo cambiaría el SSOT y desincronizaría el documento. Se documentó en su lugar.
- I2 (unificar los dos η_rad) — las constantes de `flpda.eta_rad` están calibradas para dar exactamente 0,5972 @550 MHz; alterarlas cambiaría P_DC. Se documentó la diferencia intencional.
- M2 (tanδ dispersivo en flpda) — igual: rompería η_rad canónico.
- I1/I3/I8 (limitaciones de PCE, η_rad calibrada, media condicional MC) — son hipótesis del modelo, no bugs; se **expusieron con transparencia** en la página `Detrás del modelo` en vez de "corregirse".

**Pendiente (fase dedicada):** reorganización visual completa de las 14 páginas al flujo narrativo de 7 niveles (§4). La página `Detrás del modelo` es la primera pieza (Niveles 4-6); el resto es un rediseño de UX que conviene hacer en una pasada enfocada, no mezclado con estos arreglos de corrección.
