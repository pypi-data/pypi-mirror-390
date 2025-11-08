"""
Enhanced Visualization Module for MHA Toolbox
============================================

Provides advanced visualizations for single algorithm analysis including:
- Agent trajectory plots
- Exploration vs exploitation analysis  
- Contour plots for optimization landscape
- Agent fitness matrices
- Convergence analysis with detailed breakdowns
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import time
import uuid

# Unique key generator for plotly charts
def get_unique_key(base_name):
    """Generate unique key for plotly charts to avoid conflicts"""
    if 'viz_chart_counter' not in st.session_state:
        st.session_state.viz_chart_counter = 0
    st.session_state.viz_chart_counter += 1
    return f"{base_name}_{st.session_state.viz_chart_counter}_{str(uuid.uuid4())[:8]}"


class EnhancedVisualizer:
    """Advanced visualization for algorithm analysis"""
    
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
    
    def plot_agent_trajectories(self, tracking_data, max_agents=10):
        """Plot individual agent trajectories in 2D/3D space"""
        try:
            if 'agent_positions_history' not in tracking_data:
                return None
            
            positions_history = tracking_data['agent_positions_history']
            if not positions_history or len(positions_history) == 0:
                return None
            
            # Get dimensions
            dimensions = len(positions_history[0][0]) if positions_history[0] else 0
            if dimensions < 2:
                return None
            
            # Limit number of agents for readability
            num_agents = min(len(positions_history[0]), max_agents)
            iterations = len(positions_history)
            
            if dimensions == 2:
                fig = go.Figure()
                
                # Plot trajectories for each agent
                for agent_idx in range(num_agents):
                    x_coords = []
                    y_coords = []
                    
                    for iter_idx in range(iterations):
                        if (iter_idx < len(positions_history) and 
                            agent_idx < len(positions_history[iter_idx])):
                            pos = positions_history[iter_idx][agent_idx]
                            if len(pos) >= 2:
                                x_coords.append(pos[0])
                                y_coords.append(pos[1])
                    
                    if x_coords and y_coords:
                        # Plot trajectory
                        fig.add_trace(go.Scatter(
                            x=x_coords, y=y_coords,
                            mode='lines+markers',
                            name=f'Agent {agent_idx+1}',
                            line=dict(color=self.colors[agent_idx % len(self.colors)]),
                            marker=dict(size=4),
                            hovertemplate=f'Agent {agent_idx+1}<br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<extra></extra>'
                        ))
                        
                        # Mark start position
                        fig.add_trace(go.Scatter(
                            x=[x_coords[0]], y=[y_coords[0]],
                            mode='markers',
                            marker=dict(
                                size=10, 
                                color=self.colors[agent_idx % len(self.colors)],
                                symbol='star'
                            ),
                            name=f'Agent {agent_idx+1} Start',
                            showlegend=False,
                            hovertemplate=f'Agent {agent_idx+1} Start<br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<extra></extra>'
                        ))
                
                fig.update_layout(
                    title="Agent Trajectories in Search Space",
                    xaxis_title="Dimension 1",
                    yaxis_title="Dimension 2",
                    height=600,
                    hovermode='closest'
                )
                
                return fig
                
            else:  # 3D plot for higher dimensions (use first 3 dimensions)
                fig = go.Figure()
                
                for agent_idx in range(num_agents):
                    x_coords, y_coords, z_coords = [], [], []
                    
                    for iter_idx in range(iterations):
                        if (iter_idx < len(positions_history) and 
                            agent_idx < len(positions_history[iter_idx])):
                            pos = positions_history[iter_idx][agent_idx]
                            if len(pos) >= 3:
                                x_coords.append(pos[0])
                                y_coords.append(pos[1])
                                z_coords.append(pos[2])
                    
                    if x_coords and y_coords and z_coords:
                        fig.add_trace(go.Scatter3d(
                            x=x_coords, y=y_coords, z=z_coords,
                            mode='lines+markers',
                            name=f'Agent {agent_idx+1}',
                            line=dict(color=self.colors[agent_idx % len(self.colors)]),
                            marker=dict(size=3)
                        ))
                
                fig.update_layout(
                    title="Agent Trajectories in 3D Search Space",
                    scene=dict(
                        xaxis_title="Dimension 1",
                        yaxis_title="Dimension 2",
                        zaxis_title="Dimension 3"
                    ),
                    height=700
                )
                
                return fig
                
        except Exception as e:
            st.warning(f"Could not plot agent trajectories: {e}")
            return None
    
    def plot_fitness_matrix(self, tracking_data):
        """Plot fitness evolution matrix for all agents"""
        try:
            if 'agent_fitness_history' not in tracking_data:
                return None
            
            fitness_history = tracking_data['agent_fitness_history']
            if not fitness_history:
                return None
            
            # Create fitness matrix: [iterations x agents]
            fitness_matrix = []
            for iter_fitness in fitness_history:
                fitness_matrix.append(iter_fitness)
            
            if not fitness_matrix:
                return None
            
            fitness_array = np.array(fitness_matrix)
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=fitness_array,
                x=[f'Agent {i+1}' for i in range(fitness_array.shape[1])],
                y=[f'Iter {i+1}' for i in range(fitness_array.shape[0])],
                colorscale='RdYlBu_r',
                hovertemplate='Agent: %{x}<br>Iteration: %{y}<br>Fitness: %{z:.6f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Agent Fitness Evolution Matrix",
                xaxis_title="Agents",
                yaxis_title="Iterations",
                height=500
            )
            
            return fig
            
        except Exception as e:
            st.warning(f"Could not plot fitness matrix: {e}")
            return None
    
    def plot_exploration_exploitation(self, tracking_data):
        """Plot exploration vs exploitation over time"""
        try:
            if 'exploration_exploitation_ratio' not in tracking_data:
                return None
            
            exp_exp_data = tracking_data['exploration_exploitation_ratio']
            if not exp_exp_data:
                return None
            
            iterations = list(range(1, len(exp_exp_data) + 1))
            
            fig = go.Figure()
            
            # Plot exploration/exploitation ratio
            fig.add_trace(go.Scatter(
                x=iterations,
                y=exp_exp_data,
                mode='lines+markers',
                name='Exploration Ratio',
                line=dict(color='blue', width=2),
                fill='tonexty',
                hovertemplate='Iteration: %{x}<br>Exploration Ratio: %{y:.3f}<extra></extra>'
            ))
            
            # Add reference lines
            fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                         annotation_text="Balanced", annotation_position="bottom right")
            fig.add_hline(y=0.7, line_dash="dot", line_color="green", 
                         annotation_text="High Exploration", annotation_position="top right")
            fig.add_hline(y=0.3, line_dash="dot", line_color="red", 
                         annotation_text="High Exploitation", annotation_position="bottom right")
            
            fig.update_layout(
                title="Exploration vs Exploitation Over Time",
                xaxis_title="Iteration",
                yaxis_title="Exploration Ratio (0=Exploitation, 1=Exploration)",
                height=400,
                yaxis=dict(range=[0, 1])
            )
            
            return fig
            
        except Exception as e:
            st.warning(f"Could not plot exploration/exploitation: {e}")
            return None
    
    def plot_diversity_evolution(self, tracking_data):
        """Plot population diversity over time"""
        try:
            if 'diversity_measures' not in tracking_data:
                return None
            
            diversity_data = tracking_data['diversity_measures']
            if not diversity_data:
                return None
            
            iterations = list(range(1, len(diversity_data) + 1))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=iterations,
                y=diversity_data,
                mode='lines+markers',
                name='Population Diversity',
                line=dict(color='purple', width=2),
                fill='tozeroy',
                hovertemplate='Iteration: %{x}<br>Diversity: %{y:.6f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Population Diversity Evolution",
                xaxis_title="Iteration", 
                yaxis_title="Diversity Measure",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.warning(f"Could not plot diversity evolution: {e}")
            return None
    
    def plot_convergence_analysis(self, convergence_data, algorithm_name):
        """Enhanced convergence analysis with multiple metrics"""
        try:
            if not convergence_data:
                return None
            
            iterations = list(range(1, len(convergence_data) + 1))
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "Fitness Convergence", "Convergence Rate",
                    "Improvement per Iteration", "Convergence Progress"
                ],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 1. Fitness convergence (log scale)
            fig.add_trace(
                go.Scatter(
                    x=iterations, y=convergence_data,
                    mode='lines',
                    name='Fitness',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
            
            # 2. Convergence rate (rolling window)
            if len(convergence_data) > 10:
                window_size = max(5, len(convergence_data) // 20)
                convergence_rate = []
                
                for i in range(window_size, len(convergence_data)):
                    rate = abs(convergence_data[i] - convergence_data[i-window_size]) / window_size
                    convergence_rate.append(rate)
                
                fig.add_trace(
                    go.Scatter(
                        x=iterations[window_size:], y=convergence_rate,
                        mode='lines',
                        name='Convergence Rate',
                        line=dict(color='red', width=2)
                    ),
                    row=1, col=2
                )
            
            # 3. Improvement per iteration
            improvements = [0] + [abs(convergence_data[i] - convergence_data[i-1]) 
                                for i in range(1, len(convergence_data))]
            
            fig.add_trace(
                go.Bar(
                    x=iterations, y=improvements,
                    name='Improvement',
                    marker_color='green',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # 4. Convergence progress (cumulative improvement)
            total_improvement = convergence_data[0] - min(convergence_data)
            progress = [(convergence_data[0] - fitness) / total_improvement * 100 
                       for fitness in convergence_data]
            
            fig.add_trace(
                go.Scatter(
                    x=iterations, y=progress,
                    mode='lines+markers',
                    name='Progress %',
                    line=dict(color='orange', width=2),
                    fill='tozeroy'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title=f"Convergence Analysis - {algorithm_name.upper()}",
                height=600,
                showlegend=False
            )
            
            # Update y-axis for log scale on fitness plot
            fig.update_yaxes(type="log", row=1, col=1)
            fig.update_yaxes(title_text="Progress (%)", row=2, col=2)
            
            return fig
            
        except Exception as e:
            st.warning(f"Could not create convergence analysis: {e}")
            return None
    
    def create_algorithm_dashboard(self, run_results, algorithm_name):
        """Create comprehensive dashboard for single algorithm analysis"""
        try:
            st.markdown(f"## 🔬 **Detailed Analysis - {algorithm_name.upper()}**")
            
            # Check if we have detailed tracking data
            detailed_tracking = None
            if 'detailed_tracking' in run_results['runs'][0]:
                detailed_tracking = run_results['runs'][0]['detailed_tracking']
            
            # Basic metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Best Fitness", 
                    f"{run_results['statistics']['best_fitness']:.6f}",
                    f"±{run_results['statistics']['std_fitness']:.6f}"
                )
            
            with col2:
                st.metric(
                    "Execution Time", 
                    f"{run_results['statistics']['mean_time']:.2f}s"
                )
            
            with col3:
                st.metric(
                    "Total Runs", 
                    run_results['statistics']['total_runs']
                )
            
            with col4:
                convergence_curve = run_results['runs'][0].get('convergence_curve', [])
                if convergence_curve:
                    final_improvement = ((convergence_curve[0] - convergence_curve[-1]) / 
                                       convergence_curve[0] * 100)
                    st.metric(
                        "Improvement", 
                        f"{final_improvement:.1f}%"
                    )
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Convergence", "🎯 Agent Tracking", "🔄 Exploration/Exploitation", 
                "📊 Fitness Matrix", "📋 Detailed Stats"
            ])
            
            with tab1:
                st.markdown("### Convergence Analysis")
                convergence_curve = run_results['runs'][0].get('convergence_curve', [])
                if convergence_curve:
                    conv_fig = self.plot_convergence_analysis(convergence_curve, algorithm_name)
                    if conv_fig:
                        st.plotly_chart(conv_fig, use_container_width=True, key=get_unique_key(f"convergence_{algorithm_name}"))
                else:
                    st.warning("No convergence data available")
            
            with tab2:
                st.markdown("### Agent Trajectories")
                if detailed_tracking:
                    traj_fig = self.plot_agent_trajectories(detailed_tracking)
                    if traj_fig:
                        st.plotly_chart(traj_fig, use_container_width=True, key=get_unique_key(f"trajectories_{algorithm_name}"))
                    else:
                        st.info("Agent trajectory data not available for this run")
                else:
                    st.info("Enable detailed tracking mode for agent trajectory analysis")
            
            with tab3:
                st.markdown("### Exploration vs Exploitation")
                if detailed_tracking:
                    exp_fig = self.plot_exploration_exploitation(detailed_tracking)
                    if exp_fig:
                        st.plotly_chart(exp_fig, use_container_width=True, key=get_unique_key(f"exploration_{algorithm_name}"))
                    
                    div_fig = self.plot_diversity_evolution(detailed_tracking)
                    if div_fig:
                        st.plotly_chart(div_fig, use_container_width=True, key=get_unique_key(f"diversity_{algorithm_name}"))
                else:
                    st.info("Enable detailed tracking mode for exploration/exploitation analysis")
            
            with tab4:
                st.markdown("### Agent Fitness Matrix")
                if detailed_tracking:
                    matrix_fig = self.plot_fitness_matrix(detailed_tracking)
                    if matrix_fig:
                        st.plotly_chart(matrix_fig, use_container_width=True, key=get_unique_key(f"matrix_{algorithm_name}"))
                else:
                    st.info("Enable detailed tracking mode for fitness matrix analysis")
            
            with tab5:
                st.markdown("### Detailed Statistics")
                
                # Performance breakdown
                st.markdown("#### Performance Breakdown")
                stats_df = pd.DataFrame([
                    {"Metric": "Best Fitness", "Value": f"{run_results['statistics']['best_fitness']:.6f}"},
                    {"Metric": "Mean Fitness", "Value": f"{run_results['statistics']['mean_fitness']:.6f}"},
                    {"Metric": "Std Fitness", "Value": f"{run_results['statistics']['std_fitness']:.6f}"},
                    {"Metric": "Worst Fitness", "Value": f"{run_results['statistics']['worst_fitness']:.6f}"},
                    {"Metric": "Mean Time", "Value": f"{run_results['statistics']['mean_time']:.3f}s"},
                    {"Metric": "Std Time", "Value": f"{run_results['statistics']['std_time']:.3f}s"},
                ])
                st.dataframe(stats_df, use_container_width=True)
                
                # Run-by-run breakdown
                st.markdown("#### Individual Run Results")
                runs_data = []
                for run in run_results['runs']:
                    runs_data.append({
                        "Run": run['run'],
                        "Fitness": f"{run['best_fitness']:.6f}",
                        "Time": f"{run['execution_time']:.2f}s",
                        "Success": "✅" if run.get('success', True) else "❌"
                    })
                
                runs_df = pd.DataFrame(runs_data)
                st.dataframe(runs_df, use_container_width=True)
            
            return True
            
        except Exception as e:
            st.error(f"Error creating algorithm dashboard: {e}")
            return False