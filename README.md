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
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Alcance del modelo](#alcance-del-modelo)
6. [Páginas del dashboard](#páginas-del-dashboard)
7. [Licencia](#licencia)

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

51 tests bloquean los valores canónicos. Ejecutar:

```bash
python -m pytest tests/ -v
```

Verificación rápida (sanity check sin pytest):

```bash
python tests/verify_canonical.py
```

Cualquier cambio en `core/` o `configs/parametros.py` que altere los 20 valores canónicos rompe la regresión.

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
│   └── parametros.py               CANONICAL: 20 magnitudes (SSOT)
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
├── pages/                          10 páginas Streamlit
├── plots/charts.py                 Templates Plotly simple_white
├── utils/                          pagina, circuit_drawing, exportar, graficas
└── tests/
    ├── test_regression_canonical.py  16 valores bloqueados
    ├── test_models.py                35 tests unitarios
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

| Página | Contenido |
|---|---|
| **Resultados de Referencia del Proyecto** | Sankey, diagrama de bloques, tabla canónica |
| **Aplicación del nodo IoT** | Mapa EIRP×distancia×SF, mensajes/día, LoRa timeline, supercap sawtooth |
| **Escenario A — Sierpinski multibanda** | 3 modos (Manual / Auto / Comparar), topologías |
| **Escenario B — FLPDA Koch** | Región activa, iteraciones Koch 0–4, mapa τ–σ, Greinacher 3 estados, I-V Shockley |
| **Validación con literatura** | Scatter vs Wang, descomposición del error |
| **Cálculos avanzados** | Tornado, Monte Carlo, link budget, supercap |
| **Sensibilidad** | Sweep Q_L, R_load, mapa τ–σ |
| **Calculadora** | Sandbox interactivo con 7 sliders |
| **Preparación para defensa** | 9 Q&A + L1–L8 + clip anatomy |
| **Información del proyecto** | Metodología APA7 + referencias |

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
