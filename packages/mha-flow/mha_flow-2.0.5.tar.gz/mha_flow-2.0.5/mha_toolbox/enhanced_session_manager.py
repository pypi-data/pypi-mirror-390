"""
Enhanced Session Manager for Algorithm Comparison
===============================================

Implements comprehensive session management for:
- Session revival and continuation
- Adding new algorithms to existing sessions
- Comprehensive Excel export with multiple sheets
- Dashboard-style visualizations
- Systematic result organization
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference, BarChart
import io


class EnhancedSessionManager:
    """Advanced session management with revival and update capabilities"""
    
    def __init__(self, detailed_collector=None):
        self.collector = detailed_collector
        self.current_session_data = None
        self.dashboard_data = {}
        
    def display_session_management_interface(self):
        """Main interface for session management"""
        
        st.markdown("## 🔄 **ENHANCED SESSION MANAGEMENT**")
        st.info("🔄 **Session Management**: Revive sessions, add algorithms, generate comprehensive reports")
        
        # Session management tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Browse Sessions", 
            "🔄 Revive & Update", 
            "📊 Dashboard", 
            "📋 Export Center"
        ])
        
        with tab1:
            self.display_session_browser()
        
        with tab2:
            self.display_session_revival_interface()
        
        with tab3:
            self.display_enhanced_dashboard()
        
        with tab4:
            self.display_comprehensive_export_center()
    
    def display_session_browser(self):
        """Browse and explore available sessions"""
        
        st.markdown("### 🔍 **SESSION BROWSER**")
        
        # Get all sessions organized by dataset
        available_results = self.collector.list_available_results()
        
        if not available_results:
            st.warning("⚠️ No sessions found. Run some experiments first!")
            return
        
        # Organize by dataset and session
        sessions_data = {}
        for result in available_results:
            dataset = result['dataset']
            session = result['session']
            
            if dataset not in sessions_data:
                sessions_data[dataset] = {}
            
            if session not in sessions_data[dataset]:
                sessions_data[dataset][session] = {
                    'algorithms': [],
                    'total_size': 0,
                    'created_at': None,
                    'total_iterations': 0
                }
            
            session_info = sessions_data[dataset][session]
            session_info['algorithms'].append(result['metadata']['algorithm_name'])
            session_info['total_size'] += result['metadata']['file_size_mb']
            session_info['total_iterations'] += result['metadata']['total_iterations']
            
            if not session_info['created_at']:
                session_info['created_at'] = result['metadata']['created_at']
        
        # Display sessions in organized format
        for dataset_name, sessions in sessions_data.items():
            st.markdown(f"### 📊 **Dataset: {dataset_name}**")
            
            session_cols = st.columns(min(len(sessions), 3))
            
            for i, (session_id, session_info) in enumerate(sessions.items()):
                with session_cols[i % 3]:
                    with st.container():
                        st.markdown(f"#### 📁 **{session_id}**")
                        st.markdown(f"**📅 Created:** {session_info['created_at'][:16]}")
                        st.markdown(f"**🔬 Algorithms:** {len(session_info['algorithms'])}")
                        st.markdown(f"**💽 Total Size:** {session_info['total_size']:.2f} MB")
                        st.markdown(f"**🔢 Total Iterations:** {session_info['total_iterations']:,}")
                        
                        # Algorithm list
                        alg_text = ", ".join(session_info['algorithms'][:3])
                        if len(session_info['algorithms']) > 3:
                            alg_text += f" +{len(session_info['algorithms']) - 3} more"
                        st.markdown(f"**Algorithms:** {alg_text}")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"🔄 Revive", key=f"revive_{dataset_name}_{session_id}"):
                                self.set_revival_session(dataset_name, session_id)
                                st.success(f"Session {session_id} selected for revival!")
                        
                        with col2:
                            if st.button(f"📊 Dashboard", key=f"dash_{dataset_name}_{session_id}"):
                                self.load_session_dashboard(dataset_name, session_id)
                                st.success(f"Dashboard loaded for {session_id}!")
    
    def display_session_revival_interface(self):
        """Interface for reviving and updating sessions"""
        
        st.markdown("### 🔄 **SESSION REVIVAL & UPDATE**")
        st.info("➕ **Add new algorithms to existing sessions for comprehensive comparison**")
        
        # Check if a session is selected for revival
        if 'revival_session' not in st.session_state:
            st.warning("👆 Please select a session to revive from the Session Browser tab")
            return
        
        revival_info = st.session_state.revival_session
        dataset_name = revival_info['dataset']
        session_id = revival_info['session']
        
        st.success(f"📁 **Reviving Session**: {session_id}")
        st.info(f"📊 **Dataset**: {dataset_name}")
        
        # Load existing session data
        existing_algorithms = self.get_session_algorithms(dataset_name, session_id)
        
        st.markdown("#### 📋 **Current Session Contents**")
        
        # Display existing algorithms
        if existing_algorithms:
            cols = st.columns(min(len(existing_algorithms), 4))
            for i, alg_info in enumerate(existing_algorithms):
                with cols[i % 4]:
                    st.success(f"✅ **{alg_info['algorithm'].upper()}**")
                    st.text(f"Fitness: {alg_info['best_fitness']:.6f}")
                    st.text(f"Iterations: {alg_info['total_iterations']}")
        
        st.markdown("---")
        st.markdown("#### ➕ **Add New Algorithms to Session**")
        
        # Algorithm selection for adding to session
        from mha_comparison_toolbox import MHAComparisonToolbox
        
        try:
            toolbox = MHAComparisonToolbox()
            available_algorithms = toolbox.get_algorithm_names()
            
            # Filter out algorithms already in session
            existing_alg_names = [alg['algorithm'] for alg in existing_algorithms]
            new_algorithms = [alg for alg in available_algorithms if alg not in existing_alg_names]
            
            if new_algorithms:
                st.markdown(f"**Available algorithms to add:** {len(new_algorithms)}")
                
                # Multi-select for new algorithms
                selected_new_algorithms = st.multiselect(
                    "Select algorithms to add to session:",
                    new_algorithms,
                    help=f"These algorithms will be added to session {session_id}"
                )
                
                if selected_new_algorithms:
                    # Parameters for new algorithms
                    st.markdown("#### ⚙️ **Parameters for New Algorithms**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_max_iterations = st.number_input("Max Iterations", 10, 1000, 50)
                        new_population_size = st.number_input("Population Size", 10, 200, 30)
                    with col2:
                        new_n_runs = st.number_input("Number of Runs", 1, 10, 3)
                        new_timeout = st.number_input("Timeout (minutes)", 1, 60, 5)
                    
                    # Add algorithms button
                    if st.button("➕ Add Selected Algorithms to Session", type="primary"):
                        self.add_algorithms_to_session(
                            dataset_name, session_id, selected_new_algorithms,
                            new_max_iterations, new_population_size, new_n_runs, new_timeout
                        )
            else:
                st.info("All available algorithms are already in this session!")
        
        except Exception as e:
            st.error(f"Error loading algorithms: {e}")
    
    def add_algorithms_to_session(self, dataset_name, session_id, new_algorithms, 
                                 max_iterations, population_size, n_runs, timeout_minutes):
        """Add new algorithms to existing session"""
        
        st.markdown("---")
        st.markdown("### 🚀 **ADDING ALGORITHMS TO EXISTING SESSION**")
        
        # Load dataset (need to get from session metadata or user input)
        # For now, we'll need the user to provide the dataset
        dataset_placeholder = st.empty()
        
        with st.spinner("🔄 Preparing to add algorithms to session..."):
            # We need to load the original dataset
            # This would normally be stored in session metadata
            st.warning("⚠️ **Dataset Selection Needed**: Please select the same dataset used in the original session")
            
            # Dataset selection for revival
            dataset_choice = st.selectbox(
                "Select dataset (must match original):",
                ["Breast Cancer", "Wine", "Iris", "Digits", "California Housing", "Diabetes"]
            )
            
            if st.button("🚀 Start Adding Algorithms", type="primary"):
                # Load dataset
                X, y, dataset_display_name = self.load_dataset_for_revival(dataset_choice)
                
                if X is not None:
                    # Update the session collector to continue in existing session
                    self.collector.current_session = session_id
                    self.collector.current_dataset = dataset_name
                    self.collector.session_dir = self.collector.base_dir / dataset_name / session_id
                    
                    # Run new algorithms
                    self.run_additional_algorithms(
                        X, y, dataset_display_name, new_algorithms,
                        max_iterations, population_size, n_runs, timeout_minutes
                    )
    
    def run_additional_algorithms(self, X, y, dataset_name, algorithms, 
                                 max_iterations, population_size, n_runs, timeout_minutes):
        """Run additional algorithms and add to existing session"""
        
        st.markdown("### 🔬 **RUNNING ADDITIONAL ALGORITHMS**")
        
        from mha_toolbox.enhanced_runner import run_algorithm_with_detailed_tracking
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_additions = 0
        
        for i, alg_name in enumerate(algorithms):
            progress = (i / len(algorithms))
            progress_bar.progress(progress)
            status_text.text(f"🔬 Adding {alg_name.upper()} to session [{i+1}/{len(algorithms)}]...")
            
            try:
                # Run algorithm with detailed tracking
                alg_results = run_algorithm_with_detailed_tracking(
                    algorithm_name=alg_name,
                    X=X, y=y,
                    task_type='feature_selection',  # Could be made configurable
                    max_iterations=max_iterations,
                    population_size=population_size,
                    n_runs=n_runs,
                    timeout_seconds=timeout_minutes * 60,
                    collector=self.collector,
                    show_progress=False
                )
                
                if alg_results:
                    successful_additions += 1
                    st.success(f"✅ {alg_name.upper()} successfully added to session!")
                else:
                    st.error(f"❌ {alg_name.upper()} failed to complete")
                    
            except Exception as e:
                st.error(f"❌ Error adding {alg_name.upper()}: {str(e)}")
        
        # Finalize updated session
        progress_bar.progress(1.0)
        status_text.text(f"✅ Session update complete! Added {successful_additions}/{len(algorithms)} algorithms")
        
        if successful_additions > 0:
            # Update session metadata
            session_result = self.collector.finalize_session()
            
            st.success(f"🎉 **SESSION SUCCESSFULLY UPDATED!**")
            st.success(f"✅ Added {successful_additions} new algorithms to existing session")
            
            # Refresh session data
            self.refresh_session_data()
    
    def display_enhanced_dashboard(self):
        """Display comprehensive dashboard with complete analysis"""
        
        st.markdown("### 📊 **ENHANCED ALGORITHM DASHBOARD**")
        st.info("📊 **Comprehensive Dashboard**: Complete visualization suite")
        
        # Session selection for dashboard
        if 'dashboard_session' not in st.session_state:
            st.warning("👆 Please select a session from the Session Browser to load dashboard")
            return
        
        dashboard_info = st.session_state.dashboard_session
        dataset_name = dashboard_info['dataset']
        session_id = dashboard_info['session']
        
        st.success(f"📊 **Dashboard for**: {session_id} | Dataset: {dataset_name}")
        
        # Load session data for dashboard
        session_algorithms = self.get_session_algorithms(dataset_name, session_id)
        
        if not session_algorithms:
            st.error("No algorithm data found for dashboard")
            return
        
        # Dashboard layout
        self.create_comprehensive_dashboard(session_algorithms, dataset_name, session_id)
    
    def create_comprehensive_dashboard(self, algorithms_data, dataset_name, session_id):
        """Create comprehensive dashboard with all visualizations"""
        
        # Dashboard header
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 **Algorithms**", len(algorithms_data))
        with col2:
            total_iterations = sum(alg['total_iterations'] for alg in algorithms_data)
            st.metric("🔢 **Total Iterations**", f"{total_iterations:,}")
        with col3:
            best_fitness = min(alg['best_fitness'] for alg in algorithms_data)
            st.metric("🏆 **Best Fitness**", f"{best_fitness:.6f}")
        with col4:
            total_time = sum(alg.get('total_time', 0) for alg in algorithms_data)
            st.metric("⏱️ **Total Time**", f"{total_time:.1f}s")
        
        # Main dashboard visualizations
        st.markdown("---")
        
        # 1. Convergence Curves Comparison
        st.markdown("### 📈 **CONVERGENCE CURVES COMPARISON**")
        self.create_convergence_dashboard(algorithms_data)
        
        st.markdown("---")
        
        # 2. Performance Matrix
        st.markdown("### 📊 **PERFORMANCE MATRIX DASHBOARD**")
        self.create_performance_matrix_dashboard(algorithms_data)
        
        st.markdown("---")
        
        # 3. Statistical Analysis Dashboard
        st.markdown("### 📋 **STATISTICAL ANALYSIS DASHBOARD**")
        self.create_statistical_dashboard(algorithms_data)
        
        st.markdown("---")
        
        # 4. Algorithm Comparison Matrix
        st.markdown("### 🔍 **ALGORITHM COMPARISON MATRIX**")
        self.create_comparison_matrix_dashboard(algorithms_data)
    
    def create_convergence_dashboard(self, algorithms_data):
        """Create convergence curves dashboard"""
        
        # Algorithm selection for convergence plot
        algorithm_names = [alg['algorithm'] for alg in algorithms_data]
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("#### 🎛️ **Plot Controls**")
            selected_algorithms = st.multiselect(
                "Select algorithms for convergence plot:",
                algorithm_names,
                default=algorithm_names[:3] if len(algorithm_names) >= 3 else algorithm_names,
                help="Choose specific algorithms to compare"
            )
            
            plot_type = st.selectbox(
                "Plot Type:",
                ["Line Plot", "Line + Markers", "Markers Only"],
                index=0
            )
            
            show_confidence = st.checkbox("Show Confidence Intervals", value=False)
            log_scale = st.checkbox("Logarithmic Y-axis", value=False)
        
        with col1:
            if selected_algorithms:
                # Load NPZ data for selected algorithms
                convergence_data = {}
                
                for alg_data in algorithms_data:
                    if alg_data['algorithm'] in selected_algorithms:
                        # Load NPZ file
                        npz_path = alg_data['npz_path']
                        try:
                            npz_data = self.collector.load_algorithm_npz(npz_path)
                            if npz_data and 'convergence_curve' in npz_data:
                                convergence_data[alg_data['algorithm']] = npz_data['convergence_curve']
                        except Exception as e:
                            st.error(f"Error loading {alg_data['algorithm']}: {e}")
                
                # Create convergence plot
                if convergence_data:
                    fig = go.Figure()
                    
                    colors = px.colors.qualitative.Set1
                    
                    for i, (alg_name, convergence) in enumerate(convergence_data.items()):
                        iterations = np.arange(len(convergence))
                        
                        mode = 'lines'
                        if plot_type == "Line + Markers":
                            mode = 'lines+markers'
                        elif plot_type == "Markers Only":
                            mode = 'markers'
                        
                        fig.add_trace(go.Scatter(
                            x=iterations,
                            y=convergence,
                            mode=mode,
                            name=alg_name.upper(),
                            line=dict(color=colors[i % len(colors)], width=3),
                            marker=dict(size=6) if 'markers' in mode else None,
                            hovertemplate=f"<b>{alg_name.upper()}</b><br>" +
                                        "Iteration: %{x}<br>" +
                                        "Fitness: %{y:.6f}<br>" +
                                        "<extra></extra>"
                        ))
                    
                    fig.update_layout(
                        title=dict(
                            text="🚀 Algorithm Convergence Comparison Dashboard",
                            font=dict(size=20, color='darkblue')
                        ),
                        xaxis_title="Iteration",
                        yaxis_title="Best Fitness",
                        yaxis_type="log" if log_scale else "linear",
                        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)'),
                        hovermode='x unified',
                        template="plotly_white",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export convergence data button
                    if st.button("📥 Export Convergence Data as CSV"):
                        self.export_convergence_csv(convergence_data, selected_algorithms)
                
                else:
                    st.warning("No convergence data found for selected algorithms")
            else:
                st.info("👆 Select algorithms to display convergence curves")
    
    def export_convergence_csv(self, convergence_data, algorithm_names):
        """Export convergence data as CSV"""
        
        # Create DataFrame with convergence data
        max_iterations = max(len(curve) for curve in convergence_data.values())
        
        # Prepare data dictionary
        csv_data = {'Iteration': list(range(max_iterations))}
        
        for alg_name, convergence in convergence_data.items():
            # Pad shorter curves with NaN
            padded_curve = list(convergence) + [np.nan] * (max_iterations - len(convergence))
            csv_data[f"{alg_name.upper()}_Fitness"] = padded_curve
        
        df = pd.DataFrame(csv_data)
        
        # Create download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📥 Download Convergence CSV",
            data=csv_buffer.getvalue(),
            file_name=f"convergence_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.success("📊 Convergence data exported successfully!")
    
    def load_dataset_for_revival(self, dataset_choice):
        """Load dataset for session revival"""
        
        if dataset_choice == "Breast Cancer":
            from sklearn.datasets import load_breast_cancer
            data = load_breast_cancer()
            return data.data, data.target, "Breast Cancer"
        
        elif dataset_choice == "Wine":
            from sklearn.datasets import load_wine
            data = load_wine()
            return data.data, data.target, "Wine"
        
        elif dataset_choice == "Iris":
            from sklearn.datasets import load_iris
            data = load_iris()
            return data.data, data.target, "Iris"
        
        # Add other datasets as needed
        else:
            st.error(f"Dataset {dataset_choice} not implemented yet")
            return None, None, None
    
    def get_session_algorithms(self, dataset_name, session_id):
        """Get all algorithms in a specific session"""
        
        available_results = self.collector.list_available_results(dataset_name)
        
        session_algorithms = []
        for result in available_results:
            if result['session'] == session_id:
                metadata = result['metadata']
                session_algorithms.append({
                    'algorithm': metadata['algorithm_name'],
                    'best_fitness': metadata['best_fitness'],
                    'total_iterations': metadata['total_iterations'],
                    'file_size_mb': metadata['file_size_mb'],
                    'created_at': metadata['created_at'],
                    'npz_path': result['npz_path'],
                    'metadata_path': result['metadata_path']
                })
        
        return sorted(session_algorithms, key=lambda x: x['best_fitness'])
    
    def set_revival_session(self, dataset_name, session_id):
        """Set session for revival"""
        st.session_state.revival_session = {
            'dataset': dataset_name,
            'session': session_id
        }
    
    def load_session_dashboard(self, dataset_name, session_id):
        """Load session for dashboard"""
        st.session_state.dashboard_session = {
            'dataset': dataset_name,
            'session': session_id
        }
    
    def create_performance_matrix_dashboard(self, algorithms_data):
        """Create performance matrix dashboard"""
        from .comprehensive_exporter import DashboardComponents
        DashboardComponents.create_performance_matrix_dashboard(algorithms_data)
    
    def create_statistical_dashboard(self, algorithms_data):
        """Create statistical analysis dashboard"""
        from .comprehensive_exporter import DashboardComponents
        DashboardComponents.create_statistical_dashboard(algorithms_data)
    
    def create_comparison_matrix_dashboard(self, algorithms_data):
        """Create comparison matrix dashboard"""
        from .comprehensive_exporter import DashboardComponents
        DashboardComponents.create_comparison_matrix_dashboard(algorithms_data)
    
    def display_comprehensive_export_center(self):
        """Display comprehensive export center with complete analysis"""
        
        st.markdown("### 📋 **COMPREHENSIVE EXPORT CENTER**")
        st.info("📊 **Export Center**: Multi-sheet Excel exports with complete analysis")
        
        # Check if session is loaded for export
        if 'dashboard_session' not in st.session_state:
            st.warning("👆 Please load a session from the Dashboard tab first")
            return
        
        dashboard_info = st.session_state.dashboard_session
        dataset_name = dashboard_info['dataset']
        session_id = dashboard_info['session']
        
        st.success(f"📊 **Export Session**: {session_id} | Dataset: {dataset_name}")
        
        # Load session data
        session_algorithms = self.get_session_algorithms(dataset_name, session_id)
        
        if not session_algorithms:
            st.error("No algorithm data found for export")
            return
        
        # Export options
        st.markdown("#### 📊 **Available Export Formats**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Comprehensive Excel Export
            st.markdown("##### 📋 **Comprehensive Excel Report**")
            st.markdown("""
            **Includes 6 sheets:**
            - 📄 Summary Overview
            - 📊 Detailed Statistics  
            - 📈 Convergence Data
            - 🎯 Performance Matrix
            - 🔍 Comparison Analysis
            - 📋 Raw Data Export
            """)
            
            if st.button("📥 Generate Comprehensive Excel", type="primary"):
                from .comprehensive_exporter import ComprehensiveExporter
                exporter = ComprehensiveExporter(self)
                exporter.create_comprehensive_excel_export(session_algorithms, dataset_name, session_id)
        
        with col2:
            # Individual exports
            st.markdown("##### 📊 **Individual Exports**")
            
            if st.button("📈 Export Convergence CSV"):
                self.export_individual_convergence_csv(session_algorithms)
            
            if st.button("📋 Export Summary CSV"):
                self.export_summary_csv(session_algorithms, dataset_name, session_id)
            
            if st.button("📊 Export Statistics JSON"):
                self.export_statistics_json(session_algorithms, dataset_name, session_id)
        
        # Export preview
        st.markdown("---")
        st.markdown("#### 👀 **Export Preview**")
        
        # Show what will be exported
        with st.expander("📋 **Data Preview - Summary Table**"):
            preview_data = []
            for alg in session_algorithms:
                preview_data.append({
                    'Algorithm': alg['algorithm'].upper(),
                    'Best Fitness': f"{alg['best_fitness']:.6f}",
                    'Iterations': alg['total_iterations'],
                    'File Size': f"{alg['file_size_mb']:.2f} MB"
                })
            
            df_preview = pd.DataFrame(preview_data)
            st.dataframe(df_preview, width=600)
    
    def export_individual_convergence_csv(self, algorithms_data):
        """Export convergence data as individual CSV"""
        
        # Load convergence data
        convergence_data = {}
        max_iterations = 0
        
        for alg_data in algorithms_data:
            try:
                npz_data = self.collector.load_algorithm_npz(alg_data['npz_path'])
                if npz_data and 'convergence_curve' in npz_data:
                    convergence_curve = npz_data['convergence_curve']
                    convergence_data[alg_data['algorithm'].upper()] = convergence_curve
                    max_iterations = max(max_iterations, len(convergence_curve))
            except Exception as e:
                st.warning(f"Could not load convergence for {alg_data['algorithm']}: {e}")
        
        if convergence_data:
            # Create DataFrame
            df_convergence = pd.DataFrame({'Iteration': range(max_iterations)})
            
            for alg_name, curve in convergence_data.items():
                padded_curve = list(curve) + [np.nan] * (max_iterations - len(curve))
                df_convergence[f"{alg_name}_Fitness"] = padded_curve
            
            # Create download
            csv_buffer = io.StringIO()
            df_convergence.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📥 Download Convergence CSV",
                data=csv_buffer.getvalue(),
                file_name=f"convergence_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("📈 Convergence CSV exported successfully!")
    
    def export_summary_csv(self, algorithms_data, dataset_name, session_id):
        """Export summary data as CSV"""
        
        summary_data = []
        for i, alg in enumerate(algorithms_data):
            summary_data.append({
                'Rank': i + 1,
                'Algorithm': alg['algorithm'].upper(),
                'Best_Fitness': alg['best_fitness'],
                'Total_Iterations': alg['total_iterations'],
                'File_Size_MB': alg['file_size_mb'],
                'Created_At': alg['created_at']
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        csv_buffer = io.StringIO()
        df_summary.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📥 Download Summary CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{dataset_name}_{session_id}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.success("📋 Summary CSV exported successfully!")
    
    def export_statistics_json(self, algorithms_data, dataset_name, session_id):
        """Export detailed statistics as JSON"""
        
        stats_export = {
            'metadata': {
                'dataset': dataset_name,
                'session_id': session_id,
                'export_date': datetime.now().isoformat(),
                'total_algorithms': len(algorithms_data)
            },
            'algorithms': {},
            'summary_statistics': {
                'best_overall_fitness': min(alg['best_fitness'] for alg in algorithms_data),
                'worst_overall_fitness': max(alg['best_fitness'] for alg in algorithms_data),
                'mean_fitness': np.mean([alg['best_fitness'] for alg in algorithms_data]),
                'total_iterations': sum(alg['total_iterations'] for alg in algorithms_data)
            }
        }
        
        # Add individual algorithm data
        for alg in algorithms_data:
            stats_export['algorithms'][alg['algorithm']] = {
                'best_fitness': alg['best_fitness'],
                'total_iterations': alg['total_iterations'],
                'file_size_mb': alg['file_size_mb'],
                'created_at': alg['created_at'],
                'npz_path': alg['npz_path']
            }
        
        # Convert to JSON
        json_str = json.dumps(stats_export, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Statistics JSON",
            data=json_str,
            file_name=f"{dataset_name}_{session_id}_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("📊 Statistics JSON exported successfully!")
    
    def refresh_session_data(self):
        """Refresh session data after updates"""
        # Clear cached data to force refresh
        if 'revival_session' in st.session_state:
            del st.session_state.revival_session
        if 'dashboard_session' in st.session_state:
            del st.session_state.dashboard_session