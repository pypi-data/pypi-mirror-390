"""
Problem creation utilities for the MHA Toolbox.

This module provides functions to create optimization problems in a standardized
format that can be used by all algorithms in the toolbox.
"""

import numpy as np
from typing import Callable, Union, List, Tuple, Optional

def create_problem(objective_function: Callable = None,
                  dimensions: int = None, 
                  bounds: Union[Tuple, List] = (-100, 100),
                  minimize: bool = True,
                  constraints: Optional[List[Callable]] = None,
                  X: np.ndarray = None,
                  y: np.ndarray = None,
                  problem_type: str = 'auto'):
    """
    Create a standardized optimization problem definition.
    
    This function creates a problem dictionary that can be used by any
    algorithm in the toolbox. It automatically detects problem type and
    sets appropriate defaults.
    
    Parameters
    ----------
    objective_function : callable, optional
        Function to optimize f(x) -> float
    dimensions : int, optional
        Problem dimensions (auto-detected if not provided)
    bounds : tuple or list, default=(-100, 100)
        Search space bounds. Can be:
        - Single tuple: (lower, upper) applied to all dimensions
        - List of tuples: [(lower1, upper1), (lower2, upper2), ...]
    minimize : bool, default=True
        Whether to minimize (True) or maximize (False)
    constraints : list, optional
        List of constraint functions g(x) <= 0
    X : numpy.ndarray, optional
        Feature matrix for feature selection problems
    y : numpy.ndarray, optional
        Target values for feature selection problems
    problem_type : str, default='auto'
        Problem type: 'function', 'feature_selection', or 'auto'
        
    Returns
    -------
    dict
        Standardized problem definition
        
    Examples
    --------
    >>> # Simple function optimization
    >>> problem = create_problem(lambda x: sum(x**2), dimensions=10)
    
    >>> # Feature selection problem
    >>> problem = create_problem(X=data, y=targets)
    
    >>> # Custom bounds for each dimension
    >>> bounds = [(-5, 5), (-10, 10), (0, 1)]
    >>> problem = create_problem(objective_function=func, dimensions=3, bounds=bounds)
    """
    
    # Auto-detect problem type
    if problem_type == 'auto':
        if X is not None and y is not None:
            problem_type = 'feature_selection'
        elif objective_function is not None:
            problem_type = 'function'
        else:
            raise ValueError("Must provide either (X, y) for feature selection or objective_function for optimization")
    
    # Handle feature selection problems
    if problem_type == 'feature_selection':
        if X is None or y is None:
            raise ValueError("Feature selection requires both X and y data")
        
        # Auto-detect dimensions from data
        if dimensions is None:
            dimensions = X.shape[1]
        
        # Feature selection uses binary bounds [0, 1]
        bounds = [(0, 1)] * dimensions
        
        # Create feature selection objective function
        def feature_selection_objective(solution):
            return _feature_selection_fitness(solution, X, y)
        
        objective_function = feature_selection_objective
    
    # Handle function optimization problems  
    elif problem_type == 'function':
        if objective_function is None:
            raise ValueError("Function optimization requires an objective_function")
        
        if dimensions is None:
            raise ValueError("Function optimization requires dimensions parameter")
    
    # Process bounds
    if isinstance(bounds, (tuple, list)) and len(bounds) == 2 and isinstance(bounds[0], (int, float)):
        # Single bounds tuple - apply to all dimensions
        bounds = [bounds] * dimensions
    elif len(bounds) != dimensions:
        raise ValueError(f"Bounds length ({len(bounds)}) must match dimensions ({dimensions})")
    
    # Create problem dictionary
    problem = {
        'objective_function': objective_function,
        'dimensions': dimensions,
        'bounds': bounds,
        'minimize': minimize,
        'constraints': constraints or [],
        'problem_type': problem_type,
        'X': X,
        'y': y
    }
    
    return problem

