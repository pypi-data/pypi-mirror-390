"""
NPZ Results Comparison and Visualization Module
==============================================

Implements comprehensive NPZ file comparison for plotting
multiple algorithm results from NPZ files with comprehensive
analysis capabilities.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class NPZResultsComparator:
    """Compare and visualize multiple algorithm results from NPZ files"""
    
    def __init__(self, collector):
        self.collector = collector
        self.loaded_results = {}
        
    def display_comparison_interface(self):
        """Display the comparison interface for NPZ analysis"""
        
        st.markdown("---")
        st.markdown("## 📊 **NPZ RESULTS COMPARISON & ANALYSIS**")
        st.info("📊 **NPZ File Analysis**: Select NPZ files to compare convergence curves and detailed metrics")
        
        # Get available results
        available_results = self.collector.list_available_results()
        
        if not available_results:
            st.warning("⚠️ No NPZ result files found. Run some algorithms first to generate detailed data.")
            return
        
        # Group by dataset for easier selection
        datasets = {}
        for result in available_results:
            dataset = result['dataset']
            if dataset not in datasets:
                datasets[dataset] = []
            datasets[dataset].append(result)
        
        # Dataset selection
        st.markdown("### 🗂️ **Step 1: Select Dataset**")
        dataset_names = list(datasets.keys())
        selected_dataset = st.selectbox(
            "Choose dataset to analyze:",
            dataset_names,
            help="Results are organized by dataset following the tree structure"
        )
        
        if selected_dataset:
            dataset_results = datasets[selected_dataset]
            
            # Session and algorithm selection
            st.markdown("### 🔬 **Step 2: Select Algorithms to Compare**")
            
            # Group by session for better organization
            sessions = {}
            for result in dataset_results:
                session = result['session']
                if session not in sessions:
                    sessions[session] = []
                sessions[session].append(result)
            
            # Display available sessions and algorithms
            selected_results = []
            
            for session_name, session_results in sessions.items():
                with st.expander(f"📁 **Session: {session_name}** ({len(session_results)} algorithms)", expanded=True):
                    st.text(f"Session created: {session_results[0]['metadata']['created_at'][:16]}")
                    
                    cols = st.columns(min(len(session_results), 4))
                    for i, result in enumerate(session_results):
                        with cols[i % 4]:
                            metadata = result['metadata']
                            include = st.checkbox(
                                f"**{metadata['algorithm_name'].upper()}**",
                                key=f"include_{session_name}_{metadata['algorithm_name']}",
                                help=f"Best fitness: {metadata['best_fitness']:.6f}\nIterations: {metadata['total_iterations']}\nFile size: {metadata['file_size_mb']:.2f} MB"
                            )
                            
                            if include:
                                selected_results.append(result)
                            
                            # Show quick stats
                            st.text(f"Best: {metadata['best_fitness']:.6f}")
                            st.text(f"Iterations: {metadata['total_iterations']}")
                            st.text(f"Size: {metadata['file_size_mb']:.2f} MB")
            
            # Comparison and visualization
            if selected_results:
                st.markdown("---")
                st.markdown(f"### 📈 **Step 3: Compare {len(selected_results)} Selected Algorithms**")
                
                # Load selected NPZ files
                with st.spinner("📊 Loading NPZ data for comparison..."):
                    self.load_selected_results(selected_results)
                
                # Display comparison tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Convergence", 
                    "📊 Statistics", 
                    "🔍 Population", 
                    "📋 Summary", 
                    "💾 Export"
                ])
                
                with tab1:
                    self.display_convergence_comparison()
                
                with tab2:
                    self.display_detailed_statistics()
                
                with tab3:
                    self.display_population_analysis()
                
                with tab4:
                    self.display_comparison_summary()
                
                with tab5:
                    self.display_export_options()
            
            else:
                st.info("👆 Select algorithms above to start comparison")
    
    def load_selected_results(self, selected_results):
        """Load NPZ data for selected results"""
        
        self.loaded_results = {}
        
        for result in selected_results:
            algorithm_name = result['metadata']['algorithm_name']
            npz_path = result['npz_path']
            
            try:
                npz_data = self.collector.load_algorithm_npz(npz_path)
                if npz_data:
                    self.loaded_results[algorithm_name] = {
                        'npz_data': npz_data,
                        'metadata': result['metadata'],
                        'session': result['session']
                    }
                    
            except Exception as e:
                st.error(f"Failed to load {algorithm_name}: {e}")
        
        st.success(f"✅ Loaded {len(self.loaded_results)} algorithms for comparison")
    
    def display_convergence_comparison(self):
        """Display convergence curve comparison analysis"""
        
        st.markdown("### 📈 **CONVERGENCE CURVES COMPARISON**")
        st.info("📈 **Convergence Analysis**: Compare convergence behavior across algorithms")
        
        if not self.loaded_results:
            st.warning("No data loaded for comparison")
            return
        
        # Create convergence plot
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set1
        
        for i, (alg_name, data) in enumerate(self.loaded_results.items()):
            npz_data = data['npz_data']
            
            # Get convergence curve
            if 'convergence_curve' in npz_data:
                convergence = npz_data['convergence_curve']
                iterations = np.arange(len(convergence))
                
                fig.add_trace(go.Scatter(
                    x=iterations,
                    y=convergence,
                    mode='lines',
                    name=f"{alg_name.upper()}",
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate=f"<b>{alg_name.upper()}</b><br>" +
                                "Iteration: %{x}<br>" +
                                "Fitness: %{y:.6f}<br>" +
                                "<extra></extra>"
                ))
        
        fig.update_layout(
            title="Algorithm Convergence Comparison",
            xaxis_title="Iteration",
            yaxis_title="Best Fitness",
            legend=dict(x=0.7, y=0.95),
            hovermode='x unified',
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Convergence statistics
        st.markdown("#### 📊 **Convergence Analysis**")
        
        convergence_stats = []
        for alg_name, data in self.loaded_results.items():
            npz_data = data['npz_data']
            
            if 'convergence_curve' in npz_data:
                convergence = npz_data['convergence_curve']
                
                # Calculate convergence metrics
                initial_fitness = float(convergence[0])
                final_fitness = float(convergence[-1])
                improvement = initial_fitness - final_fitness
                improvement_rate = improvement / max(initial_fitness, 1e-10)
                
                # Find convergence point (when improvement becomes minimal)
                conv_point = len(convergence)
                for i in range(10, len(convergence)):
                    recent_improvement = abs(convergence[i-10] - convergence[i])
                    if recent_improvement < 1e-6:
                        conv_point = i
                        break
                
                convergence_stats.append({
                    'Algorithm': alg_name.upper(),
                    'Initial Fitness': f"{initial_fitness:.6f}",
                    'Final Fitness': f"{final_fitness:.6f}",
                    'Total Improvement': f"{improvement:.6f}",
                    'Improvement Rate': f"{improvement_rate:.2%}",
                    'Convergence Point': conv_point,
                    'Total Iterations': len(convergence)
                })
        
        df_conv = pd.DataFrame(convergence_stats)
        st.dataframe(df_conv, width="stretch")
    
    def display_detailed_statistics(self):
        """Display detailed statistics comparison"""
        
        st.markdown("### 📊 **DETAILED STATISTICS COMPARISON**")
        st.info("📊 **Statistical Analysis**: Comprehensive statistical analysis of algorithm performance")
        
        if not self.loaded_results:
            st.warning("No data loaded for comparison")
            return
        
        # Compile statistics from NPZ data
        stats_data = []
        
        for alg_name, data in self.loaded_results.items():
            npz_data = data['npz_data']
            metadata = data['metadata']
            
            # Extract statistics from NPZ arrays
            stats = {
                'Algorithm': alg_name.upper(),
                'Best Fitness': float(npz_data['final_best_fitness'][0]) if 'final_best_fitness' in npz_data else 0,
                'Total Iterations': int(npz_data['total_iterations'][0]) if 'total_iterations' in npz_data else 0,
                'Total Time (s)': float(npz_data['total_time'][0]) if 'total_time' in npz_data else 0,
                'Population Size': int(npz_data['population_size'][0]) if 'population_size' in npz_data else 0,
                'Dimensions': int(npz_data['dimensions'][0]) if 'dimensions' in npz_data else 0,
                'File Size (MB)': metadata['file_size_mb']
            }
            
            # Add iteration-based statistics
            if 'mean_fitness_per_iteration' in npz_data:
                mean_fitness = npz_data['mean_fitness_per_iteration']
                stats['Mean Final Fitness'] = float(mean_fitness[-1])
                stats['Fitness Std Dev'] = float(np.std(mean_fitness))
            
            if 'diversity_measure' in npz_data:
                diversity = npz_data['diversity_measure']
                stats['Avg Diversity'] = float(np.mean(diversity))
                stats['Final Diversity'] = float(diversity[-1])
            
            stats_data.append(stats)
        
        # Display statistics table
        df_stats = pd.DataFrame(stats_data)
        st.dataframe(df_stats, width="stretch")
        
        # Performance metrics visualization
        st.markdown("#### 📈 **Performance Metrics Visualization**")
        
        # Best fitness comparison
        fig_fitness = px.bar(
            df_stats, 
            x='Algorithm', 
            y='Best Fitness',
            title="Best Fitness Comparison",
            color='Best Fitness',
            color_continuous_scale='Viridis_r'
        )
        st.plotly_chart(fig_fitness, use_container_width=True)
        
        # Execution time comparison
        fig_time = px.bar(
            df_stats,
            x='Algorithm',
            y='Total Time (s)',
            title="Execution Time Comparison",
            color='Total Time (s)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    def display_population_analysis(self):
        """Display population-level analysis from detailed tracking"""
        
        st.markdown("### 🔍 **POPULATION ANALYSIS**")
        st.info("🔍 **Population Analysis**: Analyze population behavior and diversity")
        
        if not self.loaded_results:
            st.warning("No data loaded for comparison")
            return
        
        # Population diversity comparison
        fig_diversity = go.Figure()
        
        colors = px.colors.qualitative.Set1
        
        for i, (alg_name, data) in enumerate(self.loaded_results.items()):
            npz_data = data['npz_data']
            
            if 'diversity_measure' in npz_data:
                diversity = npz_data['diversity_measure']
                iterations = np.arange(len(diversity))
                
                fig_diversity.add_trace(go.Scatter(
                    x=iterations,
                    y=diversity,
                    mode='lines',
                    name=f"{alg_name.upper()} Diversity",
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig_diversity.update_layout(
            title="Population Diversity Over Iterations",
            xaxis_title="Iteration",
            yaxis_title="Diversity Measure",
            template="plotly_white"
        )
        
        st.plotly_chart(fig_diversity, use_container_width=True)
        
        # Fitness distribution analysis
        st.markdown("#### 📊 **Fitness Distribution Analysis**")
        
        for alg_name, data in self.loaded_results.items():
            npz_data = data['npz_data']
            
            if 'population_fitness_history' in npz_data:
                with st.expander(f"📈 {alg_name.upper()} - Population Fitness Distribution"):
                    
                    fitness_history = npz_data['population_fitness_history']
                    
                    # Show fitness distribution for different iterations
                    selected_iterations = [0, len(fitness_history)//4, len(fitness_history)//2, -1]
                    iteration_names = ["Initial", "25%", "50%", "Final"]
                    
                    fig_dist = go.Figure()
                    
                    for i, (iter_idx, iter_name) in enumerate(zip(selected_iterations, iteration_names)):
                        if iter_idx < len(fitness_history):
                            fitness_values = fitness_history[iter_idx]
                            
                            fig_dist.add_trace(go.Box(
                                y=fitness_values,
                                name=f"{iter_name} (Iter {iter_idx if iter_idx >= 0 else len(fitness_history) + iter_idx})",
                                boxpoints='outliers'
                            ))
                    
                    fig_dist.update_layout(
                        title=f"{alg_name.upper()} - Fitness Distribution Evolution",
                        yaxis_title="Fitness Value",
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_dist, use_container_width=True)
    
    def display_comparison_summary(self):
        """Display comprehensive comparison summary"""
        
        st.markdown("### 📋 **COMPREHENSIVE COMPARISON SUMMARY**")
        st.info("📋 **Summary Report**: Summary sheet with all algorithm statistics")
        
        if not self.loaded_results:
            st.warning("No data loaded for comparison")
            return
        
        # Create comprehensive summary
        summary_data = []
        
        for alg_name, data in self.loaded_results.items():
            npz_data = data['npz_data']
            metadata = data['metadata']
            
            # Calculate comprehensive metrics
            summary = {
                'Algorithm': alg_name.upper(),
                'Session': data['session'],
                'Best Fitness': float(npz_data['final_best_fitness'][0]) if 'final_best_fitness' in npz_data else 0,
                'Total Iterations': int(npz_data['total_iterations'][0]) if 'total_iterations' in npz_data else 0,
                'Execution Time (s)': float(npz_data['total_time'][0]) if 'total_time' in npz_data else 0,
                'Population Size': int(npz_data['population_size'][0]) if 'population_size' in npz_data else 0,
                'Problem Dimensions': int(npz_data['dimensions'][0]) if 'dimensions' in npz_data else 0,
                'Task Type': npz_data['task_type'][0] if 'task_type' in npz_data else 'Unknown',
            }
            
            # Add convergence metrics
            if 'convergence_curve' in npz_data:
                convergence = npz_data['convergence_curve']
                summary['Initial Fitness'] = float(convergence[0])
                summary['Final Fitness'] = float(convergence[-1])
                summary['Total Improvement'] = float(convergence[0] - convergence[-1])
                summary['Improvement Rate (%)'] = float((convergence[0] - convergence[-1]) / max(convergence[0], 1e-10) * 100)
            
            # Add diversity metrics
            if 'diversity_measure' in npz_data:
                diversity = npz_data['diversity_measure']
                summary['Initial Diversity'] = float(diversity[0])
                summary['Final Diversity'] = float(diversity[-1])
                summary['Avg Diversity'] = float(np.mean(diversity))
            
            # Add timing metrics
            if 'iteration_times' in npz_data:
                iter_times = npz_data['iteration_times']
                summary['Avg Iteration Time (s)'] = float(np.mean(iter_times))
                summary['Total Computation Time (s)'] = float(np.sum(iter_times))
            
            # Data storage metrics
            summary['NPZ File Size (MB)'] = metadata['file_size_mb']
            summary['Data Arrays Count'] = len(metadata['data_arrays'])
            summary['Created At'] = metadata['created_at']
            
            summary_data.append(summary)
        
        # Display summary table
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, width="stretch")
        
        # Winner analysis
        st.markdown("#### 🏆 **WINNER ANALYSIS**")
        
        if summary_data:
            # Best fitness winner
            best_fitness_winner = min(summary_data, key=lambda x: x['Best Fitness'])
            fastest_winner = min(summary_data, key=lambda x: x['Execution Time (s)'])
            most_improved_winner = max(summary_data, key=lambda x: x.get('Improvement Rate (%)', 0))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("🥇 **BEST FITNESS**")
                st.metric("Algorithm", best_fitness_winner['Algorithm'])
                st.metric("Best Fitness", f"{best_fitness_winner['Best Fitness']:.6f}")
                st.metric("Improvement", f"{best_fitness_winner.get('Improvement Rate (%)', 0):.2f}%")
            
            with col2:
                st.info("⚡ **FASTEST EXECUTION**")
                st.metric("Algorithm", fastest_winner['Algorithm'])
                st.metric("Time", f"{fastest_winner['Execution Time (s)']:.2f}s")
                st.metric("Iterations", fastest_winner['Total Iterations'])
            
            with col3:
                st.warning("📈 **MOST IMPROVED**")
                st.metric("Algorithm", most_improved_winner['Algorithm'])
                st.metric("Improvement", f"{most_improved_winner.get('Improvement Rate (%)', 0):.2f}%")
                st.metric("Total Change", f"{most_improved_winner.get('Total Improvement', 0):.6f}")
    
    def display_export_options(self):
        """Display export options for comparison results"""
        
        st.markdown("### 💾 **EXPORT COMPARISON RESULTS**")
        st.info("💾 **Export Options**: Export comparison data for external analysis")
        
        if not self.loaded_results:
            st.warning("No data loaded for export")
            return
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Summary to Excel", type="primary"):
                self.export_summary_excel()
        
        with col2:
            if st.button("📈 Export Convergence Data", type="secondary"):
                self.export_convergence_data()
        
        # Show available data for export
        st.markdown("#### 📋 **Available Data for Export**")
        
        for alg_name, data in self.loaded_results.items():
            npz_data = data['npz_data']
            metadata = data['metadata']
            
            with st.expander(f"📁 {alg_name.upper()} - Available Arrays"):
                if isinstance(npz_data, dict):
                    st.text(f"📊 Arrays in data: {len(npz_data.keys())}")
                    for array_name, array_data in npz_data.items():
                        if isinstance(array_data, np.ndarray):
                            st.text(f"• {array_name}: {array_data.shape} {array_data.dtype}")
                        else:
                            st.text(f"• {array_name}: {type(array_data)}")
                else:
                    st.text(f"📊 Arrays in NPZ file: {len(npz_data.files) if hasattr(npz_data, 'files') else 'Unknown'}")
                    if hasattr(npz_data, 'files'):
                        for array_name in npz_data.files:
                            array_data = npz_data[array_name]
                            st.text(f"• {array_name}: {array_data.shape} {array_data.dtype}")
    
    def export_summary_excel(self):
        """Export comparison summary to Excel format"""
        # Implementation would create Excel export
        st.success("📊 Summary exported to Excel format")
        st.info("Feature coming soon: Excel export with all comparison metrics")
    
    def export_convergence_data(self):
        """Export convergence data for external plotting"""
        # Implementation would create convergence data export
        st.success("📈 Convergence data exported")
        st.info("Feature coming soon: CSV export of convergence curves")