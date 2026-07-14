"""
Funciones de visualización Plotly reutilizables.
Todas usan template 'simple_white' y paleta consistente con config.toml (tema institucional UdeA).
"""

import plotly.graph_objects as go
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

TEMPLATE = 'simple_white'


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
    """S11 [dB] vs frecuencia con marcas de bandas opcionales."""
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
        mode='lines', name='Ganancia realizada',
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


def fig_validacion_wang(data: dict) -> go.Figure:
    """PCE modelo vs Wang et al. (2022) con barras de error."""
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
    from core.lora_budget import RF_SOURCES_UHF
    fig = go.Figure()
    dists = data['dist_m']
    for src_name, src in RF_SOURCES_UHF.items():
        if src_name in data:
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


def fig_tornado(sens: dict) -> go.Figure:
    """Gráfico de tornado para análisis de sensibilidad."""
    results = sens['results']
    params  = [r['param'] for r in results]
    lows    = [r['val_low'] for r in results]
    highs   = [r['val_high'] for r in results]
    base    = sens['baseline']

    fig = go.Figure()
    for i, (p, lo, hi) in enumerate(zip(params, lows, highs)):
        fig.add_trace(go.Bar(
            x=[lo - base, hi - base],
            y=[p, p],
            orientation='h',
            marker_color=[COLORS[3], COLORS[1]],
            showlegend=False,
            base=[base, base],
            name=p,
            hovertemplate=f'{p}: [{{x:.2f}} µW]',
        ))
    # Simplify: single bars per param showing range
    fig2 = go.Figure()
    for i, r in enumerate(results):
        fig2.add_trace(go.Bar(
            name=r['param'],
            x=[r['val_low'], r['val_high']],
            y=[r['param'], r['param']],
            orientation='h',
            marker_color=COLORS[i % len(COLORS)],
            text=[f"−{r['delta']}", f"+{r['delta']}"],
            textposition='outside',
        ))
    fig2.add_vline(x=base, line=dict(color='white', dash='dash', width=2),
                   annotation_text=f'Base: {base:.1f} µW')
    fig2.update_layout(
        **_base_layout(f'Tornado de sensibilidad — base: {base:.2f} µW', height=max(300, 80 * len(results))),
        xaxis_title='P_DC [µW]',
        barmode='overlay',
        bargroupgap=0.1,
    )
    return fig2


def fig_mc_histogram(mc: dict) -> go.Figure:
    """Histograma de distribución Monte Carlo."""
    samples = [float(s) for s in mc['samples'] if s > 0]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=samples, nbinsx=80,
        marker_color=COLORS[0], opacity=0.75,
        name='P_DC [µW]',
    ))
    fig.add_vline(x=mc['mean'], line=dict(color=COLORS[4], width=2, dash='dash'),
                  annotation_text=f"Media: {mc['mean']:.1f} µW", annotation_position='top right')
    fig.add_vline(x=mc['ci_95'][0], line=dict(color=COLORS[3], width=1.5, dash='dot'),
                  annotation_text='P2.5%')
    fig.add_vline(x=mc['ci_95'][1], line=dict(color=COLORS[3], width=1.5, dash='dot'),
                  annotation_text='P97.5%')
    fig.update_layout(
        **_base_layout(f"Monte Carlo P_DC — N={mc['n_total']:,} muestras", height=380),
        xaxis_title='P_DC [µW]',
        yaxis_title='Frecuencia',
    )
    return fig


def fig_rectifier_bw(bw: dict) -> go.Figure:
    """Curva PCE vs frecuencia con ancho de banda marcado."""
    freqs_mhz = [f / 1e6 for f in bw['freqs_hz']]
    pce_pct   = [p * 100 for p in bw['pce']]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs_mhz, y=pce_pct,
        mode='lines', name='PCE',
        line=dict(color=COLORS[0], width=2),
    ))
    # -3 dB threshold
    thresh_pct = bw['pce_max'] * 50.0  # pce_max/2 * 100
    fig.add_hline(y=thresh_pct, line=dict(color=COLORS[3], dash='dash', width=1),
                  annotation_text=f'−3 dB ({thresh_pct:.1f}%)', annotation_position='right')
    fig.add_vline(x=bw['f_low_3dB'] / 1e6, line=dict(color=COLORS[4], dash='dot', width=1),
                  annotation_text=f"{bw['f_low_3dB']/1e6:.0f} MHz")
    fig.add_vline(x=bw['f_high_3dB'] / 1e6, line=dict(color=COLORS[4], dash='dot', width=1),
                  annotation_text=f"{bw['f_high_3dB']/1e6:.0f} MHz")
    fig.update_layout(
        **_base_layout(f"BW rectificador — PCE máx: {bw['pce_max']*100:.1f}%", height=380),
        xaxis_title='Frecuencia [MHz]',
        yaxis_title='PCE [%]',
    )
    return fig
