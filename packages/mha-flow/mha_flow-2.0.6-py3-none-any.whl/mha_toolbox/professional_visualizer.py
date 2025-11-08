"""
Professional Results Visualizer
================================

Creates publication-quality plots as requested by user with:
- Feature importance with threshold slider  
- Box plots with mean ± SD
- Multi-metric comparisons
- Statistical summaries
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional


def plot_feature_threshold(best_solution: np.ndarray,
                           feature_names: Optional[List[str]] = None,
                           initial_threshold: float = 0.5):
    """
    Create interactive feature importance plot with threshold slider.
    
    As per user requirement #13:
    - Bar plot of positions for all dimensions (0-1 range)
    - Slider (0-1) controlling threshold interactively
    - threshold=0.5: significant features
    - threshold>0.5: most significant features
    - threshold<0.5: features that contributed in some iterations
    """
    if feature_names is None:
        feature_names = [f"F{i+1}" for i in range(len(best_solution))]
    
    # Create figure
    fig = go.Figure()
    
    # Create frames for different threshold values
    frames = []
    thresholds = np.arange(0, 1.01, 0.05)
    
    for thresh in thresholds:
        colors = ['#2ecc71' if val >= thresh else '#95a5a6' for val in best_solution]
        selected_count = sum(1 for val in best_solution if val >= thresh)
        
        frame = go.Frame(
            data=[go.Bar(
                x=feature_names,
                y=best_solution,
                marker_color=colors,
                marker_line_color='#34495e',
                marker_line_width=1.5,
                text=[f'{val:.3f}' for val in best_solution],
                textposition='outside',
                textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>Position: %{y:.4f}<extra></extra>'
            )],
            layout=go.Layout(
                title_text=f"Feature Importance (Threshold: {thresh:.2f})<br>" +
                          f"<sub>Selected: {selected_count}/{len(best_solution)} features</sub>"
            ),
            name=str(thresh)
        )
        frames.append(frame)
    
    # Initial frame
    initial_colors = ['#2ecc71' if val >= initial_threshold else '#95a5a6' 
                     for val in best_solution]
    initial_selected = sum(1 for val in best_solution if val >= initial_threshold)
    
    fig.add_trace(go.Bar(
        x=feature_names,
        y=best_solution,
        marker_color=initial_colors,
        marker_line_color='#34495e',
        marker_line_width=1.5,
        text=[f'{val:.3f}' for val in best_solution],
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Position: %{y:.4f}<extra></extra>'
    ))
    
    # Add threshold line
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(best_solution)-0.5,
        y0=initial_threshold,
        y1=initial_threshold,
        line=dict(color="#e74c3c", width=3, dash="dash"),
    )
    
    # Add slider
    sliders = [dict(
        active=int(initial_threshold * 20),
        yanchor="top",
        y=-0.15,
        xanchor="left",
        currentvalue=dict(
            prefix="Threshold: ",
            visible=True,
            xanchor="center",
            font=dict(size=16, color="#2c3e50")
        ),
        pad=dict(b=10, t=50),
        len=0.9,
        x=0.05,
        steps=[
            dict(
                args=[
                    [str(thresh)],
                    dict(
                        frame=dict(duration=0, redraw=True),
                        mode="immediate",
                        transition=dict(duration=0)
                    )
                ],
                label=f'{thresh:.2f}',
                method="animate"
            )
            for thresh in thresholds
        ]
    )]
    
    fig.frames = frames
    
    fig.update_layout(
        title=f"Feature Importance - Interactive Threshold Selection<br>" +
              f"<sub>Selected: {initial_selected}/{len(best_solution)} features | " +
              f"Green: Selected | Gray: Not Selected</sub>",
        xaxis_title="<b>Features</b>",
        yaxis_title="<b>Position Value</b>",
        yaxis=dict(range=[0, 1.15], gridcolor='#ecf0f1'),
        xaxis=dict(gridcolor='#ecf0f1'),
        sliders=sliders,
        height=600,
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=12),
        hovermode='x'
    )
    
    # Rotate labels if many features
    if len(feature_names) > 15:
        fig.update_xaxes(tickangle=-45)
    
    # Add annotations
    fig.add_annotation(
        text="<b>Threshold Guide:</b><br>" +
             "• 0.75+: Most significant<br>" +
             "• 0.50: Significant (default)<br>" +
             "• 0.25: Some contribution<br>" +
             "• 0.00: Any contribution",
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        showarrow=False,
        bordercolor="#34495e",
        borderwidth=2,
        borderpad=10,
        bgcolor="#ecf0f1",
        font=dict(size=10),
        align="left",
        xanchor="right",
        yanchor="top"
    )
    
    return fig


def plot_comparison_box_with_stats(results: Dict[str, Dict],
                                   metrics: List[str] = None):
    """
    Create box plot comparison with mean and standard deviation.
    
    As per user requirement #11: Use box plot for comparison with mean and SD
    """
    if metrics is None:
        metrics = ['fitness', 'accuracy', 'time', 'features']
    
    n_metrics = len(metrics)
    fig = make_subplots(
        rows=1, cols=n_metrics,
        subplot_titles=[f"<b>{m.capitalize()}</b>" for m in metrics],
        horizontal_spacing=0.1
    )
    
    for col_idx, metric in enumerate(metrics, 1):
        algorithms = []
        means = []
        stds = []
        
        for algo_name, data in results.items():
            # Get mean and std
            mean_key = f'mean_{metric}'
            std_key = f'std_{metric}'
            
            mean_val = data.get(mean_key, data.get(f'best_{metric}', data.get(metric, 0)))
            std_val = data.get(std_key, 0)
            
            algorithms.append(algo_name.upper())
            means.append(mean_val)
            stds.append(std_val)
        
        # Add bar chart with error bars
        fig.add_trace(
            go.Bar(
                name=metric,
                x=algorithms,
                y=means,
                error_y=dict(
                    type='data',
                    array=stds,
                    visible=True,
                    color='#e74c3c',
                    thickness=2,
                    width=6
                ),
                marker=dict(
                    color='#3498db',
                    line=dict(color='#2c3e50', width=1.5)
                ),
                text=[f'{m:.4f}<br>±{s:.4f}' for m, s in zip(means, stds)],
                textposition='outside',
                textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>Mean: %{y:.6f}<br>SD: %{error_y.array:.6f}<extra></extra>',
                showlegend=False
            ),
            row=1, col=col_idx
        )
        
        # Update axes
        fig.update_xaxis(
            title_text="<b>Algorithm</b>",
            tickangle=-45,
            gridcolor='#ecf0f1',
            row=1, col=col_idx
        )
        
        ylabel = {
            'fitness': 'Fitness Value',
            'accuracy': 'Accuracy (%)',
            'time': 'Time (seconds)',
            'features': 'Number of Features'
        }.get(metric, metric.capitalize())
        
        fig.update_yaxis(
            title_text=f"<b>{ylabel}</b>",
            gridcolor='#ecf0f1',
            row=1, col=col_idx
        )
    
    fig.update_layout(
        title_text="<b>Algorithm Comparison</b><br>" +
                   "<sub>Bars show Mean ± Standard Deviation (error bars)</sub>",
        height=500,
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=11),
        showlegend=False,
        hovermode='x'
    )
    
    return fig


def create_workflow_dashboard(results: Dict[str, Dict]):
    """
    Create comprehensive dashboard as per user workflow image.
    
    Shows:
    1. Summary comparison (mean ± SD for key metrics)
    2. Convergence plot
    3. Export options
    """
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '<b>Convergence: Fitness vs. Iterations</b>',
            '<b>Fitness Comparison (Mean ± SD)</b>',
            '<b>Accuracy Comparison (Mean ± SD)</b>',
            '<b>Time & Features Comparison</b>'
        ),
        specs=[
            [{'type': 'scatter', 'colspan': 2}, None],
            [{'type': 'bar'}, {'type': 'bar'}]
        ],
        row_heights=[0.5, 0.5],
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    algorithms = list(results.keys())
    
    # 1. Convergence curves (top, full width)
    for algo_name, data in results.items():
        conv = data.get('convergence_curve', [])
        if len(conv) > 0:
            fig.add_trace(
                go.Scatter(
                    x=list(range(1, len(conv) + 1)),
                    y=conv,
                    mode='lines',
                    name=algo_name.upper(),
                    line=dict(width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>Iteration: %{x}<br>Fitness: %{y:.6f}<extra></extra>'
                ),
                row=1, col=1
            )
    
    # 2. Fitness comparison with mean ± SD
    fitness_means = [results[a].get('mean_fitness', results[a].get('best_fitness', 0)) for a in algorithms]
    fitness_stds = [results[a].get('std_fitness', 0) for a in algorithms]
    
    fig.add_trace(
        go.Bar(
            x=[a.upper() for a in algorithms],
            y=fitness_means,
            error_y=dict(type='data', array=fitness_stds, visible=True),
            marker_color='#3498db',
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Mean Fitness: %{y:.6f}<br>SD: %{error_y.array:.6f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 3. Accuracy comparison with mean ± SD
    acc_means = [results[a].get('mean_accuracy', results[a].get('accuracy', 0)) * 100 for a in algorithms]
    acc_stds = [results[a].get('std_accuracy', 0) * 100 for a in algorithms]
    
    fig.add_trace(
        go.Bar(
            x=[a.upper() for a in algorithms],
            y=acc_means,
            error_y=dict(type='data', array=acc_stds, visible=True),
            marker_color='#2ecc71',
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Mean Accuracy: %{y:.2f}%<br>SD: %{error_y.array:.2f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="<b>Iteration</b>", row=1, col=1)
    fig.update_yaxes(title_text="<b>Best Fitness</b>", row=1, col=1)
    
    fig.update_xaxes(title_text="<b>Algorithm</b>", tickangle=-45, row=2, col=1)
    fig.update_yaxes(title_text="<b>Fitness</b>", row=2, col=1)
    
    fig.update_xaxes(title_text="<b>Algorithm</b>", tickangle=-45, row=2, col=2)
    fig.update_yaxes(title_text="<b>Accuracy (%)</b>", row=2, col=2)
    
    fig.update_layout(
        title_text="<b>MHA Comparative Analysis Dashboard</b><br>" +
                   "<sub>Comprehensive view of algorithm performance with statistical measures</sub>",
        height=900,
        template='plotly_white',
        font=dict(family="Arial, sans-serif"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='closest'
    )
    
    return fig


def export_results_to_csv(results: Dict[str, Dict], filename: str = "mha_results.csv"):
    """
    Export results to CSV with proper axis labels.
    
    As per user requirement #10: Implement exporting values and CSV files
    """
    export_data = []
    
    for algo_name, data in results.items():
        row = {
            'Algorithm': algo_name.upper(),
            'Best_Fitness': data.get('best_fitness', 0),
            'Mean_Fitness': data.get('mean_fitness', 0),
            'Std_Fitness': data.get('std_fitness', 0),
            'Best_Accuracy': data.get('accuracy', 0) * 100,
            'Mean_Accuracy': data.get('mean_accuracy', 0) * 100,
            'Std_Accuracy': data.get('std_accuracy', 0) * 100,
            'Execution_Time': data.get('execution_time', 0),
            'Mean_Time': data.get('mean_time', 0),
            'Std_Time': data.get('std_time', 0),
            'Selected_Features': data.get('n_selected_features', 0),
            'Mean_Features': data.get('mean_features', 0),
            'Std_Features': data.get('std_features', 0),
            'Total_Runs': data.get('n_runs', 1)
        }
        export_data.append(row)
    
    df = pd.DataFrame(export_data)
    df.to_csv(filename, index=False)
    
    return df


def create_statistical_table(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Create comprehensive statistical summary table.
    
    Columns:
    - Algorithm
    - Fitness (Mean ± SD)
    - Accuracy (Mean ± SD)  
    - Time (Mean ± SD)
    - Features (Mean ± SD)
    """
    summary_data = []
    
    for algo_name, data in results.items():
        row = {
            'Algorithm': algo_name.upper(),
            'Fitness': f"{data.get('mean_fitness', 0):.6f} ± {data.get('std_fitness', 0):.6f}",
            'Accuracy (%)': f"{data.get('mean_accuracy', 0)*100:.2f} ± {data.get('std_accuracy', 0)*100:.2f}",
            'Time (s)': f"{data.get('mean_time', 0):.2f} ± {data.get('std_time', 0):.2f}",
            'Features': f"{data.get('mean_features', 0):.1f} ± {data.get('std_features', 0):.1f}",
            'Best': f"{data.get('best_fitness', 0):.6f}"
        }
        summary_data.append(row)
    
    return pd.DataFrame(summary_data)
