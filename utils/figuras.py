"""
Fuente gráfica ÚNICA para Streamlit.
================================================================================
Streamlit NO genera figuras propias: reutiliza los PNG producidos por el
pipeline (`_regen/out/figuras/`), los mismos que consumen el documento y el
póster. Una sola identidad visual para los tres medios.

Uso:
    from utils.figuras import figura, FIG
    figura(FIG["flujo"], "El método en seis pasos.")
"""

import os
import streamlit as st

_FIGS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "_regen", "out", "figuras",
)

# Catálogo con nombres estables (independientes del archivo) → PNG del pipeline.
FIG = {
    # Conceptuales / metodológicas
    "fuentes":    "FigC1_fuentes_a_caso.png",
    "maestra":    "FigC5_maestra.png",
    "anatomia":   "FigC3_anatomia_rectena.png",
    "flujo":      "FigC2_flujo_metodologico.png",
    "repro":      "FigC4_cadena_reproducible.png",
    # Resultados / validación
    "s11_a":      "Fig01_S11_Sierpinski.png",
    "eta_a":      "Fig02_eta_banda_A.png",
    "s11_b":      "Fig03_S11_FLPDA.png",
    "geom_b":     "Fig04_geometria_FLPDA.png",
    "cascada":    "Fig05_cascada_RFDC.png",
    "pdc_dist":   "Fig06_PDC_distancia.png",
    "tciclo":     "Fig07_Tciclo_distancia.png",
    "tornado":    "Fig08_tornado.png",
    "montecarlo": "Fig09_montecarlo.png",
    "pce_ambos":  "Fig10_PCE_ambos.png",
    "wang":       "Fig11_validacion_Wang.png",
}


def ruta(nombre_archivo: str) -> str:
    return os.path.join(_FIGS, nombre_archivo)


def figura(nombre_archivo: str, caption: str | None = None, ancho: str = "stretch"):
    """Muestra una figura del pipeline. `nombre_archivo` viene de FIG[...]."""
    p = ruta(nombre_archivo)
    if os.path.exists(p):
        st.image(p, caption=caption, use_container_width=(ancho == "stretch"))
    else:
        st.warning(
            f"Figura no encontrada: {nombre_archivo}. "
            "Regenera el sistema gráfico con `python _regen/generate_artifacts.py`."
        )
