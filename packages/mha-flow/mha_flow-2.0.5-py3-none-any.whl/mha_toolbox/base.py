
import numpy as np
import time
import json
import os
from datetime import datetime
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class OptimizationModel:
    def save_training_history(self, filename):
        """Save the full training history (local_fitness and local_positions) to a file."""
        history = {
            'local_fitness': self.local_fitness_,
            'local_positions': self.local_positions_
        }
        with open(filename, 'w') as f:
            json.dump(self._deep_serialize(history), f, indent=4)

    def plot_curve(self, curve_name, title=None, save_path=None):
        """Plot any curve (global_fitness, local_fitness, etc.) from saved data."""
        import matplotlib.pyplot as plt
        data = getattr(self, curve_name, None)
        if data is None:
            print(f"Curve '{curve_name}' not found.")
            return
        plt.figure(figsize=(10, 6))
        if curve_name == 'local_fitness_':
            # Plot mean fitness per iteration
            means = [np.mean(f) for f in data]
            plt.plot(means, label='Mean Local Fitness', linewidth=2)
        else:
            plt.plot(data, linewidth=2)
        plt.title(title or f'{curve_name} Curve')
        plt.xlabel('Iteration')
        plt.ylabel('Fitness')
        plt.grid(True, linestyle='--', alpha=0.6)
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=300)
        # Only show interactively if no save_path was provided
        if save_path is None:
            plt.show()

    def save_model(self, filename):
        """Save the full OptimizationModel object for later loading/reuse."""
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_model(filename):
        """Load a previously saved OptimizationModel object."""
        import pickle
        with open(filename, 'rb') as f:
            return pickle.load(f)
    """
    A standardized object to store and manage optimization results.
    
    This class provides a consistent interface for accessing all information
    related to an optimization run, including the best solution, fitness,
    convergence history, and parameters used. It also includes methods for
    analysis and visualization.
    """
    
    def __init__(self, algorithm_name, best_solution, best_fitness, global_fitness, execution_time, parameters,
                 problem_type='unknown', X_data=None, y_data=None, local_fitness=None, local_positions=None):
        self.algorithm_name_ = algorithm_name
        self.best_solution_ = np.array(best_solution)
        self.best_fitness_ = best_fitness
        self.global_fitness_ = global_fitness
        self.execution_time_ = execution_time
        self.parameters_ = parameters
        self.problem_type_ = problem_type
        self.timestamp_ = datetime.now().isoformat()
        self.local_fitness_ = local_fitness
        self.local_positions_ = local_positions
        
        # Error tracking and validation
        self.error_log_ = []
        self.warnings_ = []
        self.validation_status_ = 'unknown'
        
        # For feature selection, store binary solution and selected features
        if self.problem_type_ == 'feature_selection':
            self.best_solution_binary_ = (self.best_solution_ > 0.5).astype(int)
            self.n_selected_features_ = sum(self.best_solution_binary_)
            self.selected_feature_indices_ = np.where(self.best_solution_binary_)[0]
        # Store a reference to the data if provided
        self._X_data_ = X_data
        self._y_data_ = y_data
    
    def add_error(self, error_msg, iteration=None, severity='error'):
        """
        Log an error that occurred during optimization.
        
        Parameters
        ----------
        error_msg : str
            Error message
        iteration : int, optional
            Iteration at which error occurred
        severity : str, default='error'
            Severity level: 'error', 'warning', 'info'
        """
        error_entry = {
            'message': error_msg,
            'iteration': iteration,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        if severity == 'warning':
            self.warnings_.append(error_entry)
        else:
            self.error_log_.append(error_entry)
    
    def is_successful(self):
        """
        Check if optimization completed successfully.
        
        Returns
        -------
        bool
            True if no critical errors and valid results exist
        """
        has_critical_errors = any(e.get('severity') == 'error' for e in self.error_log_)
        has_valid_results = (self.best_fitness_ is not None and 
                           not np.isnan(self.best_fitness_) and 
                           not np.isinf(self.best_fitness_))
        
        return not has_critical_errors and has_valid_results
    
    def get_convergence_quality(self):
        """
        Assess convergence quality based on improvement trend.
        
        Returns
        -------
        dict
            Quality metrics including improvement rate, stagnation detection
        """
        if len(self.global_fitness_) < 2:
            return {'quality': 'insufficient_data', 'improvement': 0.0}
        
        # Calculate improvement
        initial_fitness = self.global_fitness_[0]
        final_fitness = self.global_fitness_[-1]
        improvement = initial_fitness - final_fitness
        improvement_pct = (improvement / abs(initial_fitness)) * 100 if initial_fitness != 0 else 0
        
        # Detect stagnation (no improvement in last 20% of iterations)
        last_20_pct = int(len(self.global_fitness_) * 0.2)
        if last_20_pct > 0:
            recent_improvement = self.global_fitness_[-last_20_pct] - self.global_fitness_[-1]
            is_stagnant = abs(recent_improvement) < 1e-6
        else:
            is_stagnant = False
        
        # Assess quality
        if improvement_pct > 10:
            quality = 'excellent'
        elif improvement_pct > 1:
            quality = 'good'
        elif improvement_pct > 0.01:
            quality = 'fair'
        else:
            quality = 'poor'
        
        return {
            'quality': quality,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'is_stagnant': is_stagnant,
            'n_iterations': len(self.global_fitness_)
        }

    def summary(self):
        """
        Print a comprehensive summary of the optimization results.
        """
        print("\n" + "="*60)
        print(f"📈 Optimization Results Summary: {self.algorithm_name}")
        print("="*60)
        print(f"  - Timestamp: {self.timestamp}")
        print(f"  - Problem Type: {self.problem_type}")
        print(f"  - Execution Time: {self.execution_time:.4f} seconds")
        print(f"  - Best Fitness: {self.best_fitness:.6f}")
        
        if self.problem_type == 'feature_selection':
            print(f"  - Selected Features: {self.n_selected_features} / {len(self.best_solution)}")
            print(f"  - Selected Indices: {self.selected_feature_indices[:10]}...")
        else:
            print(f"  - Best Solution: {self.best_solution[:10]}...")
        
        print("\n" + "-"*60)
        print("⚙️  Parameters Used:")
        print("-"*60)
        for key, value in self.parameters.items():
            print(f"  - {key:<20}: {value}")
        print("="*60)

    def plot_convergence(self, title=None, save_path=None):
        """
        Plot the convergence curve using global_fitness_.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self.global_fitness_, linewidth=2)
        plt.title(title or f'{self.algorithm_name_} Convergence Curve')
        plt.xlabel('Iteration')
        plt.ylabel('Best Fitness')
        plt.grid(True, linestyle='--', alpha=0.6)
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=300)
        # only show interactively if no save_path was provided
        if save_path is None:
            plt.show()

    def save(self, filename, format='json'):
        """
        Save the optimization results to a file. User must specify filename.
        """
        data_to_save = {
            'algorithm_name': self.algorithm_name_,
            'best_fitness': float(self.best_fitness_),
            'best_solution': self.best_solution_.tolist(),
            'global_fitness': [float(x) for x in self.global_fitness_],
            'execution_time': float(self.execution_time_),
            'parameters': self._serialize_parameters(self.parameters_),
            'problem_type': self.problem_type_,
            'timestamp': self.timestamp_,
            'local_fitness': self.local_fitness_ if self.local_fitness_ is not None else None,
            'local_positions': self.local_positions_ if self.local_positions_ is not None else None
        }
        if self.problem_type_ == 'feature_selection':
            data_to_save['n_selected_features'] = int(self.n_selected_features_)
            data_to_save['selected_feature_indices'] = self.selected_feature_indices_.tolist()
        # New: auto-export options (plots, history, model) by default
        return self.export_all(filename, data_to_save, format=format, export_plots=True, save_history=True, save_model=False)

    def export_all(self, filename, data_to_save=None, format='json', export_plots=True, save_history=True, save_model=False):
        """Save results + optional exports (plots, history, pickled model).

        - filename: base filename (recommended .json)
        - export_plots: save convergence and local-mean plots
        - save_history: save local_fitness/local_positions as JSON
        - save_model: pickle the OptimizationModel
        Returns: path to primary saved file
        """
        try:
            base, ext = (filename.rsplit('.', 1) + [''])[:2]
            primary = filename if ext else f"{filename}.json"
            outdir = os.path.dirname(primary) or 'results'
            os.makedirs(outdir, exist_ok=True)

            # Write primary JSON (if requested)
            if data_to_save is None:
                data_to_save = {
                    'algorithm_name': self.algorithm_name_,
                    'best_fitness': float(self.best_fitness_),
                    'best_solution': self.best_solution_.tolist(),
                    'global_fitness': [float(x) for x in self.global_fitness_],
                    'execution_time': float(self.execution_time_),
                    'parameters': self._serialize_parameters(self.parameters_),
                    'problem_type': self.problem_type_,
                    'timestamp': self.timestamp_,
                    'local_fitness': self.local_fitness_ if self.local_fitness_ is not None else None,
                    'local_positions': self.local_positions_ if self.local_positions_ is not None else None
                }
                if self.problem_type_ == 'feature_selection':
                    data_to_save['n_selected_features'] = int(self.n_selected_features_)
                    data_to_save['selected_feature_indices'] = self.selected_feature_indices_.tolist()

            # Save primary JSON using deep serialization to handle numpy types
            with open(primary, 'w') as f:
                serial = self._deep_serialize(data_to_save)
                if format == 'json':
                    json.dump(serial, f, indent=4)
                else:
                    f.write(json.dumps(serial, indent=4))

            # Always save convergence CSV
            csv_filename = f"{base}_convergence.csv"
            self._save_convergence_csv(csv_filename)

            # Export plots
            if export_plots:
                conv_png = f"{base}_convergence.png"
                self.plot_convergence(save_path=conv_png)
                if self.local_fitness_ is not None:
                    local_png = f"{base}_local_mean.png"
                    # plot_curve expects attribute name
                    self.plot_curve('local_fitness_', title=f"{self.algorithm_name_} Mean Local Fitness", save_path=local_png)

            # Save training history
            if save_history and self.local_fitness_ is not None:
                history_json = f"{base}_history.json"
                with open(history_json, 'w') as hf:
                    json.dump(self._deep_serialize({'local_fitness': self.local_fitness_, 'local_positions': self.local_positions_}), hf, indent=4)

            # Optionally save pickled model
            if save_model:
                model_file = f"{base}_model.pkl"
                self.save_model(model_file)

            return primary
        except Exception as e:
            print(f"Error exporting results: {e}")
            return None

    def _save_convergence_csv(self, filename):
        """Save convergence curve as CSV file."""
        try:
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['iteration', 'best_fitness'])
                for i, fitness in enumerate(self.global_fitness_):
                    writer.writerow([i+1, float(fitness)])
            print(f"Convergence curve saved to {filename}")
        except Exception as e:
            print(f"Error saving convergence curve: {e}")

    def _serialize_parameters(self, params):
        """Convert numpy arrays in parameters to lists for JSON serialization."""
        serialized = {}
        for key, value in params.items():
            if isinstance(value, np.ndarray):
                serialized[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                serialized[key] = value.item()  # Convert numpy scalar to Python scalar
            else:
                serialized[key] = value
        return serialized

    def _deep_serialize(self, obj):
        """Recursively convert numpy arrays and numpy scalars into Python types for JSON dumping."""
        # numpy array
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # numpy scalar
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        # dict
        if isinstance(obj, dict):
            return {k: self._deep_serialize(v) for k, v in obj.items()}
        # list/tuple
        if isinstance(obj, (list, tuple)):
            return [self._deep_serialize(v) for v in obj]
        # builtin types
        return obj

    @classmethod
    def load(cls, filename):
        """
        Load optimization results from a file.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        model = cls(
            algorithm_name=data.get('algorithm_name'),
            best_solution=data.get('best_solution'),
            best_fitness=data.get('best_fitness'),
            global_fitness=data.get('global_fitness', data.get('convergence_curve', [])),
            execution_time=data.get('execution_time'),
            parameters=data.get('parameters'),
            problem_type=data.get('problem_type', 'unknown'),
            local_fitness=data.get('local_fitness'),
            local_positions=data.get('local_positions')
        )
        return model

class BaseOptimizer(ABC):
    """
    Abstract base class for all metaheuristic optimizers.
    
    This class provides the core structure and functionality for all algorithms,
    including parameter initialization, data handling, and result formatting.
    
    Supports flexible initialization:
    - PSO(15, 100) -> population_size=15, max_iterations=100
    - PSO(population_size=30, max_iterations=200)
    """
    
    def __init__(self, *args, population_size=30, max_iterations=None, 
                 lower_bound=None, upper_bound=None, dimensions=None, 
                 verbose=True, mode=True, **kwargs):
        
        # Handle flexible positional arguments: PSO(15, 100)
        if len(args) >= 1:
            population_size = args[0]
        if len(args) >= 2:
            max_iterations = args[1]
        if len(args) >= 3:
            dimensions = args[2]
            
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations if max_iterations is not None else 100
        self.lower_bound_ = lower_bound
        self.upper_bound_ = upper_bound
        self.dimensions_ = dimensions
        self.verbose_ = verbose
        self.mode_ = mode
        self.algorithm_name_ = self.__class__.__name__
        self.extra_params_ = kwargs

    def get_params(self):
        """Get all parameters of the optimizer."""
        params = {
            'population_size': self.population_size_,
            'max_iterations': self.max_iterations_,
            'lower_bound': self.lower_bound_,
            'upper_bound': self.upper_bound_,
            'dimensions': self.dimensions_,
            'verbose': self.verbose_
        }
        params.update(getattr(self, 'extra_params_', {}))
        return params

    def _initialize_parameters(self, X=None, y=None, objective_function=None):
        """
        Automatically initialize parameters if they are not provided.
        """
        # Determine problem type
        if y is not None and X is not None:
            self.problem_type_ = 'feature_selection'
        elif objective_function is not None:
            self.problem_type_ = 'function_optimization'
        else:
            raise ValueError("Either (X, y) for feature selection or objective_function must be provided.")
        if self.dimensions_ is None:
            if self.problem_type_ == 'feature_selection':
                self.dimensions_ = X.shape[1]
            elif self.problem_type_ == 'function_optimization':
                self.dimensions_ = 10
            if self.verbose_ and self.mode_:
                pass # print(f"Auto-detected dimensions: {self.dimensions_}")
        if self.lower_bound_ is None or self.upper_bound_ is None:
            if self.problem_type_ == 'feature_selection':
                defaults = {'lower_bound_': 0.0, 'upper_bound_': 1.0}
            else:
                defaults = {'lower_bound_': -100.0, 'upper_bound_': 100.0}
            self.lower_bound_ = self.lower_bound_ if self.lower_bound_ is not None else defaults['lower_bound_']
            self.upper_bound_ = self.upper_bound_ if self.upper_bound_ is not None else defaults['upper_bound_']
            if self.verbose_ and self.mode_:
                pass # print(f"No bounds specified. Using default bounds for {self.problem_type_}: [{self.lower_bound_}, {self.upper_bound_}]")
        self._format_bounds()
        def _initialize_parameters(self, X=None, y=None, objective_function=None):
            if y is not None and X is not None:
                self.problem_type_ = 'feature_selection'
            elif objective_function is not None:
                self.problem_type_ = 'function_optimization'
            else:
                raise ValueError("Either (X, y) for feature selection or objective_function must be provided.")
            if self.dimensions_ is None:
                if self.problem_type_ == 'feature_selection':
                    self.dimensions_ = X.shape[1]
                elif self.problem_type_ == 'function_optimization':
                    self.dimensions_ = 10
                if self.verbose_ and self.mode_:
                    pass # print(f"Auto-detected dimensions: {self.dimensions_}")
            if self.lower_bound_ is None or self.upper_bound_ is None:
                if self.problem_type_ == 'feature_selection':
                    defaults = {'lower_bound_': 0.0, 'upper_bound_': 1.0}
                else:
                    defaults = {'lower_bound_': -100.0, 'upper_bound_': 100.0}
                self.lower_bound_ = self.lower_bound_ if self.lower_bound_ is not None else defaults['lower_bound_']
                self.upper_bound_ = self.upper_bound_ if self.upper_bound_ is not None else defaults['upper_bound_']
                if self.verbose_ and self.mode_:
                    pass # print(f"No bounds specified. Using default bounds for {self.problem_type_}: [{self.lower_bound_}, {self.upper_bound_}]")
            self._format_bounds()

    def _format_bounds(self):
        """Ensure bounds are numpy arrays of correct dimension (trailing underscore attributes only)."""
        if not isinstance(self.lower_bound_, np.ndarray) or np.isscalar(self.lower_bound_):
            self.lower_bound_ = np.full(self.dimensions_, self.lower_bound_)
        if not isinstance(self.upper_bound_, np.ndarray) or np.isscalar(self.upper_bound_):
            self.upper_bound_ = np.full(self.dimensions_, self.upper_bound_)

    def _create_objective_function(self, X, y):
        """
        Create a default objective function for feature selection.
        This function calculates classification error.
        """
        from sklearn.model_selection import train_test_split
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.metrics import accuracy_score

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        def objective(solution):
            # Convert solution to binary
            binary_solution = (np.array(solution) > 0.5).astype(int)
            
            # If no features are selected, return worst fitness
            if sum(binary_solution) == 0:
                return 1.0
            
            # Select features
            selected_features = X_train[:, binary_solution == 1]
            selected_features_test = X_test[:, binary_solution == 1]
            
            # Train a simple classifier
            model = KNeighborsClassifier(n_neighbors=3)
            model.fit(selected_features, y_train)
            
            # Calculate error rate
            y_pred = model.predict(selected_features_test)
            error_rate = 1.0 - accuracy_score(y_test, y_pred)
            
            return error_rate
        
        return objective

    def optimize(self, problem=None, X=None, y=None, objective_function=None):
        """
        Run the optimization process.
        
        This method can accept either a problem object or direct parameters.
        
        Parameters
        ----------
        problem : dict, optional
            Problem definition dictionary from create_problem()
        X : array-like, optional
            Feature matrix (alternative to problem)
        y : array-like, optional
            Target values (alternative to problem)
        objective_function : callable, optional
            Objective function (alternative to problem)
        """
        
        # Handle problem object
        if problem is not None:
            objective_function = problem['objective_function']
            X = problem.get('X')
            y = problem.get('y')
            if 'dimensions' in problem:
                self.dimensions = problem['dimensions']
            if 'bounds' in problem:
                bounds = problem['bounds']
                self.lower_bound = [b[0] for b in bounds]
                self.upper_bound = [b[1] for b in bounds]
        
        # Enforce that we have what we need
        if objective_function is None:
            raise ValueError("Objective function is required")
        
        start_time = time.time()
        
        self._initialize_parameters(X, y, objective_function)
        
        # Run the algorithm-specific optimization
        best_solution, best_fitness, global_fitness, local_fitness, local_positions = self._optimize(
            objective_function=objective_function, X=X, y=y
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Create and return the standardized model object
        model = self._create_model(
            best_solution, best_fitness, global_fitness, execution_time, X, y, local_fitness, local_positions
        )

        if self.verbose_:
            print(f"\nOptimization finished in {execution_time:.4f} seconds.")
            print(f"Best fitness: {best_fitness:.6f}")

        return model
        def optimize(self, problem=None, X=None, y=None, objective_function=None):
            if problem is not None:
                objective_function = problem['objective_function']
                X = problem.get('X')
                y = problem.get('y')
                if 'dimensions' in problem:
                    self.dimensions_ = problem['dimensions']
                if 'bounds' in problem:
                    bounds = problem['bounds']
                    self.lower_bound_ = [b[0] for b in bounds]
                    self.upper_bound_ = [b[1] for b in bounds]
            if objective_function is None:
                raise ValueError("Objective function is required")
            start_time = time.time()
            self._initialize_parameters(X, y, objective_function)
            best_solution, best_fitness, global_fitness, local_fitness, local_positions = self._optimize(
                objective_function=objective_function, X=X, y=y
            )
            end_time = time.time()
            execution_time = end_time - start_time
            model = self._create_model(
                best_solution, best_fitness, global_fitness, execution_time, X, y, local_fitness, local_positions
            )
            if self.verbose_ and self.mode_:
                pass # print(f"\nOptimization finished in {execution_time:.4f} seconds.")
                pass # print(f"Best fitness: {best_fitness:.6f}")
            return model

    def _create_model(self, best_solution, best_fitness, global_fitness, execution_time, X=None, y=None, local_fitness=None, local_positions=None):
        """Create and return the OptimizationModel object."""
        return OptimizationModel(
            algorithm_name=self.algorithm_name_,
            best_solution=best_solution,
            best_fitness=best_fitness,
            global_fitness=global_fitness,
            execution_time=execution_time,
            parameters=self.get_params(),
            problem_type=getattr(self, 'problem_type_', 'unknown'),
            X_data=X,
            y_data=y,
            local_fitness=local_fitness,
            local_positions=local_positions
        )
        def _create_model(self, best_solution, best_fitness, global_fitness, execution_time, X=None, y=None, local_fitness=None, local_positions=None):
            return OptimizationModel(
                algorithm_name=self.algorithm_name_,
                best_solution=best_solution,
                best_fitness=best_fitness,
                global_fitness=global_fitness,
                execution_time=execution_time,
                parameters=self.get_params(),
                problem_type=getattr(self, 'problem_type_', 'unknown'),
                X_data=X,
                y_data=y,
                local_fitness=local_fitness,
                local_positions=local_positions
            )

    @abstractmethod
    def _optimize(self, objective_function, **kwargs):
        """
        Core optimization logic for the specific algorithm.
        
        This method must be implemented by all subclasses. It should contain
        the main loop of the algorithm and return the best solution, best
        fitness, and convergence history.
        
        Returns
        -------
        tuple
            (best_solution, best_fitness, convergence_curve)
        """
        pass
        @abstractmethod
        def _optimize(self, objective_function, **kwargs):
            """
            Core optimization logic for the specific algorithm.
            This method must be implemented by all subclasses. It should contain
            the main loop of the algorithm and return:
            Returns
            -------
            tuple
                (best_solution, best_fitness, global_fitness, local_fitness, local_positions)
            """
            pass

# Alias for backward compatibility
OptimizationAlgorithm = BaseOptimizer
