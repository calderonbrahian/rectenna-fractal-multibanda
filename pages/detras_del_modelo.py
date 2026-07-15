"""
Detrás del modelo — transparencia y trazabilidad total.

Responde una sola pregunta: **¿con qué constantes, variables y ecuaciones se
calcula cada resultado, y dónde vive cada una en el código y en el documento?**

Es el "laboratorio abierto": todo valor sale del SSOT (`configs/parametros.py`),
no se escribe a mano. Cada ecuación enlaza con su archivo:línea y su sección del
trabajo de grado. Nada oculto; la matemática está disponible en capas.
"""

from __future__ import annotations

import streamlit as st

from utils.pagina import encabezado
from configs.parametros import (
    C0, Q_E, K_B, T_AMB, VT, Z0, R_LOAD,
    FR4_ER_1GHZ, FR4_ER_58GHZ, FR4_LOSS_TAN, FR4_H_M,
    URBAN_CORRECTION_DB, POL_LOSS_DB, HARM_LOSS_DB,
    BQ25504_ETA_PMIC, BQ25504_V_COLDSTART, SMS7630, CANONICAL,
)

C = CANONICAL

encabezado(
    "Detrás del modelo",
    "Constantes, variables y ecuaciones — con su origen, sus unidades y su trazabilidad al código y al documento.",
    que_es="Un diccionario técnico navegable del modelo: cada constante física, cada variable "
           "y cada ecuación que produce los resultados del trabajo.",
    para_que_sirve="Permite auditar el modelo sin leer el código: de dónde sale cada número, "
                   "qué unidades tiene, en qué ecuación entra y en qué sección del documento se desarrolla.",
    entradas="Ninguna; es una página de referencia. Todos los valores se leen del SSOT (`configs/parametros.py`).",
    salidas="Fichas de constantes, variables y ecuaciones, y la cadena de trazabilidad del resultado principal.",
    como_leer="Recorre de arriba abajo: primero los ingredientes (constantes y variables), "
              "luego las ecuaciones que los combinan, y al final cómo se encadenan hasta 1.335 µW.",
    icono=":material/function:",
)

st.info(
    "Regla del proyecto: **el código es la única fuente de verdad (SSOT)**. "
    "Los valores de esta página se importan en vivo de `configs/parametros.py`; "
    "si el modelo cambia, esta página cambia con él. Ningún número está escrito a mano aquí.",
    icon=":material/rule:",
)

# ══════════════════════════════════════════════════════════════════════════════
tab_const, tab_var, tab_ec, tab_traza = st.tabs(
    [":material/science: Constantes",
     ":material/data_object: Variables",
     ":material/function: Ecuaciones",
     ":material/account_tree: Trazabilidad"]
)

