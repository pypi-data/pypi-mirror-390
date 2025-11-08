
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional
import webbrowser
from pathlib import Path

from pv_diagnostix_su.equipment.base_equipment import BaseEquipment

logger = logging.getLogger(__name__)

def plot_signal_analysis(signal_data: pd.Series, technique_results: Dict[str, Any], technique: str) -> go.Figure:
    """
    Generates a Plotly interactive subplot showing raw signal and processed result.

    Parameters
    ----------
    signal_data : pd.Series
        The raw signal data.
    technique_results : Dict[str, Any]
        Results from a single signal processing technique.
    technique : str
        Name of the technique (e.g., 'FFT', 'Wavelet').

    Returns
    -------
    go.Figure
        A Plotly figure object.
    """
    # Ensure signal_data is a pandas Series
    if not isinstance(signal_data, pd.Series):
        logger.error(f"plot_signal_analysis received non-Series signal_data: {type(signal_data)}")
        fig = go.Figure()
        fig.add_annotation(text=f"Error: Invalid signal_data type for {technique} analysis.",
                           xref="paper", yref="paper", showarrow=False,
                           font=dict(color="#d62728", size=16))
        fig.update_layout(plot_bgcolor='#2c3e50', paper_bgcolor='#1a242a', font_color='#f0f0f0')
        return fig

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=[f"Raw Signal ({signal_data.name})", f"{technique} Analysis"]) # Include signal_data name

    # Raw Signal Plot
    fig.add_trace(go.Scatter(x=signal_data.index.to_numpy(), y=signal_data.values.to_numpy(), mode='lines', name='Raw Signal', line=dict(color='#ff9900')), # Accent orange
                  row=1, col=1)

def plot_signal_analysis(signal_data: pd.Series, technique_results: Dict[str, Any], technique: str) -> go.Figure:
    """
    Generates a Plotly interactive subplot showing raw signal and processed result.

    Parameters
    ----------
    signal_data : pd.Series
        The raw signal data.
    technique_results : Dict[str, Any]
        Results from a single signal processing technique.
    technique : str
        Name of the technique (e.g., 'FFT', 'Wavelet').

    Returns
    -------
    go.Figure
        A Plotly figure object.
    """
    # Ensure signal_data is a pandas Series
    if not isinstance(signal_data, pd.Series):
        logger.error(f"plot_signal_analysis received non-Series signal_data: {type(signal_data)}")
        fig = go.Figure()
        fig.add_annotation(text=f"Error: Invalid signal_data type for {technique} analysis.",
                           xref="paper", yref="paper", showarrow=False,
                           font=dict(color="#d62728", size=16))
        fig.update_layout(plot_bgcolor='#2c3e50', paper_bgcolor='#1a242a', font_color='#f0f0f0')
        return fig

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=[f"Raw Signal ({signal_data.name})", f"{technique} Analysis"]) # Include signal_data name

    # Raw Signal Plot
    fig.add_trace(go.Scatter(x=signal_data.index.to_numpy(), y=signal_data.values.to_numpy(), mode='lines', name='Raw Signal', line=dict(color='#ff9900')), # Accent orange
                  row=1, col=1)

    # Add a simple placeholder for the second subplot
    fig.add_annotation(text=f"Analysis for {technique}",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(color="#f0f0f0", size=16), row=2, col=1)

    fig.update_layout(title_text=f"Signal Analysis: {technique}", height=600, showlegend=True,
                      plot_bgcolor='#2c3e50',
                      paper_bgcolor='#1a242a',
                      font_color='#f0f0f0',
                      title_font_color='#ff9900',
                      legend=dict(font=dict(color='#f0f0f0'))
                      )
    return fig

