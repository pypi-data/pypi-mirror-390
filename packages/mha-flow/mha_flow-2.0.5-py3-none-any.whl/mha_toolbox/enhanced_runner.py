"""
Enhanced Runner with Live Progress Support
==========================================

This module provides generator-based algorithm execution that yields results
after each algorithm completes, enabling live UI updates.
"""

import numpy as np
import time
from datetime import datetime


def run_comparison_with_live_progress(X, y, dataset_name, task_type, algorithms,
                                      max_iterations, population_size, n_runs):
    """
    Generator function that yields results for each algorithm as it completes.
    
    This enables live progress updates in the UI by yielding after each algorithm finishes.
    
    Args:
        X: Feature matrix
        y: Target vector
        dataset_name: Name of the dataset
        task_type: Type of optimization task
        algorithms: List of algorithm names to run
        max_iterations: Maximum iterations per algorithm
        population_size: Population size for algorithms
        n_runs: Number of independent runs per algorithm
        
    Yields:
        dict: Result dictionary for each completed algorithm.
    """
    
    try:
        import mha_toolbox as mha
    except ImportError:
        yield {
            'algorithm': 'system',
            'status': 'failed',
            'error': 'mha_toolbox not found. Please install it first.'
        }
        return
    
    total_algorithms = len(algorithms)
    
    for i, alg_name in enumerate(algorithms):
        yield {
            'algorithm': alg_name,
            'status': 'running',
            'progress': i / total_algorithms,
            'iteration': f"{i+1}/{total_algorithms}"
        }
        
        try:
            alg_start_time = time.time()
            
            params = {
                'max_iterations': max_iterations,
                'population_size': population_size,
                'verbose': False
            }
            
            runs_data = []
            
            for run in range(n_runs):
                # The timeout check has been removed from here.
                
                run_start_time = time.time()
                
                try:
                    # The logic for running different task types remains the same.
                    if task_type == 'feature_selection':
                        result = mha.optimize(alg_name, X, y, **params)
                        
                        run_result = {
                            'run': run + 1,
                            'best_fitness': float(result.best_fitness_),
                            'n_selected_features': int(result.n_selected_features_),
                            'convergence_curve': [float(x) for x in result.global_fitness_],
                            'execution_time': time.time() - run_start_time,
                            'final_accuracy': float(1 - result.best_fitness_),
                            'success': True,
                            'total_iterations': len(result.global_fitness_)
                        }
                        
                    elif task_type == 'feature_optimization':
                        # Feature optimization objective
                        def feature_objective(weights):
                            try:
                                weights = np.array(weights)
                                weights = np.clip(weights, 0, 1)
                                
                                if len(weights) != X.shape[1]:
                                    if len(weights) < X.shape[1]:
                                        weights = np.tile(weights, (X.shape[1] // len(weights)) + 1)[:X.shape[1]]
                                    else:
                                        weights = weights[:X.shape[1]]
                                
                                X_weighted = X * weights.reshape(1, -1)
                                
                                from sklearn.ensemble import RandomForestClassifier
                                from sklearn.model_selection import cross_val_score
                                
                                model = RandomForestClassifier(n_estimators=10, random_state=42)
                                scores = cross_val_score(model, X_weighted, y, cv=3, scoring='accuracy')
                                return 1.0 - np.mean(scores)
                                
                            except Exception:
                                return 1.0
                        
                        result = mha.optimize(
                            alg_name,
                            objective_function=feature_objective,
                            dimensions=X.shape[1],
                            bounds=[(0, 1)] * X.shape[1],
                            **params
                        )
                        
                        run_result = {
                            'run': run + 1,
                            'best_fitness': float(result.best_fitness_),
                            'convergence_curve': [float(x) for x in result.global_fitness_],
                            'execution_time': time.time() - run_start_time,
                            'optimized_weights': result.best_solution_.tolist(),
                            'performance_score': float(1 - result.best_fitness_),
                            'success': True,
                            'total_iterations': len(result.global_fitness_)
                        }
                        
                    elif task_type == 'hyperparameter_tuning':
                        # Hyperparameter optimization objective
                        def hyperparameter_objective(params_vector):
                            try:
                                params_vector = np.array(params_vector)
                                params_vector = np.clip(params_vector, 0, 1)
                                
                                n_estimators = max(10, int(params_vector[0] * 190 + 10))
                                max_depth = max(3, int(params_vector[1] * 17 + 3)) if params_vector[1] > 0.1 else None
                                min_samples_split = max(2, int(params_vector[2] * 18 + 2))
                                
                                from sklearn.ensemble import RandomForestClassifier
                                from sklearn.model_selection import cross_val_score
                                
                                rf = RandomForestClassifier(
                                    n_estimators=n_estimators,
                                    max_depth=max_depth,
                                    min_samples_split=min_samples_split,
                                    random_state=42
                                )
                                
                                scores = cross_val_score(rf, X, y, cv=3, scoring='accuracy')
                                return 1.0 - np.mean(scores)
                                
                            except Exception:
                                return 1.0
                        
                        result = mha.optimize(
                            alg_name,
                            objective_function=hyperparameter_objective,
                            dimensions=3,
                            bounds=[(0, 1)] * 3,
                            **params
                        )
                        
                        best_params = result.best_solution_
                        best_n_estimators = max(10, int(best_params[0] * 190 + 10))
                        best_max_depth = max(3, int(best_params[1] * 17 + 3)) if best_params[1] > 0.1 else None
                        best_min_samples_split = max(2, int(best_params[2] * 18 + 2))
                        
                        run_result = {
                            'run': run + 1,
                            'best_fitness': float(result.best_fitness_),
                            'convergence_curve': [float(x) for x in result.global_fitness_],
                            'execution_time': time.time() - run_start_time,
                            'best_accuracy': float(1 - result.best_fitness_),
                            'optimized_params': result.best_solution_.tolist(),
                            'best_hyperparameters': {
                                'n_estimators': best_n_estimators,
                                'max_depth': best_max_depth,
                                'min_samples_split': best_min_samples_split
                            },
                            'success': True,
                            'total_iterations': len(result.global_fitness_)
                        }
                    
                    runs_data.append(run_result)
                    
                except Exception as e:
                    runs_data.append({'success': False, 'error': str(e)})
                    continue
            
            # Calculate statistics if we have successful runs
            if runs_data:
                successful_runs = [r for r in runs_data if r.get('success')]
                
                if successful_runs:
                    fitnesses = [run['best_fitness'] for run in successful_runs]
                    times = [run['execution_time'] for run in successful_runs]
                    
                    statistics = {
                        'mean_fitness': float(np.mean(fitnesses)),
                        'std_fitness': float(np.std(fitnesses)),
                        'best_fitness': float(np.min(fitnesses)),
                        'worst_fitness': float(np.max(fitnesses)),
                        'mean_time': float(np.mean(times)),
                        'std_time': float(np.std(times)),
                        'total_runs': len(runs_data),
                        'successful_runs': len(successful_runs)
                    }
                    
                    if task_type == 'feature_selection':
                        n_features = [run['n_selected_features'] for run in successful_runs]
                        accuracies = [run['final_accuracy'] for run in successful_runs]
                        if n_features and accuracies:
                            statistics.update({
                                'mean_features': float(np.mean(n_features)),
                                'std_features': float(np.std(n_features)),
                                'mean_accuracy': float(np.mean(accuracies)),
                                'std_accuracy': float(np.std(accuracies))
                            })
                    
                    yield {
                        'algorithm': alg_name,
                        'status': 'completed',
                        'result_data': {
                            'algorithm': alg_name,
                            'runs': successful_runs, # Only pass successful runs to the dashboard
                            'statistics': statistics,
                            'task_type': task_type,
                            'total_execution_time': time.time() - alg_start_time
                        },
                        'progress': (i + 1) / total_algorithms
                    }
                else:
                    yield {
                        'algorithm': alg_name,
                        'status': 'failed',
                        'error': 'All runs failed.',
                        'progress': (i + 1) / total_algorithms
                    }
            else:
                yield {
                    'algorithm': alg_name,
                    'status': 'failed',
                    'error': 'No runs were completed.',
                    'progress': (i + 1) / total_algorithms
                }
                
        except Exception as e:
            yield {
                'algorithm': alg_name,
                'status': 'failed',
                'error': str(e),
                'progress': (i + 1) / total_algorithms
            }
    
    yield {
        'algorithm': 'all',
        'status': 'completed',
        'progress': 1.0,
        'message': 'All algorithms completed'
    }