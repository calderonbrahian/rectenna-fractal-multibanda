"""
Funciones de visualización Plotly reutilizables.
Todas usan template 'plotly_dark' y paleta consistente con config.toml.
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Paleta coherente con config.toml chartCategoricalColors
COLORS = [
    '#60A5FA',  # azul
    '#34D399',  # verde
    '#A78BFA',  # violeta
    '#F87171',  # rojo
    '#FBBF24',  # amarillo
    '#38BDF8',  # celeste
    '#94A3B8',  # gris
    '#FB923C',  # naranja
]

TEMPLATE = 'plotly_dark'
BAND_COLOR = 'rgba(96, 165, 250, 0.15)'


def _base_layout(title: str = '', height: int = 380) -> dict:
    return dict(
        template=TEMPLATE,
        height=height,
        title={'text': title, 'font': {'size': 14}},
        margin=dict(l=60, r=20, t=45, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
    )


def fig_s11(freqs, s11_dB, titulo: str = 'S11 vs Frecuencia',
            xunit: str = 'GHz', bandas: dict = None) -> go.Figure:
    """Gráfico de S11 [dB] vs frecuencia con marcas de bandas opcionales."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs, y=s11_dB,
        mode='lines', name='S11',
        line=dict(color=COLORS[0], width=2),
    ))
    fig.add_hline(y=-10, line=dict(color='#F87171', dash='dash', width=1),
                  annotation_text='-10 dB', annotation_position='right')
    if bandas:
        for i, (name, f) in enumerate(bandas.items()):
            fig.add_vline(x=f, line=dict(color=COLORS[i % len(COLORS)],
                          dash='dot', width=1),
                          annotation_text=name, annotation_position='top left',
                          annotation_font_size=9)
    fig.update_layout(**_base_layout(titulo))
    fig.update_xaxes(title_text=f'Frecuencia [{xunit}]')
    fig.update_yaxes(title_text='S₁₁ [dB]', range=[-25, 2])
    return fig


def fig_pce_pin(pins, pce_series: dict, titulo: str = 'PCE vs Potencia de entrada') -> go.Figure:
    """PCE [%] vs Pin [dBm] — múltiples series."""
    fig = go.Figure()
    for i, (name, vals) in enumerate(pce_series.items()):
        fig.add_trace(go.Scatter(
            x=pins, y=vals,
            mode='lines', name=name,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))
    fig.update_layout(**_base_layout(titulo))
    fig.update_xaxes(title_text='P_in [dBm]')
    fig.update_yaxes(title_text='PCE [%]', range=[0, 90])
    return fig


def fig_gain(freqs, gain, titulo: str = 'Ganancia realizada vs Frecuencia',
             xunit: str = 'GHz') -> go.Figure:
    """Ganancia [dBi] vs frecuencia."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs, y=gain,
        mode='lines', name='Ganancia',
        line=dict(color=COLORS[1], width=2),
    ))
    fig.update_layout(**_base_layout(titulo))
    fig.update_xaxes(title_text=f'Frecuencia [{xunit}]')
    fig.update_yaxes(title_text='Ganancia [dBi]')
    return fig


def fig_impedancia(freqs, za_real, za_imag,
                   titulo: str = 'Impedancia de entrada Za(f)', xunit: str = 'GHz') -> go.Figure:
    """Re(Za) y Im(Za) vs frecuencia en subplots."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.06,
                        subplot_titles=['Re(Zₐ) [Ω]', 'Im(Zₐ) [Ω]'])
    fig.add_trace(go.Scatter(x=freqs, y=za_real, mode='lines', name='Re(Zₐ)',
                             line=dict(color=COLORS[0], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs, y=za_imag, mode='lines', name='Im(Zₐ)',
                             line=dict(color=COLORS[2], width=2)), row=2, col=1)
    fig.update_layout(**_base_layout(titulo, height=450))
    fig.update_xaxes(title_text=f'Frecuencia [{xunit}]', row=2, col=1)
    return fig


def fig_sierpinski(triangulos: list, iterations: int = 3) -> go.Figure:
    """Visualización del Sierpinski Gasket."""
    fig = go.Figure()
    for tri in triangulos:
        xs = [tri[0][0], tri[1][0], tri[2][0], tri[0][0]]
        ys = [tri[0][1], tri[1][1], tri[2][1], tri[0][1]]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself',
            fillcolor='rgba(96, 165, 250, 0.35)',
            line=dict(color=COLORS[0], width=0.5),
            mode='lines', showlegend=False,
        ))
    fig.update_layout(
        **_base_layout(f'Sierpinski Gasket it.{iterations} (geometría normalizada)', height=380),
        xaxis=dict(scaleanchor='y', scaleratio=1, showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    return fig


def fig_koch(puntos: list) -> go.Figure:
    """Visualización de la curva de Koch."""
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
                             line=dict(color=COLORS[1], width=2), showlegend=False))
    fig.update_layout(
        **_base_layout('Curva de Koch it.2 (dipolo)', height=250),
        xaxis=dict(scaleanchor='y', scaleratio=1, showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    return fig


def fig_polar_pattern(theta_deg: list, pattern_dB: list,
                      titulo: str = 'Patrón de radiación (plano E)') -> go.Figure:
    """Patrón de radiación en coordenadas polares."""
    theta_rad = [t * np.pi / 180 for t in theta_deg]
    r_lin     = [10 ** (v / 20) for v in pattern_dB]
    fig = go.Figure(go.Scatterpolar(
        r=r_lin, theta=theta_deg,
        mode='lines', line=dict(color=COLORS[0], width=2),
    ))
    fig.update_layout(
        template=TEMPLATE,
        height=380,
        title={'text': titulo, 'font': {'size': 14}},
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.1]),
            angularaxis=dict(direction='clockwise', tickfont_size=10),
        ),
        margin=dict(l=30, r=30, t=50, b=30),
    )
    return fig


