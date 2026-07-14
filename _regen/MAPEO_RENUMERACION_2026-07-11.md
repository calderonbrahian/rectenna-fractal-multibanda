# Mapeo de renumeración — citas de Streamlit vs. documento vigente (v3)

Generado durante la auditoría de alineación Documento↔Código↔Streamlit↔GitHub (2026-07-13).
Verificado contra `Calderon_Munera_B_TG_UdeA_APA7_FINAL_13072026_v3.docx` (TOC + Lista de
tablas/figuras + Anexo B.13 extraídos directamente del XML).

**Causa raíz:** el documento se reestructuró el 2026-07-11 (Objetivos pasó de estar dentro del
Cap. 1 a ser el Cap. 2 independiente; Marco 2→3, Metodología 3→4, Resultados 4→5,
Conclusiones 5→6). Las citas `_ref(...)` de Streamlit se escribieron ANTES de esa
reestructuración y nunca se actualizaron. Este archivo es la referencia única para corregirlas.

## Capítulos y secciones (desplazamiento +1 para caps. 2–5 antiguos)

| Cita antigua (Streamlit) | Cita correcta (documento vigente) |
|---|---|
| §1.3 Alcance y limitaciones | §1.2 Alcance y limitaciones del estudio |
| §2.1 El sistema rectenna | §3.1 El sistema rectenna: arquitectura y eficiencia |
| §2.2 Estado del arte | §3.2 Estado del arte en rectenas fractales |
| §2.3 Geometría fractal | §3.3 Geometría fractal aplicada a antenas |
| §2.3.1 Dimensión de Hausdorff | §3.3.1 Dimensión de Hausdorff y autosimilitud |
| §2.3.2 Triángulo de Sierpinski | §3.3.2 Triángulo de Sierpinski: propiedades y dimensionado |
| §2.3.3 Curva de Koch | §3.3.3 Curva de Koch: reducción por iteración |
| §2.3.4 Compromisos miniaturización Koch | (subsección ya no existe; citar §3.3.3) |
| §2.4 / §2.4.2 / §2.4.3 / §2.4.4 Parámetros de antena | §3.4 Parámetros fundamentales de antenas y rectenas (sin subsecciones) |
| §2.5 Propagación RF y Friis | §3.5 Propagación RF y modelo de Friis |
| §2.6.2 Espectro UHF colombiano | §3.6.2 El espectro UHF colombiano (Escenario B) |
| §2.7 Física del diodo Schottky | §3.7 Física del diodo Schottky: modelo de Shockley y parámetros SPICE |
| §2.7.1 Ecuación de Shockley | §3.7.1 Ecuación de Shockley |
| §2.7.2 Parámetros SPICE / frecuencia de corte | §3.7.2 Parámetros SPICE del SMS7630 y frecuencia de corte |
| §2.8 Redes de adaptación (IMN) | §3.8 Redes de adaptación de impedancias (IMN) |
| §2.9 Métodos de análisis electromagnético | §3.9 Métodos de análisis electromagnético: enfoque adoptado y alternativas |
| §3.2 Justificación entorno Python | §4.2 Justificación del entorno Python de código abierto |
| §3.3 Arquitectura del pipeline de simulación | §4.3 Estructura del modelo de simulación (título cambió) |
| §3.4.1 Sierpinski modelo RLC | §4.4.1 Sierpinski: modelo RLC y resonancias |
| §3.4.2 FLPDA Koch método Carrel | §4.4.2 FLPDA Koch: método de Carrel y número de dipolos |
| §3.5 Módulo 2 — Cadena RF-DC | §4.5 Etapa 1: Geometrías fractales / Etapa 2: Cadena RF-DC (título cambió: "Módulo"→"Etapa") — usar §4.5 |
| §3.6 Módulo 3 — Presupuesto energético | §4.6 Etapa 3: Presupuesto energético del nodo IoT |
| §3.7 Estrategia de validación cruzada | §4.7 Estrategia de validación cruzada |
| §4.1 Escenario A | §5.1 Escenario A: Sierpinski (1,8–5,8 GHz) |
| §4.1.1 Resultados del modelo computacional | §5.1.1 Resultados del modelo computacional |
| §4.2 Escenario B | §5.2 Escenario B: FLPDA Koch (470–900 MHz) |
| §4.2.1 Diseño paramétrico | §5.2.1 Diseño paramétrico y dimensiones calculadas |
| §4.3 Caso de estudio Cerro Nutibara | §5.3 Caso de estudio: Cerro Nutibara |
| §4.3.1 Cálculo de la cadena de potencia | §5.3.1 Cálculo de la cadena de potencia |
| §4.3.2 Sensibilidad y Monte Carlo | §5.3.2 Robustez del resultado: incertidumbre, sensibilidad y Monte Carlo |
| §4.4 Análisis comparativo | §5.4 Análisis comparativo de los dos escenarios |
| §4.5 Validación cruzada y análisis del error | §5.5 Validación cruzada y análisis del error (RMSE = 15,50 pp) |
| §5.1 Conclusiones | §6.1 Conclusiones |
| §5.2 Aportaciones del trabajo | §6.2 Características del trabajo realizado (título cambió, reposicionamiento 2026-07-12) |
| §5.3 Limitaciones del estudio | §6.3 Limitaciones del estudio |
| §5.4 Trabajo futuro | §6.4 Recomendaciones y trabajo futuro |

