# Fases 1–2 — Marco conceptual (dos modos) + matriz de escenarios

Fuente de redacción para el documento v6. Todos los números provienen del código
(`core/multiband.py`, `core/lora_budget.py`, canónicos vigentes) — cero valores a mano.

## Fase 1 — Reformulación del objetivo y del criterio de viabilidad

### Objetivo (reformulado)
De *"evaluar la viabilidad y elegir la mejor antena"* →
**"caracterizar dos topologías fractales de rectena y determinar las condiciones de
operación bajo las cuales cada una es favorable"**. Ninguna es superior en absoluto;
son complementarias y cubren nichos distintos del despliegue IoT real.

### Los dos modos de operación (anclados en literatura)
La distinción no es ad hoc: corresponde a dos regímenes reconocidos en RF energy
harvesting (Valenta & Durgin 2014; Kim et al. 2014, Proc. IEEE):

- **Modo 1 — sin batería / autonomía continua.** La cosecha instantánea supera de
  forma continua el umbral de operación del nodo. Criterio: `P_cosechada ≥ P_umbral`
  (p. ej. 438,5 µW para LoRa SF12). Requiere **fuente fuerte, conocida y cercana**.
- **Modo 2 — energía-asistido / net-positive (energy-neutral operation).** El nodo
  NO opera de forma continua: duerme, despierta esporádicamente y transmite con ciclo
  de trabajo bajo; una batería/supercondensador tampón amortigua los picos. Criterio:
  **`P_cosechada_media ≥ P_consumida_media`** (con ciclo de trabajo). Si el balance
  medio es positivo, el tampón nunca se agota. Habilita cosechas pequeñas (µW) en
  entornos dispersos.

El criterio del Modo 2 es el que rescata la topología multibanda: bajo "potencia
continua" era inviable; bajo "energía media con ciclo de trabajo" tiene un nicho real.

## Fase 2 — Matriz de escenarios (entorno → topología → sensor → modo → viabilidad)

| # | Entorno de despliegue | Fuente RF | Topología idónea | Sensor / ciclo | Modo | Resultado (modelo) |
|---|----------------------|-----------|------------------|----------------|------|--------------------|
| E1 | Sensor remoto con línea de vista a torre TDT (≤100 m) | DVB-T 550 MHz, 10 kW ERP (única, fuerte) | **FLPDA Koch dirigida** | LoRa SF12 continuo | **Modo 1** | 1.335 µW ≫ 438 µW → **viable, autonomía continua**; frontera ~175 m |
| E2 | Sensor en periferia de la torre (100–175 m) | misma TDT, más lejos | FLPDA dirigida | LoRa esporádico + tampón | Modo 1→2 | cae bajo umbral continuo hacia ~175 m; con tampón, ciclo bajo aún viable |
| E3 | Sensor urbano denso (techo, bajo repetidores WiFi/celular) | multibanda dispersa (GSM/LTE/WiFi/5G) | **Sierpinski multibanda integrada** | sensor ADC / telemetría muy esporádica | **Modo 2** | a −20 dBm/banda ≈ 2,4 µW → sostiene sensor ultra-bajo (1,2 µW), **no** LoRa continuo |
| E4 | Urbano muy denso / cerca de fuentes fuertes (−10 dBm/banda) | multibanda intensa | Sierpinski multibanda | telemetría periódica | Modo 2 | ≈83 µW → sostiene ciclos de trabajo moderados |
| E5 | Sensor en árbol/campo lejos de infraestructura | RF ambiental muy débil | ninguna capta suficiente | — | — | inviable por RF; requiere otra fuente (solar) — límite honesto |

### Números de respaldo (del modelo, Escenario A urbano difuso)
- Adaptación conjugada integrada: **6/7 bandas** con η_cm 0,43–0,74 (vs 1/7 en 50 Ω).
- Cosecha total vs ambiente (uniforme): −25→0,3 µW · −20→2,1 µW · −15→12 µW ·
  −10→83 µW · −5→466 µW. **El cuello de botella a niveles urbanos reales es el PCE
  del rectificador a baja potencia**, no el acople de la antena.
- Monte Carlo (10⁴, ambiente ±5 dB): mediana 2,3 µW, p95 46 µW, CV≈390 % — la
  viabilidad depende **abrumadoramente del sitio de despliegue** (tornado: ambiente
  562 % vs Q 23 % vs R_load 10 %).
- Sensor ADC (1,2 µW) viable a ambiente nominal (margen ≈2×); LoRa SF12 (438 µW)
  requiere ≥ −5 dBm/banda.

### Tipos de sensor por modo (para el documento)
- **Modo 1 (dirigida):** monitoreo continuo, telemetría frecuente, actuadores de
  bajo consumo con fuente fuerte a la vista.
- **Modo 2 (multibanda):** sensores de despertar esporádico — temperatura/humedad
  ambiental, conteo, presencia, telemetría cada minutos/horas — con tampón que se
  rellena entre eventos y nunca se descarga del todo.

## Limitaciones a declarar (integridad)
- Estudio de **modelado analítico**, no medición; sin prototipo (L1).
- El nivel RF ambiental es un **supuesto parametrizado** (rango Piñuela 2013), no
  medido en Medellín — de ahí que la viabilidad del Modo 2 se presente como **curva
  frente al ambiente**, no como un único valor.
- Arquitectura multibanda = **rectificador de varias ramas combinadas en DC**
  (Bode-Fano impide una sola red pasiva para 6 bandas).
- η_rad del FR-4 (0,32–0,61) y PCE de bajo nivel limitan la magnitud absoluta.