def fig_validacion_wang(data: dict) -> go.Figure:
    """Gráfico de validación PCE modelo vs Wang et al. (2022)."""
    freqs = data['freqs_GHz']
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs, y=data['pce_referencia'],
        mode='lines+markers', name='Wang (2022) medido',
        line=dict(color=COLORS[0], width=2),
        marker=dict(symbol='square', size=8),
    ))
    fig.add_trace(go.Scatter(
        x=freqs, y=data['pce_simulacion'],
        mode='lines+markers', name='Modelo analítico (FR-4)',
        line=dict(color=COLORS[2], width=2, dash='dash'),
        marker=dict(symbol='circle', size=8),
    ))
    # Barras de error absoluto
    err_abs = data['error_abs_pp']
    fig.add_trace(go.Bar(
        x=freqs, y=err_abs,
        name='Error [pp]',
        marker_color=[COLORS[3] if e < 0 else COLORS[1] for e in err_abs],
        opacity=0.65,
        yaxis='y2',
    ))
    fig.update_layout(
        **_base_layout('PCE: Modelo analítico vs Wang et al. (2022) IEEE TAP', height=420),
        xaxis=dict(title='Frecuencia [GHz]'),
        yaxis=dict(title='PCE [%]', range=[0, 60]),
        yaxis2=dict(title='Error [pp]', overlaying='y', side='right',
                    range=[-40, 20], showgrid=False),
    )
    return fig


def fig_harvested_vs_dist(data: dict) -> go.Figure:
    """Potencia cosechada [µW] vs distancia para múltiples fuentes."""
    fig = go.Figure()
    dists = data['dist_m']
    from core.lora_budget import RF_SOURCES_UHF
    for src_name, src in RF_SOURCES_UHF.items():
        fig.add_trace(go.Scatter(
            x=dists, y=data[src_name],
            mode='lines', name=src_name,
            line=dict(color=src['color'], width=2),
        ))
    consumos = data.get('consumos_uw', {})
    for i, (prof, p_uw) in enumerate(consumos.items()):
        fig.add_hline(
            y=p_uw,
            line=dict(color=COLORS[i % len(COLORS)], dash='dot', width=1),
            annotation_text=f'{prof} ({p_uw:.1f} µW)',
            annotation_position='right',
            annotation_font_size=9,
        )
    fig.update_layout(**_base_layout('Potencia cosechada DC útil vs Distancia', height=420))
    fig.update_xaxes(title_text='Distancia [m]')
    fig.update_yaxes(title_text='P_DC útil [µW]', type='log')
    return fig


def fig_heatmap_tau_sigma(data: dict) -> go.Figure:
    """Heatmap de ganancia media FLPDA vs τ y σ."""
    fig = go.Figure(go.Heatmap(
        x=data['sigmas'],
        y=data['taus'],
        z=data['gain_map'],
        colorscale='Blues',
        colorbar=dict(title='Ganancia media [dBi]'),
    ))
    fig.update_layout(**_base_layout('Ganancia media FLPDA vs τ y σ (Carrel 1961)', height=400))
    fig.update_xaxes(title_text='σ (espaciado relativo)')
    fig.update_yaxes(title_text='τ (razón de escala)')
    return fig


def fig_sweep_generic(x, y_series: dict, x_label: str, y_label: str,
                      titulo: str = '') -> go.Figure:
    """Gráfico de líneas genérico para análisis de sensibilidad."""
    fig = go.Figure()
    for i, (name, vals) in enumerate(y_series.items()):
        fig.add_trace(go.Scatter(
            x=x, y=vals, mode='lines', name=name,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))
    fig.update_layout(**_base_layout(titulo))
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)
    return fig


def fig_barras_bandas(bandas: list, valores: list, labels: list,
                      titulo: str = '', y_label: str = '') -> go.Figure:
    """Gráfico de barras por banda objetivo."""
    fig = go.Figure()
    colores = [COLORS[i % len(COLORS)] for i in range(len(bandas))]
    for i, (b, v, lbl) in enumerate(zip(bandas, valores, labels)):
        fig.add_trace(go.Bar(
            x=[b], y=[v], name=lbl,
            marker_color=colores[i],
            text=[f'{v:.1f}'], textposition='outside',
            showlegend=False,
        ))
    fig.update_layout(**_base_layout(titulo))
    fig.update_yaxes(title_text=y_label)
    return fig
