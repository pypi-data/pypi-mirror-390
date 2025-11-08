"""
Parallel Optimization Module
=============================
Execute multiple optimization runs in parallel for faster comparison
and ensemble methods.
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing as mp
from typing import List, Dict, Optional, Callable, Any
import time
import warnings


class ParallelOptimizer:
    """
    Execute multiple optimization runs in parallel.
    
    Supports:
    - Running same algorithm multiple times (for statistics)
    - Running different algorithms in parallel (for comparison)
    - Ensemble optimization (combining results from multiple runs)
    
    Parameters
    ----------
    n_jobs : int, default=-1
        Number of parallel jobs. -1 means use all CPU cores
    backend : str, default='process'
        'process' for CPU-bound tasks, 'thread' for I/O-bound tasks
    timeout : float, optional
        Timeout for each optimization run in seconds
    """
    
    def __init__(self, n_jobs: int = -1, backend: str = 'process', timeout: Optional[float] = None):
        self.n_jobs = n_jobs if n_jobs > 0 else mp.cpu_count()
        self.backend = backend
        self.timeout = timeout
        
        if self.backend == 'process':
            self.executor_class = ProcessPoolExecutor
        elif self.backend == 'thread':
            self.executor_class = ThreadPoolExecutor
        else:
            raise ValueError(f"Unknown backend '{backend}'. Use 'process' or 'thread'")
    
    def run_multiple(self, 
                    algorithm_name: str,
                    n_runs: int,
                    objective_function: Optional[Callable] = None,
                    X: Optional[np.ndarray] = None,
                    y: Optional[np.ndarray] = None,
                    **kwargs) -> Dict[str, Any]:
        """
        Run the same algorithm multiple times in parallel.
        
        Useful for statistical analysis and robustness testing.
        
        Parameters
        ----------
        algorithm_name : str
            Name of the algorithm to run
        n_runs : int
            Number of independent runs
        objective_function : callable, optional
            Objective function for function optimization
        X : ndarray, optional
            Features for feature selection
        y : ndarray, optional
            Target for feature selection
        **kwargs
            Additional parameters for the algorithm
            
        Returns
        -------
        dict
            Dictionary containing:
            - results: List of all results
            - best_result: Best result across all runs
            - statistics: Mean, std, min, max fitness
            - execution_time: Total execution time
        """
        from mha_toolbox import optimize
        
        print(f"🔄 Running {algorithm_name} {n_runs} times in parallel ({self.n_jobs} jobs)...")
        
        start_time = time.time()
        results = []
        errors = []
        
        with self.executor_class(max_workers=self.n_jobs) as executor:
            # Submit all jobs
            futures = {
                executor.submit(
                    self._run_single,
                    algorithm_name, 
                    objective_function,
                    X, y, 
                    kwargs,
                    run_id
                ): run_id 
                for run_id in range(n_runs)
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                run_id = futures[future]
                try:
                    result = future.result(timeout=self.timeout)
                    results.append(result)
                    print(f"  ✓ Run {run_id + 1}/{n_runs} completed (fitness: {result.best_fitness_:.6e})")
                except Exception as e:
                    error_msg = f"Run {run_id} failed: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ✗ Run {run_id + 1}/{n_runs} failed: {e}")
        
        total_time = time.time() - start_time
        
        if not results:
            raise RuntimeError(f"All {n_runs} runs failed. Errors: {errors}")
        
        # Calculate statistics
        fitness_values = [r.best_fitness_ for r in results]
        best_idx = np.argmin(fitness_values)
        
        statistics = {
            'mean_fitness': float(np.mean(fitness_values)),
            'std_fitness': float(np.std(fitness_values)),
            'min_fitness': float(np.min(fitness_values)),
            'max_fitness': float(np.max(fitness_values)),
            'median_fitness': float(np.median(fitness_values)),
            'success_rate': len(results) / n_runs,
            'n_successful': len(results),
            'n_failed': len(errors)
        }
        
        print(f"\n✅ Completed {len(results)}/{n_runs} runs in {total_time:.2f}s")
        print(f"📊 Statistics: mean={statistics['mean_fitness']:.6e}, "
              f"std={statistics['std_fitness']:.6e}, best={statistics['min_fitness']:.6e}")
        
        return {
            'results': results,
            'best_result': results[best_idx],
            'worst_result': results[np.argmax(fitness_values)],
            'statistics': statistics,
            'execution_time': total_time,
            'errors': errors
        }
    
    def compare_algorithms(self,
                          algorithm_names: List[str],
                          objective_function: Optional[Callable] = None,
                          X: Optional[np.ndarray] = None,
                          y: Optional[np.ndarray] = None,
                          n_runs_per_algorithm: int = 1,
                          **kwargs) -> Dict[str, Any]:
        """
        Compare multiple algorithms by running them in parallel.
        
        Parameters
        ----------
        algorithm_names : list of str
            Names of algorithms to compare
        objective_function : callable, optional
            Objective function for function optimization
        X : ndarray, optional
            Features for feature selection
        y : ndarray, optional
            Target for feature selection
        n_runs_per_algorithm : int, default=1
            Number of runs per algorithm (for statistical robustness)
        **kwargs
            Additional parameters for the algorithms
            
        Returns
        -------
        dict
            Comparison results with rankings and statistics
        """
        print(f"⚖️  Comparing {len(algorithm_names)} algorithms in parallel...")
        
        start_time = time.time()
        all_results = {}
        
        # Run each algorithm (potentially multiple times)
        for alg_name in algorithm_names:
            try:
                if n_runs_per_algorithm > 1:
                    # Multiple runs for statistics
                    result = self.run_multiple(
                        alg_name, n_runs_per_algorithm,
                        objective_function, X, y, **kwargs
                    )
                    all_results[alg_name] = result
                else:
                    # Single run
                    from mha_toolbox import optimize
                    result = optimize(alg_name, 
                                    objective_function=objective_function,
                                    X=X, y=y, **kwargs)
                    all_results[alg_name] = {
                        'results': [result],
                        'best_result': result,
                        'statistics': {
                            'mean_fitness': result.best_fitness_,
                            'min_fitness': result.best_fitness_
                        }
                    }
            except Exception as e:
                print(f"❌ {alg_name} failed: {e}")
                all_results[alg_name] = {'error': str(e)}
        
        # Create ranking
        successful_algs = {
            name: res for name, res in all_results.items() 
            if 'error' not in res
        }
        
        if successful_algs:
            sorted_algs = sorted(
                successful_algs.items(),
                key=lambda x: x[1]['statistics']['mean_fitness']
            )
            
            ranking = [
                {
                    'rank': i + 1,
                    'algorithm': name,
                    'mean_fitness': res['statistics']['mean_fitness'],
                    'best_fitness': res['statistics']['min_fitness'],
                    'std_fitness': res['statistics'].get('std_fitness', 0.0),
                    'execution_time': res['best_result'].execution_time_
                }
                for i, (name, res) in enumerate(sorted_algs)
            ]
        else:
            ranking = []
        
        total_time = time.time() - start_time
        
        print(f"\n🏆 Comparison Results (sorted by mean fitness):")
        print(f"{'Rank':<6} {'Algorithm':<30} {'Mean Fitness':<15} {'Best Fitness':<15} {'Time(s)':<10}")
        print("-" * 80)
        for entry in ranking[:10]:  # Show top 10
            print(f"{entry['rank']:<6} {entry['algorithm']:<30} "
                  f"{entry['mean_fitness']:<15.6e} {entry['best_fitness']:<15.6e} "
                  f"{entry['execution_time']:<10.2f}")
        
        return {
            'all_results': all_results,
            'ranking': ranking,
            'best_algorithm': ranking[0]['algorithm'] if ranking else None,
            'total_time': total_time
        }
    
    def ensemble_optimize(self,
                         algorithm_names: List[str],
                         objective_function: Callable,
                         method: str = 'best',
                         **kwargs) -> Any:
        """
        Run multiple algorithms and combine results using ensemble method.
        
        Parameters
        ----------
        algorithm_names : list of str
            Algorithms to use in ensemble
        objective_function : callable
            Objective function to optimize
        method : str, default='best'
            Ensemble method: 'best', 'mean', 'weighted_mean', 'voting'
        **kwargs
            Parameters for algorithms
            
        Returns
        -------
        result
            Combined optimization result
        """
        print(f"🤝 Ensemble optimization with {len(algorithm_names)} algorithms...")
        
        # Run all algorithms in parallel
        comparison = self.compare_algorithms(
            algorithm_names,
            objective_function=objective_function,
            **kwargs
        )
        
        if method == 'best':
            # Return best result from all algorithms
            best_alg = comparison['best_algorithm']
            return comparison['all_results'][best_alg]['best_result']
        
        elif method == 'mean':
            # Average the solutions
            successful_results = [
                res['best_result'] 
                for res in comparison['all_results'].values()
                if 'error' not in res
            ]
            
            if not successful_results:
                raise RuntimeError("All ensemble algorithms failed")
            
            # Average solutions
            mean_solution = np.mean([r.best_solution_ for r in successful_results], axis=0)
            mean_fitness = objective_function(mean_solution)
            
            # Create result from best algorithm but with mean solution
            best_result = successful_results[0]
            best_result.best_solution_ = mean_solution
            best_result.best_fitness_ = mean_fitness
            best_result.algorithm_name_ = f"Ensemble({method})"
            
            return best_result
        
        else:
            raise ValueError(f"Unknown ensemble method '{method}'")
    
    @staticmethod
    def _run_single(algorithm_name, objective_function, X, y, kwargs, run_id):
        """Helper function to run a single optimization (must be static for pickling)."""
        from mha_toolbox import optimize
        
        # Add run-specific seed for reproducibility
        run_kwargs = kwargs.copy()
        if 'seed' in run_kwargs:
            run_kwargs['seed'] = run_kwargs['seed'] + run_id
        
        return optimize(
            algorithm_name,
            objective_function=objective_function,
            X=X, y=y,
            **run_kwargs
        )


def parallel_optimize(algorithm_name: str, 
                     n_runs: int = 10,
                     n_jobs: int = -1,
                     **kwargs) -> Dict[str, Any]:
    """
    Convenience function for parallel optimization.
    
    Parameters
    ----------
    algorithm_name : str
        Algorithm to run
    n_runs : int, default=10
        Number of parallel runs
    n_jobs : int, default=-1
        Number of parallel jobs (-1 = all cores)
    **kwargs
        Optimization parameters
        
    Returns
    -------
    dict
        Results with statistics
    """
    optimizer = ParallelOptimizer(n_jobs=n_jobs)
    return optimizer.run_multiple(algorithm_name, n_runs, **kwargs)


def parallel_compare(algorithm_names: List[str],
                    n_runs_per_algorithm: int = 5,
                    n_jobs: int = -1,
                    **kwargs) -> Dict[str, Any]:
    """
    Convenience function for parallel algorithm comparison.
    
    Parameters
    ----------
    algorithm_names : list of str
        Algorithms to compare
    n_runs_per_algorithm : int, default=5
        Runs per algorithm for statistics
    n_jobs : int, default=-1
        Number of parallel jobs
    **kwargs
        Optimization parameters
        
    Returns
    -------
    dict
        Comparison results with rankings
    """
    optimizer = ParallelOptimizer(n_jobs=n_jobs)
    return optimizer.compare_algorithms(
        algorithm_names,
        n_runs_per_algorithm=n_runs_per_algorithm,
        **kwargs
    )
