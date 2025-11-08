"""
Henry Gas Solubility Optimization (HGSO) Algorithm

A physics-inspired optimization algorithm based on Henry's law
of gas solubility in liquids.

Reference:
Hashim, F. A., Houssein, E. H., Mabrouk, M. S., Al-Atabany, W., & Mirjalili, S. (2019). 
Henry gas solubility optimization: A novel physics-based algorithm. 
Future Generation Computer Systems, 101, 646-667.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class HenryGasSolubilityOptimization(BaseOptimizer):
    """
    Henry Gas Solubility Optimization (HGSO) Algorithm
    
    A physics-inspired optimization algorithm based on Henry's law.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of gas clusters
    max_iterations : int, default=100
        Maximum number of iterations
    n_clusters : int, default=2
        Number of gas clusters (H2O and N2)
    """
    
    aliases = ['hgso', 'henry', 'gas_solubility']
    
    def __init__(self, population_size=50, max_iterations=100, n_clusters=2, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.n_clusters = n_clusters
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.n_clusters_ = n_clusters
        self.algorithm_name_ = "Henry Gas Solubility Optimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the optimization algorithm
        """
        # Use trailing underscore attributes
        if X is not None:
            dimensions = X.shape[1]
            lower_bound = np.zeros(dimensions)
            upper_bound = np.ones(dimensions)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                raise ValueError("Dimensions must be specified")
            dimensions = self.dimensions_
            lower_bound = self.lower_bound_
            upper_bound = self.upper_bound_
            
        objective_func = objective_function
        # Initialize gas molecules
        population = np.random.uniform(lower_bound, upper_bound, 
                                     (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # Divide population into clusters
        cluster_size = self.population_size // self.n_clusters
        clusters = []
        for i in range(self.n_clusters):
            start_idx = i * cluster_size
            end_idx = start_idx + cluster_size if i < self.n_clusters - 1 else self.population_size
            clusters.append(list(range(start_idx, end_idx)))
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        # Henry's constants for different gases
        henry_constants = np.random.uniform(0.1, 2.0, self.n_clusters)
        
        for iteration in range(self.max_iterations):
            # Update Henry's constants based on temperature
            temperature = 1 - iteration / self.max_iterations
            for k in range(self.n_clusters):
                henry_constants[k] *= (1 + 0.1 * temperature)
            
            for cluster_idx, cluster in enumerate(clusters):
                for i in cluster:
                    # Calculate solubility coefficient
                    solubility = henry_constants[cluster_idx] * np.random.random()
                    
                    # Gas dissolution process
                    if np.random.random() < solubility:
                        # High solubility - exploitation
                        best_in_cluster = min(cluster, key=lambda x: fitness[x])
                        direction = population[best_in_cluster] - population[i]
                        step_size = np.random.uniform(0.1, 0.5)
                        new_position = population[i] + step_size * direction
                    else:
                        # Low solubility - exploration
                        random_position = np.random.uniform(lower_bound, upper_bound, dimensions)
                        mixing_factor = np.random.random()
                        new_position = mixing_factor * population[i] + (1 - mixing_factor) * random_position
                    
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[i]:
                        population[i] = new_position
                        fitness[i] = new_fitness
            
            # Gas escape and re-entry
            if iteration % 10 == 0:
                worst_indices = np.argsort(fitness)[-self.population_size // 10:]
                for idx in worst_indices:
                    if np.random.random() < 0.1:  # Gas escapes
                        population[idx] = np.random.uniform(lower_bound, upper_bound, dimensions)
                        fitness[idx] = objective_func(population[idx])
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
            
            if hasattr(self, "verbose_") and self.verbose_:
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions