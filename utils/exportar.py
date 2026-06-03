"""Utilidades de exportación a CSV."""

import io
import pandas as pd


def resultados_a_csv(resultados: list[dict]) -> bytes:
    """Convierte lista de dicts de simulación a CSV en bytes."""
    df = pd.DataFrame(resultados)
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding='utf-8')
    return buf.getvalue().encode('utf-8')


def sweep_a_csv(sweep_data: dict, cols: list = None) -> bytes:
    """Convierte dict de barrido a CSV."""
    if cols:
        data = {k: sweep_data[k] for k in cols if k in sweep_data}
    else:
        data = {k: v for k, v in sweep_data.items() if isinstance(v, list)}
    df = pd.DataFrame(data)
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding='utf-8')
    return buf.getvalue().encode('utf-8')
