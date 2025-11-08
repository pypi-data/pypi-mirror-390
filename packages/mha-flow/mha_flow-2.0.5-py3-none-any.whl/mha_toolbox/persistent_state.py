"""
Persistent State Manager for MHA Toolbox
=========================================

Handles state persistence across browser sessions, sleep mode, and refreshes.
Ensures results and progress are never lost.
"""

import os
import json
import pickle
import time
from datetime import datetime
from pathlib import Path
import streamlit as st


class PersistentStateManager:
    """Manages persistent state across browser sessions and system sleep"""
    
    def __init__(self, base_dir="persistent_state"):
        self.base_dir = Path(base_dir)
        self.setup_directories()
        self.state_file = self.base_dir / "current_state.json"
        self.results_cache = self.base_dir / "results_cache.pkl"
        
    def setup_directories(self):
        """Create persistent state directories"""
        directories = [
            "persistent_state",
            "persistent_state/sessions",
            "persistent_state/downloads",
            "persistent_state/temp_results",
            "persistent_state/agent_tracking"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_current_state(self, state_data):
        """Save current application state"""
        try:
            # Add timestamp and session info
            state_data.update({
                'last_saved': datetime.now().isoformat(),
                'session_id': self.get_session_id(),
                'state_version': '2.0'
            })
            
            # Save to JSON file
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            # Also save to session state with backup
            if 'persistent_backup' not in st.session_state:
                st.session_state.persistent_backup = {}
            
            st.session_state.persistent_backup.update(state_data)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save state: {e}")
            return False
    
    def load_current_state(self):
        """Load persistent state on startup"""
        try:
            # First try loading from file
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Check if state is recent (within 24 hours)
                if 'last_saved' in state_data:
                    last_saved = datetime.fromisoformat(state_data['last_saved'])
                    hours_since = (datetime.now() - last_saved).total_seconds() / 3600
                    
                    if hours_since < 24:  # State is fresh
                        return state_data
            
            # Try loading from session state backup
            if hasattr(st.session_state, 'persistent_backup'):
                return st.session_state.persistent_backup
            
            return None
            
        except Exception as e:
            st.warning(f"Could not load previous state: {e}")
            return None
    
    def save_results_cache(self, results_data):
        """Save results to pickle cache for faster loading"""
        try:
            cache_data = {
                'results': results_data,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.get_session_id()
            }
            
            with open(self.results_cache, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to cache results: {e}")
            return False
    
    def load_results_cache(self):
        """Load cached results"""
        try:
            if self.results_cache.exists():
                with open(self.results_cache, 'rb') as f:
                    cache_data = pickle.load(f)
                
                # Check if cache is recent
                timestamp = datetime.fromisoformat(cache_data['timestamp'])
                hours_since = (datetime.now() - timestamp).total_seconds() / 3600
                
                if hours_since < 24:
                    return cache_data['results']
            
            return None
            
        except Exception as e:
            st.warning(f"Could not load cached results: {e}")
            return None
    
    def get_session_id(self):
        """Get or create session ID"""
        if 'persistent_session_id' not in st.session_state:
            st.session_state.persistent_session_id = f"session_{int(time.time())}_{os.getpid()}"
        
        return st.session_state.persistent_session_id
    
    def create_download_file(self, data, filename, file_type="json"):
        """Create persistent download file that won't vanish"""
        try:
            download_dir = self.base_dir / "downloads"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if file_type == "json":
                file_path = download_dir / f"{filename}_{timestamp}.json"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif file_type == "csv":
                file_path = download_dir / f"{filename}_{timestamp}.csv"
                data.to_csv(file_path, index=False)
            
            # Store file reference in session
            if 'download_files' not in st.session_state:
                st.session_state.download_files = []
            
            st.session_state.download_files.append({
                'path': str(file_path),
                'filename': file_path.name,
                'created': timestamp,
                'type': file_type
            })
            
            return file_path
            
        except Exception as e:
            st.error(f"Failed to create download file: {e}")
            return None
    
    def get_download_files(self):
        """Get list of available download files"""
        download_dir = self.base_dir / "downloads"
        files = []
        
        if download_dir.exists():
            for file_path in download_dir.glob("*"):
                if file_path.is_file():
                    files.append({
                        'path': str(file_path),
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def cleanup_old_files(self, days=7):
        """Clean up files older than specified days"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            for directory in [self.base_dir / "downloads", self.base_dir / "temp_results"]:
                if directory.exists():
                    for file_path in directory.glob("*"):
                        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
            
        except Exception as e:
            st.warning(f"Cleanup warning: {e}")


class EnhancedAgentTracker:
    """Enhanced agent tracking for detailed analysis"""
    
    def __init__(self, base_dir="persistent_state/agent_tracking"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_tracking(self, algorithm, population_size, dimensions, run_id):
        """Initialize agent tracking for a run"""
        self.run_id = run_id
        self.algorithm = algorithm
        self.population_size = population_size
        self.dimensions = dimensions
        
        # Initialize tracking structures
        self.agent_history = {
            'positions': [],  # [iteration][agent][dimension]
            'fitness': [],    # [iteration][agent]
            'local_best': [], # [iteration][agent]
            'velocities': [], # [iteration][agent][dimension] (for applicable algorithms)
            'exploration_exploitation': []  # [iteration] - exploration/exploitation ratio
        }
        
        self.global_tracking = {
            'global_best_fitness': [],
            'global_best_position': [],
            'convergence_rate': [],
            'diversity_measure': [],
            'search_bounds': {'lower': [], 'upper': []},
            'iteration_times': []
        }
        
        return True
    
    def track_iteration(self, iteration, agents_data, global_best, bounds=None):
        """Track detailed data for each iteration"""
        try:
            # Extract agent positions and fitness
            positions = []
            fitness_values = []
            local_bests = []
            
            for agent in agents_data:
                positions.append(agent.get('position', []))
                fitness_values.append(agent.get('fitness', float('inf')))
                local_bests.append(agent.get('local_best', float('inf')))
            
            # Store iteration data
            self.agent_history['positions'].append(positions)
            self.agent_history['fitness'].append(fitness_values)
            self.agent_history['local_best'].append(local_bests)
            
            # Track global metrics
            self.global_tracking['global_best_fitness'].append(global_best.get('fitness', float('inf')))
            self.global_tracking['global_best_position'].append(global_best.get('position', []))
            
            # Calculate diversity measure
            if positions:
                diversity = self.calculate_diversity(positions)
                self.global_tracking['diversity_measure'].append(diversity)
            
            # Track exploration vs exploitation
            if iteration > 0:
                exp_exp_ratio = self.calculate_exploration_exploitation_ratio(positions, iteration)
                self.agent_history['exploration_exploitation'].append(exp_exp_ratio)
            
            # Track bounds if provided
            if bounds:
                self.global_tracking['search_bounds']['lower'].append(bounds.get('lower', []))
                self.global_tracking['search_bounds']['upper'].append(bounds.get('upper', []))
            
            return True
            
        except Exception as e:
            st.warning(f"Agent tracking error at iteration {iteration}: {e}")
            return False
    
    def calculate_diversity(self, positions):
        """Calculate population diversity measure"""
        try:
            import numpy as np
            
            if not positions or len(positions) < 2:
                return 0.0
            
            positions_array = np.array(positions)
            mean_position = np.mean(positions_array, axis=0)
            
            # Calculate average Euclidean distance from centroid
            distances = []
            for pos in positions_array:
                dist = np.linalg.norm(pos - mean_position)
                distances.append(dist)
            
            return float(np.mean(distances))
            
        except Exception:
            return 0.0
    
    def calculate_exploration_exploitation_ratio(self, current_positions, iteration):
        """Calculate exploration vs exploitation ratio"""
        try:
            import numpy as np
            
            if iteration == 0 or not hasattr(self, 'agent_history'):
                return 0.5
            
            prev_positions = self.agent_history['positions'][-1]
            current_positions = np.array(current_positions)
            prev_positions = np.array(prev_positions)
            
            # Calculate movement distances
            movements = []
            for i in range(len(current_positions)):
                if i < len(prev_positions):
                    movement = np.linalg.norm(current_positions[i] - prev_positions[i])
                    movements.append(movement)
            
            if not movements:
                return 0.5
            
            avg_movement = np.mean(movements)
            
            # High movement = exploration, low movement = exploitation
            # Normalize to 0-1 range (0 = pure exploitation, 1 = pure exploration)
            max_expected_movement = 1.0  # This can be tuned based on problem
            ratio = min(avg_movement / max_expected_movement, 1.0)
            
            return float(ratio)
            
        except Exception:
            return 0.5
    
    def save_tracking_data(self):
        """Save comprehensive tracking data"""
        try:
            tracking_file = self.base_dir / f"tracking_{self.algorithm}_{self.run_id}.json"
            
            complete_data = {
                'metadata': {
                    'algorithm': self.algorithm,
                    'run_id': self.run_id,
                    'population_size': self.population_size,
                    'dimensions': self.dimensions,
                    'total_iterations': len(self.agent_history['positions']),
                    'timestamp': datetime.now().isoformat()
                },
                'agent_history': self.agent_history,
                'global_tracking': self.global_tracking,
                'analysis': self.generate_analysis()
            }
            
            with open(tracking_file, 'w') as f:
                json.dump(complete_data, f, indent=2, default=str)
            
            return str(tracking_file)
            
        except Exception as e:
            st.error(f"Failed to save tracking data: {e}")
            return None
    
    def generate_analysis(self):
        """Generate analysis summary"""
        try:
            import numpy as np
            
            analysis = {
                'convergence_analysis': {},
                'diversity_analysis': {},
                'exploration_exploitation_analysis': {},
                'agent_performance': {}
            }
            
            # Convergence analysis
            if self.global_tracking['global_best_fitness']:
                fitness_history = self.global_tracking['global_best_fitness']
                analysis['convergence_analysis'] = {
                    'final_fitness': fitness_history[-1],
                    'best_fitness': min(fitness_history),
                    'convergence_rate': self.calculate_convergence_rate(fitness_history),
                    'convergence_achieved': self.check_convergence(fitness_history)
                }
            
            # Diversity analysis
            if self.global_tracking['diversity_measure']:
                diversity = self.global_tracking['diversity_measure']
                analysis['diversity_analysis'] = {
                    'initial_diversity': diversity[0] if diversity else 0,
                    'final_diversity': diversity[-1] if diversity else 0,
                    'avg_diversity': float(np.mean(diversity)) if diversity else 0,
                    'diversity_maintained': diversity[-1] > diversity[0] * 0.1 if diversity else False
                }
            
            # Exploration/Exploitation analysis
            if self.agent_history['exploration_exploitation']:
                exp_exp = self.agent_history['exploration_exploitation']
                analysis['exploration_exploitation_analysis'] = {
                    'avg_exploration_ratio': float(np.mean(exp_exp)),
                    'exploration_phases': sum(1 for x in exp_exp if x > 0.6),
                    'exploitation_phases': sum(1 for x in exp_exp if x < 0.4),
                    'balanced_search': sum(1 for x in exp_exp if 0.4 <= x <= 0.6)
                }
            
            return analysis
            
        except Exception as e:
            st.warning(f"Analysis generation warning: {e}")
            return {}
    
    def calculate_convergence_rate(self, fitness_history):
        """Calculate convergence rate"""
        try:
            if len(fitness_history) < 10:
                return 0.0
            
            # Calculate rate of improvement over the last 25% of iterations
            quarter_point = len(fitness_history) * 3 // 4
            recent_fitness = fitness_history[quarter_point:]
            
            if len(recent_fitness) < 2:
                return 0.0
            
            # Calculate relative improvement rate
            initial_fitness = recent_fitness[0]
            final_fitness = recent_fitness[-1]
            
            if initial_fitness == 0:
                return 0.0
            
            improvement_rate = abs(final_fitness - initial_fitness) / abs(initial_fitness)
            return float(improvement_rate)
            
        except Exception:
            return 0.0
    
    def check_convergence(self, fitness_history, tolerance=1e-6, window=10):
        """Check if algorithm has converged"""
        try:
            if len(fitness_history) < window:
                return False
            
            recent_values = fitness_history[-window:]
            variance = np.var(recent_values)
            
            return variance < tolerance
            
        except Exception:
            return False