# Rectenna Fractal Multibanda — Dashboard Interactivo

Proyecto computacional de simulación de rectenas fractales multibanda para
recolección de energía RF ambiental (RFEH) en aplicaciones IoT.

**Autor:** Brahian Calderón Múnera — Ingeniería de Telecomunicaciones, UdeA — 2026
**Director:** Luis Alberto Flórez Serna

---

## Ejecución local

```bash
.venv/Scripts/activate
streamlit run app.py
```

## Estructura

```
rectenna_dashboard_st/
├── app.py                  Punto de entrada Streamlit
├── core/                   Modelos de cálculo (canónico)
│   ├── antenna.py          Sierpinski (Escenario A)
│   ├── flpda.py            FLPDA Koch (Escenario B)
│   ├── matching.py         Red L de adaptación
│   ├── rectifier.py        Diodo SMS7630 + topologías
│   ├── lora_budget.py      Presupuesto energético LoRa
│   ├── comparacion.py      Validación cruzada (Wang, Carrel)
│   └── analysis.py         Análisis avanzado (sensibilidad, Monte Carlo)
├── simulation/             Orquestadores Escenario A / B
├── analysis/               Análisis avanzado y sensibilidad
├── pages/                  Páginas Streamlit
├── configs/                Constantes y parámetros canónicos
├── utils/                  Exportación CSV
├── tests/                  Tests de regresión numérica
├── assets/                 Imágenes y figuras
└── requirements.txt
```

## Alcance del modelo

Simulación **analítica circuital** en Python (NumPy/SciPy). **No utiliza
simuladores electromagnéticos full-wave** (HFSS, CST, FEKO, ADS). Ver
documento de tesis §3.1.2 para la justificación metodológica completa.

## Valores canónicos de referencia

| Parámetro            | Valor       | Origen                          |
|----------------------|-------------|---------------------------------|
| P_DC @ 100 m TDT     | 1 638 µW    | core.lora_budget                |
| Ganancia FLPDA       | 7,10 dBi    | core.flpda                      |
| PCE Sierpinski       | 85 % (clip) | core.rectifier (límite físico)  |
| RMSE vs Wang (2022)  | 15,50 pp    | core.comparacion                |
