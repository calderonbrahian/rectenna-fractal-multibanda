# Rectenna Fractal Multibanda — Dashboard Interactivo

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit 1.57+](https://img.shields.io/badge/streamlit-1.57%2B-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://github.com/calderonbrahian/rectenna-fractal-multibanda/actions/workflows/tests.yml/badge.svg)](https://github.com/calderonbrahian/rectenna-fractal-multibanda/actions/workflows/tests.yml)
[![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red.svg)](./NOTICE.md)
[![Status: Defendible](https://img.shields.io/badge/status-defendible%20v1.0-success.svg)](#)

Proyecto computacional de simulación de **rectenas fractales multibanda** para recolección de energía RF ambiental (RFEH) en aplicaciones IoT.

**Autor:** Brahian Calderón Múnera — Ingeniería de Telecomunicaciones, UdeA — 2026
**Director:** Luis Alberto Flórez Serna

---

## Tabla de contenido

1. [Resultado canónico defendido](#resultado-canónico-defendido)
2. [Ejecución local](#ejecución-local)
3. [Tests de regresión](#tests-de-regresión)
4. [Reproducibilidad del pipeline](#reproducibilidad-del-pipeline-figuras-tablas-y-valores-del-documento)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Alcance del modelo](#alcance-del-modelo)
7. [Páginas del dashboard](#páginas-del-dashboard)
8. [Licencia](#licencia)

---

## Resultado canónico defendido

Escenario: TDT Cerro Nutibara, Medellín · 100 m · EIRP 70 dBm · FR-4 · diodo Schottky SMS7630 · PMIC BQ25504.

| Magnitud | Valor | Test que la bloquea |
|---|---|---|
| Potencia DC útil — **P_DC** | **1 637,6 µW** | `test_cadena_potencia_canonica` |
| Voltaje DC de salida — **V_DC** | 1 459,1 mV | `test_output_voltage_positivo` |
| Eficiencia total — **η_total** (FOM 5 factores) | 0,6715 | `test_eta_total_producto` |
| Ganancia FLPDA Koch @ 550 MHz | 7,10 dBi | `test_flpda_ganancia_550mhz` |
| PCE máxima (cap) | 0,85 | `test_pce_clip_85pct` |
| RMSE vs Wang (2022) | 15,50 pp | `test_validacion_wang2022_rmse` |
| T_ciclo LoRa SF12 | 158,3 s | derivado E_ciclo/P_DC |

Identidades canónicas:
- `P_DC = P_in · η_mm · η_IMN · PCE · η_PMIC` (4 factores; η_rad ya está embebido en G realizada)
- `η_total = η_rad · η_mm · η_IMN · PCE · η_PMIC` (FOM 5 factores)

---

## Ejecución local

### Requisitos

- Python ≥ 3.9 (testeado en 3.13)
- pip
- (Opcional) Git para clonar

### Setup en Windows (PowerShell)

```powershell
git clone https://github.com/calderonbrahian/rectenna-fractal-multibanda.git
cd rectenna-fractal-multibanda
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

### Setup en Linux / macOS

```bash
git clone https://github.com/calderonbrahian/rectenna-fractal-multibanda.git
cd rectenna-fractal-multibanda
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

La app queda disponible en `http://localhost:8501`. Tema institucional UdeA (blanco) preconfigurado en `.streamlit/config.toml`.

---

## Tests de regresión

56 tests (51 canónicos/modelos + 5 pipeline) bloquean los valores y artefactos. Ejecutar:

```bash
python -m pytest tests/ -v
```

Verificación rápida (sanity check sin pytest):

```bash
python tests/verify_canonical.py
```

Cualquier cambio en `core/` o `configs/parametros.py` que altere los 19 valores canónicos rompe la regresión.

---

## Reproducibilidad del pipeline (figuras, tablas y valores del documento)

Todas las figuras y tablas del trabajo de grado se regeneran desde el modelo actual, sin intervención manual. Fuente única de verdad: `configs/parametros.py` → pipeline → artefactos.

```bash
# 1. Regenera 11 figuras de datos + 5 conceptuales (PNG 300 dpi) + 7 tablas CSV + verificación
python _regen/generate_artifacts.py
#    Salida: _regen/out/figuras/  _regen/out/tablas/  _regen/out/verificacion.json

# 2. Deriva todos los valores numéricos que usa el documento (Tablas 2/9/11, E.7, E.8,
#    umbrales de viabilidad, supercondensador, ganancia media…)
python _regen/derive_doc_values.py
#    Salida: _regen/out/doc_values.json
```

`generate_artifacts.py` imprime, para cada artefacto, un `[OK]`/`[ERR]` y una verificación en vivo contra `CANONICAL` (deltas ≈ 0). La cadena completa es:

```
configs/parametros.py  →  core/ + simulation/ + analysis/  →  _regen/*.py  →  figuras / tablas / doc_values.json
```

---

## Estructura del proyecto

```
rectenna-fractal-multibanda/
├── app.py                          Punto de entrada Streamlit (st.navigation)
├── requirements.txt
├── README.md
├── NOTICE.md
├── .streamlit/
│   └── config.toml                 Tema institucional UdeA blanco
├── configs/
│   └── parametros.py               CANONICAL: 19 magnitudes (SSOT)
├── core/                           Modelo físico (NO TOCAR sin tests)
│   ├── antenna.py                  FractalAntenna Sierpinski
│   ├── flpda.py                    FLPDA Koch (Carrel 1961)
│   ├── matching.py                 Red L de adaptación
│   ├── rectifier.py                Schottky SMS7630 + Greinacher
│   ├── analysis.py                 Cadena de potencia + Tornado + MC
│   ├── comparacion.py              Validación cruzada Wang/Carrel
│   └── lora_budget.py              E_ciclo, T_ciclo, mensajes/día
├── analysis/                       Runners cacheados (avanzado, sensibilidad)
├── simulation/                     Runners cacheados (escenarios A, B)
├── pages/                          14 páginas Streamlit (recorrido guiado)
├── plots/charts.py                 Templates Plotly simple_white
├── utils/                          pagina, glosario, circuit_drawing, exportar
├── _regen/                         Pipeline de regeneración de artefactos
│   ├── generate_artifacts.py       11 figuras datos + 5 conceptuales + 7 tablas CSV
│   ├── figuras_conceptuales.py     C1–C5 (fuentes→caso, maestra, anatomía, flujo, repro)
│   ├── estilo_figuras.py           sistema gráfico unificado (paleta + iconos técnicos)
│   ├── derive_doc_values.py        doc_values.json (todos los valores del documento)
│   └── out/                        figuras/, tablas/, doc_values.json, verificacion.json
└── tests/
    ├── test_regression_canonical.py  11 tests · valores canónicos bloqueados
    ├── test_models.py                40 tests unitarios
    ├── test_pipeline_smoke.py         5 tests · figuras conceptuales C1–C5
    └── verify_canonical.py           Script de verificación rápida
```

---

## Alcance del modelo

Simulación **analítica circuital** en Python (NumPy / SciPy). **No utiliza simuladores electromagnéticos full-wave** (HFSS, CST, FEKO, ADS).

Validación contra dataset físico publicado: **Wang et al. (2022)**, RMSE = 15,50 pp sobre 7 frecuencias canónicas [1,84 — 2,04 — 2,36 — 2,54 — 3,30 — 4,76 — 5,80] GHz.

Limitaciones explícitas (L1–L8):
1. Sin prototipo físico medido por el autor.
2. PCE acotada por cap del modelo (0,85).
3. Validación restringida a un dataset.
4. Sustrato FR-4 con pérdidas altas en bandas superiores.
5. PMIC sin caracterización térmica.
6. Propagación Friis con corrección urbana fija (6 dB).
7. Régimen lineal del rectificador P_in ∈ [−15, +5] dBm.
8. Iteración fractal limitada (Sierpinski it. 3, Koch it. 2).

---

## Páginas del dashboard

La app tiene **dos niveles** (`st.navigation`). El Nivel 1 usa las figuras del pipeline (`_regen/out/figuras/`) — la misma fuente gráfica que el documento y el póster.

**Nivel 1 · Demostración (3 min)** — recorrido para quien nunca vio el proyecto:

| # | Página (`pages/…`) | Contenido |
|---|---|---|
| 1 | `demo_1_problema` | El problema del IoT y la pregunta de investigación (figura de fuentes→caso) |
| 2 | `demo_2_metodo` | La metodología = el aporte (flujo, anatomía de la rectena, reproducibilidad) |
| 3 | `demo_3_resultados` | Qué se demostró: KPIs + cascada, PCE de ambos escenarios, validación |
| 4 | `demo_4_aporte` | El aporte y su alcance (figura maestra); el caso colombiano como demostración |

**Nivel 2 · Laboratorio** — detalle técnico e interacción:

| Grupo | Página (`pages/…`) | Contenido |
|---|---|---|
| Escenarios | `escenario_a` · `escenario_b` · `comparacion` | S₁₁, impedancia, PCE, geometría, presupuesto, comparación integral |
| Caso y viabilidad | `inicio` · `viabilidad_iot` | Resultado de referencia; mensajes/día, mapa EIRP×distancia, supercondensador |
| Validación y análisis | `validacion` · `analisis_avanzado` · `sensibilidad` | Wang/Carrel; tornado, Monte Carlo, link budget; barridos Q_L, R_load, τ–σ |
| Cierre y referencia | `conclusiones` · `acerca` | Hallazgos y limitaciones; metodología, arquitectura y referencias |

---

## Licencia

© 2026 Brahian Calderón Múnera. **All Rights Reserved.** Ver [NOTICE.md](./NOTICE.md) para términos completos. Este repositorio es privado y se distribuye únicamente a personas explícitamente autorizadas por el autor.

---

## Referencias

- Wang, Y. et al. (2022). *Multiband fractal rectenna for RF energy harvesting*. IEEE TAP.
- Carrel, R. L. (1961). *Analysis and design of the log-periodic dipole antenna*. Univ. of Illinois.
- Pozar, D. M. (1998). *Microwave Engineering*. Wiley.
- Shockley, W. (1949). *Theory of p-n junctions in semiconductors*. Bell System Tech. J.
- Friis, H. T. (1946). *A note on a simple transmission formula*. Proc. IRE.
- ITU-R P.1546-6 (2019). *Method for point-to-area predictions for terrestrial services*.
- Texas Instruments. *BQ25504 datasheet* (SLUSCY3).
- Skyworks. *SMS7630 datasheet* (AN-4003).
