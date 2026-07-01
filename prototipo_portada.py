"""
PROTOTIPO (experimental) — Portada / cubierta del conjunto de simulaciones.

Pantalla de apertura para la defensa proyectada y la convención: título del
trabajo, cifras de impacto (canónicas) y guía de las seis simulaciones con la
pregunta que responde cada una. NO forma parte de la aplicación oficial.
"""

import streamlit as st

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

PDC = CANONICAL.get('p_dc_uW', CANONICAL.get('P_dc_uW', 1637.6))
VDC = CANONICAL['V_dc_mV']
MSG = 86400.0 / CANONICAL['T_ciclo_s']
ETA_CONS = PDC / (CANONICAL['P_in_mW'] * 1000.0) * 100.0
G = CANONICAL['gain_dBi']
RMSE = CANONICAL['RMSE_wang']

st.markdown(
    """
    <div style="font-family:'Segoe UI',system-ui,sans-serif;
         background:radial-gradient(1200px 400px at 20% -10%,rgba(124,58,237,0.16),transparent),
                    linear-gradient(135deg,#0B1220 0%,#111A2E 100%);
         border-radius:18px;padding:34px 38px 30px 38px;color:#E2E8F0;
         box-shadow:0 10px 40px rgba(15,23,42,0.25);">
      <div style="font-size:0.92rem;letter-spacing:2px;text-transform:uppercase;
           color:#A78BFA;font-weight:700;">Universidad de Antioquia · Ingeniería de Telecomunicaciones</div>
      <div style="font-size:2.15rem;line-height:1.15;font-weight:800;margin:10px 0 6px 0;
           letter-spacing:-0.5px;">
        Rectenas fractales multibanda para cosecha de energía RF en entornos urbanos
      </div>
      <div style="font-size:1.05rem;color:#CBD5E1;max-width:760px;">
        De la onda de televisión digital al mensaje de un sensor IoT autónomo —
        comparación de una antena <b style="color:#A78BFA;">Sierpinski</b> (multibanda,
        exploratoria) y una <b style="color:#22C55E;">FLPDA Koch</b> (dirigida, cuantitativa).
      </div>
      <div style="margin-top:14px;font-size:0.95rem;color:#94A3B8;">
        Brahian Calderón Múnera · Trabajo de grado · Simulación en Python
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.markdown("##### Cifras de referencia del trabajo")


def chip(value, label, color):
    return (
        f"<div style='flex:1;min-width:150px;background:#fff;border:1px solid #E2E8F0;"
        f"border-top:4px solid {color};border-radius:12px;padding:14px 16px;"
        f"box-shadow:0 1px 3px rgba(15,23,42,0.06);'>"
        f"<div style='font-size:1.5rem;font-weight:800;color:#0F172A;'>{value}</div>"
        f"<div style='font-size:0.82rem;color:#64748B;margin-top:2px;'>{label}</div></div>"
    )


chips = "".join([
    chip(f"{PDC:,.0f} µW".replace(",", " "), "Potencia DC útil (P_DC)", "#7C3AED"),
    chip(f"{MSG:,.0f}".replace(",", " "), "Mensajes LoRa al día", "#16A34A"),
    chip(f"{VDC:,.0f} mV".replace(",", " "), "Voltaje DC de salida", "#0EA5E9"),
    chip(f"{ETA_CONS:.1f} %", "Se conserva de P_in", "#F59E0B"),
    chip(f"{G:.2f} dBi", "Ganancia FLPDA @ 550 MHz", "#22C55E"),
    chip(f"{RMSE:.2f} pp", "RMSE validación (Wang 2022)", "#64748B"),
])
st.markdown(
    f"<div style='display:flex;gap:12px;flex-wrap:wrap;'>{chips}</div>",
    unsafe_allow_html=True,
)

st.write("")
st.markdown("##### Recorrido — seis simulaciones, seis preguntas")

GUIDE = [
    ("🛰️", "Cómo funciona la rectena", "#0EA5E9",
     "¿Qué le pasa a la energía de radio después de captarla?", "conceptual"),
    ("⚡", "Doblador Greinacher", "#F59E0B",
     "¿Cómo convierte el rectificador la RF alterna en corriente continua?", "conceptual"),
    ("💧", "Cascada de energía", "#16A34A",
     "¿Dónde se pierde la energía entre la torre y el nodo, y cuánta llega?", "analítica"),
    ("📡", "Espectro urbano", "#7C3AED",
     "¿Por qué se cosecha de la TV digital (UHF) y no de Wi-Fi o 5G?", "conceptual"),
    ("⚖️", "Escenario A vs B", "#EF4444",
     "¿Por qué el trabajo necesita dos escenarios, uno explora y otro cuantifica?", "analítica"),
    ("🎯", "Patrón de radiación", "#22C55E",
     "¿Por qué una antena dirigida capta más y por qué hay que apuntarla?", "validación"),
]
cols = st.columns(3)
for i, (ico, title, col, q, kind) in enumerate(GUIDE):
    with cols[i % 3]:
        st.markdown(
            f"<div style='background:#fff;border:1px solid #E2E8F0;border-left:4px solid {col};"
            f"border-radius:12px;padding:14px 16px;margin-bottom:12px;min-height:150px;"
            f"box-shadow:0 1px 3px rgba(15,23,42,0.05);'>"
            f"<div style='font-size:1.4rem;'>{ico}</div>"
            f"<div style='font-weight:700;color:#0F172A;margin:4px 0 6px 0;'>{title}</div>"
            f"<div style='font-size:0.88rem;color:#475569;line-height:1.35;'>{q}</div>"
            f"<div style='margin-top:8px;display:inline-block;font-size:0.72rem;font-weight:600;"
            f"color:{col};background:{col}1A;padding:2px 9px;border-radius:10px;'>{kind}</div></div>",
            unsafe_allow_html=True,
        )

st.info(
    "Usa el menú lateral para abrir cada simulación. Cada lámina tiene un botón **⬇ PNG** "
    "para exportar la imagen y llevarla al póster o a las diapositivas.",
    icon=":material/lightbulb:",
)
st.caption(
    "Conjunto de prototipos experimentales con fines ilustrativos y de defensa. No forma parte "
    "de la aplicación oficial del trabajo de grado; las cifras mostradas son canónicas del modelo."
)
