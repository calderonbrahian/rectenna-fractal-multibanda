# -*- coding: utf-8 -*-
"""
================================================================================
DERIVACIÓN: Eficiencia RF→DC de cadena completa por antena y escenario
================================================================================
Responde a la pregunta del autor: "¿qué % de la energía RF disponible se
convierte en DC a lo largo de TODA la cadena (antena+rectificador) para cada
antena?", desglosado por escenario de fuente (débil/difusa vs. fuerte cercana
vs. firme distante) para las 3 antenas del trabajo (Sierpinski, parche
microcinta, FLPDA Koch).

Convención de nombres (NO se rompe en ningún artefacto derivado de este script):
    eta_cadena = eta_mm · eta_imn · PCE · eta_pmic     (4 factores POST-antena)
    eta_total  = eta_rad · eta_cadena                  (5 factores, FOM completa)
Verificación: para el caso canónico FLPDA@100m TDT, eta_cadena=0.6735(67.36%)
y eta_total=0.4023(40.23%) — EXACTAMENTE los valores ya publicados en el
documento (CANONICAL['eta_total'] en configs/parametros.py).

──────────────────────────────────────────────────────────────────────────────
 DECISIONES DE MODELADO (documentadas aquí, no en el texto de la tesis)
──────────────────────────────────────────────────────────────────────────────
0. CORRECCIÓN DE ARQUITECTURA (revisión posterior a la primera versión de este
   script): Sierpinski y Parche operan bajo CO-DISEÑO CONJUGADO INTEGRADO
   (core.matching.LMatchNetwork.conjugate_efficiency — antena→red→diodo SIN
   interfaz forzada de 50 Ω; ver core/multiband.py y §5.1.3 del documento).
   La primera versión de este script usaba `LMatchNetwork.design()` (adapta
   una fuente de 50 Ω) para ambos escenarios de estas dos antenas — eso
   REINTRODUCE la arquitectura modular de 50 Ω que el co-diseño conjugado
   reemplaza, y daba P_dc muy por debajo del valor ya publicado y auditado
   (2,43 / 2,32 µW agregados urbanos). Todas las cadenas de Sierpinski y
   Parche en este script usan ahora `conjugate_efficiency()`, nunca
   `design()`. FLPDA (Escenario B, dirigida, arquitectura modular de 50 Ω por
   diseño) no se toca: sigue usando `harvested_uw_full()`/CANONICAL sin
   cambios.
1. Escenario "ambiente urbano difuso" (Sierpinski, Parche): NO es una cadena
   de una sola banda. Es la cosecha AGREGADA de las 7 bandas de BANDS_A ya
   establecida en core.multiband.harvest_per_band()/harvest_total_uw() (SSOT:
   2,43 µW Sierpinski, 2,32 µW Parche). Este script reconstruye el desglose
   de tres factores agregados — ya citado en el documento en §5.1.3 como la
   identidad "66,0 µW × 0,549 × 0,079 × 0,850 = 2,43 µW" — ponderando por
   potencia cada banda: η_cm_agregado = Σ(P_amb,i·η_cm,i)/ΣP_amb,i y
   PCE_agregado = (P_dc_total/η_pmic)/Σ(P_amb,i·η_cm,i). El producto
   η_cm_agregado·PCE_agregado·η_pmic reproduce el η_sistema ya publicado
   (≈3,68 % Sierpinski) SIN necesidad de recalcular nada del pipeline
   original. No hay un factor η_rad/η_mm/η_imn separado en esta arquitectura
   integrada: la reflexión de antena no es pérdida (por eso no hay S11 de 50 Ω
   en esta cadena) y la radiación/acople queda embebida en η_cm. Se usa
   'eta_cadena' = 'eta_total' = η_sistema en el JSON para esta arquitectura
   (no hay un quinto factor eta_rad que restar aparte).
2. Escenario "fuente fuerte cercana" (Sierpinski, Parche): un emisor intencional
   de UNA sola banda, co-diseño conjugado igual que (1) pero para un único
   enlace: P_in en el puerto de antena = EIRP − FSPL(d,f) + G_antena(f) (enlace
   LOS de interior, SIN la corrección urbana NLOS de exteriores de 6 dB que
   aplica harvested_uw_full() para el caso macro-escala FLPDA↔TDT — no tiene
   sentido físico para un emisor a metros en interior con línea de vista).
   eta_cm se obtiene de conjugate_efficiency(f, Z_antena, Z_diodo), no de una
   IMN de 50 Ω. EIRP=20 dBm, distancia 0,4 m (proximidad directa, aún en campo
   lejano para antenas eléctricamente pequeñas). La FRECUENCIA se elige DENTRO
   del dominio de validez del acople de cada antena (corrección de dominio, K1):
   - Sierpinski: f=3,30 GHz (small cell 5G en banda). NO 2,45 GHz: esa es una
     anti-resonancia del fractal (resonancias calibradas 1,84/3,68 GHz) y la
     banda de BANDS_A con mejor acople es 3,30 GHz (5G_3.5). El fractal radia
     pobremente en esa banda (G≈−0,7 dBi, η_rad≈0,47), de modo que el enlace
     único a 3,30 GHz entrega MENOS P_dc agregado (0,99 µW) que la cosecha de
     7 bandas del ambiente (2,43 µW): eta_total "fuerte" (3,55 %) queda incluso
     por debajo del ambiente (3,68 %). Es un resultado físico honesto — POR
     BANDA, el enlace a 3,30 GHz sí supera el aporte de esa banda en el ambiente.
   - Parche FR-4: f=2,45 GHz — es su banda de diseño (f0), plenamente en dominio;
     conserva su etiqueta 'fuente_fuerte_wifi'. Aquí sí P_dc_fuerte ≫ P_dc_amb.
3. Banda dominante por antena para el escenario ambiente (referencia
   informativa del cálculo agregado, no determina el resultado):
   - Sierpinski: 5G_3.5 (3.30 GHz) — mejor S11/η_cm dentro de BANDS_A.
   - Parche FR-4: WiFi_2.4 (2.45 GHz) — banda de diseño (f0).
4. FLPDA + "fuente fuerte cercana tipo WiFi" NO se evalúa a 2.45 GHz: la FLPDA
   Koch está diseñada para 470–900 MHz (UHF). Forzarla a 2.45 GHz violaría su
   dominio de validez física (S11, ganancia y η_rad del modelo no están
   calibrados fuera de esa banda) y produciría un número sin sentido físico.
   En su lugar se reutiliza, dentro de SU banda de diseño (550 MHz, misma
   fuente TDT), la comparación de distancias YA existente en el pipeline
   (_regen/derive_doc_values.py::anexoB10_cadena, 50–1000 m): 100 m como
   "fuente fuerte/cercana" y 1000 m como "fuente débil/lejana". El escenario
   canónico TDT@100m (b) reutiliza CANONICAL sin recálculo y es, por
   construcción, idéntico numéricamente al punto "cercano" de (a) — se deja
   así intencionalmente para que quede trazable al valor ya publicado.
5. SEMÁNTICA ÚNICA DE eta_total POR ARQUITECTURA (auditoría K1). No hay UNA
   sola definición de eta_total válida para las tres antenas; cada arquitectura
   fija su referencia de potencia y su identidad auto-multiplicable:
   - Conjugada (Sierpinski, parche): eta_total = eta_cadena = P_dc / P_in_puerto
     = eta_cm·PCE_intrínseca·eta_pmic. Referencia = potencia en el puerto de
     antena. Identidad exacta: P_dc = P_in · eta_total.
   - Modular de 50 Ω (FLPDA): eta_total (5 factores, con eta_rad) es una FIGURA
     DE MÉRITO que multiplica sobre P_INCIDENTE = P_in/eta_rad (potencia RF antes
     de la antena); eta_cadena (4 factores, sin eta_rad) multiplica sobre P_in
     (puerto). Dos identidades exactas: P_dc = P_incidente·eta_total =
     P_in·eta_cadena. Mezclar P_in con eta_total (primera versión) NO era
     auto-multiplicable — corregido añadiendo el campo P_incidente_uW.
6. LIMITACIÓN — SATURACIÓN DEL PCE AL 85 %. RectifierCircuit.PCE está clipeado
   al 85 % (límite físico declarado del SMS7630). En banda UHF, con las
   potencias de la fuente TDT (P_in ~ 0 a +3 dBm a 100 m; aún ~−17 dBm a
   1000 m), el modelo satura en 85 % en TODO el rango — por eso eta_total es
   idéntico a 100 y 1000 m para la FLPDA (la diferencia real está en la potencia
   absoluta, no en el %). El punto FLPDA@1000 m es OPTIMISTA: el modelo de
   Re_Zd a 0,55 GHz sostiene un PCE alto incluso a baja potencia donde un
   rectificador real caería. Es una limitación del modelo, se DOCUMENTA (no se
   re-modela): el RMSE validado depende de este mismo rectifier.
7. LIMITACIÓN — eta_cm CON Z_d DE PEQUEÑA SEÑAL A BIAS CERO. La eficiencia de
   acople conjugado usa la impedancia del diodo evaluada en pequeña señal a
   bias cero (rectifier.diode.impedance(f) con V_bias=0). En gran señal el punto
   de operación del diodo se desplaza y Z_d varía; el tratamiento riguroso
   exigiría balance armónico. eta_cm es por tanto una APROXIMACIÓN de pequeña
   señal, coherente con el resto del pipeline (misma Z_d que multiband).
8. ESCENARIO AMBIENTE — REFERENCIA DE POTENCIA. Los escenarios
   'ambiente_urbano_difuso' usan URBAN_AMBIENT_DBM, que YA está definido EN EL
   PUERTO DE ANTENA (no es una densidad de flujo incidente): por eso NO se
   aplica un factor eta_rad separado y P_in_uW es directamente la potencia
   agregada en el puerto. La reflexión/radiación queda embebida en eta_cm
   (arquitectura integrada, sin interfaz de 50 Ω). Es coherente con la decisión
   de modelado 1.

Salida: _regen/out/efficiency_values.json
Ejecutar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/derive_efficiency_values.py
================================================================================
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from configs.parametros import (
    CANONICAL, BANDS_A, URBAN_AMBIENT_DBM,
    BQ25504_ETA_PMIC as ETA_PMIC,
    FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)
from core.antenna import FractalAntenna
from core.patch import MicrostripPatchAntenna
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.matching import LMatchNetwork
from core.lora_budget import harvested_uw_full, fspl_dB
from core import multiband as mb

OUT_DIR = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT_DIR, exist_ok=True)


# ── Cadena RF→DC de UNA banda, co-diseño CONJUGADO integrado (sin 50 Ω) —
#    mismo patrón que core.multiband.harvest_per_band(), reutilizado aquí
#    para un único enlace (ver decisión de modelado 2). ──
def chain_conjugate_single_band(P_in_dBm: float, freq_hz: float,
                                 antenna, rectifier, matching_net,
                                 eta_pmic: float = ETA_PMIC) -> dict:
    """Cadena RF→DC de una sola banda con co-diseño conjugado integrado.

    SEMÁNTICA DE LOS CAMPOS DEVUELTOS (auditoría K1, corrección de doble conteo)
    --------------------------------------------------------------------------
    RectifierCircuit.PCE(Pin, IL_dB=il_cm_dB) ya incorpora la pérdida de acople
    dentro del factor `eta_match = 10^(-IL_dB/10) = eta_cm`, de modo que el valor
    que devuelve es P_dc_ANTES_de_PMIC / P_in_puerto — es decir, la conversión
    RF→DC medida DESDE EL PUERTO DE ANTENA, con el acople ya descontado. Por eso
    NO debe volver a multiplicarse por eta_cm: la primera versión calculaba
    `eta_sistema = eta_cm · pce · eta_pmic` y DOBLE-CONTABA eta_cm (bug K1).

      - eta_total = eta_cadena = eta_sistema = P_dc / P_in_puerto = pce · eta_pmic.
        (equivalentemente P_dc_uW / P_in_uW — ambas vías coinciden a coma
        flotante porque output_power_uw() reusa exactamente el mismo pce).
      - Campo 'PCE' del dict = PCE INTRÍNSECA POST-ACOPLE = pce / eta_cm =
        P_dc_antes_PMIC / P_después_del_acople. Con esta definición el producto
        de las franjas del Sankey conjugado (eta_cm · PCE · eta_pmic) reproduce
        EXACTAMENTE eta_sistema, y por tanto franjas × P_in = P_dc.
      - 'eta_cm' : eficiencia de acople conjugado antena→diodo (1 − |Γ|² con la
        Z conjugada), único factor de pérdida antes del rectificador.
      - 'eta_rad': informativo; en esta arquitectura integrada la radiación/acople
        queda embebida en eta_cm y NO es un factor separado de la cadena.
    """
    gain = float(antenna.gain_dBi(freq_hz))
    eta_r = float(antenna.eta_rad(freq_hz))

    Za = antenna.impedance(freq_hz)
    Zd = rectifier.diode.impedance(freq_hz)
    eta_cm = float(matching_net.conjugate_efficiency(freq_hz, Za, Zd))
    il_cm_dB = -10.0 * np.log10(max(eta_cm, 1e-6))

    # pce = P_dc_antes_de_PMIC / P_in_puerto (la IL del acople ya va dentro)
    pce = float(rectifier.PCE(P_in_dBm, freq_hz, IL_dB=il_cm_dB, gamma=0.0))
    P_dc_uW = float(rectifier.output_power_uw(P_in_dBm, freq_hz,
                                              IL_dB=il_cm_dB, gamma=0.0))
    P_dc_uW *= eta_pmic

    P_in_uW = 10.0 ** (P_in_dBm / 10.0) * 1000.0

    # eta_sistema por dos vías independientes (deben coincidir a coma flotante):
    #   (1) pce · eta_pmic   (2) P_dc_uW / P_in_uW
    eta_via_pce = pce * eta_pmic
    eta_via_pot = P_dc_uW / P_in_uW if P_in_uW > 0.0 else eta_via_pce
    assert abs(eta_via_pce - eta_via_pot) < 1e-9, (
        f"vías de eta_sistema divergen: {eta_via_pce} vs {eta_via_pot}")
    eta_sistema = eta_via_pce

    # PCE intrínseca post-acople (P_dc_antes_PMIC / P_después_del_acople), para
    # que eta_cm · PCE · eta_pmic == eta_sistema en el Sankey conjugado.
    pce_intrinseca = pce / max(eta_cm, 1e-9)

    return {
        'gain_dBi':   gain,
        'eta_rad':    eta_r,          # informativo; no es un factor de la cadena
        'eta_cm':     eta_cm,
        'PCE':        float(pce_intrinseca),  # PCE INTRÍNSECA post-acople (ver docstring)
        'eta_pmic':   eta_pmic,
        'eta_cadena': float(eta_sistema),
        'eta_total':  float(eta_sistema),
        'P_in_dBm':   float(P_in_dBm),
        'P_in_uW':    float(P_in_uW),
        'P_dc_uW':    float(P_dc_uW),
    }


# ── Cadena RF→DC para el escenario "fuente fuerte cercana": enlace directo LOS
#    de interior a un emisor intencional (SOLO FSPL + ganancia de antena, sin la
#    corrección urbana NLOS de exteriores que usa harvested_uw_full). Ver
#    decisión de modelado (2) arriba. Reutiliza chain_conjugate_single_band()
#    para el resto de la cadena (acople conjugado, PCE, PMIC). Válida para
#    cualquier frecuencia DENTRO del dominio de validez del acople de la antena
#    (Sierpinski: 3,30 GHz, mejor acople de BANDS_A; parche: 2,45 GHz = f0). ──
def chain_los_wifi(eirp_dbm: float, dist_m: float, freq_ghz: float,
                   antenna, rectifier, matching_net,
                   eta_pmic: float = ETA_PMIC) -> dict:
    freq_hz = freq_ghz * 1e9
    gain = float(antenna.gain_dBi(freq_hz))
    Pr_dBm = eirp_dbm - fspl_dB(dist_m, freq_ghz) + gain
    return chain_conjugate_single_band(Pr_dBm, freq_hz, antenna, rectifier,
                                       matching_net, eta_pmic)


# ── Cadena RF→DC AGREGADA (7 bandas, co-diseño conjugado) — reconstruye el
#    desglose de 3 factores ponderado por potencia a partir de
#    core.multiband.harvest_per_band(), sin recalcular el SSOT (ver decisión
#    de modelado 1). Reproduce exactamente el η_sistema y P_dc ya publicados
#    (2,43 µW Sierpinski, 2,32 µW Parche). ──
def chain_conjugate_aggregate(antenna, rectifier, matching_net,
                              eta_pmic: float = ETA_PMIC) -> dict:
    filas = mb.harvest_per_band(antenna, rectifier, matching_net,
                                eta_pmic=eta_pmic)
    p_amb_uW = np.array([10.0 ** (f['P_amb_dBm'] / 10.0) * 1000.0
                         for f in filas])
    p_after_cm_uW = p_amb_uW * np.array([f['eta_cm'] for f in filas])
    p_dc_uW = np.array([f['P_dc_uW'] for f in filas])

    P_in_total = float(p_amb_uW.sum())
    P_after_cm_total = float(p_after_cm_uW.sum())
    P_dc_total = float(p_dc_uW.sum())

    eta_cm_agregado = P_after_cm_total / P_in_total
    P_dc_before_pmic_total = P_dc_total / eta_pmic
    pce_agregado = P_dc_before_pmic_total / P_after_cm_total
    eta_sistema = P_dc_total / P_in_total

    return {
        'eta_cm':     float(eta_cm_agregado),
        'PCE':        float(pce_agregado),
        'eta_pmic':   eta_pmic,
        'eta_cadena': float(eta_sistema),
        'eta_total':  float(eta_sistema),
        'P_in_dBm':   float(10.0 * np.log10(P_in_total / 1000.0)),
        'P_in_uW':    P_in_total,
        'P_dc_uW':    P_dc_total,
        'bandas':     filas,
    }


def from_harvested_full(res: dict) -> dict:
    """Normaliza el dict de harvested_uw_full() a la convención eta_cadena/eta_total.

    CONVENCIÓN DE POTENCIAS (arquitectura modular de 50 Ω, FLPDA — corrección K1
    de terna auto-multiplicable): la ganancia realizada de la antena YA incluye
    eta_rad, de modo que P_in (= 'P_in_uW', potencia en el PUERTO de antena) ya
    tiene la eficiencia de radiación aplicada. Por eso hay DOS potencias de
    referencia y DOS identidades exactas, según sobre qué eficiencia se
    multiplique:

      - eta_total (5 factores: eta_rad·eta_mm·eta_imn·PCE·eta_pmic, FOM completa)
        multiplica sobre P_INCIDENTE = P_in / eta_rad (la potencia RF ANTES de la
        antena, campo 'P_incidente_uW'):     P_dc = P_incidente · eta_total.
      - eta_cadena (4 factores post-antena: eta_mm·eta_imn·PCE·eta_pmic)
        multiplica sobre P_in (puerto de antena):  P_dc = P_in · eta_cadena.

    Ambas identidades son exactas a coma flotante porque derivan del mismo cálculo
    físico (harvested_uw_full): P_dc = P_in·eta_cadena y
    P_incidente·eta_total = (P_in/eta_rad)·(eta_rad·eta_cadena) = P_in·eta_cadena.
    Mezclar P_in con eta_total (como hacía la primera versión) NO es
    auto-multiplicable y era el bug reportado."""
    eta_cadena = res['eta_mm'] * res['eta_imn'] * res['PCE'] * res['eta_pmic']
    P_incidente_uW = res['P_rf_uW'] / max(res['eta_rad'], 1e-9)
    return {
        'gain_dBi':   res['gain_dBi'],
        'eta_rad':    res['eta_rad'],
        'eta_mm':     res['eta_mm'],
        'eta_imn':    res['eta_imn'],
        'IL_dB':      res['IL_dB'],
        'PCE':        res['PCE'],
        'eta_pmic':   res['eta_pmic'],
        'eta_cadena': float(eta_cadena),
        'eta_total':  res['eta_total'],
        'P_in_dBm':   res['P_rf_dBm'],
        'P_in_uW':    res['P_rf_uW'],
        'P_incidente_uW': float(P_incidente_uW),
        'P_dc_uW':    res['P_dc_uW'],
    }


out = {}

rect = RectifierCircuit(topology='doubler', R_load=1300.0)
imn = LMatchNetwork(Z_src=50.0)

# ═══════════════════════════════════════════════════════════════════════════
# SIERPINSKI (Escenario A)
# ═══════════════════════════════════════════════════════════════════════════
sierp = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)

# (a) ambiente urbano difuso: cosecha AGREGADA de las 7 bandas, co-diseño
#     conjugado — reproduce el SSOT de 2,43 µW (ver decisión de modelado 1)
chain_amb = chain_conjugate_aggregate(sierp, rect, imn)
chain_amb['descripcion'] = (
    "Ambiente urbano difuso, cosecha agregada de 7 bandas (BANDS_A) por "
    "co-diseño conjugado integrado (sin interfaz de 50 Ω); "
    f"P_in={chain_amb['P_in_uW']:.1f} µW agregados (URBAN_AMBIENT_DBM, "
    "ya en el puerto de antena)."
)

# (b) fuente fuerte cercana: emisor intencional EN BANDA (p. ej. small cell 5G
#     a 3,30 GHz). NO se usa 2,45 GHz para el Sierpinski: esa frecuencia es
#     anti-resonancia del fractal (resonancias calibradas 1,84/3,68 GHz) y queda
#     FUERA del dominio de validez del acople; la banda de BANDS_A con mejor
#     acople es 3,30 GHz (5G_3.5). Ver decisión de modelado (2).
chain_fuerte = chain_los_wifi(eirp_dbm=20.0, dist_m=0.4, freq_ghz=3.30,
                              antenna=sierp, rectifier=rect, matching_net=imn)
chain_fuerte['descripcion'] = (
    "Fuente fuerte cercana — emisor intencional en banda (p. ej. small cell 5G "
    "a 3,3 GHz): EIRP=20,0 dBm, d=0,4 m (LOS de interior, sin corrección urbana "
    "NLOS), f=3,30 GHz, co-diseño conjugado de una sola banda. Se evita 2,45 GHz "
    "por ser anti-resonancia del Sierpinski (dominio de validez del acople)."
)

out['sierpinski'] = {
    'ambiente_urbano_difuso': chain_amb,
    'fuente_fuerte_cercana':  chain_fuerte,
}

# ═══════════════════════════════════════════════════════════════════════════
# PARCHE MICROCINTA (FR-4)
# ═══════════════════════════════════════════════════════════════════════════
patch = MicrostripPatchAntenna(2.45e9, 'FR4')

# (a) ambiente urbano difuso: cosecha AGREGADA de las 7 bandas, co-diseño
#     conjugado — reproduce el SSOT de 2,32 µW
chain_amb_p = chain_conjugate_aggregate(patch, rect, imn)
chain_amb_p['descripcion'] = (
    "Ambiente urbano difuso, cosecha agregada de 7 bandas (BANDS_A) por "
    "co-diseño conjugado integrado (sin interfaz de 50 Ω); "
    f"P_in={chain_amb_p['P_in_uW']:.1f} µW agregados (URBAN_AMBIENT_DBM, "
    "ya en el puerto de antena)."
)

chain_wifi_p = chain_los_wifi(eirp_dbm=20.0, dist_m=0.4, freq_ghz=2.45,
                              antenna=patch, rectifier=rect, matching_net=imn)
chain_wifi_p['descripcion'] = (
    "Fuente fuerte cercana tipo WiFi/router: EIRP=20,0 dBm, d=0,4 m (LOS de "
    "interior, sin corrección urbana NLOS), f=2,45 GHz, co-diseño conjugado "
    "de una sola banda (coincide con la banda de diseño f0 del parche)."
)

out['parche_FR4'] = {
    'ambiente_urbano_difuso': chain_amb_p,
    'fuente_fuerte_wifi':     chain_wifi_p,
}

# ═══════════════════════════════════════════════════════════════════════════
# FLPDA KOCH (Escenario B) — no se evalúa a 2.45 GHz (fuera de banda física,
# ver decisión de modelado 4). Se usa la comparación de distancias 100/1000 m
# ya existente en el pipeline (misma fuente TDT, dentro de su banda de diseño).
# ═══════════════════════════════════════════════════════════════════════════
flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                   f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
rect_flpda = RectifierCircuit(topology='doubler')  # sin IMN explícita (canónico)

# (a1) fuente "fuerte/cercana" dentro de su propia banda: TDT @ 100 m, 550 MHz
res_near = harvested_uw_full(72.15, 100, 0.550, flpda, rect_flpda, matching_net=None)
chain_near = from_harvested_full(res_near)
chain_near['descripcion'] = (
    "FLPDA no aplica a WiFi 2.45 GHz (fuera de su banda de diseño 470-900 MHz; "
    "forzarla violaría el dominio de validez del modelo). Sustituto honesto: "
    "fuente fuerte/cercana DENTRO de su banda — TDT DVB-T (EIRP=72.15 dBm) "
    "@ 100 m, 550 MHz (idéntico al caso canónico)."
)

# (a2) fuente "débil/lejana" dentro de su propia banda: TDT @ 1000 m, 550 MHz
res_far = harvested_uw_full(72.15, 1000, 0.550, flpda, rect_flpda, matching_net=None)
chain_far = from_harvested_full(res_far)
chain_far['descripcion'] = (
    "Fuente débil/lejana dentro de la banda de diseño de la FLPDA — "
    "TDT DVB-T (EIRP=72.15 dBm) @ 1000 m, 550 MHz."
)

# (b) TDT Cerro Nutibara @ 100 m — CANÓNICO, reutiliza CANONICAL sin recalcular
chain_canon = {
    'gain_dBi':   CANONICAL['gain_dBi'],
    'eta_rad':    CANONICAL['eta_rad'],
    'eta_mm':     CANONICAL['eta_mm'],
    'eta_imn':    CANONICAL['eta_imn'],
    'IL_dB':      None,
    'PCE':        CANONICAL['PCE'],
    'eta_pmic':   CANONICAL['eta_pmic'],
    'eta_cadena': round(CANONICAL['eta_mm'] * CANONICAL['eta_imn']
                         * CANONICAL['PCE'] * CANONICAL['eta_pmic'], 6),
    'eta_total':  CANONICAL['eta_total'],
    'P_in_dBm':   CANONICAL['P_in_dBm'],
    'P_in_uW':    CANONICAL['P_in_mW'] * 1000.0,
    'P_incidente_uW': round(CANONICAL['P_in_mW'] * 1000.0 / CANONICAL['eta_rad'], 4),
    'P_dc_uW':    CANONICAL['P_dc_uW'],
    'descripcion': (
        "TDT Cerro Nutibara @ 100 m, 550 MHz — caso CANÓNICO del documento. "
        "Reutiliza CANONICAL de configs/parametros.py sin recalcular; "
        "eta_cadena=67.36% (4 factores post-antena) sobre P_in en puerto "
        "(1982 µW), eta_total=40.23% (5 factores, con eta_rad) sobre "
        "P_incidente (≈3319 µW = P_in/eta_rad). Pequeño residuo en las "
        "identidades por el redondeo de los factores CANÓNICOS publicados."
    ),
}

out['flpda'] = {
    'fuente_cercana_100m':   chain_near,
    'fuente_lejana_1000m':   chain_far,
    'tdt_100m_canonico':     chain_canon,
}

# ── Verificación de reproducción exacta del canónico ─────────────────────────
_tol = 1e-6
assert abs(chain_near['P_dc_uW'] - CANONICAL['P_dc_uW']) < 0.05, (
    f"FLPDA@100m no reproduce P_dc_uW canónico: {chain_near['P_dc_uW']} vs "
    f"{CANONICAL['P_dc_uW']}")
assert abs(chain_near['eta_total'] - CANONICAL['eta_total']) < 1e-3, (
    f"FLPDA@100m no reproduce eta_total canónico: {chain_near['eta_total']} vs "
    f"{CANONICAL['eta_total']}")

# ── Guardar JSON ──────────────────────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "efficiency_values.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"[OK] {out_path}")

# ── Resumen [min, max] de eta_total por antena ────────────────────────────────
print("\n=== Resumen eta_total por antena (rango sobre sus escenarios) ===")
for antena, escenarios in out.items():
    vals = [(nombre, d['eta_total']) for nombre, d in escenarios.items()]
    etas = [v for _, v in vals]
    lo, hi = min(etas), max(etas)
    print(f"{antena:14s}: eta_total in [{lo*100:6.2f}%, {hi*100:6.2f}%]  "
          f"({', '.join(f'{n}={v*100:.2f}%' for n, v in vals)})")

print("\n=== Sanity check FLPDA @ TDT 100 m (canónico) ===")
print(f"P_dc_uW  = {chain_near['P_dc_uW']:.1f}  (canónico: {CANONICAL['P_dc_uW']})")
print(f"eta_cadena = {chain_near['eta_cadena']*100:.2f}%  (canónico ~67.36%)")
print(f"eta_total  = {chain_near['eta_total']*100:.2f}%  (canónico: "
      f"{CANONICAL['eta_total']*100:.2f}%)")