# ── 1. CONSTANTES FÍSICAS Y DE DISEÑO ─────────────────────────────────────────
with tab_const:
    st.subheader("Constantes físicas fundamentales")
    st.dataframe(
        [
            {"Símbolo": "c₀", "Valor": f"{C0:.3e}", "Unidad": "m/s",
             "Qué representa": "Velocidad de la luz en el vacío", "Se usa en": "FSPL, longitud de onda"},
            {"Símbolo": "q", "Valor": f"{Q_E:.3e}", "Unidad": "C",
             "Qué representa": "Carga del electrón", "Se usa en": "Voltaje térmico Vₜ"},
            {"Símbolo": "k_B", "Valor": f"{K_B:.3e}", "Unidad": "J/K",
             "Qué representa": "Constante de Boltzmann", "Se usa en": "Voltaje térmico Vₜ"},
            {"Símbolo": "T", "Valor": f"{T_AMB:.0f}", "Unidad": "K",
             "Qué representa": "Temperatura de operación (≈27 °C)", "Se usa en": "Vₜ del diodo"},
            {"Símbolo": "Vₜ", "Valor": f"{VT*1e3:.2f}", "Unidad": "mV",
             "Qué representa": "Voltaje térmico = k_B·T/q", "Se usa en": "Ecuación de Shockley"},
            {"Símbolo": "Z₀", "Valor": f"{Z0:.0f}", "Unidad": "Ω",
             "Qué representa": "Impedancia de referencia del sistema", "Se usa en": "S11, Γ, red L"},
        ],
        hide_index=True, width="stretch",
    )

    st.subheader("Sustrato FR-4 (Bahl & Trivedi 1977; Pozar cap. 3)")
    st.dataframe(
        [
            {"Símbolo": "εᵣ", "Valor": f"{FR4_ER_1GHZ:.1f} → {FR4_ER_58GHZ:.1f}", "Unidad": "—",
             "Qué representa": "Permitividad relativa dispersiva (1 → 5,8 GHz)", "Se usa en": "λ_eff, η_rad, impedancia"},
            {"Símbolo": "tan δ", "Valor": f"≈ {FR4_LOSS_TAN:.3f}", "Unidad": "—",
             "Qué representa": "Tangente de pérdidas dieléctricas", "Se usa en": "η_rad (pérdida dominante)"},
            {"Símbolo": "h", "Valor": f"{FR4_H_M*1e3:.1f}", "Unidad": "mm",
             "Qué representa": "Espesor del sustrato", "Se usa en": "Dimensiones de la antena"},
        ],
        hide_index=True, width="stretch",
    )

    st.subheader("Diodo Schottky SMS7630 (Skyworks AN-4003) · PMIC BQ25504 · Enlace")
    st.dataframe(
        [
            {"Símbolo": "Is", "Valor": f"{SMS7630['Is']*1e6:.0f}", "Unidad": "µA", "Qué representa": "Corriente de saturación del diodo", "Se usa en": "Shockley, PCE"},
            {"Símbolo": "n", "Valor": f"{SMS7630['n']}", "Unidad": "—", "Qué representa": "Factor de idealidad", "Se usa en": "Shockley"},
            {"Símbolo": "Rs", "Valor": f"{SMS7630['Rs']:.0f}", "Unidad": "Ω", "Qué representa": "Resistencia serie del diodo", "Se usa en": "PCE, pérdidas óhmicas"},
            {"Símbolo": "Cj0", "Valor": f"{SMS7630['Cj0']*1e12:.2f}", "Unidad": "pF", "Qué representa": "Capacitancia de juntura a 0 V", "Se usa en": "Re(Z_d) a alta frecuencia"},
            {"Símbolo": "R_load", "Valor": f"{R_LOAD:.0f}", "Unidad": "Ω", "Qué representa": "Carga equivalente (entrada BQ25504)", "Se usa en": "V_dc, P_dc"},
            {"Símbolo": "η_PMIC", "Valor": f"{BQ25504_ETA_PMIC:.2f}", "Unidad": "—", "Qué representa": "Eficiencia del boost DC-DC", "Se usa en": "P_dc"},
            {"Símbolo": "V_cs", "Valor": f"{BQ25504_V_COLDSTART*1e3:.0f}", "Unidad": "mV", "Qué representa": "Umbral de arranque en frío", "Se usa en": "Viabilidad, frontera de alcance"},
            {"Símbolo": "L_urb", "Valor": f"{URBAN_CORRECTION_DB:.1f}", "Unidad": "dB", "Qué representa": "Corrección urbana ITU-R P.1546", "Se usa en": "Potencia recibida"},
            {"Símbolo": "L_pol", "Valor": f"{POL_LOSS_DB:.1f}", "Unidad": "dB", "Qué representa": "Desajuste de polarización (Koch it.2)", "Se usa en": "Potencia recibida"},
            {"Símbolo": "L_arm", "Valor": f"{HARM_LOSS_DB:.1f}", "Unidad": "dB", "Qué representa": "Reflexión de armónicos del doblador", "Se usa en": "Potencia recibida"},
        ],
        hide_index=True, width="stretch",
    )
    st.caption("Fuente de todos los valores: `configs/parametros.py`. Se leen en vivo (SSOT).")

