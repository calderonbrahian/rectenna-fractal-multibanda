"""
Escenario B — FLPDA Koch it.2, 470–900 MHz.
Tabs: S11 · Ganancia · Geometría · Presupuesto LoRa · PCE UHF

Escenario cuantitativo del proyecto: sustenta el resultado de referencia
(P_DC = 1 637,6 µW). Conserva las visualizaciones de mecanismo (región activa
del FLPDA, doblador Greinacher por semiciclo, curva I-V del diodo), que
corresponden a contenidos del informe.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from simulation.escenario_b import (
    run_sweep_freq_b, run_geometry_b,
    run_budget_lora, run_harvested_vs_dist,
    run_pce_uhf_curve,
)
from plots.charts import (
    fig_s11, fig_gain, fig_impedancia,
    fig_pce_pin, fig_harvested_vs_dist, COLORS,
)
from utils.exportar import sweep_a_csv
from configs.parametros import CANONICAL
from utils.pagina import (encabezado, badge_exploracion,
                          control_interactivo, donde_se_desarrolla as _ref)
from utils.glosario import glosario_pagina, metrica


def render():
    encabezado(
        "Escenario B — FLPDA Koch (diagnóstico cuantitativo)",
        "Antena log-periódica fractal it.2 · FR-4 · 470–900 MHz",
        que_es=("Página de **diagnóstico** del modelo de la antena log-periódica fractal "
                 "(FLPDA) Koch. Muestra el comportamiento del modelo en función de la "
                 "frecuencia: coeficiente de reflexión, ganancia realizada, impedancia "
                 "de entrada, geometría de los 8 dipolos y conversión a potencia DC útil."),
        para_que_sirve=("Verificar las propiedades clave de la antena del Escenario B: "
                         "que opera en la banda 470–900 MHz, que el S₁₁ es bajo, que la "
                         "ganancia es ≈ 7 dBi en banda y entender de dónde sale el "
                         "valor canónico de P_DC = 1 637,6 µW del escenario de referencia."),
        entradas=("Controles dentro de cada pestaña: distancia al transmisor TDT (en "
                  "*Presupuesto LoRa*), selectores de frecuencia para las curvas PCE-vs-Pin "
                  "y la región activa del arreglo de dipolos."),
        salidas=("Gráficas de S₁₁(f), ganancia(f), impedancia(f), tabla de los 8 dipolos, "
                  "vista de lado de la antena con la región activa resaltada, miniaturización "
                  "de Koch, curva PCE-vs-Pin, esquemático del doblador y curva I-V del diodo."),
        como_leer=("**S₁₁ < −10 dB** en banda significa que la antena está bien adaptada "
                   "(refleja menos del 10 % de la potencia incidente). La región activa "
                   "se *desplaza* sobre el boom con la frecuencia: dipolos largos a f baja, "
                   "dipolos cortos a f alta. Esto es lo que hace que la antena sea de "
                   "banda ancha sin necesidad de redes de adaptación complejas."),
    )

    badge_exploracion("Esta página es **diagnóstico técnico**: muestra el comportamiento "
                       "del modelo de la antena en toda la banda. El **resultado de "
                       "referencia** (P_DC = 1 637,6 µW) se presenta en **Resultados de "
                       "Referencia del Proyecto**.")

    st.markdown(
        "**Topologías** presentó la FLPDA como la apuesta *cuantitativa*: una antena "
        "**dirigida** que apunta a una fuente real y bien caracterizada —el transmisor de "
        "TDT del Cerro Nutibara—. La pregunta que pone a prueba este escenario es **cuánta "
        "energía útil puede entregar**.\n\n"
        "**Si la antena cumpliera su papel**, deberíamos ver cuatro cosas: adaptación "
        "**continua** en toda la banda UHF (no en puntos sueltos como el Sierpinski), una "
        "**ganancia** que concentre la energía hacia la torre, una geometría **compacta** "
        "pese a operar en UHF, y una potencia continua que **baste para arrancar y "
        "sostener** un nodo IoT a distancias realistas. Las pestañas lo comprueban una a una."
    )
    _ref("§3.4.2 FLPDA Koch: método de Carrel y número de dipolos · "
         "§4.2 Escenario B — FLPDA Koch (470–900 MHz) · "
         "§2.3.3 Curva de Koch: reducción por iteración")

    with st.spinner("Barrido de frecuencia FLPDA..."):
        sweep = run_sweep_freq_b()
    with st.spinner("Calculando geometría..."):
        geom  = run_geometry_b()

    st.markdown(
        "**Primera comprobación: ¿es una antena viable para UHF?** Una antena dirigida para "
        "esta banda debería ser razonablemente compacta y rondar 7–9 dBi de ganancia. Estos "
        "son sus números de partida:"
    )
    with st.container(horizontal=True):
        st.metric("Elementos FLPDA",  geom['n_elements'],             border=True)
        st.metric("Boom físico",       f"{geom['boom_cm']} cm",        border=True)
        st.metric("L_máx física",      f"{geom['L_max_phys_cm']} cm",  border=True)
        st.metric("Reducción Koch",    f"−{geom['reduccion_pct']}%",   border=True)
        metrica("Ganancia @ 550 MHz", f"{CANONICAL['gain_dBi']:.2f} dBi",
                interpretacion="alta para el objetivo (7–9 dBi es lo esperado en una LPDA)",
                ayuda="Ganancia realizada; concentra la energía hacia la torre TDT. Más "
                      "ganancia → más P_in → mayor P_DC.")
    st.caption(
        ":material/lightbulb: **Geometría:** 8 dipolos sobre un boom de ~50 cm; la curva de "
        "Koch **reduce −43 % la dimensión** del dipolo sin cambiar su frecuencia → antena "
        "más compacta para el mismo rango de operación."
    )

    st.divider()

    glosario_pagina("S11", "adaptación", "ganancia", "impedancia", "PCE", "P_DC")
    tab_s11, tab_gain, tab_geom, tab_budget, tab_pce = st.tabs([
        ":material/show_chart: S11",
        ":material/trending_up: Ganancia",
        ":material/schema: Geometría",
        ":material/bolt: Presupuesto LoRa",
        ":material/percent: PCE UHF",
    ])

    with tab_s11:
        st.markdown(
            "Lo primero que debe cumplir la antena es **dejar entrar la energía** en toda la "
            "banda de la fuente. La línea de **−10 dB** es el aprobado; la zona sombreada es "
            "la banda de diseño (470–900 MHz). A diferencia del Sierpinski, aquí "
            "esperaríamos ver la curva **por debajo del umbral en toda la banda**, no solo "
            "en un punto:"
        )
        fig = fig_s11(sweep['freqs_MHz'], sweep['s11_dB'],
                      'S11 — FLPDA Koch it.2 (470–900 MHz)', xunit='MHz')
        fig.add_vrect(
            x0=sweep['f_low_MHz'], x1=sweep['f_high_MHz'],
            fillcolor='rgba(52, 211, 153, 0.10)',
            line_color='rgba(52, 211, 153, 0.4)',
            annotation_text='Banda de diseño',
            annotation_position='top left',
            annotation_font_size=10,
        )
        st.plotly_chart(fig)
        st.markdown(
            "**¿Qué nos muestra esta evidencia?**\n\n"
            "La FLPDA mantiene **S₁₁ < −10 dB de forma continua** en toda la banda UHF. Es "
            "el contraste directo con el Sierpinski: allí solo una de siete bandas se "
            "adaptaba; aquí la antena acepta la energía **en todo el rango** de la fuente "
            "TDT. La primera condición de la cadena —que la energía entre— se cumple.\n\n"
            "Que la energía entre bien no dice todavía **cuánta** se capta ni hacia dónde. "
            "Eso depende de cuánto **concentre** la antena la señal hacia la torre: la "
            "siguiente pestaña, *Ganancia*."
        )
        _ref("§2.4.3 Coeficiente de reflexión y parámetros S · "
             "§4.2.1 Diseño paramétrico y dimensiones calculadas · "
             "Figura 3 (S₁₁ FLPDA Koch)")

    with tab_gain:
        st.markdown(
            "Una antena dirigida no capta por igual en todas direcciones: **concentra** la "
            "energía hacia donde apunta. Cuanta más ganancia, más potencia recoge de la "
            "torre. ¿Cuánta ganancia logra la FLPDA en su banda?"
        )
        fig = fig_gain(sweep['freqs_MHz'], sweep['gain_dBi'],
                       'Ganancia realizada FLPDA Koch (modelo paramétrico, base ≈ 7,5 dBi)', xunit='MHz')
        fig.add_vrect(
            x0=sweep['f_low_MHz'], x1=sweep['f_high_MHz'],
            fillcolor='rgba(96, 165, 250, 0.08)',
            line_color='rgba(96, 165, 250, 0.3)',
        )
        st.plotly_chart(fig)
        st.markdown(
            f"**Lo que se observa:** la ganancia realizada se mantiene en torno a "
            f"**{CANONICAL['gain_dBi']:.1f} dBi** en la banda (η_rad = "
            f"{CANONICAL['eta_rad']:.3f}), un valor consistente con lo que Carrel (1961) "
            f"predice para una log-periódica de {geom['n_elements']} elementos (7–9 dBi). La "
            f"antena, por tanto, **concentra bien** la energía hacia la torre TDT.\n\n"
            "Adaptación continua y buena ganancia significan que **mucha energía entra y se "
            "concentra**. Queda la pregunta que de verdad cuantifica el escenario: a una "
            "distancia real de la torre, **¿cuánta potencia continua llega al nodo?** Eso se "
            "mide en *Presupuesto LoRa*. *(Curva del modelo paramétrico de Carrel, §3.4.2; "
            "no es una figura del documento.)*"
        )
        _ref("§2.4.4 Directividad, eficiencia de radiación y ganancia · "
             "§3.4.2 FLPDA Koch: método de Carrel y número de dipolos")

    with tab_geom:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Parámetros de diseño")
            with st.container(border=True):
                st.markdown(f"- **τ** = 0.90 (razón de escala Carrel)")
                st.markdown(f"- **σ** = 0.15 (espaciado relativo)")
                st.markdown(f"- **N elementos** = {geom['n_elements']}")
                st.markdown(f"- **k_red Koch it.2** = (3/4)² = {geom['k_red']:.4f}")
                st.markdown(f"- **Reducción física** = {geom['reduccion_pct']}%")
                st.markdown(f"- **Boom** = {geom['boom_cm']} cm")
                st.markdown(f"- **L_máx física** = {geom['L_max_phys_cm']} cm")
        with col2:
            st.markdown("#### Tabla de dipolos")
            df = pd.DataFrame({
                'Dipolo':      list(range(1, geom['n_elements'] + 1)),
                'f_res [MHz]': [round(f, 1) for f in geom['res_freqs_MHz']],
                'L_elec [cm]': [round(l, 1) for l in geom['lengths_elec_cm']],
                'L_fís [cm]':  [round(l, 1) for l in geom['lengths_phys_cm']],
                'Pos. [cm]':   [round(p, 1) for p in geom['positions_cm']],
            })
            st.dataframe(df, hide_index=True)
            st.caption(":material/content_copy: Corresponde a la **Tabla 6** del trabajo "
                       "(geometría de los dipolos Koch).")

        st.divider()
        st.markdown("#### La antena en imágenes — *qué estamos diseñando*")

        # ── Vista de lado del FLPDA Koch + slider de frecuencia activa ──────
        st.markdown(
            "**Vista de lado de la antena.** El boom es la línea horizontal central. "
            "Los 8 dipolos son las barras verticales: largos a la izquierda "
            "(resonantes a baja frecuencia), cortos a la derecha (alta frecuencia). "
            "La región activa cambia con la frecuencia: solo los dipolos cuya "
            "longitud está cerca de λ/2 participan en la radiación."
        )
        st.markdown(
            "**Predice antes de mover:** al **subir** la frecuencia, ¿se activarán los "
            "dipolos **largos** (izquierda) o los **cortos** (derecha)? Mueve el control y "
            "compruébalo."
        )
        freq_active = st.select_slider(
            "Frecuencia operativa [MHz]",
            options=[470, 550, 600, 700, 800, 900],
            value=550,
            key="freq_active_flpda",
            help="Cada frecuencia activa un subconjunto distinto de dipolos.",
        )
        st.plotly_chart(_fig_flpda_schematic(geom, freq_active), width="stretch",
                         key="flpda_active_region")
        st.caption(
            ":material/lightbulb: El **dipolo amarillo brillante** es el más activo "
            "(longitud más cercana a λ/2). Los azules tenues están fuera de resonancia. "
            "La línea verde discontinua marca λ/2 a la frecuencia seleccionada para "
            "comparar con las longitudes de los dipolos. La radiación es **endfire** "
            "hacia el apex (la flecha verde)."
        )

        st.markdown("")
        st.markdown(
            "##### La miniaturización de Koch en una imagen"
        )
        st.markdown(
            "Varias versiones del **mismo dipolo** con la misma longitud total de conductor "
            "(la que fija la frecuencia de resonancia), pero **extensión física distinta**. "
            "Cuanto mayor la iteración de Koch, más se *encoge* el dipolo lateralmente "
            "manteniendo la resonancia. Esta es la razón de ser de la geometría fractal."
        )
        koch_extended = st.toggle(
            "Llegar al límite fractal (iteraciones 3 y 4)",
            value=False,
            key="koch_extended",
            help="Activar para ver cómo la curva tiende al monstruo fractal: a iter 4 "
                  "tiene 256 segmentos y ocupa solo el 31,6 % del espacio rectilíneo.",
        )
        st.plotly_chart(_fig_koch_miniaturization(extended=koch_extended), width="stretch")
        if koch_extended:
            st.caption(
                ":material/info: A iteración 4 la curva tiene 4⁴ = **256 segmentos** "
                "y el dipolo ocupa solo el **31,64 %** del espacio rectilíneo equivalente. "
                "El trabajo adopta la iteración 2 por razones de fabricación (fresado SMD): "
                "más allá, el conductor empieza a tener detalles del orden de la décima de "
                "milímetro y las pérdidas óhmicas crecen más rápido que la miniaturización."
            )
        else:
            st.caption(
                ":material/info: La iteración 2 (verde, adoptada en este trabajo) tiene "
                "sólo el **56,25 %** de la extensión física del dipolo rectilíneo equivalente. "
                "Aplicado a los 8 dipolos del FLPDA, eso reduce la silueta de la antena "
                "sin cambiar la frecuencia de operación."
            )

        st.divider()
        st.markdown("##### Diseño paramétrico — *por qué τ = 0,90 y σ = 0,15*")
        st.markdown(
            "Al variar los dos parámetros de Carrel, el arreglo cambia: "
            "**τ** (razón de escala) controla cuán parecidas son las longitudes de "
            "dipolos consecutivos; **σ** (factor de espaciado relativo) controla "
            "qué tan separados van. El diseño del proyecto (τ = 0,90, σ = 0,15) es "
            "el equilibrio entre ganancia, banda y tamaño."
        )
        col_tau, col_sigma = st.columns(2)
        with col_tau:
            tau_param = st.slider("τ (razón de escala)",
                                  min_value=0.80, max_value=0.95,
                                  value=0.90, step=0.01, key="tau_param",
                                  help="Más alto → más dipolos → más ganancia pero antena más larga.")
        with col_sigma:
            sigma_param = st.slider("σ (espaciado relativo)",
                                    min_value=0.10, max_value=0.22,
                                    value=0.15, step=0.01, key="sigma_param",
                                    help="Más alto → más separación entre dipolos → boom más largo.")

        # Recalcular geometría con los parámetros del usuario
        from core.flpda import FLPDA_Koch
        flpda_param = FLPDA_Koch(tau=tau_param, sigma=sigma_param,
                                  f_low=470e6, f_high=900e6, koch_iter=2)
        geom_param = {
            'n_elements':      flpda_param.n_elements,
            'positions_cm':    (flpda_param.positions * 100).tolist(),
            'lengths_phys_cm': (flpda_param.lengths_phys * 100).tolist(),
            'lengths_elec_cm': (flpda_param.lengths_elec * 100).tolist(),
            'res_freqs_MHz':   (flpda_param.resonant_freqs / 1e6).tolist(),
            'boom_cm':         flpda_param.boom_length_m * 100,
        }
        # KPIs del diseño paramétrico
        is_canonical = (abs(tau_param - 0.90) < 1e-9) and (abs(sigma_param - 0.15) < 1e-9)
        with st.container(horizontal=True):
            st.metric("N dipolos", f"{geom_param['n_elements']}",
                       delta="canónico = 8" if not is_canonical else "canónico ✓",
                       delta_color="off", border=True)
            st.metric("Boom", f"{geom_param['boom_cm']:.1f} cm",
                       delta="canónico = 50 cm" if not is_canonical else "canónico ✓",
                       delta_color="off", border=True)
            st.metric("L_max físico", f"{geom_param['lengths_phys_cm'][0]:.1f} cm",
                       delta="canónico = 17,9 cm" if not is_canonical else "canónico ✓",
                       delta_color="off", border=True)
            # Ganancia heurística: G0 = 7,5 + 0,5·log10(N/8)
            import math
            G0 = 7.5 + 0.5 * math.log10(geom_param['n_elements'] / 8)
            st.metric("Ganancia base", f"{G0:.2f} dBi",
                       delta="canónico = 7,50 dBi" if not is_canonical else "canónico ✓",
                       delta_color="off", border=True)

        st.plotly_chart(
            _fig_flpda_schematic(geom_param, freq_active_mhz=550),
            width="stretch", key="flpda_parametric",
        )
        st.caption(
            f":material/lightbulb: Con τ = {tau_param:.2f} y σ = {sigma_param:.2f}, "
            f"el arreglo tiene **{geom_param['n_elements']} dipolos** sobre un boom de "
            f"**{geom_param['boom_cm']:.1f} cm**. "
            "La sección responde a preguntas como "
            "*'¿qué pasaría si τ fuera 0,80?'* (menos dipolos, menos ganancia) "
            "o *'¿por qué no σ = 0,22?'* (boom más largo sin ganancia adicional)."
        )
        _ref("§3.4.2 FLPDA Koch: método de Carrel · §2.3.3 Curva de Koch: reducción por "
             "iteración · §2.3.4 Compromisos de la miniaturización Koch · "
             "§4.2.1 Diseño paramétrico y dimensiones · "
             "Figura 4 (geometría del arreglo) · Tabla 6 (geometría de dipolos) · "
             "Apéndice E.4 Mapa de diseño τ–σ")

    with tab_budget:
        st.markdown("#### Potencia cosechada DC en el nodo IoT")
        with st.container(border=True):
            st.markdown("**:material/tune: Distancia a la fuente TDT**")
            c_dist, c_dinfo = st.columns([1, 1])
            with c_dist:
                dist_m = st.slider(
                    "Distancia fuente–antena [m]",
                    min_value=50, max_value=2000, value=500, step=50,
                )
            with c_dinfo:
                st.caption("Propagación: FSPL + corrección urbana ITU-R P.1546 +6 dB")
                st.caption("Antena: FLPDA Koch it.2 · τ = 0,90 · σ = 0,15")
        control_interactivo(
            magnitud="**Distancia** entre la antena y la torre TDT del Cerro Nutibara, "
                     "en metros.",
            referencia="**100 m** en el escenario de referencia (P_DC = 1 638 µW); el "
                       "control parte de 500 m.",
            al_subir="La potencia recibida cae como 1/d² (Friis): más lejos → menos P_DC, "
                     "períodos entre mensajes más largos y, pasado cierto punto, el PMIC "
                     "deja de arrancar.",
            al_bajar="Más cerca → más P_DC y mensajes más frecuentes, hasta saturar el "
                     "techo de la cadena.",
            limite="Por debajo de ~50 m la hipótesis de campo lejano y la corrección "
                   "urbana media dejan de ser fiables; más allá de ~1 000 m el cold-start "
                   "(V_DC ≥ 130 mV) ya no está asegurado.",
        )
        st.markdown(
            "**Explóralo tú:** mueve la distancia y vigila dos umbrales. ¿A qué distancia el "
            "**V_DC cae por debajo de 130 mV** y el nodo ya no arranca? ¿Y cómo cambia el "
            "margen al pasar de **SF12** (lento, robusto) a **SF7** (rápido, exigente)?"
        )
        with st.spinner(f"Presupuesto a {dist_m} m..."):
            budget = run_budget_lora(dist_m=float(dist_m))
        st.caption(f"Modelo: cadena completa Shockley sobre P_in (4 factores: "
                   f"η_mm · η_IMN · PCE · η_PMIC). Resultados a **d = {dist_m} m**, "
                   f"recalculados con el control de arriba.")

        # ── KPIs reactivos a la distancia seleccionada (fuente TDT) ─────────
        _tdt_key = next(iter(budget['cosecha']))            # 'TV UHF (DVB-T)'
        _sf12_key = next(iter(budget['cosecha'][_tdt_key])) # primer perfil = SF12
        _tdt = budget['cosecha'][_tdt_key][_sf12_key]
        _cold_ok = _tdt['Vdc_mV'] >= CANONICAL['V_cs_mV']
        with st.container(horizontal=True):
            st.metric(f"P_DC (TDT @ {dist_m} m)", f"{_tdt['P_cosechada_uW']:.1f} µW",
                      delta=f"{_tdt['P_cosechada_uW'] - CANONICAL['P_dc_uW']:+.0f} µW vs canónico (100 m)",
                      delta_color="off", border=True)
            st.metric("P recibida en antena", f"{_tdt['Pr_dBm']:.1f} dBm", border=True)
            st.metric("V_DC al PMIC", f"{_tdt['Vdc_mV']:.0f} mV",
                      delta="≥ 130 mV: arranca ✓" if _cold_ok else "< 130 mV: NO arranca ✗",
                      delta_color="off", border=True)
            _margen = _tdt['margen_uW']
            st.metric("Margen vs consumo SF12", f"{_margen:+.1f} µW",
                      delta="sostenible" if _margen > 0 else "déficit",
                      delta_color="normal" if _margen > 0 else "inverse", border=True)

        # ── Tabla reactiva: cada fuente RF × cada perfil LoRa ───────────────
        st.markdown("**Presupuesto por fuente RF y perfil LoRa** — "
                    "*¿qué fuente sostiene qué perfil a esta distancia?*")
        _rows = []
        for _src, _profs in budget['cosecha'].items():
            _first = next(iter(_profs.values()))
            _row = {
                'Fuente RF': _src,
                'P_rx [dBm]': _first['Pr_dBm'],
                'P_DC [µW]': _first['P_cosechada_uW'],
                'V_DC [mV]': _first['Vdc_mV'],
            }
            for _prof, _d in _profs.items():
                _sf = _prof.split()[1]  # 'SF12', 'SF9', 'SF7'
                _row[_sf] = ("✓ " if _d['viable'] else "✗ ") + f"{_d['margen_uW']:+.1f} µW"
            _rows.append(_row)
        st.dataframe(pd.DataFrame(_rows), hide_index=True,
                     column_config={
                         'SF12': st.column_config.TextColumn('SF12 (margen)', help="✓ = P_DC supera el consumo medio del perfil; el número es el margen."),
                         'SF9':  st.column_config.TextColumn('SF9 (margen)'),
                         'SF7':  st.column_config.TextColumn('SF7 (margen)'),
                     })
        st.markdown(
            "**Lo que vas viendo:** al alejarte, la potencia recibida cae 6 dB por cada "
            "duplicación de distancia (Friis ∝ 1/d²), y la potencia continua cae aún más "
            "rápido, porque a baja señal el diodo convierte peor (zona sub-umbral de "
            "Shockley). Cuando V_DC baja de 130 mV, el nodo ya no arranca por sí solo, "
            "aunque coseche algo de energía. **Ese par —cuánta energía y si arranca— es la "
            "respuesta cuantitativa del Escenario B a su pregunta.**"
        )

        st.divider()

        # ── Curva P_DC vs distancia con marcador en la distancia elegida ─────
        with st.spinner("Curva P_DC vs distancia..."):
            dist_data = run_harvested_vs_dist()
        _fig_dist = fig_harvested_vs_dist(dist_data)
        _fig_dist.add_vline(
            x=dist_m, line=dict(color='#B45309', dash='dash', width=1.6),
            annotation_text=f"d = {dist_m} m (slider)",
            annotation_position='top right', annotation_font_size=10,
        )
        st.plotly_chart(_fig_dist, key="curva_pdc_dist")
        st.caption(
            "Modelo: Friis (Pozar eq. 2.6) + ITU-R P.1546 +6 dB | "
            "Shockley cadena completa | PMIC BQ25504 η=85 % | cold-start 130 mV. "
            "La **línea vertical ámbar** sigue al slider de distancia: donde cruza cada "
            "curva de color es la P_DC de esa fuente; las líneas punteadas horizontales "
            "son el consumo medio de cada perfil LoRa — si el cruce queda por encima, "
            "el nodo es autónomo con esa fuente y ese perfil."
        )

        st.info(
            ":material/cell_tower: **El mapa de viabilidad operativa** "
            "(EIRP × distancia × SF, modo autónomo, mensajes/día) está en "
            "**Aplicación IoT → Viabilidad IoT**. Esta página es diagnóstico técnico "
            "del modelo; aquella es la conclusión de uso.",
            icon=":material/info:",
        )
        _ref("§3.6 Módulo 3 — Presupuesto energético del nodo IoT · "
             "§2.5 Propagación RF y modelo de Friis · §4.3 Caso de estudio: Cerro Nutibara · "
             "Figura 6 (P_DC vs distancia) · Figura 7 (T_ciclo vs distancia) · "
             "Tabla 8 (presupuesto de enlace) · Tabla 9 (cadena de potencia completa)")

    with tab_pce:
        f_mhz_sel = st.select_slider(
            "Frecuencia [MHz]", options=[470, 550, 700, 800, 900, 915], value=550,
            help="Frecuencia a la que se traza la curva PCE-vs-Pin. Es una vista; el "
                 "escenario de referencia es 550 MHz (canal 30 TDT).",
        )
        st.markdown(
            "**Explóralo tú:** el escenario de referencia opera a 550 MHz. Cambia la "
            "frecuencia y observa cómo se desplaza la curva — ¿la PCE mejora o empeora al "
            "subir en la banda? Lo retoma la pregunta de más abajo (*¿en qué punto del UHF "
            "conviene operar?*)."
        )
        with st.spinner(f"Curva PCE @ {f_mhz_sel} MHz..."):
            pce_data = run_pce_uhf_curve(f_hz=float(f_mhz_sel) * 1e6)
        fig = fig_pce_pin(
            pce_data['Pin_dBm'],
            {'PCE Shockley [%]': pce_data['PCE_pct']},
            f'PCE rectificador doubler SMS7630 @ {f_mhz_sel} MHz',
        )
        # Marca del punto canónico
        fig.add_vline(x=CANONICAL['P_in_dBm'],
                       line=dict(color='#B45309', dash='dash', width=1.4),
                       annotation_text=f"P_in canónico = {CANONICAL['P_in_dBm']:.2f} dBm",
                       annotation_position='top right',
                       annotation_font_size=10)
        st.plotly_chart(fig)
        st.markdown(
            f"**Lo que se observa:** la PCE crece con la potencia de entrada hasta saturar "
            f"en el techo del modelo (~{CANONICAL['PCE']*100:.0f} %); la línea vertical "
            f"marca el P_in canónico del escenario de referencia. Y aquí está el contraste "
            f"con el Sierpinski: allí la señal ambiental era débil y la PCE quedaba muy por "
            f"debajo del techo; aquí la fuente TDT es **potente y estable**, así que el "
            f"rectificador trabaja **cerca de su máximo**. *(Modelo PCE–P_in, Tabla 7; la "
            f"versión combinada de ambos escenarios es la Figura 10.)*"
        )
        st.download_button(
            "Descargar CSV", sweep_a_csv(pce_data),
            file_name=f"pce_uhf_{f_mhz_sel}MHz.csv", mime="text/csv",
        )
        _ref("§2.7.2 Parámetros SPICE del SMS7630 y frecuencia de corte · "
             "§4.3.1 Cálculo de la cadena de potencia · "
             "Tabla 7 (dependencia PCE–P_in) · Figura 10 (PCE vs P_in, ambos escenarios)")

        st.divider()
        st.markdown("##### ¿En qué punto del UHF conviene operar?")
        st.markdown(
            "El barrido de potencia continua vs frecuencia (Tab *Presupuesto LoRa*) "
            "muestra que dentro de la banda 470–900 MHz **el óptimo se sitúa entre "
            "500 y 600 MHz** por dos razones que compiten:"
        )
        st.markdown(
            "- **A frecuencia más baja**: menor FSPL → más potencia disponible (gana).\n"
            "- **A frecuencia más alta**: mayor PCE del rectificador (gana hasta la "
            "  saturación) y mejor adaptación con la red L de diseño.\n\n"
            f"El **canal 30 de UHF Colombia (550 MHz)** del transmisor TDT cae "
            "justamente en el punto de equilibrio y por eso es el elegido como "
            "escenario de referencia. Esto **no es coincidencia**: la antena se "
            "diseñó para esa banda."
        )
        _ref("§2.6.2 El espectro UHF colombiano — Escenario B · "
             "§4.3 Caso de estudio: Cerro Nutibara")

        st.divider()
        st.markdown("##### Cómo funciona el doblador Greinacher — *paso a paso*")
        st.markdown(
            "El rectificador es la pieza que define la PCE del trabajo. Esta es "
            "su topología (dos diodos Schottky SMS7630 y dos capacitores), con el "
            "camino de corriente resaltado en cada semiciclo de la RF."
        )
        modo_rect = st.segmented_control(
            "Estado del circuito",
            options=["Semiciclo +", "Semiciclo −", "Régimen DC (ambos)"],
            default="Semiciclo +",
            key="modo_doubler",
        ) or "Semiciclo +"
        st.plotly_chart(_fig_greinacher_doubler(modo_rect), width="stretch")
        if modo_rect == "Semiciclo +":
            st.caption(
                ":material/bolt: **Durante el semiciclo positivo de la RF**: la tensión "
                "de entrada se *suma* a la carga acumulada en C1 (de un ciclo previo). "
                "El nodo X alcanza ≈ 2·V_pico, **D2 conduce** y C2 se carga al doble del "
                "pico (menos la caída V_f de cada diodo). De aquí sale el *doblado*."
            )
        elif modo_rect == "Semiciclo −":
            st.caption(
                ":material/bolt: **Durante el semiciclo negativo**: la entrada se "
                "vuelve negativa, el nodo X intenta bajar por debajo de tierra, "
                "**D1 conduce** y bloquea esa caída. C1 se carga al valor de pico "
                "con la polaridad necesaria para que en el siguiente semiciclo + "
                "se sume."
            )
        else:
            st.caption(
                ":material/bolt: **En régimen DC permanente** (lo que ve la carga): "
                "C2 mantiene V_DC ≈ 2·(V_pico − V_f) constante. **Ambos diodos** "
                "conducen alternadamente, pero la salida es DC porque C2 actúa "
                "como reservorio. Esta es la ecuación V_DC = N·(V_oc,pk − V_f) con N=2."
            )
        _ref("Apéndice E.8 Operación interna del doblador Greinacher · "
             "§3.5 Módulo 2 — Cadena RF-DC con Python/SciPy")

        st.divider()
        st.markdown("##### El diodo Schottky en su curva característica")
        st.markdown(
            "El comportamiento físico del SMS7630 está descrito por la ecuación de Shockley:"
        )
        st.latex(r"I_D = I_S \left( e^{V_D / (n\,V_T)} - 1 \right)")
        st.markdown(
            "donde **I_D** es la corriente del diodo [A], **V_D** la tensión sobre la unión "
            "[V], **I_S** la corriente de saturación inversa [A], **n** el factor de "
            "idealidad (adimensional) y **V_T** el voltaje térmico (≈ 25,85 mV a 300 K). "
            "La corriente crece **exponencialmente** con V_D: por eso el diodo pasa de "
            "casi-aislante a conductor en una franja estrecha de tensión."
        )
        st.markdown(
            "El punto operativo sobre la curva I-V se sitúa con el control de esta sección, y muestra "
            "la corriente del diodo y su **resistencia dinámica** "
            "R_d = n·V_T / (|I| + I_S). El cambio de R_d con el punto operativo es la "
            "razón por la que el rectificador se comporta como casi-lineal a pequeña "
            "señal y como conmutador a gran señal."
        )
        V_op_mV = st.slider(
            "Punto operativo V_D [mV]",
            min_value=-50, max_value=250, value=0, step=5,
            key="V_op_diode",
            help="Tensión instantánea sobre la unión. V_D = 0 → R_d0 ≈ 5,4 kΩ (pequeña señal).",
        )
        control_interactivo(
            magnitud="**V_D**, la tensión instantánea sobre la unión del diodo [mV]; fija "
                     "el punto de operación sobre la curva I-V.",
            referencia="**V_D = 0** (sin polarización): R_d0 ≈ 5,4 kΩ, el valor que define "
                       "la impedancia del diodo a pequeña señal usada en el modelo.",
            al_subir="El diodo entra en régimen exponencial: la corriente sube rápido y la "
                     "resistencia dinámica R_d cae varios órdenes de magnitud (conducción).",
            al_bajar="Hacia V_D negativo el diodo se bloquea: solo circula la pequeña "
                     "corriente de saturación inversa I_S.",
            limite="Por encima de ~250 mV la resistencia serie R_S = 20 Ω domina las "
                   "pérdidas óhmicas; ese extremo ya no es representativo del régimen de "
                   "cosecha (pequeña señal).",
        )
        V_op = V_op_mV / 1000.0
        st.plotly_chart(_fig_diode_iv_curve(V_op), width="stretch")
        st.caption(
            ":material/info: A **V_D = 0** (sin polarización) R_d0 = n·V_T / I_S ≈ "
            "**5,4 kΩ**. Es el valor que define la impedancia del diodo a pequeña "
            "señal, Re(Z_D) ≈ R_S + R_d0, y entra en V_oc,pk = √(8·P_avail·Re(Z_D)) — "
            "la tensión inducida por la RF en circuito abierto, antes del clip de PCE. "
            "Por encima de ~100 mV el diodo entra en régimen exponencial y R_d cae "
            "varios órdenes de magnitud; por encima de 250 mV la resistencia serie "
            "R_S = 20 Ω empieza a dominar las pérdidas óhmicas."
        )
        _ref("§2.7.1 Ecuación de Shockley · §2.7.2 Parámetros SPICE del SMS7630 · "
             "Tabla 3 (parámetros SPICE del SMS7630) · "
             "Apéndice E.5 Caracterización numérica I-V del diodo SMS7630")


# ──────────────────────────────────────────────────────────────────────────────
#  Visualizaciones conceptuales (antena + rectificador)
# ──────────────────────────────────────────────────────────────────────────────

def _fig_diode_iv_curve(V_op: float):
    """Curva I-V del SMS7630 (modelo de Shockley) con punto operativo y R_dinámica.
    Eje Y logarítmico para que el carácter exponencial se vea como recta."""
    import numpy as np

    Is = 5e-6      # A
    n = 1.05
    Vt = 0.02585   # V @ 300 K
    Vj = 0.34      # V

    V_sweep = np.linspace(-0.05, 0.25, 600)
    I_sweep = Is * (np.exp(V_sweep / (n * Vt)) - 1)
    I_floor = 0.1e-6   # 0.1 µA — para que el log no explote en V_D = 0
    I_abs_uA = np.maximum(np.abs(I_sweep), I_floor) * 1e6

    I_op = Is * (np.exp(V_op / (n * Vt)) - 1)
    I_op_abs_uA = max(abs(I_op), I_floor) * 1e6
    R_d_op = (n * Vt) / (abs(I_op) + Is)

    fig = go.Figure()

    # Bandas de fondo por régimen
    fig.add_vrect(
        x0=-0.05, x1=0,
        fillcolor='rgba(248, 113, 113, 0.10)', line_width=0,
        annotation_text='Saturación<br>inversa',
        annotation_position='top left', annotation_font_size=9,
    )
    fig.add_vrect(
        x0=0, x1=0.10,
        fillcolor='rgba(167, 139, 250, 0.06)', line_width=0,
        annotation_text='Sub-umbral<br>(cuasi-lineal)',
        annotation_position='top left', annotation_font_size=9,
    )
    fig.add_vrect(
        x0=0.10, x1=0.25,
        fillcolor='rgba(251, 191, 36, 0.08)', line_width=0,
        annotation_text='Exponencial<br>(conducción)',
        annotation_position='top left', annotation_font_size=9,
    )

    # Curva I-V
    fig.add_trace(go.Scatter(
        x=V_sweep, y=I_abs_uA, mode='lines',
        line=dict(color='#2563EB', width=2.8),
        name='|I_D(V)|',
        hovertemplate='V_D=%{x:.3f} V<br>|I_D|=%{y:.3g} µA<extra></extra>',
    ))

    # Punto operativo
    fig.add_trace(go.Scatter(
        x=[V_op], y=[I_op_abs_uA],
        mode='markers',
        marker=dict(size=18, color='#B45309', symbol='star',
                    line=dict(color='white', width=2)),
        name='Punto operativo',
        hoverinfo='skip',
    ))

    # Líneas de referencia
    fig.add_hline(
        y=Is * 1e6,
        line=dict(color='#475569', dash='dash', width=1.2),
        annotation_text=f'I_S = {Is*1e6:.0f} µA  (saturación inversa)',
        annotation_position='bottom right', annotation_font_size=10,
    )
    fig.add_vline(
        x=Vj,
        line=dict(color='rgba(167,139,250,0.45)', dash='dot', width=1),
        annotation_text=f'V_j = {Vj*1000:.0f} mV<br>(potencial de juntura)',
        annotation_position='top right', annotation_font_size=9,
    )

    # Helpers de formato
    def _fmt_R(R):
        if R < 1000:    return f"{R:.1f} Ω"
        if R < 1e6:     return f"{R/1000:.2f} kΩ"
        return f"{R/1e6:.2f} MΩ"

    def _fmt_I(I):
        a = abs(I)
        if a < 1e-9:    return f"{I*1e12:.2f} pA"
        if a < 1e-6:    return f"{I*1e9:.2f} nA"
        if a < 1e-3:    return f"{I*1e6:.3f} µA"
        return f"{I*1e3:.3f} mA"

    # Caja informativa con el punto operativo
    fig.add_annotation(
        x=0.03, y=0.97, xref='paper', yref='paper', xanchor='left', yanchor='top',
        text=(f"<b>Punto operativo</b><br>"
              f"V_D = {V_op*1000:.1f} mV<br>"
              f"I_D = {_fmt_I(I_op)}<br>"
              f"<b style='color:#B45309'>R_dinámica = {_fmt_R(R_d_op)}</b><br>"
              f"<br><b>SMS7630 (Skyworks AN-4003)</b><br>"
              f"I_S = 5 µA · n = 1,05<br>"
              f"V_T = 25,85 mV (T = 300 K)<br>"
              f"V_j = 340 mV · R_S = 20 Ω"),
        showarrow=False, align='left',
        font=dict(size=10, color='#0F172A'),
        bgcolor='rgba(248, 250, 252, 0.95)',
        bordercolor='#B45309', borderwidth=1, borderpad=10,
    )

    fig.update_layout(
        template='simple_white',
        title=dict(text='Curva I-V del SMS7630 (Shockley · escala log)',
                   font=dict(size=13)),
        xaxis=dict(title='Tensión V_D [V]',
                    tickvals=[-0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25]),
        yaxis=dict(title='|Corriente I_D| [µA]', type='log',
                    range=[-1, 5],   # 0,1 µA a 100 mA
                    tickvals=[0.1, 1, 10, 100, 1000, 10000, 100000],
                    ticktext=['0,1', '1', '10', '100', '1 000', '10 000', '100 000']),
        height=420, showlegend=False,
        margin=dict(l=70, r=20, t=50, b=60),
    )
    return fig


def _fig_greinacher_doubler(mode: str = "Semiciclo +"):
    """Esquemático del doblador de tensión Greinacher con dos diodos SMS7630.
    Resalta el camino de corriente según el modo seleccionado."""
    fig = go.Figure()

    # Colores: activo = amarillo brillante, inactivo = gris tenue
    if mode == "Semiciclo +":
        col_d1, col_d2 = "rgba(100,116,139,0.35)", "#B45309"
        col_c1, col_c2 = "rgba(100,116,139,0.35)", "#B45309"
        wire_top_color, wire_bottom_color = "#B45309", "rgba(100,116,139,0.35)"
    elif mode == "Semiciclo −":
        col_d1, col_d2 = "#B45309", "rgba(100,116,139,0.35)"
        col_c1, col_c2 = "#B45309", "rgba(100,116,139,0.35)"
        wire_top_color, wire_bottom_color = "rgba(100,116,139,0.35)", "#B45309"
    else:  # Régimen DC
        col_d1, col_d2 = "#7C3AED", "#7C3AED"
        col_c1, col_c2 = "#7C3AED", "#7C3AED"
        wire_top_color, wire_bottom_color = "#7C3AED", "#7C3AED"

    wire_neutral = "#94A3B8"
    label_color = "#0F172A"

    # ── Topología del Greinacher half-wave doubler ──────────────────────────
    #
    #   V_in ──[C1]──● X ──[D2 ►|]──● V_DC ──┐
    #                 │                       │
    #                 │                      [C2]
    #                 │                       │
    #                 ▽ D1                    │
    #                 │                       │
    #                ─┴── GND ────────────────┘

    # Coordenadas clave
    x_in = -0.5;   y_top = 1.5
    x_C1_L = 0.4;  x_C1_R = 0.9
    x_X = 1.7
    x_D2_L = 2.2; x_D2_R = 3.0
    x_VDC = 3.6
    x_load = 4.4

    # Cable RF input → C1
    fig.add_shape(type="line",
                  x0=x_in, y0=y_top, x1=x_C1_L, y1=y_top,
                  line=dict(color=wire_neutral, width=2))
    # C1 (dos líneas verticales)
    fig.add_shape(type="line", x0=x_C1_L, y0=y_top - 0.25, x1=x_C1_L, y1=y_top + 0.25,
                  line=dict(color=col_c1, width=4))
    fig.add_shape(type="line", x0=x_C1_R, y0=y_top - 0.25, x1=x_C1_R, y1=y_top + 0.25,
                  line=dict(color=col_c1, width=4))
    fig.add_annotation(x=(x_C1_L + x_C1_R) / 2, y=y_top + 0.55, text="<b>C1</b>",
                       showarrow=False, font=dict(color=col_c1, size=11))
    # Cable C1 → X → D2
    fig.add_shape(type="line", x0=x_C1_R, y0=y_top, x1=x_X, y1=y_top,
                  line=dict(color=wire_top_color, width=2))
    fig.add_shape(type="line", x0=x_X, y0=y_top, x1=x_D2_L, y1=y_top,
                  line=dict(color=wire_top_color, width=2))
    # Nodo X (círculo)
    fig.add_shape(type="circle",
                  x0=x_X - 0.06, y0=y_top - 0.06, x1=x_X + 0.06, y1=y_top + 0.06,
                  fillcolor=label_color, line_color=label_color)
    fig.add_annotation(x=x_X, y=y_top + 0.30, text="<b>X</b>",
                       showarrow=False, font=dict(color=label_color, size=12))

    # D2: triángulo (anode→cathode) apuntando a la derecha
    fig.add_shape(type="path",
                  path=f"M {x_D2_L},{y_top - 0.22} L {x_D2_L},{y_top + 0.22} "
                        f"L {x_D2_R - 0.12},{y_top} Z",
                  fillcolor=col_d2, line_color=col_d2)
    # Barra del cátodo (D2)
    fig.add_shape(type="line",
                  x0=x_D2_R - 0.12, y0=y_top - 0.25,
                  x1=x_D2_R - 0.12, y1=y_top + 0.25,
                  line=dict(color=col_d2, width=4))
    fig.add_annotation(x=(x_D2_L + x_D2_R) / 2, y=y_top + 0.55, text="<b>D2</b>",
                       showarrow=False, font=dict(color=col_d2, size=11))

    # Cable D2 → V_DC node
    fig.add_shape(type="line", x0=x_D2_R - 0.12, y0=y_top, x1=x_VDC, y1=y_top,
                  line=dict(color=wire_top_color, width=2))
    # Nodo V_DC
    fig.add_shape(type="circle",
                  x0=x_VDC - 0.06, y0=y_top - 0.06, x1=x_VDC + 0.06, y1=y_top + 0.06,
                  fillcolor=label_color, line_color=label_color)
    fig.add_annotation(x=x_VDC, y=y_top + 0.30, text="<b>V_DC</b>",
                       showarrow=False, font=dict(color="#059669", size=12))

    # Cable V_DC → load resistor (a la derecha)
    fig.add_shape(type="line", x0=x_VDC, y0=y_top, x1=x_load, y1=y_top,
                  line=dict(color=wire_neutral, width=2))

    # ── Camino de tierra ────────────────────────────────────────────────────
    y_bot = 0.0

    # GND rail
    fig.add_shape(type="line", x0=x_in, y0=y_bot, x1=x_load + 0.4, y1=y_bot,
                  line=dict(color=wire_bottom_color, width=2))

    # Conexión bajo V_in al GND (return RF source)
    fig.add_shape(type="line", x0=x_in, y0=y_top, x1=x_in, y1=y_bot,
                  line=dict(color=wire_bottom_color, width=2))
    fig.add_annotation(x=x_in - 0.05, y=(y_top + y_bot) / 2, xanchor="right",
                       text="V_in<br>(RF)",
                       showarrow=False, font=dict(color="#0EA5E9", size=11))

    # D1 entre X y GND (vertical, apunta hacia abajo: anode at X, cathode at GND)
    fig.add_shape(type="path",
                  path=f"M {x_X - 0.18},{y_top - 0.7} L {x_X + 0.18},{y_top - 0.7} "
                        f"L {x_X},{y_top - 1.15} Z",
                  fillcolor=col_d1, line_color=col_d1)
    # Cable X → D1
    fig.add_shape(type="line", x0=x_X, y0=y_top - 0.05, x1=x_X, y1=y_top - 0.7,
                  line=dict(color=wire_neutral, width=2))
    # Barra cátodo D1
    fig.add_shape(type="line",
                  x0=x_X - 0.22, y0=y_top - 1.15, x1=x_X + 0.22, y1=y_top - 1.15,
                  line=dict(color=col_d1, width=4))
    # Cable D1 → GND
    fig.add_shape(type="line", x0=x_X, y0=y_top - 1.15, x1=x_X, y1=y_bot,
                  line=dict(color="rgba(100,116,139,0.35)" if mode != "Semiciclo −" else "#B45309",
                            width=2))
    fig.add_annotation(x=x_X - 0.3, y=y_top - 0.85, xanchor="right",
                       text="<b>D1</b>", showarrow=False,
                       font=dict(color=col_d1, size=11))

    # C2 entre V_DC y GND (vertical capacitor)
    fig.add_shape(type="line",
                  x0=x_VDC - 0.25, y0=y_top - 0.55, x1=x_VDC + 0.25, y1=y_top - 0.55,
                  line=dict(color=col_c2, width=4))
    fig.add_shape(type="line",
                  x0=x_VDC - 0.25, y0=y_top - 0.85, x1=x_VDC + 0.25, y1=y_top - 0.85,
                  line=dict(color=col_c2, width=4))
    # Cables del C2
    fig.add_shape(type="line", x0=x_VDC, y0=y_top, x1=x_VDC, y1=y_top - 0.55,
                  line=dict(color=wire_top_color, width=2))
    fig.add_shape(type="line", x0=x_VDC, y0=y_top - 0.85, x1=x_VDC, y1=y_bot,
                  line=dict(color=wire_bottom_color, width=2))
    fig.add_annotation(x=x_VDC + 0.45, y=y_top - 0.7,
                       text="<b>C2</b>", showarrow=False,
                       font=dict(color=col_c2, size=11))

    # Resistor de carga (R_load) entre x_load y GND
    fig.add_shape(type="rect",
                  x0=x_load + 0.1, y0=y_top - 0.85, x1=x_load + 0.6, y1=y_top - 0.55,
                  line=dict(color=wire_neutral, width=2), fillcolor="rgba(0,0,0,0)")
    # Cables R_load
    fig.add_shape(type="line", x0=x_load, y0=y_top, x1=x_load + 0.35, y1=y_top,
                  line=dict(color=wire_neutral, width=2))
    fig.add_shape(type="line", x0=x_load + 0.35, y0=y_top, x1=x_load + 0.35, y1=y_top - 0.55,
                  line=dict(color=wire_neutral, width=2))
    fig.add_shape(type="line", x0=x_load + 0.35, y0=y_top - 0.85, x1=x_load + 0.35, y1=y_bot,
                  line=dict(color=wire_neutral, width=2))
    fig.add_annotation(x=x_load + 0.85, y=y_top - 0.7,
                       text="R_L<br>(1300 Ω)", showarrow=False,
                       font=dict(color=wire_neutral, size=10))

    # Símbolo de GND (varias líneas paralelas decrecientes)
    for i, frac in enumerate([0.20, 0.13, 0.07]):
        fig.add_shape(type="line",
                      x0=x_X - frac, y0=y_bot - 0.05 - i * 0.05,
                      x1=x_X + frac, y1=y_bot - 0.05 - i * 0.05,
                      line=dict(color=wire_neutral, width=1.5))

    # Etiqueta de modo activo (arriba)
    if mode == "Semiciclo +":
        text_mode = "Semiciclo +: V_in alto → X ≈ 2·V_p → <b>D2 conduce</b> → C2 se carga"
        col_mode = "#B45309"
    elif mode == "Semiciclo −":
        text_mode = "Semiciclo −: V_in bajo → X intenta caer → <b>D1 conduce</b> → C1 se carga"
        col_mode = "#B45309"
    else:
        text_mode = "Régimen DC permanente: V_DC ≈ 2·(V_pico − V_f) ≈ 1 460 mV (canónico)"
        col_mode = "#7C3AED"

    fig.add_annotation(
        x=2.0, y=y_top + 1.0, xref="x", yref="y", xanchor="center",
        text=f"<b>{text_mode}</b>",
        showarrow=False, font=dict(color=col_mode, size=12),
        bgcolor="rgba(248, 250, 252, 0.9)",
        bordercolor=col_mode, borderwidth=1, borderpad=6,
    )

    fig.update_layout(
        template="simple_white",
        height=380,
        showlegend=False,
        xaxis=dict(visible=False, range=[-1.2, 5.6]),
        yaxis=dict(visible=False, range=[-0.5, 3.1], scaleanchor="x", scaleratio=0.8),
        margin=dict(l=10, r=10, t=20, b=20),
    )
    return fig


def _fig_flpda_schematic(geom, freq_active_mhz):
    """Vista de lado del FLPDA Koch: 8 dipolos sobre el boom, resaltando los
    activos a la frecuencia dada (peso por proximidad, idéntico al modelo)."""
    n = geom['n_elements']
    pos = list(geom['positions_cm'])        # cm; pos[0] = 0 (dipolo más largo)
    L_phys = list(geom['lengths_phys_cm'])  # cm; longitud física del brazo completo
    res = list(geom['res_freqs_MHz'])

    weights = []
    for fr in res:
        delta = abs(freq_active_mhz - fr) / fr
        w = 1.0 / (1.0 + (delta * 8.0) ** 2)
        weights.append(w)
    w_max = max(weights) if weights else 1.0
    w_norm = [w / w_max for w in weights]

    lam_half_cm = (3e8 / (freq_active_mhz * 1e6)) / 2 * 100

    fig = go.Figure()
    fig.add_shape(type="line",
                  x0=pos[0] - 4, y0=0, x1=pos[-1] + 4, y1=0,
                  line=dict(color="#475569", width=2.5))
    fig.add_shape(type="line",
                  x0=pos[0] - 4, y0=lam_half_cm / 2, x1=pos[-1] + 4, y1=lam_half_cm / 2,
                  line=dict(color="#059669", dash="dash", width=1))
    fig.add_shape(type="line",
                  x0=pos[0] - 4, y0=-lam_half_cm / 2, x1=pos[-1] + 4, y1=-lam_half_cm / 2,
                  line=dict(color="#059669", dash="dash", width=1))
    fig.add_annotation(
        x=pos[0] - 4, y=lam_half_cm / 2 + 2,
        text=f"λ/2 a {freq_active_mhz} MHz = {lam_half_cm:.1f} cm",
        showarrow=False, font=dict(color="#059669", size=10),
        xanchor="left",
    )

    for i in range(n):
        half = L_phys[i] / 2.0
        intensity = w_norm[i]
        if intensity > 0.7:
            color = f"rgba(251, 191, 36, {0.4 + 0.6 * intensity})"
            width = 5
        else:
            color = f"rgba(96, 165, 250, {0.20 + 0.30 * intensity})"
            width = 3
        fig.add_shape(type="line",
                      x0=pos[i], y0=-half, x1=pos[i], y1=half,
                      line=dict(color=color, width=width))
        fig.add_annotation(
            x=pos[i], y=-half - 5,
            text=f"#{i+1}<br>{res[i]:.0f} MHz",
            showarrow=False, font=dict(size=9, color="#334155"),
        )

    fig.add_annotation(
        x=pos[-1] + 2, y=0,
        text="<b>apex</b><br>(feed)",
        showarrow=False, font=dict(color="#DC2626", size=11),
        xanchor="left",
    )
    fig.add_annotation(
        x=pos[-1] + 10, y=12,
        ax=pos[-1] - 5, ay=12,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.3,
        arrowwidth=2.5, arrowcolor="#059669",
    )
    fig.add_annotation(
        x=pos[-1] + 10, y=15,
        text="<b>radiación endfire</b>",
        showarrow=False, font=dict(color="#059669", size=11),
        xanchor="left",
    )

    fig.update_layout(
        template='simple_white',
        title=dict(
            text=f"FLPDA Koch · vista de lado · región activa a {freq_active_mhz} MHz",
            font=dict(size=13),
        ),
        height=380,
        showlegend=False,
        xaxis=dict(
            title="Posición a lo largo del boom [cm]",
            range=[pos[0] - 8, pos[-1] + 22],
            zeroline=False, showgrid=False,
        ),
        yaxis=dict(
            title="Extensión transversal del dipolo [cm]",
            range=[-max(L_phys) / 1.6, max(L_phys) / 1.6],
            scaleanchor="x", scaleratio=1,
            zeroline=False, showgrid=False,
        ),
        margin=dict(l=70, r=20, t=50, b=70),
    )
    return fig


def _fig_koch_miniaturization(extended: bool = False):
    """Iteraciones de Koch con la MISMA longitud de conductor; muestra cómo el dipolo
    se 'encoge' físicamente al subir la iteración. Si extended=True, llega a it.4."""
    import math

    def koch_points(iterations: int, length: float = 1.0):
        pts = [(0.0, 0.0), (length, 0.0)]
        for _ in range(iterations):
            new_pts = []
            for i in range(len(pts) - 1):
                p0 = pts[i]; p1 = pts[i + 1]
                dx = p1[0] - p0[0]; dy = p1[1] - p0[1]
                a = (p0[0] + dx / 3, p0[1] + dy / 3)
                b = (p0[0] + 2 * dx / 3, p0[1] + 2 * dy / 3)
                vx = b[0] - a[0]; vy = b[1] - a[1]
                cos60 = 0.5; sin60 = math.sin(math.pi / 3)
                px = a[0] + vx * cos60 - vy * sin60
                py = a[1] + vx * sin60 + vy * cos60
                new_pts.extend([p0, a, (px, py), b])
            new_pts.append(pts[-1])
            pts = new_pts
        return pts

    fig = go.Figure()
    L_conductor = 1.0

    if extended:
        iters = [0, 1, 2, 3, 4]
        colors = ["#2563EB", "#B45309", "#059669", "#7C3AED", "#DC2626"]
        y_offsets = [1.4, 0.7, 0.0, -0.7, -1.4]
        labels = [
            "Iter. 0  ·  rectilínea",
            "Iter. 1  ·  −25 %",
            "Iter. 2  ·  −43,75 %  ★ adoptada",
            "Iter. 3  ·  −57,81 %",
            "Iter. 4  ·  −68,36 %  (256 segmentos)",
        ]
        height = 520
        y_range = [-1.95, 2.05]
    else:
        iters = [0, 1, 2]
        colors = ["#2563EB", "#B45309", "#059669"]
        y_offsets = [0.6, 0.0, -0.6]
        labels = [
            "Iteración 0  ·  rectilínea",
            "Iteración 1  ·  −25 %",
            "Iteración 2  ·  −43,75 %  ★ adoptada",
        ]
        height = 380
        y_range = [-1.15, 1.5]

    for it, color, label, y0 in zip(iters, colors, labels, y_offsets):
        phys_ext = (3 / 4) ** it * L_conductor
        pts = koch_points(it, length=phys_ext)
        xs = [p[0] for p in pts]
        ys = [p[1] + y0 for p in pts]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode='lines',
            line=dict(color=color, width=2.4),
            name=label, showlegend=False,
            hovertemplate=f'{label}<br>Ext. física = {phys_ext:.4f}<extra></extra>',
        ))
        fig.add_annotation(
            x=L_conductor + 0.06, y=y0,
            text=label, showarrow=False,
            font=dict(color=color, size=11),
            xanchor="left", yanchor="middle",
        )
        fig.add_shape(type="line",
                      x0=0, y0=y0 - 0.18, x1=phys_ext, y1=y0 - 0.18,
                      line=dict(color=color, dash="dot", width=1))
        fig.add_annotation(
            x=phys_ext / 2, y=y0 - 0.26,
            text=f"ext. física = {phys_ext:.4f}",
            showarrow=False, font=dict(color=color, size=9),
        )

    fig.add_annotation(
        x=L_conductor / 2, y=y_range[1] - 0.18,
        text="<b>Todas las curvas tienen la misma longitud de conductor</b><br>"
             "<i>(la que fija la frecuencia de resonancia ≈ λ/2)</i>",
        showarrow=False, font=dict(color="#0F172A", size=12),
        bgcolor="rgba(248, 250, 252, 0.92)", bordercolor="#475569",
        borderwidth=1, borderpad=6,
    )

    fig.update_layout(
        template='simple_white',
        height=height,
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.05, L_conductor + 0.65]),
        yaxis=dict(visible=False, range=y_range, scaleanchor="x", scaleratio=1),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


render()
