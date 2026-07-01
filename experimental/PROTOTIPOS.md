# Prototipos animados — descripción detallada

Seis simulaciones de canvas (HTML/JS, 60 fps, se reproducen en el navegador) que
ilustran el trabajo de grado de forma visual y cercana. **Experimentales: no forman
parte de la aplicación oficial.** Todas usan los valores **canónicos** del proyecto
(`configs/parametros.py`), no inventan cifras.

- **Hub (una sola app con selector lateral):** `prototipos.py`
  `\.venv/Scripts/streamlit run prototipos.py`
- Cada simulación también corre suelta: `streamlit run prototipo_<nombre>.py`

## Material para póster / defensa / convención

El conjunto está pensado como material visual para exponer en público:

- **Portada (`prototipo_portada.py`)** — pantalla de apertura con el título del
  trabajo, las cifras de impacto (P_DC 1 638 µW, ≈546 mensajes/día, V_DC 1 459 mV,
  67,5 % conservado, G 7,10 dBi, RMSE 15,5 pp) y la guía de las seis simulaciones con
  la pregunta que responde cada una. Es la primera página del hub.
- **Exportar PNG** — cada lámina tiene un botón **⬇ PNG** (arriba a la derecha del
  canvas) que descarga la imagen actual para llevarla al póster o a las diapositivas.
  Los archivos salen como `rectena_flujo.png`, `doblador_greinacher.png`,
  `cascada_energia.png`, `espectro_urbano.png`, `escenario_a_vs_b.png`,
  `patron_radiacion.png`.
- **Estilo de presentación (`_proto_ui.py`)** — CSS común: tipografía legible a
  distancia, tarjetas de métricas con acento, y se oculta el chrome de Streamlit para
  un panel limpio en proyección. Los canvas se renderizan a ≥2× para que la imagen
  exportada sea nítida.

---

## 1. Cómo funciona la rectena — `prototipo_dia_sensor.py`

**Qué responde:** ¿qué le pasa a la energía desde la torre hasta que el sensor envía un mensaje?

**Qué muestra:** la cadena completa de izquierda a derecha, en movimiento:
torre TDT con ondas y baliza que parpadea → antena → rectificador → filtro/PMIC →
supercondensador que se carga → nodo IoT → gateway con nubecita de datos. Cada etapa
tiene su osciloscopio (RF alterna, rectificada, DC), un radiómetro de campo, y un
panel de lecturas (P_in, P_DC, mensajes, tiempo, cadencia real).

**Enriquecido en esta ronda:**
- **Pérdidas como calor**: partículas rojas que se desprenden en el rectificador (≈14 %)
  y el PMIC (≈12 %), haciendo visible que la eficiencia es un producto y dónde se pierde más.
- **Reflexión en la antena**: parte de la onda rebota (más cuanto más lejos), atado a S₁₁/η_mm.
- **Registro de mensajes**: panel "🛰 Mensajes recibidos" con los últimos envíos y su instante.
- **Gateway → nube** de datos para cerrar el lazo IoT.

**Controles:** distancia a la torre, perfil LoRa (SF7/SF9/SF12).
**Cifras canónicas:** P_DC(d)=P_DC(100 m)·(100/d)² (Friis), E_ciclo por perfil, arranque PMIC 130 mV.

---

## 2. El doblador Greinacher — `prototipo_doblador.py`

**Qué responde:** ¿cómo el rectificador convierte la RF alterna en continua y **duplica** la tensión?

**Qué muestra:** el esquemático (fuente RF, C1, nodo X, D1, D2, C2, R_L) animado
semiciclo a semiciclo: el diodo activo se ilumina, la corriente fluye por su rama,
los condensadores se cargan, y la salida V_DC sube hasta ≈ 1.459 mV. Osciloscopios de
entrada (AC) y salida (DC).

**Enriquecido en esta ronda:**
- **Curva I-V del diodo en vivo** (Shockley) con el punto de operación que se mueve:
  verde "conduce ▶" en directo, gris "bloquea ✕" en inverso.
- **Tensión del nodo X numérica**, que alcanza ~2·V_pico en el semiciclo positivo.
- **Badge de semiciclo** arriba (qué diodo conduce, qué condensador carga).
- **C1 y C2 con su voltaje** mostrado mientras se cargan.

**Controles:** velocidad de la animación, rótulos on/off.
**Cifras canónicas:** V_DC ≈ 2·(V_pico − V_f) ≈ 1.459 mV (SMS7630, §3.5, Apéndice E.8).

---

## 3. La cascada de energía — `prototipo_cascada.py`

**Qué responde:** ¿de dónde sale el resultado P_DC = 1.638 µW y dónde se pierde la energía?

**Qué muestra:** dos partes ligadas:
1. **El viaje en dB** (escalera): EIRP +70 dBm → −FSPL → −urbano → +ganancia → P_in,
   con un punto que recorre el camino.
2. **El río que se estrecha** (la conversión): P_in al 100 % se angosta en ×η_mm, ×η_IMN,
   ×PCE, ×η_PMIC hasta P_DC (67,5 % de P_in), con el calor que se escapa en cada etapa.

**Enriquecido en esta ronda:**
- **Conexión visual** entre las dos partes: un conector lleva P_in del final de la escalera
  a la cabecera del río (una sola travesía).
