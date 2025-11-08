"""
Input Validation Module
========================
Validates optimization inputs, parameters, bounds, and datasets.
"""

import numpy as np
from typing import Tuple, Union, Optional
import warnings


class OptimizationValidator:
    """
    Comprehensive input validation for optimization problems.
    
    Validates:
    - Bounds and dimensions
    - Datasets (X, y)
    - Algorithm parameters
    - Objective functions
    """
    
    @staticmethod
    def validate_bounds(bounds: Union[Tuple, np.ndarray], dimensions: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Validate and normalize optimization bounds.
        
        Parameters
        ----------
        bounds : tuple or ndarray
            Either (lower, upper) tuple for uniform bounds across all dimensions,
            or array of shape (dimensions, 2) for per-dimension bounds
        dimensions : int
            Number of dimensions
            
        Returns
        -------
        lower_bounds : ndarray
            Lower bounds array of shape (dimensions,)
        upper_bounds : ndarray
            Upper bounds array of shape (dimensions,)
            
        Raises
        ------
        ValueError
            If bounds are invalid or inconsistent
        """
        if dimensions <= 0:
            raise ValueError(f"Dimensions must be positive, got {dimensions}")
        
        # Handle tuple bounds (uniform across all dimensions)
        if isinstance(bounds, tuple):
            if len(bounds) != 2:
                raise ValueError(f"Bounds tuple must have 2 elements (lower, upper), got {len(bounds)}")
            
            lb, ub = bounds
            
            # Convert to numpy if needed
            if not isinstance(lb, np.ndarray):
                lb = np.array(lb) if hasattr(lb, '__iter__') else np.full(dimensions, lb)
            if not isinstance(ub, np.ndarray):
                ub = np.array(ub) if hasattr(ub, '__iter__') else np.full(dimensions, ub)
            
            # Validate lower < upper
            if np.any(lb >= ub):
                raise ValueError(f"Lower bound must be < upper bound. Got lb={lb}, ub={ub}")
            
            return lb, ub
        
        # Handle array bounds (per-dimension)
        elif isinstance(bounds, np.ndarray):
            if bounds.ndim != 2 or bounds.shape[1] != 2:
                raise ValueError(f"Bounds array must have shape (dimensions, 2), got {bounds.shape}")
            
            if bounds.shape[0] != dimensions:
                raise ValueError(f"Bounds shape[0] ({bounds.shape[0]}) doesn't match dimensions ({dimensions})")
            
            lb, ub = bounds[:, 0], bounds[:, 1]
            
            if np.any(lb >= ub):
                raise ValueError("All lower bounds must be < upper bounds")
            
            return lb, ub
        
        else:
            raise TypeError(f"Bounds must be tuple or ndarray, got {type(bounds)}")
    
    @staticmethod
    def validate_dataset(X: np.ndarray, y: np.ndarray, min_samples: int = 10) -> bool:
        """
        Validate feature selection dataset.
        
        Parameters
        ----------
        X : ndarray
            Feature matrix of shape (n_samples, n_features)
        y : ndarray
            Target vector of shape (n_samples,)
        min_samples : int, default=10
            Minimum number of samples required
            
        Returns
        -------
        bool
            True if validation passes
            
        Raises
        ------
        ValueError
            If dataset is invalid
        """
        # Check types
        if not isinstance(X, np.ndarray) or not isinstance(y, np.ndarray):
            raise TypeError("X and y must be numpy arrays")
        
        # Check dimensions
        if X.ndim != 2:
            raise ValueError(f"X must be 2D array, got shape {X.shape}")
        
        if y.ndim != 1:
            if y.ndim == 2 and y.shape[1] == 1:
                y = y.ravel()
            else:
                raise ValueError(f"y must be 1D array, got shape {y.shape}")
        
        # Check sample counts match
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X samples ({X.shape[0]}) and y samples ({y.shape[0]}) don't match")
        
        # Check minimum samples
        if X.shape[0] < min_samples:
            warnings.warn(f"Small dataset ({X.shape[0]} samples < {min_samples}). May lead to overfitting.")
        
        # Check for NaN/Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("X contains NaN or Inf values")
        
        if np.any(np.isnan(y)) or np.any(np.isinf(y)):
            raise ValueError("y contains NaN or Inf values")
        
        # Check for constant features
        constant_features = np.where(np.std(X, axis=0) == 0)[0]
        if len(constant_features) > 0:
            warnings.warn(f"Found {len(constant_features)} constant features that should be removed")
        
        return True
    
    @staticmethod
    def validate_population_size(population_size: int, 
                                dimensions: int,
                                min_ratio: float = 2.0,
                                max_size: int = 1000) -> int:
        """
        Validate and adjust population size.
        
        Parameters
        ----------
        population_size : int
            Desired population size
        dimensions : int
            Problem dimensions
        min_ratio : float, default=2.0
            Minimum ratio of population_size to dimensions
        max_size : int, default=1000
            Maximum allowed population size
            
        Returns
        -------
        int
            Validated (possibly adjusted) population size
        """
        if population_size <= 0:
            raise ValueError(f"Population size must be positive, got {population_size}")
        
        if population_size > max_size:
            warnings.warn(f"Population size {population_size} > {max_size}. May be slow.")
        
        min_pop = int(dimensions * min_ratio)
        if population_size < min_pop:
            warnings.warn(f"Population size {population_size} < recommended minimum {min_pop}")
        
        return population_size
    
    @staticmethod
    def validate_iterations(max_iterations: int, 
                          min_iters: int = 10,
                          max_iters: int = 10000) -> int:
        """
        Validate iteration count.
        
        Parameters
        ----------
        max_iterations : int
            Desired maximum iterations
        min_iters : int, default=10
            Minimum iterations (warning if below)
        max_iters : int, default=10000
            Maximum iterations (warning if above)
            
        Returns
        -------
        int
            Validated max_iterations
        """
        if max_iterations <= 0:
            raise ValueError(f"Max iterations must be positive, got {max_iterations}")
        
        if max_iterations < min_iters:
            warnings.warn(f"Max iterations {max_iterations} < {min_iters}. May not converge.")
        
        if max_iterations > max_iters:
            warnings.warn(f"Max iterations {max_iterations} > {max_iters}. May be very slow.")
        
        return max_iterations
    
    @staticmethod
    def validate_objective_function(objective_function, 
                                   test_dimension: int = 5) -> bool:
        """
        Validate objective function can be called and returns valid output.
        
        Parameters
        ----------
        objective_function : callable
            Function to validate
        test_dimension : int, default=5
            Dimension for test input
            
        Returns
        -------
        bool
            True if function is valid
            
        Raises
        ------
        ValueError
            If function is invalid or returns invalid output
        """
        if not callable(objective_function):
            raise TypeError("Objective function must be callable")
        
        # Test with random input
        test_input = np.random.randn(test_dimension)
        
        try:
            result = objective_function(test_input)
        except Exception as e:
            raise ValueError(f"Objective function failed on test input: {e}")
        
        # Check result is numeric scalar
        try:
            result_float = float(result)
        except (TypeError, ValueError):
            raise ValueError(f"Objective function must return numeric scalar, got {type(result)}")
        
        # Check for NaN/Inf
        if np.isnan(result_float) or np.isinf(result_float):
            warnings.warn("Objective function returned NaN or Inf on test input")
        
        return True
    
    @staticmethod
    def validate_algorithm_parameters(**kwargs) -> dict:
        """
        Validate common algorithm parameters.
        
        Parameters
        ----------
        **kwargs : dict
            Algorithm parameters to validate
            
        Returns
        -------
        dict
            Validated parameters
        """
        validated = {}
        
        # Common parameter ranges
        param_ranges = {
            'w': (0.0, 1.0, "Inertia weight"),
            'c1': (0.0, 4.0, "Cognitive coefficient"),
            'c2': (0.0, 4.0, "Social coefficient"),
            'crossover_rate': (0.0, 1.0, "Crossover rate"),
            'mutation_rate': (0.0, 1.0, "Mutation rate"),
            'beta': (0.0, 2.0, "Levy flight beta parameter"),
            'alpha': (0.0, 2.0, "Alpha parameter"),
        }
        
        for key, value in kwargs.items():
            if key in param_ranges:
                min_val, max_val, name = param_ranges[key]
                if not (min_val <= value <= max_val):
                    warnings.warn(f"{name} '{key}'={value} outside typical range [{min_val}, {max_val}]")
            
            validated[key] = value
        
        return validated


# Convenience validation function
def validate_optimization_inputs(objective_function=None,
                                X=None, 
                                y=None,
                                bounds=None,
                                dimensions=None,
                                population_size=None,
                                max_iterations=None,
                                **kwargs) -> dict:
    """
    Comprehensive validation of all optimization inputs.
    
    Returns
    -------
    dict
        Validated parameters
    """
    validator = OptimizationValidator()
    validated = {}
    
    # Determine problem type
    is_feature_selection = X is not None and y is not None
    is_function_optimization = objective_function is not None
    
    if not is_feature_selection and not is_function_optimization:
        raise ValueError("Must provide either (X, y) for feature selection or objective_function")
    
    # Validate feature selection
    if is_feature_selection:
        validator.validate_dataset(X, y)
        validated['X'] = X
        validated['y'] = y
        if dimensions is None:
            dimensions = X.shape[1]
    
    # Validate function optimization
    if is_function_optimization:
        validator.validate_objective_function(objective_function)
        validated['objective_function'] = objective_function
        
        if dimensions is None:
            raise ValueError("Must specify dimensions for function optimization")
        
        if bounds is not None:
            lb, ub = validator.validate_bounds(bounds, dimensions)
            validated['bounds'] = (lb, ub)
    
    # Validate parameters
    if dimensions is not None:
        validated['dimensions'] = dimensions
    
    if population_size is not None:
        validated['population_size'] = validator.validate_population_size(
            population_size, dimensions or 10
        )
    
    if max_iterations is not None:
        validated['max_iterations'] = validator.validate_iterations(max_iterations)
    
    # Validate algorithm-specific parameters
    if kwargs:
        validated.update(validator.validate_algorithm_parameters(**kwargs))
    
    return validated
