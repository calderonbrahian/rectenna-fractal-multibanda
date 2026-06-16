# Informe de auditoría — Stage 1 (artefactos)

**Fecha:** 2026-06-15 · **Alcance:** verificación del modelo + regeneración de figuras/tablas desde el código actual + auditoría de la app. **No** se tocó `core/`, `configs/parametros.py` ni el documento Word.

---

## 1. Verificación del modelo (¿es confiable la "verdad" actual?)

- **51/51 tests de regresión PASAN** → el `core` reproduce los valores canónicos auditados (2026-05-28).
- Identidades canónicas recomputadas en vivo (`verificacion.json`):

| Magnitud | Modelo | Canónico | Δ |
|---|---|---|---|
| S₁₁ @ 550 MHz | −18,158 dB | −18,16 dB | +0,002 |
| Ganancia @ 550 MHz | 7,0997 dBi | 7,10 dBi | −0,000 |
| η_total (FOM 5 factores) | 0,6715 | 0,6715 | 0,000 |
| P_DC (identidad 4 factores) | 1637,58 µW | 1637,6 µW | −0,018 |

**Conclusión:** el modelo vigente es la referencia confiable. Las figuras del documento que no coinciden con la app son **renders desactualizados**, no errores del modelo actual.

---

## 2. Hallazgos de integridad (lo que la verificación destapó)

### 🔴 F1 — Inconsistencia del RMSE de Wang en la app (drift del wrapper, no del core)

El RMSE de validación vs Wang et al. (2022) se calcula de **dos formas distintas** según quién llame:

| Vía | Llamada | RMSE | Coherente con |
|---|---|---|---|
| **Documento / test / canónico** | `validate_wang2022(rect, matching_net=None)` | **15,50 pp** | §4.5, T11, Fig 11, `CANONICAL['RMSE_wang']`, `test_validacion_wang2022_rmse`, y el *caveat* de la app ("adaptación ideal") |
| **App (página Validación)** | `run_validacion_wang()` → `validate_wang2022(rect, matching_net=imn)` | **22,68 pp** | nada — contradice el texto de su propia página |

- Archivo del drift: `analysis/sensibilidad.py:88` (pasa `matching_net=imn`).
- Efecto visible: en `pages/validacion.py` el **KPI "RMSE" muestra 22,68 pp** (vía `metrica(res['RMSE'])`) mientras el `como_leer` y el `_ref` dicen **15,50 pp**. La página se contradice.
- **Correcto = 15,50 pp** (metodología documentada: adaptación ideal). La Fig 11 y T11 regeneradas usan esa metodología.
- **Acción recomendada (capa app, NO core):** en `run_validacion_wang` pasar `matching_net=None` para que app = documento = 15,50 pp. *(Pendiente de tu visto bueno: cambia un número visible.)*

### 🟠 F2 — Media de Monte Carlo por encima de la base (Fig 9)

- Con semilla fija, la media MC de P_DC = **1831 µW**, ~12 % por encima de la base determinista **1637,6 µW**. No es azar: es la asimetría de propagar incertidumbre de EIRP (normal en dBm → asimétrica en potencia lineal).
- `core/analysis.monte_carlo_pdc` **no fija semilla** → la figura no era reproducible. En la regeneración se fijó `seed=42`.
- **A contrastar con el docx:** si el texto/figura de la tesis presenta la media MC ≈ base, hay que reconciliar la redacción (la media está legítimamente desplazada).

### 🟡 F3 — Figuras del documento desactualizadas respecto al modelo

- Confirmado para **Fig 3** (S₁₁ FLPDA): el docx muestra un trazo suave con joroba a −10 dB; el modelo auditado da una curva plana ≈ −15…−18 dB (cobertura continua, físicamente más coherente con una LPDA). Probable para Fig 1, 2, 6, etc.
- Las 11 figuras regeneradas (`out/figuras/`) salen del modelo actual → al insertarlas, **docx = app**.

---

