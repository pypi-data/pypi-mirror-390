import os
import json
from pathlib import Path
from datetime import datetime
import shutil # <-- ADD THIS IMPORT

class ResultsManager:
    """Manages experiment results and provides summary functions"""
    
    def __init__(self):
        self.base_dir = Path("results")
        self.persistent_storage = self.base_dir / "persistent_storage" / "sessions"
        self.detailed_storage = self.base_dir / "detailed_storage"
        
        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.persistent_storage.mkdir(parents=True, exist_ok=True)
        self.detailed_storage.mkdir(parents=True, exist_ok=True)
    
    def get_latest_run_summary(self):
        """
        Get summary of the most recent experiment run.
        
        This function scans the results directories to find the most recently
        modified session and returns a summary suitable for the Dashboard Home.
        
        Returns:
            dict: Summary containing:
                - dataset_name: Name of the dataset
                - best_performer_name: Algorithm with best fitness
                - best_performer_fitness: Best fitness value achieved
                - fastest_algorithm_name: Algorithm with fastest execution
                - fastest_algorithm_time: Execution time of fastest algorithm
                - total_algorithms: Number of algorithms in the session
                - session_id: The session identifier
                - last_run_date: Timestamp of the last run
                
            None if no results found
        """
        try:
            # Find the most recently modified session directory
            latest_session_dir = None
            latest_mtime = 0
            dataset_name = None
            session_id = None
            
            # Check detailed storage
            if self.detailed_storage.exists():
                for dataset_dir in self.detailed_storage.iterdir():
                    if not dataset_dir.is_dir():
                        continue
                    
                    for session_dir in dataset_dir.iterdir():
                        if not session_dir.is_dir():
                            continue
                        
                        session_mtime = session_dir.stat().st_mtime
                        if session_mtime > latest_mtime:
                            latest_mtime = session_mtime
                            latest_session_dir = session_dir
                            dataset_name = dataset_dir.name
                            session_id = session_dir.name
            
            if not latest_session_dir or not latest_session_dir.exists():
                return None
            
            # Scan the session directory for algorithm results
            algorithms_data = []
            
            for item in latest_session_dir.iterdir():
                if item.is_file() and item.name.endswith('_metadata.json'):
                    try:
                        with open(item, 'r') as f:
                            metadata = json.load(f)
                            
                            algorithms_data.append({
                                'name': metadata.get('algorithm_name', 'unknown'),
                                'best_fitness': metadata.get('best_fitness', float('inf')),
                                'execution_time': metadata.get('execution_time', 0),
                                'total_iterations': metadata.get('total_iterations', 0)
                            })
                    except Exception:
                        continue
            
            if not algorithms_data:
                return None
            
            # Find best performer (lowest fitness = best)
            best_performer = min(algorithms_data, key=lambda x: x['best_fitness'])
            
            # Find fastest algorithm
            fastest_algorithm = min(algorithms_data, key=lambda x: x['execution_time'])
            
            # Create summary
            summary = {
                'dataset_name': dataset_name,
                'best_performer_name': best_performer['name'],
                'best_performer_fitness': best_performer['best_fitness'],
                'fastest_algorithm_name': fastest_algorithm['name'],
                'fastest_algorithm_time': fastest_algorithm['execution_time'],
                'total_algorithms': len(algorithms_data),
                'session_id': session_id,
                'last_run_date': datetime.fromtimestamp(latest_mtime).isoformat(),
                'last_run_date_human': datetime.fromtimestamp(latest_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return summary
            
        except Exception as e:
            print(f"Error generating latest run summary: {e}")
            return None
    
    def save_experiment_results(self, results, dataset_name, session_id=None):
        """
        Save experiment results to persistent storage.
        
        Args:
            results: Results dictionary
            dataset_name: Name of the dataset
            session_id: Optional session ID (generated if not provided)
        """
        try:
            # Generate session ID if not provided
            if session_id is None:
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create session directory
            session_dir = self.persistent_storage / dataset_name / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Save results
            results_file = session_dir / "results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            return str(results_file)
            
        except Exception as e:
            print(f"Error saving experiment results: {e}")
            return None
    
    def load_experiment_results(self, dataset_name, session_id):
        """
        Load experiment results from persistent storage.
        
        Args:
            dataset_name: Name of the dataset
            session_id: Session identifier
            
        Returns:
            dict: Results dictionary or None if not found
        """
        try:
            results_file = self.persistent_storage / dataset_name / session_id / "results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error loading experiment results: {e}")
            return None
    
    def list_all_experiments(self):
        """
        List all experiment sessions.
        
        Returns:
            list: List of experiment session dictionaries
        """
        experiments = []
        
        try:
            if self.persistent_storage.exists():
                for dataset_dir in self.persistent_storage.iterdir():
                    if not dataset_dir.is_dir():
                        continue
                    
                    dataset_name = dataset_dir.name
                    
                    for session_dir in dataset_dir.iterdir():
                        if not session_dir.is_dir():
                            continue
                        
                        session_id = session_dir.name
                        results_file = session_dir / "results.json"
                        
                        if results_file.exists():
                            session_stat = session_dir.stat()
                            
                            experiments.append({
                                'dataset_name': dataset_name,
                                'session_id': session_id,
                                'created_at': datetime.fromtimestamp(session_stat.st_ctime).isoformat(),
                                'modified_at': datetime.fromtimestamp(session_stat.st_mtime).isoformat(),
                                'results_file': str(results_file)
                            })
            
            # Sort by modified date (most recent first)
            experiments.sort(key=lambda x: x['modified_at'], reverse=True)
            
            return experiments
            
        except Exception as e:
            print(f"Error listing experiments: {e}")
            return []

    # --- NEW DELETION METHODS ---

    def delete_experiment(self, dataset_name, session_id):
        """
        Deletes all files and directories associated with a specific experiment.
        """
        # The target directory is inside self.persistent_storage
        exp_dir = self.persistent_storage / dataset_name / session_id

        if exp_dir.exists() and exp_dir.is_dir():
            # shutil.rmtree removes the directory and all its contents
            shutil.rmtree(exp_dir)
            print(f"Successfully deleted experiment directory: {exp_dir}")
        else:
            print(f"Warning: Could not find experiment directory to delete: {exp_dir}")

    def delete_all_experiments(self):
        """
        Deletes all saved experiments by removing the contents of the 
        persistent_storage/sessions directory.
        """
        if self.persistent_storage.exists() and self.persistent_storage.is_dir():
            # Remove the entire sessions directory
            shutil.rmtree(self.persistent_storage)
            # Recreate the empty directory so the app doesn't crash
            self.persistent_storage.mkdir(parents=True, exist_ok=True)
            print(f"Successfully deleted all experiments and recreated directory: {self.persistent_storage}")
        else:
            print(f"Warning: Persistent storage directory not found, nothing to delete: {self.persistent_storage}")