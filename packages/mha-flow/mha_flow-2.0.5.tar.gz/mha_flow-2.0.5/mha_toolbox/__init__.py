"""
MHA Flow: Professional Meta-Heuristic Algorithm Library
Version 2.0.4 - AI-Powered Algorithm Recommendations & Modern UI

Installation modes:
    pip install mha-flow           # Library only
    pip install mha-flow[ui]       # With web interface
    pip install mha-flow[complete] # Everything

Usage:
    # Commands
    mha-flow                       # Launch local web interface
    mha-flow-web                   # Open online interface (https://mha-flow.streamlit.app/)
    mha-flow-cli                   # Command-line interface
    
    # Library Mode
    from mha_toolbox import optimize, MHAToolbox
    
    # Algorithm Recommender (AI-Powered)
    from mha_toolbox import AlgorithmRecommender
    
    # Parallel Optimization
    from mha_toolbox.parallel_optimizer import parallel_optimize, parallel_compare
    
    # Validation
    from mha_toolbox.validators import OptimizationValidator
"""

__version__ = "2.0.5"
__author__ = "MHA Flow Development Team"
__license__ = "MIT"

# Core library imports (always available)
from .toolbox import MHAToolbox, list_algorithms, run_optimizer
from .base import BaseOptimizer, OptimizationModel
from .advanced_hybrid import AdvancedHybridOptimizer
from .demo_system import MHADemoSystem, run_demo_system
from .robust_optimization import optimize_for_large_dataset
from .algorithm_recommender import AlgorithmRecommender

# Simple API for beginners (programmatic usage)
from .simple_api import (
    SimpleAPI,
    quick_optimize,
    recommend_algorithm,
    compare_algorithms,
    list_algorithms
)

# Beginner UI mode (requires Streamlit)
try:
    from .beginner_mode import BeginnerMode
    BEGINNER_UI_AVAILABLE = True
except ImportError:
    BEGINNER_UI_AVAILABLE = False
    BeginnerMode = None

# UI imports (optional - will fail gracefully if dependencies missing)
try:
    from .ui import launch_ui
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    def launch_ui():
        print("❌ UI dependencies not installed. Install with: pip install mha-toolbox[ui]")
        return None

def optimize(algorithm_name, X=None, y=None, objective_function=None, **kwargs):
    """
    Main optimization function - simplified interface with intelligent defaults.
    
    Usage patterns:
    1. Feature Selection: optimize('pso', X, y)
    2. Function Optimization: optimize('pso', objective_function=func, dimensions=10)
    3. With hyperparameter tuning: optimize('pso', X, y, hyperparameter_tuning=True)
    
    Parameters:
    -----------
    algorithm_name : str
        Name of the algorithm (e.g., 'pso', 'gwo', 'sca')
    X : array-like, optional
        Input features/data (required for feature selection)
    y : array-like, optional
        Target values (required for feature selection)
    objective_function : callable, optional
        Function to optimize (required for function optimization)
    **kwargs : optional parameters with intelligent defaults
        - population_size: default 30
        - max_iterations: default 100
        - hyperparameter_tuning: default True (auto-tunes algorithm parameters)
        - feature_selection: default True (when X,y provided)
        - timeout_seconds: default None (no timeout)
        - n_jobs: default 1 (parallel processing cores)
        
    Auto-included features:
    - Hyperparameter optimization using grid search or Bayesian optimization
    - Cross-validation for robust performance estimation
    - Early stopping to prevent overfitting
    - Automatic result visualization and saving
    - Performance metrics calculation
    - Statistical significance testing
    
    Returns:
    --------
    OptimizationModel with:
        - best_parameters: Optimized algorithm hyperparameters
        - best_fitness: Best achieved fitness score
        - selected_features: Selected features (if feature selection)
        - cv_scores: Cross-validation results
        - convergence_history: Training progress
        - performance_metrics: Detailed performance analysis
        - visualization_plots: Generated plots and charts
    """
    from mha_toolbox.validators import validate_optimization_inputs
    
    try:
        # Validate inputs before optimization
        validated_params = validate_optimization_inputs(
            objective_function=objective_function,
            X=X,
            y=y,
            bounds=kwargs.get('bounds'),
            dimensions=kwargs.get('dimensions'),
            population_size=kwargs.get('population_size', 30),
            max_iterations=kwargs.get('max_iterations', 100)
        )
        
        # Update kwargs with validated parameters (but don't duplicate)
        for key, value in validated_params.items():
            if key not in ['X', 'y', 'objective_function']:
                kwargs[key] = value
        
    except Exception as e:
        print(f"⚠️  Validation warning: {e}")
        # Continue with original parameters if validation fails non-critically
    
    # Set intelligent defaults
    kwargs.setdefault('population_size', 30)
    kwargs.setdefault('max_iterations', 100)
    kwargs.setdefault('hyperparameter_tuning', True)
    kwargs.setdefault('cross_validation', True)
    kwargs.setdefault('save_results', True)
    kwargs.setdefault('verbose', True)
    
    # Enhanced feature selection mode
    if X is not None and y is not None:
        kwargs.setdefault('feature_selection', True)
        kwargs.setdefault('performance_metrics', ['accuracy', 'f1_score', 'precision', 'recall'])
        
    return run_optimizer(algorithm_name, X=X, y=y, objective_function=objective_function, **kwargs)

__all__ = [
    'optimize', 'list_algorithms', 'MHAToolbox', 'AdvancedHybridOptimizer', 
    'run_demo_system', 'optimize_for_large_dataset'
]