def plot_health_score_dashboard(equipment: BaseEquipment, analysis_dict: Dict[str, Any]) -> go.Figure:
    """
    Generates a dashboard for the equipment's health score.

    Parameters
    ----------
    equipment : BaseEquipment
        The equipment object.
    analysis_dict : Dict[str, Any]
        The complete diagnostic report from equipment.diagnose().

    Returns
    -------
    go.Figure
        A Plotly figure object.
    """
    fig = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'indicator'}, {'type': 'bar'}]],
                        subplot_titles=("Score Global", "Scores des Composants")) # Simplified titles

    overall_score = analysis_dict['overall_score']
    severity = analysis_dict['severity']
    timestamp = analysis_dict['timestamp']
    component_scores = analysis_dict['component_scores']
    # risk_factors = analysis_dict['risk_factors'] # No longer needed here
    # recommendations = analysis_dict['recommendations'] # No longer needed here

    # Color coding for severity
    color = get_severity_color(overall_score) # Use the updated function

    # KPI Cards (using annotations for simplicity, can be go.Indicator for more complex)
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Score Global", 'font': {'color': '#f0f0f0'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#f0f0f0", 'tickfont': {'color': '#f0f0f0'}},
            'bar': {'color': color},
            'bgcolor': "#2c3e50",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, 50], 'color': "#d62728"},
                {'range': [50, 80], 'color': "#ff9900"},
                {'range': [80, 100], 'color': "#2ca02c"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': overall_score
            }
        }), row=1, col=1)

    # Component Scores Bar Chart
    fig.add_trace(go.Bar(x=list(component_scores.keys()), y=list(component_scores.values()),
                         marker_color=[get_severity_color(score) for score in component_scores.values()]),
                  row=1, col=2)
    fig.update_yaxes(range=[0, 100], title_text="Score", row=1, col=2, tickfont={'color': '#f0f0f0'}, title_font={'color': '#f0f0f0'})
    fig.update_xaxes(tickfont={'color': '#f0f0f0'}, title_font={'color': '#f0f0f0'})

    fig.update_layout(title_text=f"Tableau de Bord de Santé pour {equipment.equipment_type.capitalize()} ({equipment.equipment_id}) - {timestamp}",
                      height=400, showlegend=False,
                      plot_bgcolor='#2c3e50',
                      paper_bgcolor='#1a242a',
                      font_color='#f0f0f0',
                      title_font_color='#ff9900'
                      )

def get_severity_color(score: float) -> str:
    if score >= 80:
        return '#2ca02c' # Green
    elif 50 <= score < 80:
        return '#ff9900' # Orange
    else: # score < 50
        return '#d62728' # Red

def plot_comparison_multiple_equipments(equipments_list: List[Dict[str, Any]]) -> go.Figure:
    """
    Generates a comparison plot for multiple equipment health scores.

    Parameters
    ----------
    equipments_list : List[Dict[str, Any]]
        A list of dictionaries, each containing an 'equipment' key with a BaseEquipment object
        and an 'analysis' key with its diagnostic report.

    Returns
    -------
    go.Figure
        A Plotly figure object.
    """
    equipment_ids = [eq['equipment'].equipment_id for eq in equipments_list]
    overall_scores = [eq['analysis']['overall_score'] for eq in equipments_list]
    severities = [eq['analysis']['severity'] for eq in equipments_list]
    colors = [get_severity_color(score) for score in overall_scores]

    fig = go.Figure(data=[go.Bar(x=equipment_ids, y=overall_scores, marker_color=colors)])

    fig.update_layout(title_text="Equipment Health Comparison",
                      xaxis_title="Equipment ID",
                      yaxis_title="Overall Score (0-100)",
                      yaxis_range=[0, 100],
                      plot_bgcolor='#2c3e50',
                      paper_bgcolor='#1a242a',
                      font_color='#f0f0f0',
                      title_font_color='#ff9900',
                      xaxis=dict(tickfont=dict(color='#f0f0f0'), title_font=dict(color='#f0f0f0')),
                      yaxis=dict(tickfont=dict(color='#f0f0f0'), title_font=dict(color='#f0f0f0'))
                      )
    return fig

def export_html(plot_object: go.Figure, filepath: str, auto_open: bool = False) -> None:
    """
    Saves a Plotly figure as an interactive HTML file.

    Parameters
    ----------
    plot_object : go.Figure
        The Plotly figure to export.
    filepath : str
        The path to save the HTML file.
    auto_open : bool, optional
        If True, opens the HTML file in the default web browser after saving. Defaults to False.
    """
    filepath = Path(filepath)
    try:
        plot_object.write_html(str(filepath), auto_open=auto_open, include_plotlyjs='cdn')
        logger.info(f"Plot successfully exported to {filepath}")
    except Exception as e:
        logger.error(f"Failed to export plot to HTML: {e}")
        raise