## 3. Figuras regeneradas (11/11) — `out/figuras/`

| Fig | Archivo | Fuente de datos | Valor clave |
|---|---|---|---|
| 1 | Fig01_S11_Sierpinski.png | `run_sweep_freq` | S₁₁ min −22,6 dB |
| 2 | Fig02_eta_banda_A.png | `run_bandas` | PCE máx 28,8 % |
| 3 | Fig03_S11_FLPDA.png | `run_sweep_freq_b` | S₁₁ en banda < −10 dB en TODA la banda (máx −14,2) |
| 4 | Fig04_geometria_FLPDA.png | `run_geometry_b` | N=8 · boom 50 cm · −43,8 % Koch |
| 5 | Fig05_cascada_RFDC.png | `CANONICAL` | η_total 0,6715 |
| 6 | Fig06_PDC_distancia.png | `run_harvested_vs_dist` | 4 fuentes, 50–2000 m |
| 7 | Fig07_Tciclo_distancia.png | derivado (E_ciclo) | T≈156 s @100 m (canónico 158,3) |
| 8 | Fig08_tornado.png | `run_tornado` | base 1637,6 µW |
| 9 | Fig09_montecarlo.png | `run_monte_carlo` (seed 42) | media 1831 µW — ver F2 |
| 10 | Fig10_PCE_ambos.png | `run_pce_uhf_curve` + `run_pce_vs_pin` | PCE_B 85 % · PCE_A 32,6 % |
| 11 | Fig11_validacion_Wang.png | `validate_wang2022(None)` | **RMSE 15,50 pp** (ver F1) |

## 4. Tablas regeneradas (derivadas del código) — `out/tablas/`

T2 (bandas A), T3 (SPICE SMS7630), T6 (geometría dipolos), T7 (PCE–Pin), T8 (link budget), T9 (cadena de potencia), T11 (vs Wang).
**No regenerables automáticamente** (contenido textual, no cambian): T1, T4, T5, T10, T12, T13, T14 — se revisan a mano en Stage 2.

---

## 5. Auditoría de la app — patrones de IA / plantilla pendientes

Páginas **ya revisadas** (narrativa de defensa, sin bloques robóticos): `presentacion`, `problema`, `contexto`, `topologias`, `escenario_a`, `escenario_b`.

Páginas **pendientes** (aún con `ficha_grafica` / `correspondencia` / `aporta` / `encabezado` "entradas-salidas" / "Pasa el cursor"):

| Página | Ocurrencias de patrón |
|---|---|
| analisis_avanzado.py | 10 |
| sensibilidad.py | 7 |
| viabilidad_iot.py | 6 |
| inicio.py | 4 |
| validacion.py | 3 (+ inconsistencia RMSE de F1) |
| comparacion.py | 2 |
| conclusiones.py | 2 |
| acerca.py | 1 |

*(escenario_a/b muestran 2 cada uno = `encabezado` + `badge_exploracion`, que se conservan a propósito.)*

**Recomendación:** aplicar el mismo patrón ya consolidado (hipótesis → hallazgo → evidencia → interpretación → impacto; misiones en controles; una sola conclusión; invitación al documento) página por página, como venimos haciendo.

---

## 6. Próximos pasos (Stage 2 — requiere tu visto bueno)

1. **Decidir F1:** ¿corrijo `run_validacion_wang` a `matching_net=None` (app = doc = 15,50)? *(cambia un KPI visible)*.
2. **Insertar las 11 figuras** regeneradas en una **copia** del docx (`..._REGEN.docx`), reemplazando las antiguas.
3. **Actualizar las tablas** derivadas (T2, T3, T6–T9, T11) con los CSV regenerados.
4. **Reconciliar textos** afectados por F2 (media MC) y por cualquier cifra que haya cambiado.
5. Continuar la limpieza de patrones de IA en las páginas pendientes.

> Nada de esto toca tu documento original ni el `core`. Todo Stage 2 se hace sobre copia y con tu aprobación.