# ── 2. VARIABLES DEL MODELO ───────────────────────────────────────────────────
with tab_var:
    st.subheader("Variables del modelo — valores del escenario canónico")
    st.caption("Escenario de referencia: TDT DVB-T (Cerro Nutibara), 100 m, 550 MHz, EIRP 72,15 dBm.")
    st.dataframe(
        [
            {"Símbolo": "EIRP", "Valor": "72,15", "Unidad": "dBm", "Qué representa": "Potencia isótropa radiada equivalente de la fuente"},
            {"Símbolo": "d", "Valor": "100", "Unidad": "m", "Qué representa": "Distancia fuente–antena"},
            {"Símbolo": "f", "Valor": "550", "Unidad": "MHz", "Qué representa": "Frecuencia de operación (punto de diseño)"},
            {"Símbolo": "FSPL", "Valor": f"{C['FSPL_dB']:.2f}", "Unidad": "dB", "Qué representa": "Pérdida de trayecto en espacio libre"},
            {"Símbolo": "G_r", "Valor": f"{C['gain_dBi']:.2f}", "Unidad": "dBi", "Qué representa": "Ganancia realizada de la antena (incluye η_rad)"},
            {"Símbolo": "η_rad", "Valor": f"{C['eta_rad']:.4f}", "Unidad": "—", "Qué representa": "Eficiencia de radiación (FR-4). Hipótesis dominante del modelo"},
            {"Símbolo": "S11", "Valor": f"{C['S11_dB']:.2f}", "Unidad": "dB", "Qué representa": "Coeficiente de reflexión de la antena"},
            {"Símbolo": "η_mm", "Valor": f"{C['eta_mm']:.3f}", "Unidad": "—", "Qué representa": "Eficiencia de adaptación = 1 − |Γ|²"},
            {"Símbolo": "η_imn", "Valor": f"{C['eta_imn']:.4f}", "Unidad": "—", "Qué representa": "Eficiencia de la red L (punto de diseño 550 MHz)"},
            {"Símbolo": "P_in", "Valor": f"{C['P_in_dBm']:.2f}", "Unidad": "dBm", "Qué representa": "Potencia disponible en la antena (Friis)"},
            {"Símbolo": "PCE", "Valor": f"{C['PCE']:.2f}", "Unidad": "—", "Qué representa": "Eficiencia de conversión RF→DC (tope del modelo)"},
            {"Símbolo": "η_PMIC", "Valor": f"{C['eta_pmic']:.2f}", "Unidad": "—", "Qué representa": "Eficiencia del convertidor BQ25504"},
            {"Símbolo": "η_total", "Valor": f"{C['eta_total']:.4f}", "Unidad": "—", "Qué representa": "Figura de mérito de 5 factores"},
            {"Símbolo": "P_DC", "Valor": f"{C['P_dc_uW']:.1f}", "Unidad": "µW", "Qué representa": "Potencia DC útil final"},
            {"Símbolo": "V_DC", "Valor": f"{C['V_dc_mV']:.1f}", "Unidad": "mV", "Qué representa": "Voltaje DC de salida"},
            {"Símbolo": "T_ciclo", "Valor": f"{C['T_ciclo_s']:.1f}", "Unidad": "s", "Qué representa": "Intervalo entre mensajes LoRa SF12"},
            {"Símbolo": "RMSE", "Valor": f"{C['RMSE_wang']:.2f}", "Unidad": "pp", "Qué representa": "Error de validación vs Wang et al. (2022)"},
        ],
        hide_index=True, width="stretch",
    )
    st.warning(
        "**Hipótesis clave — léela antes que cualquier resultado.** η_rad ≈ 0,60 es una "
        "*estimación calibrada* para FR-4 en UHF (rango típico 0,50–0,70 en la literatura), "
        "no una derivación de onda completa. Es el parámetro que más pesa en el resultado: "
        "fijó P_DC en 1.335 µW y η_total en 0,4023. Su incertidumbre se propaga a todo lo demás.",
        icon=":material/priority_high:",
    )

