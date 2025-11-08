"""
Advanced Session Controller for MHA Toolbox
==========================================

Implements professional session management with:
- Single active session per user
- Automatic session updates and algorithm replacement
- Real-time progress tracking
- Session persistence across browser refreshes
- Intelligent algorithm comparison and replacement
"""

import streamlit as st
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any
import uuid


class SessionController:
    """Advanced session controller for MHA toolbox"""
    
    def __init__(self, base_dir="persistent_state"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Session configuration
        self.session_file = self.base_dir / "active_session.json"
        self.user_session_id = self._get_or_create_session_id()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _get_or_create_session_id(self) -> str:
        """Get existing session ID or create new one"""
        
        # Check if session exists in streamlit state
        if 'user_session_id' in st.session_state:
            return st.session_state.user_session_id
        
        # Check if session file exists
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                session_id = session_data.get('session_id', str(uuid.uuid4()))
            except:
                session_id = str(uuid.uuid4())
        else:
            session_id = str(uuid.uuid4())
        
        # Store in streamlit state
        st.session_state.user_session_id = session_id
        return session_id
    
    def _initialize_session_state(self):
        """Initialize session state with default values"""
        
        # Core session data
        if 'active_session' not in st.session_state:
            st.session_state.active_session = {
                'session_id': self.user_session_id,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'current_dataset': None,
                'algorithms': {},  # {algorithm_name: algorithm_data}
                'session_status': 'active',
                'total_algorithms_run': 0,
                'current_running_algorithm': None,
                'results_ready': False
            }
        
        # Algorithm tracking
        if 'algorithm_results' not in st.session_state:
            st.session_state.algorithm_results = {}
        
        # Progress tracking
        if 'current_progress' not in st.session_state:
            st.session_state.current_progress = {
                'algorithm_name': None,
                'progress_percentage': 0,
                'current_iteration': 0,
                'status': 'ready',
                'start_time': None,
                'estimated_completion': None
            }
        
        # UI state
        if 'show_results' not in st.session_state:
            st.session_state.show_results = False
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
    
    def get_active_session(self) -> Dict:
        """Get the current active session"""
        return st.session_state.active_session
    
    def update_session_dataset(self, dataset_name: str):
        """Update the dataset for current session"""
        
        session = st.session_state.active_session
        
        # If dataset changed, ask user about session reset
        if session['current_dataset'] and session['current_dataset'] != dataset_name:
            if session['algorithms']:  # If there are existing algorithms
                st.warning(f"⚠️ Changing dataset from **{session['current_dataset']}** to **{dataset_name}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Keep Current Session", key="keep_session"):
                        st.info("Keeping existing session with previous results")
                        return False
                
                with col2:
                    if st.button("🆕 Start New Session", key="new_session_dataset"):
                        self.start_new_session(dataset_name)
                        return True
                
                return False  # Don't proceed until user decides
        
        # Update dataset
        session['current_dataset'] = dataset_name
        session['last_updated'] = datetime.now().isoformat()
        self._save_session()
        
        return True
    
    def start_new_session(self, dataset_name: str = None):
        """Start a completely new session"""
        
        # Clear all current data
        st.session_state.active_session = {
            'session_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'current_dataset': dataset_name,
            'algorithms': {},
            'session_status': 'active',
            'total_algorithms_run': 0,
            'current_running_algorithm': None,
            'results_ready': False
        }
        
        # Clear algorithm results
        st.session_state.algorithm_results = {}
        
        # Reset progress
        st.session_state.current_progress = {
            'algorithm_name': None,
            'progress_percentage': 0,
            'current_iteration': 0,
            'status': 'ready',
            'start_time': None,
            'estimated_completion': None
        }
        
        st.session_state.show_results = False
        
        self._save_session()
        st.success(f"🆕 New session started! Session ID: {st.session_state.active_session['session_id'][:8]}...")
        
        return st.session_state.active_session['session_id']
    
    def add_or_update_algorithm(self, algorithm_name: str, algorithm_config: Dict, 
                               algorithm_results: Dict) -> bool:
        """Add new algorithm or update existing one if better results"""
        
        session = st.session_state.active_session
        existing_algorithm = session['algorithms'].get(algorithm_name)
        
        # Check if we should replace existing algorithm
        should_replace = False
        replacement_reason = ""
        
        if existing_algorithm:
            # Compare results
            existing_fitness = existing_algorithm.get('best_fitness', float('inf'))
            new_fitness = algorithm_results.get('best_fitness', float('inf'))
            
            # Check if new result is better
            if new_fitness < existing_fitness:
                should_replace = True
                replacement_reason = f"Better fitness: {new_fitness:.6f} vs {existing_fitness:.6f}"
            
            # Check if configuration changed
            elif algorithm_config != existing_algorithm.get('config', {}):
                should_replace = True
                replacement_reason = "Configuration updated"
            
            if should_replace:
                st.warning(f"🔄 Replacing existing {algorithm_name} results")
                st.info(f"📈 Reason: {replacement_reason}")
        
        # Add/update algorithm
        session['algorithms'][algorithm_name] = {
            'algorithm_name': algorithm_name,
            'config': algorithm_config,
            'results': algorithm_results,
            'added_at': datetime.now().isoformat(),
            'replaced': should_replace,
            'replacement_reason': replacement_reason if should_replace else None
        }
        
        # Update session metadata
        if not should_replace and algorithm_name not in session['algorithms']:
            session['total_algorithms_run'] += 1
        
        session['last_updated'] = datetime.now().isoformat()
        session['results_ready'] = True
        
        # Store in algorithm results for quick access
        st.session_state.algorithm_results[algorithm_name] = algorithm_results
        
        self._save_session()
        
        return True
    
    def start_algorithm_execution(self, algorithm_name: str, max_iterations: int):
        """Start tracking algorithm execution"""
        
        st.session_state.current_progress = {
            'algorithm_name': algorithm_name,
            'progress_percentage': 0,
            'current_iteration': 0,
            'max_iterations': max_iterations,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'estimated_completion': None
        }
        
        st.session_state.active_session['current_running_algorithm'] = algorithm_name
        self._save_session()
    
    def update_algorithm_progress(self, algorithm_name: str, current_iteration: int, 
                                 max_iterations: int, current_fitness: float = None):
        """Update algorithm execution progress"""
        
        if st.session_state.current_progress['algorithm_name'] != algorithm_name:
            return
        
        progress_percentage = (current_iteration / max_iterations) * 100
        
        st.session_state.current_progress.update({
            'progress_percentage': progress_percentage,
            'current_iteration': current_iteration,
            'max_iterations': max_iterations,
            'current_fitness': current_fitness
        })
        
        # Auto-refresh UI if enabled
        if st.session_state.auto_refresh and current_iteration % 10 == 0:  # Refresh every 10 iterations
            st.rerun()
    
    def complete_algorithm_execution(self, algorithm_name: str):
        """Complete algorithm execution"""
        
        st.session_state.current_progress.update({
            'status': 'completed',
            'progress_percentage': 100,
            'completed_at': datetime.now().isoformat()
        })
        
        st.session_state.active_session['current_running_algorithm'] = None
        st.session_state.show_results = True
        
        self._save_session()
    
    def get_session_algorithms(self) -> List[str]:
        """Get list of algorithms in current session"""
        return list(st.session_state.active_session['algorithms'].keys())
    
    def get_algorithm_results(self, algorithm_name: str = None) -> Dict:
        """Get results for specific algorithm or all algorithms"""
        
        if algorithm_name:
            return st.session_state.algorithm_results.get(algorithm_name, {})
        
        return st.session_state.algorithm_results
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        
        session = st.session_state.active_session
        algorithms = session['algorithms']
        
        if not algorithms:
            return {
                'session_id': session['session_id'],
                'dataset': session['current_dataset'],
                'total_algorithms': 0,
                'status': 'empty'
            }
        
        # Calculate statistics
        fitness_values = []
        execution_times = []
        
        for alg_data in algorithms.values():
            results = alg_data['results']
            fitness_values.append(results.get('best_fitness', float('inf')))
            execution_times.append(results.get('execution_time', 0))
        
        best_algorithm = min(algorithms.items(), key=lambda x: x[1]['results'].get('best_fitness', float('inf')))
        
        return {
            'session_id': session['session_id'][:8] + "...",
            'dataset': session['current_dataset'],
            'total_algorithms': len(algorithms),
            'best_algorithm': best_algorithm[0],
            'best_fitness': best_algorithm[1]['results'].get('best_fitness'),
            'average_fitness': np.mean(fitness_values) if fitness_values else 0,
            'total_execution_time': sum(execution_times),
            'session_duration': self._get_session_duration(),
            'status': session['session_status'],
            'last_updated': session['last_updated']
        }
    
    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        
        try:
            created = datetime.fromisoformat(st.session_state.active_session['created_at'])
            now = datetime.now()
            duration = now - created
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if duration.days > 0:
                return f"{duration.days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    
    def export_session_data(self) -> Dict:
        """Export complete session data"""
        
        return {
            'session_metadata': st.session_state.active_session,
            'algorithm_results': st.session_state.algorithm_results,
            'session_summary': self.get_session_summary(),
            'exported_at': datetime.now().isoformat()
        }
    
    def _save_session(self):
        """Save session to persistent storage"""
        
        try:
            session_data = {
                'active_session': st.session_state.active_session,
                'algorithm_results': st.session_state.algorithm_results,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
                
        except Exception as e:
            st.error(f"Failed to save session: {e}")
    
    def load_session(self) -> bool:
        """Load session from persistent storage"""
        
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                st.session_state.active_session = session_data.get('active_session', {})
                st.session_state.algorithm_results = session_data.get('algorithm_results', {})
                
                return True
        except Exception as e:
            st.error(f"Failed to load session: {e}")
        
        return False
    
    def display_session_info(self):
        """Display current session information in sidebar or main area"""
        
        summary = self.get_session_summary()
        
        st.markdown("### 📊 **Current Session**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🆔 Session", summary['session_id'])
            st.metric("📊 Dataset", summary['dataset'] or "None")
        
        with col2:
            st.metric("🧬 Algorithms", summary['total_algorithms'])
            st.metric("⏱️ Duration", summary['session_duration'])
        
        with col3:
            if summary['total_algorithms'] > 0:
                st.metric("🏆 Best Algorithm", summary['best_algorithm'])
                st.metric("📈 Best Fitness", f"{summary['best_fitness']:.6f}")
            else:
                st.metric("🏆 Best Algorithm", "None")
                st.metric("📈 Best Fitness", "N/A")
        
        # Progress bar for currently running algorithm
        progress = st.session_state.current_progress
        if progress['status'] == 'running':
            st.markdown(f"**🔄 Running: {progress['algorithm_name']}**")
            st.progress(progress['progress_percentage'] / 100)
            st.caption(f"Iteration {progress['current_iteration']}/{progress['max_iterations']}")
    
    def show_session_controls(self):
        """Show session control buttons"""
        
        st.markdown("### ⚙️ **Session Controls**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🆕 New Session", help="Start a completely new session"):
                self.start_new_session()
                st.rerun()
        
        with col2:
            if st.button("💾 Save Session", help="Save current session"):
                self._save_session()
                st.success("Session saved!")
        
        with col3:
            if st.button("📋 Export Data", help="Export session data"):
                export_data = self.export_session_data()
                summary = self.get_session_summary()
                st.download_button(
                    label="📥 Download Session",
                    data=json.dumps(export_data, indent=2, default=str),
                    file_name=f"session_{summary['session_id']}.json",
                    mime="application/json"
                )
