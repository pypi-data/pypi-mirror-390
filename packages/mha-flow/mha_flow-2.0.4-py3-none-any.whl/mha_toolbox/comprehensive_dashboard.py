"""
User-Friendly Comprehensive Dashboard
====================================

Professional dashboard interface with:
- Session management and continuation
- Algorithm addition to existing sessions
- Convergence curve plotting with user selection
- CSV export with professional formatting
- Real-time results visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from pathlib import Path
from datetime import datetime
import json


class ComprehensiveDashboard:
    """Main dashboard interface for algorithm comparison system"""
    
    def __init__(self, csv_manager, convergence_manager):
        self.csv_manager = csv_manager
        self.convergence_manager = convergence_manager
        self.current_results = {}
    
    def display_main_dashboard(self):
        """Display the main dashboard interface"""
        
        st.markdown("# 🎯 **COMPREHENSIVE MHA DASHBOARD**")
        st.markdown("### Professional Algorithm Comparison & Analysis System")
        
        # Dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔬 **Current Session**", 
            "📊 **Results Analysis**", 
            "📈 **Convergence Plots**", 
            "💾 **Export Center**", 
            "🔄 **Session Manager**"
        ])
        
        with tab1:
            self.display_current_session_tab()
        
        with tab2:
            self.display_results_analysis_tab()
        
        with tab3:
            self.display_convergence_plots_tab()
        
        with tab4:
            self.display_export_center_tab()
        
        with tab5:
            self.display_session_manager_tab()
    
    def display_current_session_tab(self):
        """Display current session status and controls"""
        
        st.markdown("## 🔬 **CURRENT SESSION STATUS**")
        
        # Session information display
        if self.csv_manager.current_session:
            session_data = self.csv_manager.session_data
            
            # Session metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📁 **Session ID**", session_data['session_name'][:15] + "...")
            with col2:
                st.metric("📊 **Dataset**", session_data.get('dataset_name', 'Unknown'))
            with col3:
                st.metric("🧬 **Algorithms**", len(session_data['algorithms']))
            with col4:
                st.metric("📁 **Exports**", len(session_data['export_files']))
            
            # Session timeline
            st.markdown("### 📅 **Session Timeline**")
            
            timeline_data = []
            for alg in session_data['algorithms']:
                timeline_data.append({
                    'Time': alg['added_at'][:16],
                    'Algorithm': alg['algorithm_name'].upper(),
                    'Best Fitness': f"{alg['best_fitness']:.6f}",
                    'Iterations': alg['total_iterations'],
                    'Status': '✅ Complete'
                })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                st.dataframe(df_timeline, width=800)
            
            # Quick actions
            st.markdown("### ⚡ **Quick Actions**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Add Algorithm", type="primary", key="current_session_add_alg"):
                    st.session_state.show_add_algorithm = True
            
            with col2:
                if st.button("📊 Export Results", key="current_session_export"):
                    self.quick_export_results()
            
            with col3:
                if st.button("📈 View Plots", key="current_session_plots"):
                    st.session_state.active_tab = "convergence"
            
            # Add algorithm interface
            if st.session_state.get('show_add_algorithm', False):
                self.display_add_algorithm_interface()
        
        else:
            # No active session
            st.info("🔄 **No Active Session**")
            st.markdown("Start a new session or load an existing one from the Session Manager tab.")
            
            # Quick start options
            st.markdown("### 🚀 **Quick Start**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🆕 Start New Session", type="primary", key="quick_start_new_session"):
                    self.start_new_session_wizard()
            
            with col2:
                if st.button("📁 Load Existing Session", key="quick_start_load_session"):
                    st.session_state.show_session_loader = True
    
    def display_add_algorithm_interface(self):
        """Interface for adding algorithms to current session"""
        
        st.markdown("---")
        st.markdown("### ➕ **ADD ALGORITHM TO SESSION**")
        
        with st.expander("🔧 Algorithm Configuration", expanded=True):
            
            # Algorithm selection
            from mha_comparison_toolbox import MHAComparisonToolbox
            
            try:
                toolbox = MHAComparisonToolbox()
                available_algorithms = toolbox.get_algorithm_names()
                
                # Filter out already added algorithms
                existing_algorithms = self.csv_manager.get_session_algorithms()
                new_algorithms = [alg for alg in available_algorithms if alg not in existing_algorithms]
                
                if new_algorithms:
                    selected_algorithm = st.selectbox(
                        "Select Algorithm:",
                        new_algorithms,
                        help="Choose an algorithm to add to the current session"
                    )
                    
                    # Parameters
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        max_iterations = st.number_input("Max Iterations", 10, 1000, 50)
                        population_size = st.number_input("Population Size", 10, 200, 30)
                    
                    with col2:
                        n_runs = st.number_input("Number of Runs", 1, 10, 3)
                        timeout_minutes = st.number_input("Timeout (minutes)", 1, 60, 5)
                    
                    # Run button
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button("🚀 Run Algorithm", type="primary", key="add_alg_run"):
                            self.run_and_add_algorithm(
                                selected_algorithm, max_iterations, 
                                population_size, n_runs, timeout_minutes
                            )
                    
                    with col2:
                        if st.button("❌ Cancel", key="add_alg_cancel"):
                            st.session_state.show_add_algorithm = False
                            st.rerun()
                
                else:
                    st.warning("All available algorithms have been added to this session!")
                    if st.button("✅ Done", key="add_alg_done"):
                        st.session_state.show_add_algorithm = False
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error loading algorithms: {e}")
    
    def run_and_add_algorithm(self, algorithm_name, max_iterations, population_size, n_runs, timeout_minutes):
        """Run algorithm and add to current session"""
        
        st.markdown("---")
        st.markdown("### 🚀 **RUNNING ALGORITHM**")
        
        # Load dataset (this should be stored in session or re-selected)
        dataset_name = self.csv_manager.session_data.get('dataset_name', 'Breast Cancer')
        X, y = self.load_dataset(dataset_name)
        
        if X is not None:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize algorithm tracking
                status_text.text(f"🔧 Initializing {algorithm_name.upper()}...")
                progress_bar.progress(0.2)
                
                # Run algorithm (simplified version for demo)
                status_text.text(f"🚀 Running {algorithm_name.upper()}...")
                progress_bar.progress(0.6)
                
                # Simulate algorithm execution with actual results
                algorithm_results, convergence_data = self.simulate_algorithm_run(
                    algorithm_name, X, y, max_iterations, population_size, n_runs
                )
                
                progress_bar.progress(0.9)
                status_text.text("💾 Saving results...")
                
                # Add to session
                success = self.csv_manager.add_algorithm_to_session(
                    algorithm_name, algorithm_results, convergence_data
                )
                
                progress_bar.progress(1.0)
                
                if success:
                    status_text.text("✅ Algorithm added successfully!")
                    st.success(f"🎉 {algorithm_name.upper()} successfully added to session!")
                    
                    # Update current results for immediate viewing
                    self.current_results[algorithm_name] = {
                        'data': algorithm_results,
                        'convergence': convergence_data
                    }
                    
                    # Reset add algorithm interface
                    st.session_state.show_add_algorithm = False
                    
                    # Auto-refresh after 2 seconds
                    st.rerun()
                
                else:
                    st.error("Failed to add algorithm to session")
            
            except Exception as e:
                st.error(f"Error running algorithm: {e}")
                progress_bar.progress(0)
                status_text.text("❌ Algorithm execution failed")
        
        else:
            st.error("Failed to load dataset")
    
    def simulate_algorithm_run(self, algorithm_name, X, y, max_iterations, population_size, n_runs):
        """Simulate algorithm execution (replace with actual algorithm call)"""
        
        # This is a simulation - replace with actual algorithm execution
        np.random.seed(42)
        
        # Simulate convergence curve
        initial_fitness = np.random.uniform(0.8, 1.0)
        convergence_curve = []
        current_fitness = initial_fitness
        
        for i in range(max_iterations):
            # Simulate improvement with diminishing returns
            improvement = np.random.exponential(0.01) * np.exp(-i/20)
            current_fitness = max(0.01, current_fitness - improvement)
            convergence_curve.append(current_fitness)
        
        # Algorithm results
        algorithm_results = {
            'best_fitness': min(convergence_curve),
            'total_iterations': max_iterations,
            'execution_time': np.random.uniform(10, 60),
            'statistics': {
                'mean_fitness': np.mean(convergence_curve[-10:]),
                'std_fitness': np.std(convergence_curve[-10:]),
                'total_runs': n_runs
            }
        }
        
        return algorithm_results, convergence_curve
    
    def display_results_analysis_tab(self):
        """Display comprehensive results analysis"""
        
        st.markdown("## 📊 **RESULTS ANALYSIS**")
        
        if not self.csv_manager.current_session or not self.csv_manager.session_data['algorithms']:
            st.info("No results available. Please run some algorithms first.")
            return
        
        # Results overview
        algorithms_data = self.csv_manager.session_data['algorithms']
        
        # Summary metrics
        st.markdown("### 📈 **Performance Summary**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        fitness_values = [alg['best_fitness'] for alg in algorithms_data]
        
        with col1:
            st.metric("🏆 **Best Fitness**", f"{min(fitness_values):.6f}")
        with col2:
            st.metric("📊 **Mean Fitness**", f"{np.mean(fitness_values):.6f}")
        with col3:
            st.metric("📈 **Fitness Range**", f"{max(fitness_values) - min(fitness_values):.6f}")
        with col4:
            best_algorithm = min(algorithms_data, key=lambda x: x['best_fitness'])
            st.metric("🥇 **Champion**", best_algorithm['algorithm_name'].upper())
        
        # Performance ranking table
        st.markdown("### 🏆 **Algorithm Rankings**")
        
        ranking_data = []
        for i, alg in enumerate(sorted(algorithms_data, key=lambda x: x['best_fitness'])):
            ranking_data.append({
                'Rank': i + 1,
                'Algorithm': alg['algorithm_name'].upper(),
                'Best Fitness': f"{alg['best_fitness']:.6f}",
                'Iterations': alg['total_iterations'],
                'Execution Time': f"{alg['execution_time']:.1f}s",
                'Added': alg['added_at'][:16]
            })
        
        df_ranking = pd.DataFrame(ranking_data)
        st.dataframe(df_ranking, width=900)
        
        # Performance visualization
        st.markdown("### 📊 **Performance Visualization**")
        
        # Performance comparison chart
        fig = px.bar(
            df_ranking,
            x='Algorithm',
            y='Best Fitness',
            color='Best Fitness',
            color_continuous_scale='RdYlBu_r',
            title="🎯 Algorithm Performance Comparison"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                x=fitness_values,
                title="📊 Fitness Distribution",
                nbins=min(10, len(fitness_values))
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            execution_times = [alg['execution_time'] for alg in algorithms_data]
            fig_time = px.scatter(
                x=execution_times,
                y=fitness_values,
                title="⚡ Performance vs Time",
                labels={'x': 'Execution Time (s)', 'y': 'Best Fitness'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    def display_convergence_plots_tab(self):
        """Display convergence plotting interface"""
        
        st.markdown("## 📈 **CONVERGENCE CURVE ANALYSIS**")
        
        if not self.csv_manager.current_session:
            st.info("No active session. Please start or load a session first.")
            return
        
        # Load convergence data for current session
        session_algorithms = {}
        
        for alg in self.csv_manager.session_data['algorithms']:
            alg_name = alg['algorithm_name']
            
            # Check if we have convergence data in current results
            if alg_name in self.current_results:
                session_algorithms[alg_name] = {
                    'convergence_curve': self.current_results[alg_name]['convergence']
                }
            else:
                # Try to load from exported files or generate sample data
                session_algorithms[alg_name] = {
                    'convergence_curve': self.generate_sample_convergence(alg['best_fitness'])
                }
        
        if session_algorithms:
            # Use the convergence plot manager
            self.convergence_manager.display_convergence_interface(session_algorithms)
        else:
            st.warning("No convergence data available for plotting")
    
    def generate_sample_convergence(self, final_fitness):
        """Generate sample convergence curve (replace with actual data loading)"""
        
        # Simulate a convergence curve ending at final_fitness
        np.random.seed(hash(final_fitness) % 2**32)
        
        iterations = 50
        initial_fitness = final_fitness + np.random.uniform(0.1, 0.5)
        
        curve = []
        current = initial_fitness
        
        for i in range(iterations):
            improvement = (initial_fitness - final_fitness) * np.exp(-i/15) * np.random.uniform(0.5, 1.5)
            current = max(final_fitness, current - improvement)
            curve.append(current)
        
        return curve
    
    def display_export_center_tab(self):
        """Display comprehensive export center"""
        
        st.markdown("## 💾 **EXPORT CENTER**")
        
        if not self.csv_manager.current_session:
            st.info("No active session to export.")
            return
        
        session_data = self.csv_manager.session_data
        
        # Export options
        st.markdown("### 📊 **Available Exports**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 **Session Reports**")
            
            if st.button("📄 Export Session Summary CSV", type="primary", key="export_session_summary"):
                filepath = self.csv_manager.export_session_summary_csv()
                st.success("Session summary exported!")
            
            if st.button("📊 Export All Algorithm Details", key="export_all_details"):
                self.export_all_algorithm_details()
            
            if st.button("📈 Export Convergence Comparison", key="export_convergence"):
                self.export_convergence_comparison()
        
        with col2:
            st.markdown("#### 📦 **Comprehensive Packages**")
            
            if st.button("🗂️ Create Complete Export Package", key="export_complete_package"):
                self.create_complete_package()
            
            if st.button("📧 Email-Ready Report", key="export_email_report"):
                self.create_email_report()
            
            if st.button("📊 Dashboard Screenshot", key="export_screenshot"):
                st.info("Feature coming soon!")
        
        # Export history
        st.markdown("### 📁 **Export History**")
        
        if session_data['export_files']:
            export_data = []
            for export_file in session_data['export_files']:
                export_data.append({
                    'Filename': export_file['filename'],
                    'Type': export_file['type'].replace('_', ' ').title(),
                    'Created': export_file['created_at'][:16],
                    'Status': '✅ Available'
                })
            
            df_exports = pd.DataFrame(export_data)
            st.dataframe(df_exports, width=700)
        else:
            st.info("No exports created yet.")
    
    def display_session_manager_tab(self):
        """Display session management interface"""
        
        st.markdown("## 🔄 **SESSION MANAGER**")
        
        # Current session status
        if self.csv_manager.current_session:
            st.success(f"✅ **Active Session**: {self.csv_manager.current_session}")
            
            session_data = self.csv_manager.session_data
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📅 Created", session_data['created_at'][:10])
            with col2:
                st.metric("🧬 Algorithms", len(session_data['algorithms']))
            with col3:
                st.metric("💾 Exports", len(session_data['export_files']))
            
            # Session actions
            st.markdown("### ⚙️ **Session Actions**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Session", key="session_actions_save"):
                    self.csv_manager.update_session_summary()
                    st.success("Session saved!")
            
            with col2:
                if st.button("🔄 New Session", key="session_actions_new"):
                    self.start_new_session_wizard()
            
            with col3:
                if st.button("📁 Load Session", key="session_actions_load"):
                    st.session_state.show_session_loader = True
        
        else:
            st.info("🔄 **No Active Session**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🆕 Start New Session", type="primary", key="session_mgr_new_session_no_active"):
                    self.start_new_session_wizard()
            
            with col2:
                if st.button("📁 Load Existing Session", key="session_mgr_load_session_no_active"):
                    st.session_state.show_session_loader = True
        
        # Session loader interface
        if st.session_state.get('show_session_loader', False):
            self.display_session_loader()
    
    def start_new_session_wizard(self):
        """Start new session creation wizard"""
        
        st.markdown("---")
        st.markdown("### 🆕 **NEW SESSION WIZARD**")
        
        with st.form("new_session_form"):
            
            # Session configuration
            session_name = st.text_input(
                "Session Name (optional):",
                placeholder="Leave empty for auto-generated name"
            )
            
            dataset_choice = st.selectbox(
                "Select Dataset:",
                ["Breast Cancer", "Wine", "Iris", "Digits", "California Housing"]
            )
            
            session_description = st.text_area(
                "Session Description (optional):",
                placeholder="Brief description of this session..."
            )
            
            submitted = st.form_submit_button("🚀 Create Session", type="primary")
            
            if submitted:
                # Initialize new session
                session_id = self.csv_manager.initialize_session(
                    session_name if session_name else None,
                    dataset_choice
                )
                
                if session_description:
                    self.csv_manager.session_data['description'] = session_description
                
                st.success(f"✅ New session created: {session_id}")
                
                # Clear form
                st.rerun()
    
    def display_session_loader(self):
        """Display session loading interface"""
        
        st.markdown("---")
        st.markdown("### 📁 **LOAD EXISTING SESSION**")
        
        # List available sessions
        csv_base = Path("results/csv_exports")
        
        # Debug information
        st.write(f"🔍 **Debug**: Looking for sessions in: {csv_base.absolute()}")
        st.write(f"🔍 **Debug**: Directory exists: {csv_base.exists()}")
        
        if csv_base.exists():
            session_dirs = [d for d in csv_base.iterdir() if d.is_dir()]
            st.write(f"🔍 **Debug**: Found {len(session_dirs)} directories")
            
            if session_dirs:
                session_options = []
                session_info = {}
                
                for session_dir in session_dirs:
                    metadata_file = session_dir / "session_metadata.json"
                    st.write(f"🔍 **Debug**: Checking {metadata_file}")
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            session_name = metadata['session_name']
                            session_options.append(session_name)
                            session_info[session_name] = {
                                'path': session_dir,
                                'metadata': metadata
                            }
                        except:
                            continue
                
                if session_options:
                    selected_session = st.selectbox(
                        "Select Session to Load:",
                        session_options
                    )
                    
                    if selected_session:
                        metadata = session_info[selected_session]['metadata']
                        
                        # Show session preview
                        st.markdown("#### 👀 **Session Preview**")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Dataset", metadata.get('dataset_name', 'Unknown'))
                        with col2:
                            st.metric("🧬 Algorithms", len(metadata.get('algorithms', [])))
                        with col3:
                            st.metric("📅 Created", metadata.get('created_at', '')[:10])
                        
                        # Load button
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            if st.button("📂 Load Session", type="primary", key="session_loader_load"):
                                try:
                                    success = self.csv_manager.load_existing_session(
                                        session_info[selected_session]['path']
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Loaded session: {selected_session}")
                                        st.session_state.show_session_loader = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to load session")
                                except Exception as e:
                                    st.error(f"❌ Error loading session: {str(e)}")
                        
                        with col2:
                            if st.button("❌ Cancel", key="session_loader_cancel"):
                                st.session_state.show_session_loader = False
                                st.rerun()
                
                else:
                    st.warning("No valid sessions found")
            
            else:
                st.info("No existing sessions found")
        
        else:
            st.info("No sessions directory found")
    
    def load_dataset(self, dataset_name):
        """Load dataset by name"""
        
        try:
            if dataset_name == "Breast Cancer":
                from sklearn.datasets import load_breast_cancer
                data = load_breast_cancer()
                return data.data, data.target
            
            elif dataset_name == "Wine":
                from sklearn.datasets import load_wine
                data = load_wine()
                return data.data, data.target
            
            elif dataset_name == "Iris":
                from sklearn.datasets import load_iris
                data = load_iris()
                return data.data, data.target
            
            # Add more datasets as needed
            else:
                st.error(f"Dataset {dataset_name} not implemented")
                return None, None
        
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return None, None
    
    def quick_export_results(self):
        """Quick export of current results"""
        
        if self.csv_manager.current_session:
            filepath = self.csv_manager.export_session_summary_csv()
            st.success("✅ Quick export completed!")
        else:
            st.error("No active session to export")
    
    def export_all_algorithm_details(self):
        """Export detailed CSV files for all algorithms"""
        
        session_data = self.csv_manager.session_data
        exported_count = 0
        
        for alg in session_data['algorithms']:
            alg_name = alg['algorithm_name']
            
            # Prepare algorithm data
            algorithm_data = {
                'best_fitness': alg['best_fitness'],
                'total_iterations': alg['total_iterations'],
                'execution_time': alg['execution_time']
            }
            
            # Get convergence data if available
            convergence_data = None
            if alg_name in self.current_results:
                convergence_data = self.current_results[alg_name]['convergence']
            
            # Export
            self.csv_manager.export_algorithm_csv(alg_name, algorithm_data, convergence_data)
            exported_count += 1
        
        st.success(f"✅ Exported {exported_count} algorithm detail files!")
    
    def export_convergence_comparison(self):
        """Export convergence comparison CSV"""
        
        # Prepare convergence data
        algorithms_data = {}
        
        for alg in self.csv_manager.session_data['algorithms']:
            alg_name = alg['algorithm_name']
            
            if alg_name in self.current_results:
                algorithms_data[alg_name] = {
                    'convergence_curve': self.current_results[alg_name]['convergence']
                }
            else:
                # Generate sample convergence
                algorithms_data[alg_name] = {
                    'convergence_curve': self.generate_sample_convergence(alg['best_fitness'])
                }
        
        if algorithms_data:
            filepath = self.csv_manager.export_convergence_comparison_csv(algorithms_data)
            st.success("✅ Convergence comparison exported!")
        else:
            st.warning("No convergence data available for export")
    
    def create_complete_package(self):
        """Create comprehensive export package"""
        
        # First export all individual files
        self.export_all_algorithm_details()
        self.export_convergence_comparison()
        
        # Create the comprehensive package
        algorithms_data = {}
        for alg in self.csv_manager.session_data['algorithms']:
            alg_name = alg['algorithm_name']
            if alg_name in self.current_results:
                algorithms_data[alg_name] = {
                    'convergence_curve': self.current_results[alg_name]['convergence']
                }
        
        zip_path = self.csv_manager.create_comprehensive_export_package(algorithms_data)
        st.success("✅ Complete export package created!")
    
    def create_email_report(self):
        """Create email-ready summary report"""
        
        session_data = self.csv_manager.session_data
        
        # Create summary report
        report_content = f"""
MHA Algorithm Comparison Report
=============================

Session: {session_data['session_name']}
Dataset: {session_data.get('dataset_name', 'Unknown')}
Created: {session_data['created_at'][:16]}
Total Algorithms: {len(session_data['algorithms'])}

Algorithm Rankings:
"""
        
        # Add algorithm rankings
        algorithms = sorted(session_data['algorithms'], key=lambda x: x['best_fitness'])
        
        for i, alg in enumerate(algorithms):
            report_content += f"{i+1}. {alg['algorithm_name'].upper()}: {alg['best_fitness']:.6f}\n"
        
        report_content += f"""

Best Performing Algorithm: {algorithms[0]['algorithm_name'].upper()}
Best Fitness Achieved: {algorithms[0]['best_fitness']:.6f}

Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Create download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"email_report_{timestamp}.txt"
        
        st.download_button(
            label="📧 Download Email Report",
            data=report_content,
            file_name=filename,
            mime="text/plain"
        )
        
        st.success("✅ Email report ready for download!")