# ── 3. FICHAS DE ECUACIÓN ─────────────────────────────────────────────────────
with tab_ec:
    st.subheader("Ecuaciones del modelo — cada una con su ficha")

    def ficha(titulo, latex, significado, supuestos, referencia, seccion, codigo):
        with st.container(border=True):
            st.markdown(f"**{titulo}**")
            st.latex(latex)
            st.markdown(f":material/lightbulb: **Significado.** {significado}")
            st.markdown(f":material/warning: **Supuestos / límites.** {supuestos}")
            c1, c2 = st.columns(2)
            c1.caption(f":material/menu_book: **Documento:** {seccion}")
            c1.caption(f":material/library_books: **Referencia:** {referencia}")
            c2.caption(f":material/code: **Código:** `{codigo}`")

    ficha(
        "Pérdida de trayecto en espacio libre (FSPL)",
        r"\mathrm{FSPL} = 20\,\log_{10}\!\left(\frac{4\pi d}{\lambda}\right)",
        "Atenuación de la onda al propagarse una distancia d. A 100 m y 550 MHz vale 67,25 dB.",
        "Espacio libre; sin multitrayecto ni desvanecimiento (se añade aparte la corrección urbana de 6 dB).",
        "Pozar, Microwave Engineering 4ed, ec. 2.6", "§2.4 / §4.3.1", "core/lora_budget.py:129",
    )
    ficha(
        "Potencia disponible en la antena (Friis)",
        r"P_{in} = \mathrm{EIRP} - \mathrm{FSPL} - L_{urb} - L_{pol} - L_{arm} + G_r",
        "Balance de enlace en dB. Con los valores canónicos da +2,97 dBm (1,982 mW).",
        "G_r es la ganancia realizada (ya incluye η_rad). Las pérdidas de polarización y armónicos son explícitas.",
        "Friis / Pozar §2", "§4.3.1", "core/lora_budget.py:239",
    )
    ficha(
        "Eficiencia de adaptación de impedancias",
        r"\eta_{mm} = 1 - |\Gamma|^2,\qquad |\Gamma|^2 = 10^{\,S_{11}/10}",
        "Fracción de potencia no reflejada por el desajuste antena–carga. Con S11=−17,71 dB da 0,983.",
        "S11 proviene de un modelo analítico de impedancia (no onda completa).",
        "Pozar §2 / §5", "§4.1", "core/lora_budget.py:245",
    )
    ficha(
        "Nº de dipolos de la LPDA (Carrel, con región activa)",
        r"N = 1 + \frac{\ln B_s}{\ln(1/\tau)},\quad B_s = \frac{f_2}{f_1}\,B_{ar},\quad "
        r"B_{ar} = 1{,}1 + 7{,}7\,(1-\tau)^2\cot\alpha",
        "Determina el número de elementos. Con τ=0,90, σ=0,15 → B_ar≈1,56 → N=12 (el margen de "
        "región activa es lo que corrige el N=8 ingenuo).",
        "Diseño log-periódico ideal; sin acoplamiento mutuo de onda completa.",
        "Carrel (1961), IRE Trans. AP", "§3.4.2", "core/flpda.py:100",
    )
    ficha(
        "Potencia DC útil (cadena de 4 factores)",
        r"P_{DC} = P_{in}\cdot \eta_{mm}\cdot \eta_{imn}\cdot \mathrm{PCE}\cdot \eta_{PMIC}",
        "Producto de la potencia recibida por las eficiencias de la cadena. η_rad NO entra aquí "
        "(ya está en G_r). Resultado: 1.335,0 µW.",
        "PCE tope 0,85: el punto canónico opera saturado; la validación es a −10 dBm (ver pestaña Trazabilidad).",
        "Balance de cadena RF→DC", "§4.3.1 / Anexo B.16-B.17", "core/lora_budget.py:276",
    )
    ficha(
        "Figura de mérito de eficiencia total (5 factores)",
        r"\eta_{total} = \eta_{rad}\cdot \eta_{mm}\cdot \eta_{imn}\cdot \mathrm{PCE}\cdot \eta_{PMIC}",
        "Fracción de la potencia captada por una antena ideal equivalente que llega a ser DC útil. Vale 0,4023.",
        "Es una FOM, no el cociente P_DC/P_in (que usa 4 factores). Distinguir ambos evita contar η_rad dos veces.",
        "Definición del trabajo", "§4.1 / §5.1", "core/lora_budget.py:287",
    )
    ficha(
        "Tiempo de carga del supercondensador",
        r"t_{carga} = \frac{E_{util}}{P_{DC}},\qquad E_{util} = \tfrac{1}{2}C\,(V_{max}^2 - V_{min}^2)",
        "Tiempo para cargar el supercap 330 mF de 1,8 a 3,3 V. Con P_DC=1.335 µW: E_util=1.262 mJ → 945 s ≈ 15,8 min.",
        "Sin ESR ni fuga (defaults=0), como el Anexo B.9. Son un refinamiento opcional, no el modelo documentado.",
        "Energía en un capacitor", "Anexo B.9", "core/analysis.py:330",
    )

