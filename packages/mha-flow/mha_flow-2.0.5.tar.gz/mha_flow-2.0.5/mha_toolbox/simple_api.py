"""
Simple API for Beginner Library Users
=====================================

Simplified, high-level API for users who want to use MHA Toolbox as a library
without dealing with complex configurations.

Usage:
    from mha_toolbox import quick_optimize, recommend_algorithm
    
    # Get a recommendation
    algo = recommend_algorithm(n_features=10, n_samples=1000)
    
    # Quick optimization
    result = quick_optimize(
        algorithm="PSO",
        objective_function=my_function,
        dimensions=10
    )
"""

from typing import Callable, Optional, Dict, Any, List, Union
import numpy as np
from .algorithm_recommender import AlgorithmRecommender
from .toolbox import MHAToolbox


class SimpleAPI:
    """
    Simplified API wrapper for beginners using the library programmatically.
    
    This class provides high-level functions with sensible defaults,
    automatic configuration, and helpful error messages.
    """
    
    def __init__(self):
        self.recommender = AlgorithmRecommender()
        self.toolbox = MHAToolbox()
        
    def recommend(
        self,
        n_features: Optional[int] = None,
        n_samples: Optional[int] = None,
        problem_type: str = "continuous",
        has_constraints: bool = False,
        is_noisy: bool = False
    ) -> Dict[str, Any]:
        """
        Get algorithm recommendation based on problem characteristics.
        
        Parameters:
        -----------
        n_features : int, optional
            Number of dimensions/features
        n_samples : int, optional
            Number of samples in dataset
        problem_type : str
            Type of problem: 'continuous', 'discrete', 'binary', 'mixed'
        has_constraints : bool
            Whether problem has constraints
        is_noisy : bool
            Whether objective function is noisy
            
        Returns:
        --------
        dict : Recommendation with algorithm name, confidence, and reasoning
        
        Example:
        --------
        >>> api = SimpleAPI()
        >>> rec = api.recommend(n_features=20, n_samples=1000)
        >>> print(f"Recommended: {rec['algorithm']} (confidence: {rec['confidence']})")
        """
        dataset_info = {}
        if n_features is not None:
            dataset_info['n_features'] = n_features
        if n_samples is not None:
            dataset_info['n_samples'] = n_samples
            
        problem_info = {
            'type': problem_type,
            'has_constraints': has_constraints,
            'is_noisy': is_noisy
        }
        
        return self.recommender.recommend_algorithm(
            dataset_info=dataset_info,
            problem_info=problem_info
        )
    
    def optimize(
        self,
        algorithm: str,
        objective_function: Callable,
        dimensions: int,
        bounds: Optional[List[tuple]] = None,
        population_size: int = 50,
        max_iterations: int = 100,
        minimize: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run optimization with sensible defaults and automatic configuration.
        
        Parameters:
        -----------
        algorithm : str
            Name of algorithm (e.g., 'PSO', 'GA', 'GWO')
        objective_function : callable
            Function to optimize, takes np.array and returns float
        dimensions : int
            Number of dimensions in solution space
        bounds : list of tuples, optional
            Bounds for each dimension [(min, max), ...]. 
            If None, uses [(-100, 100)] for all dimensions
        population_size : int
            Number of solutions in population (default: 50)
        max_iterations : int
            Maximum number of iterations (default: 100)
        minimize : bool
            If True, minimize; if False, maximize (default: True)
        **kwargs : dict
            Additional algorithm-specific parameters
            
        Returns:
        --------
        dict : Results containing:
            - 'best_solution': Best solution found
            - 'best_fitness': Best fitness value
            - 'convergence_curve': Fitness over iterations
            - 'execution_time': Time taken
            - 'success': Whether optimization succeeded
            
        Example:
        --------
        >>> def sphere(x):
        ...     return np.sum(x**2)
        >>> 
        >>> api = SimpleAPI()
        >>> result = api.optimize(
        ...     algorithm="PSO",
        ...     objective_function=sphere,
        ...     dimensions=10,
        ...     population_size=30,
        ...     max_iterations=50
        ... )
        >>> print(f"Best fitness: {result['best_fitness']:.6f}")
        """
        # Set default bounds if not provided
        if bounds is None:
            bounds = [(-100, 100)] * dimensions
        
        # Validate algorithm
        available = self.toolbox.list_algorithms()
        if algorithm.upper() not in [a.upper() for a in available]:
            raise ValueError(
                f"Algorithm '{algorithm}' not found. "
                f"Available: {', '.join(available[:10])}... "
                f"Use list_algorithms() for complete list."
            )
        
        # Prepare configuration
        config = {
            'population_size': population_size,
            'max_iterations': max_iterations,
            'dimensions': dimensions,
            'bounds': np.array(bounds),
            **kwargs
        }
        
        # Run optimization
        try:
            result = self.toolbox.optimize(
                algorithm=algorithm,
                objective_function=objective_function,
                config=config,
                minimize=minimize
            )
            result['success'] = True
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'best_solution': None,
                'best_fitness': None,
                'convergence_curve': []
            }
    
    def compare(
        self,
        algorithms: List[str],
        objective_function: Callable,
        dimensions: int,
        bounds: Optional[List[tuple]] = None,
        runs_per_algorithm: int = 10,
        population_size: int = 50,
        max_iterations: int = 100,
        minimize: bool = True
    ) -> Dict[str, Any]:
        """
        Compare multiple algorithms on the same problem.
        
        Parameters:
        -----------
        algorithms : list of str
            List of algorithm names to compare
        objective_function : callable
            Function to optimize
        dimensions : int
            Number of dimensions
        bounds : list of tuples, optional
            Bounds for each dimension
        runs_per_algorithm : int
            Number of independent runs per algorithm (default: 10)
        population_size : int
            Population size (default: 50)
        max_iterations : int
            Max iterations (default: 100)
        minimize : bool
            If True, minimize; if False, maximize
            
        Returns:
        --------
        dict : Comparison results with statistics for each algorithm
        
        Example:
        --------
        >>> def sphere(x):
        ...     return np.sum(x**2)
        >>> 
        >>> api = SimpleAPI()
        >>> comparison = api.compare(
        ...     algorithms=["PSO", "GA", "GWO"],
        ...     objective_function=sphere,
        ...     dimensions=10,
        ...     runs_per_algorithm=5
        ... )
        >>> for algo, stats in comparison.items():
        ...     print(f"{algo}: {stats['mean_fitness']:.6f} ± {stats['std_fitness']:.6f}")
        """
        if bounds is None:
            bounds = [(-100, 100)] * dimensions
            
        results = {}
        
        for algorithm in algorithms:
            algo_results = []
            
            for run in range(runs_per_algorithm):
                result = self.optimize(
                    algorithm=algorithm,
                    objective_function=objective_function,
                    dimensions=dimensions,
                    bounds=bounds,
                    population_size=population_size,
                    max_iterations=max_iterations,
                    minimize=minimize
                )
                
                if result['success']:
                    algo_results.append(result['best_fitness'])
            
            if algo_results:
                results[algorithm] = {
                    'mean_fitness': np.mean(algo_results),
                    'std_fitness': np.std(algo_results),
                    'min_fitness': np.min(algo_results),
                    'max_fitness': np.max(algo_results),
                    'median_fitness': np.median(algo_results),
                    'all_runs': algo_results,
                    'success_rate': len(algo_results) / runs_per_algorithm
                }
            else:
                results[algorithm] = {
                    'error': 'All runs failed',
                    'success_rate': 0.0
                }
        
        return results
    
    def list_algorithms(self, category: Optional[str] = None) -> List[str]:
        """
        List available algorithms, optionally filtered by category.
        
        Parameters:
        -----------
        category : str, optional
            Filter by category: 'swarm', 'evolutionary', 'physics', 'bio', 'hybrid'
            
        Returns:
        --------
        list : Algorithm names
        
        Example:
        --------
        >>> api = SimpleAPI()
        >>> swarm_algos = api.list_algorithms(category='swarm')
        >>> print(f"Swarm algorithms: {', '.join(swarm_algos)}")
        """
        all_algorithms = self.toolbox.list_algorithms()
        
        if category is None:
            return all_algorithms
        
        # Categorize algorithms
        categories = {
            'swarm': ['PSO', 'ABC', 'ACO', 'FA', 'BA', 'FPA', 'GWO', 'WOA', 'SSA', 'CSA'],
            'evolutionary': ['GA', 'DE', 'ES', 'EP', 'GP'],
            'physics': ['SA', 'GSA', 'MVO', 'ALO', 'MFO'],
            'bio': ['BBO', 'IWD', 'SMA', 'TSA'],
            'hybrid': [a for a in all_algorithms if 'HYBRID' in a.upper() or '_' in a]
        }
        
        cat_lower = category.lower()
        if cat_lower in categories:
            return [a for a in all_algorithms if a.upper() in [c.upper() for c in categories[cat_lower]]]
        else:
            return all_algorithms


# Global API instance for convenience functions
_api = None

def get_api() -> SimpleAPI:
    """Get or create global API instance."""
    global _api
    if _api is None:
        _api = SimpleAPI()
    return _api


# Convenience functions for direct import
def quick_optimize(
    algorithm: str,
    objective_function: Callable,
    dimensions: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick optimization with minimal configuration.
    
    Example:
    --------
    >>> from mha_toolbox import quick_optimize
    >>> 
    >>> def sphere(x):
    ...     return np.sum(x**2)
    >>> 
    >>> result = quick_optimize("PSO", sphere, dimensions=10)
    >>> print(f"Best: {result['best_fitness']}")
    """
    return get_api().optimize(algorithm, objective_function, dimensions, **kwargs)


def recommend_algorithm(
    n_features: Optional[int] = None,
    n_samples: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get algorithm recommendation for your problem.
    
    Example:
    --------
    >>> from mha_toolbox import recommend_algorithm
    >>> 
    >>> rec = recommend_algorithm(n_features=50, n_samples=10000)
    >>> print(f"Try: {rec['algorithm']} - {rec['reasoning']}")
    """
    return get_api().recommend(n_features, n_samples, **kwargs)


def compare_algorithms(
    algorithms: List[str],
    objective_function: Callable,
    dimensions: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Compare multiple algorithms quickly.
    
    Example:
    --------
    >>> from mha_toolbox import compare_algorithms
    >>> 
    >>> def sphere(x):
    ...     return np.sum(x**2)
    >>> 
    >>> results = compare_algorithms(
    ...     ["PSO", "GA", "DE"], 
    ...     sphere, 
    ...     dimensions=10,
    ...     runs_per_algorithm=5
    ... )
    """
    return get_api().compare(algorithms, objective_function, dimensions, **kwargs)


def list_algorithms(category: Optional[str] = None) -> List[str]:
    """
    List all available algorithms.
    
    Example:
    --------
    >>> from mha_toolbox import list_algorithms
    >>> 
    >>> all_algos = list_algorithms()
    >>> swarm_algos = list_algorithms(category='swarm')
    """
    return get_api().list_algorithms(category)