def create_benchmark_problem(function_name: str, dimensions: int = 10):
    """
    Create a benchmark optimization problem.
    
    Parameters
    ----------
    function_name : str
        Name of the benchmark function
    dimensions : int, default=10
        Problem dimensions
        
    Returns
    -------
    dict
        Benchmark problem definition
        
    Available Functions
    -------------------
    - 'sphere': f(x) = sum(x_i^2)
    - 'rastrigin': f(x) = A*n + sum(x_i^2 - A*cos(2*pi*x_i))
    - 'rosenbrock': Rosenbrock function
    - 'ackley': Ackley function
    - 'griewank': Griewank function
    - 'schwefel': Schwefel function
    """
    
    benchmark_functions = {
        'sphere': {
            'function': lambda x: np.sum(x**2),
            'bounds': (-100, 100),
            'global_min': 0.0
        },
        'rastrigin': {
            'function': lambda x: 10*len(x) + np.sum(x**2 - 10*np.cos(2*np.pi*x)),
            'bounds': (-5.12, 5.12), 
            'global_min': 0.0
        },
        'rosenbrock': {
            'function': lambda x: np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2),
            'bounds': (-30, 30),
            'global_min': 0.0
        },
        'ackley': {
            'function': lambda x: -20*np.exp(-0.2*np.sqrt(np.mean(x**2))) - 
                                 np.exp(np.mean(np.cos(2*np.pi*x))) + 20 + np.e,
            'bounds': (-32.768, 32.768),
            'global_min': 0.0
        },
        'griewank': {
            'function': lambda x: 1 + np.sum(x**2)/4000 - np.prod(np.cos(x/np.sqrt(np.arange(1, len(x)+1)))),
            'bounds': (-600, 600),
            'global_min': 0.0
        },
        'schwefel': {
            'function': lambda x: 418.9829*len(x) - np.sum(x * np.sin(np.sqrt(np.abs(x)))),
            'bounds': (-500, 500),
            'global_min': 0.0
        }
    }
    
    if function_name not in benchmark_functions:
        available = ', '.join(benchmark_functions.keys())
        raise ValueError(f"Function '{function_name}' not available. Choose from: {available}")
    
    func_info = benchmark_functions[function_name]
    
    return create_problem(
        objective_function=func_info['function'],
        dimensions=dimensions,
        bounds=func_info['bounds'],
        minimize=True
    )

def _feature_selection_fitness(solution, X, y):
    """
    Fitness function for feature selection problems.
    
    This function evaluates a binary solution representing selected features
    using classification accuracy and the number of selected features.
    """
    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    
    # Convert continuous solution to binary
    binary_solution = (solution > 0.5).astype(int)
    
    # Check if any features are selected
    if np.sum(binary_solution) == 0:
        return 1.0  # Worst fitness
    
    # Select features
    selected_features = np.where(binary_solution)[0]
    X_selected = X[:, selected_features]
    
    try:
        # Use cross-validation to evaluate performance
        classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        scores = cross_val_score(classifier, X_selected, y, cv=3, scoring='accuracy')
        accuracy = np.mean(scores)
        
        # Fitness combines accuracy and feature reduction
        # Minimize: (1 - accuracy) + weight * (n_selected / n_total)
        feature_ratio = len(selected_features) / len(solution)
        fitness = (1 - accuracy) + 0.1 * feature_ratio
        
        return fitness
        
    except Exception:
        # Return worst fitness if evaluation fails
        return 1.0

def validate_problem(problem):
    """
    Validate a problem definition.
    
    Parameters
    ----------
    problem : dict
        Problem definition to validate
        
    Returns
    -------
    bool
        True if valid, raises ValueError if invalid
    """
    required_keys = ['objective_function', 'dimensions', 'bounds', 'minimize']
    
    for key in required_keys:
        if key not in problem:
            raise ValueError(f"Problem missing required key: {key}")
    
    # Validate dimensions
    if not isinstance(problem['dimensions'], int) or problem['dimensions'] <= 0:
        raise ValueError("Dimensions must be a positive integer")
    
    # Validate bounds
    bounds = problem['bounds']
    if len(bounds) != problem['dimensions']:
        raise ValueError("Bounds length must match dimensions")
    
    for i, bound in enumerate(bounds):
        if not isinstance(bound, (tuple, list)) or len(bound) != 2:
            raise ValueError(f"Bound {i} must be a tuple/list of length 2")
        if bound[0] >= bound[1]:
            raise ValueError(f"Bound {i}: lower bound must be less than upper bound")
    
    # Validate objective function
    if not callable(problem['objective_function']):
        raise ValueError("Objective function must be callable")
    
    return True

def get_problem_info(problem):
    """
    Get information about a problem definition.
    
    Parameters
    ----------
    problem : dict
        Problem definition
        
    Returns
    -------
    dict
        Problem information
    """
    info = {
        'problem_type': problem.get('problem_type', 'unknown'),
        'dimensions': problem['dimensions'],
        'minimize': problem['minimize'],
        'n_constraints': len(problem.get('constraints', [])),
        'bounds_summary': f"[{problem['bounds'][0][0]}, {problem['bounds'][0][1]}]" 
                         if all(b == problem['bounds'][0] for b in problem['bounds'])
                         else "variable bounds"
    }
    
    if problem.get('X') is not None:
        info['data_shape'] = problem['X'].shape
        info['n_classes'] = len(np.unique(problem['y']))
    
    return info