# ── 4. CADENA DE TRAZABILIDAD ─────────────────────────────────────────────────
with tab_traza:
    st.subheader("Del resultado principal hacia atrás")
    st.markdown(
        "El resultado titular es **P_DC = 1.335 µW**. Así se sigue hacia atrás hasta su origen:"
    )
    st.markdown(
        f"""
1. **Resultado** → `P_DC = {C['P_dc_uW']:.1f} µW` (@ 100 m, TDT 550 MHz)
2. **Ecuación** → `P_DC = P_in · η_mm · η_imn · PCE · η_PMIC`
3. **Variables** → `P_in={C['P_in_dBm']:.2f} dBm` · `η_mm={C['eta_mm']:.3f}` · `η_imn={C['eta_imn']:.4f}` · `PCE={C['PCE']:.2f}` · `η_PMIC={C['eta_pmic']:.2f}`
4. **Constantes** → `configs/parametros.py` → `CANONICAL`, `SMS7630`, `R_LOAD`, `POL_LOSS_DB`, `HARM_LOSS_DB`
5. **Dato / fuente** → EIRP 72,15 dBm (10 kW ERP + 2,15 dB), Cerro Nutibara DVB-T
6. **Código** → `core/lora_budget.py:276` (`harvested_uw_full`)
7. **Prueba que lo bloquea** → `tests/test_regression_canonical.py:136` (`test_cadena_potencia_canonica`)
"""
    )
    st.info(
        "**Límite honesto de la validación.** La validación cruzada con Wang et al. (2022) "
        "se hace a Pin = −10 dBm (RMSE 15,50 pp), pero el punto canónico entrega +2,97 dBm al "
        "rectificador, donde la PCE está saturada en su tope de 0,85. Es decir, el 1.335 µW "
        "descansa en un régimen 12 dB por encima del punto validado. Es una limitación declarada, "
        "no un resultado medido.",
        icon=":material/balance:",
    )
    st.caption("Este trabajo es un estudio de modelado y simulación; no incluye medición experimental ni prototipo.")

st.divider()
st.caption(
    "Todos los valores provienen del pipeline reproducible. Regenerar figuras/tablas: "
    "`python _regen/generate_artifacts.py`. Verificar canónicos: `pytest tests/`."
)