- **Dramatización del FSPL**: rótulo "↓ el grueso se pierde aquí, en el aire".
- **Cuello de botella** marcado en PCE y PMIC, con plumas de calor más grandes.
- **Contador** de energía perdida vs útil.

**Cifras canónicas:** EIRP 70 dBm, FSPL/urbano (ITU-R P.1546), ganancia 7,10 dBi,
cadena P_DC = P_in·η_mm·η_IMN·PCE·η_PMIC. El 67,5 % es lo que se conserva **de P_in** (4
factores), distinto de η_total (FOM de 5 factores). §4.3.1, Figura 5, Apéndice E.12.

---

## 4. El espectro urbano — `prototipo_espectro.py`

**Qué responde:** ¿qué señales hay en el aire y por qué el trabajo apunta a la TDT en UHF?

**Qué muestra:** un analizador de espectro (frecuencia en log) con la **franja verde de
cosecha (UHF 470–900 MHz)** y una antena que capta; barras por fuente con su EIRP: la
**TDT (70 dBm)** destaca (fuerte, estable, caracterizada → Escenario B), y las de alta
frecuencia (Wi-Fi, 5G) aparecen bajas y "variables" (→ Escenario A).

**Enriquecido en esta ronda:**
- **Skyline de ciudad** de fondo (lo cotidiano).
- **Shimmer** en las barras (sensación de analizador real).
- **Fundamento del escenario**: bloque permanente de dos tarjetas (TDT vs Wi-Fi/LTE/5G)
  que justifica por qué la TDT es fuente firme y blinda la elección de preguntas implícitas.
- **Modo «¿Qué pasa si…?»**: la sonda de sintonía es el control; los resultados son tres —
  **captación %**, **potencia disponible** (fracción de la P_in canónica de 2 427 µW que
  sobrevive a esa sintonía) e **indicador visual de adaptación** (barra rojo→ámbar→verde con
  estado Adaptada/Parcial/Desadaptada).
- **Comparador de fuentes**: tabla con badges de color (TDT, LoRa, LTE, Wi-Fi, 5G) en tres
  ejes — potencia, estabilidad y caracterización. La TDT es la única que gana en las tres;
  por eso es la fuente del Escenario B.

**Controles:** sonda/frecuencia de sintonía [MHz].
**Cifras canónicas:** EIRP de `RF_UHF` (TDT 70, LTE 46/43, LoRa GW 27 dBm); P_in 2 427 µW;
alta frecuencia (Wi-Fi/5G) valorada de forma cualitativa, no caracterizada (§1.1, Tabla 1).

---

## 5. Escenario A vs B — `prototipo_avsb.py`

**Qué responde:** ¿por qué hay dos escenarios?

**Qué muestra:** pantalla dividida.
- **A · Sierpinski:** fuentes urbanas (WiFi, LTE, 5G) cuya energía **rebota** (rojo); el
  fractal con sus **7 bandas explícitas** (6 ✗ rojas que rebotan, 1 ✓ verde adaptada,
  5G-3,5 GHz); medidor bajo (cotas superiores), mensajes/día firmes ≈ 0.
- **B · FLPDA Koch:** apunta a la torre TDT con su haz directivo, captación limpia, medidor
  que sube a 1.638 µW, ≈ 546 mensajes/día.

**Enriquecido en esta ronda:**
- **Las 7 bandas explícitas** en A (hace concreto el "1 de 7").
- **Mensajes/día** en ambos (B ≈ 546, A ≈ 0 firme).

**Cifras canónicas:** A S₁₁<−10 dB en 1/7 (5G-3,5 GHz, −16,4 dB); B S₁₁ continuo, G 7,10 dBi,
P_DC 1.638 µW. §4.1, §4.2, §4.4.

---

## 6. Patrón de radiación — `prototipo_patron.py`

**Qué responde:** ¿por qué la FLPDA hay que apuntarla y el Sierpinski no?

**Qué muestra:** diagrama polar (anillos en dBi) con **los dos patrones a la vez**: el
**lóbulo directivo** de la FLPDA y el **círculo cuasi-omni** del Sierpinski. La torre está
fija arriba; un rayo ámbar marca la **ganancia captada hacia la torre**.

**Enriquecido en esta ronda:**
- **Superposición** de A y B (el resaltado en negrita).
- **Antena que gira** físicamente (flecha de la FLPDA) con la orientación.
- **Consecuencia atada**: al desapuntar, caen **P_DC y los mensajes/día** (KPIs en vivo).

**Controles:** antena resaltada, orientación de la FLPDA [°].
**Cifras canónicas:** G máx FLPDA 7,10 dBi (550 MHz); P_DC y mensajes escalan con la
ganancia captada (ilustrativo). §2.4.4.

---

## Nota de rigor

Las **formas de onda** (AC, rectificada, DC), los **patrones** y los **niveles de cosecha
del espectro** son ilustrativos. Los **números** (P_in, P_DC, η, cadencia, ganancia, S₁₁)
y la física 1/d² son los **valores canónicos** del trabajo. Nada de esto está en git ni
forma parte de la aplicación oficial hasta que se decida integrarlo.