## Apéndice → Anexo

| Cita antigua | Cita correcta |
|---|---|
| Apéndice E.N | Anexo B.N (N se conserva; ver tabla de abajo, los subtítulos también cambiaron de tema en algunos casos — verificar) |
| Apéndice E (sin número) | Anexo B |
| "Apéndice B" (acerca.py, sobre reproducibilidad) | No hay anexo de reproducibilidad — ese contenido vive en §4.2 (Justificación del entorno Python) y §3.2 del cuerpo principal. Reescribir la frase, no solo cambiar la letra. |

## Tablas (consolidación al Anexo B.13 o renumeración del cuerpo)

| Cita antigua | Tabla correcta vigente | Confianza |
|---|---|---|
| Tabla 2 (bandas del Escenario A) | Tabla B.11 (Anexo B) | Alta — título verificado idéntico |
| Tabla 3 (parámetros SPICE SMS7630) | Tabla B.12 (Anexo B) | Alta — título verificado idéntico |
| Tabla 4 (arquitectura del pipeline de simulación) | Tabla 2 (cuerpo, "Etapas del modelo de simulación", p.37) | Alta — verificado: tabla real en §4.3 con 4 etapas M1-M4 (Entrada/Proceso/Salida), coincide exactamente |
| Tabla 5 (desglose energético por ciclo) | Tabla B.13 (Anexo B) | Alta — título verificado idéntico |
| Tabla 6 (geometría de dipolos) | Tabla B.14 (Anexo B) | Alta — título verificado idéntico |
| Tabla 7 (PCE–P_in) | Tabla B.15 (Anexo B) | Alta — título verificado idéntico |
| Tabla 8 (presupuesto de enlace) | Tabla B.16 (Anexo B) | Alta — título verificado idéntico |
| Tabla 9 (cadena de potencia completa) | Tabla B.17 (Anexo B) | Alta — título verificado idéntico |
| Tabla 10 (comparación técnica integral) | Tabla 3 (cuerpo, p.49) | Alta — título verificado idéntico |
| Tabla 11 (comparación banda a banda / Wang) | Tabla B.18 (Anexo B) | Alta — título verificado idéntico |
| Tabla 12 (verificación de resonancias) | Tabla B.19 (Anexo B) | Alta — título verificado idéntico |
| Tabla 13 (limitaciones y soluciones) | Tabla 4 (cuerpo, p.57) | Alta — título verificado idéntico |
| Tabla 14 (resumen estructural por subsistema) | Tabla B.20 (Anexo B, referida desde §6.3) | Alta — mencionada explícitamente en la intro de §6.3 |

## Figuras (algunas fueron retiradas del cuerpo, no solo renumeradas)

| Cita antigua | Figura correcta vigente | Nota |
|---|---|---|
| Figura 1 (S11 Sierpinski) | Figura 9 | — |
| Figura 2 (η_total por banda) | **No existe en el cuerpo** | Retirada; vive solo en la plataforma/pipeline |
| Figura 3 (S11 FLPDA) | Figura 10 | — |
| Figura 4 (geometría del arreglo FLPDA) | Figura 6 | — |
| Figura 5 (cascada de eslabones) | Figura 11 | — |
| Figura 6 (P_DC vs distancia) | **No existe en el cuerpo** | Retirada; vive solo en la plataforma/pipeline |
| Figura 7 (T_ciclo vs distancia) | **No existe en el cuerpo** | Retirada; vive solo en la plataforma/pipeline |
| Figura 8 (tornado) | **No existe en el cuerpo** | Nunca estuvo en el cuerpo; solo pipeline/Streamlit |
| Figura 9 (Monte Carlo) | Figura 12 | — |
| Figura 10 (PCE ambos vs Pin) | Figura 13 | — |
| Figura 11 (modelo vs Wang) | Figura 14 | — |

Para las figuras "retiradas del cuerpo", la corrección es quitar el número de figura de la cita
(no inventar uno) y, si aplica, aclarar que ese gráfico es exclusivo de la plataforma interactiva.
