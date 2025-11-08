"""
Chaos Game Optimization (CGO) Algorithm

A mathematical optimization algorithm based on chaos theory and fractal geometry.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class ChaosGameOptimization(BaseOptimizer):
    """Chaos Game Optimization (CGO) Algorithm"""
    
    aliases = ['cgo', 'chaos', 'fractal']
    
    def __init__(self, population_size=50, max_iterations=100, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.algorithm_name_ = "Chaos Game Optimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the CGO optimization algorithm
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
        population = np.random.uniform(lower_bound, upper_bound, (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        for iteration in range(self.max_iterations):
            chaos_factor = np.sin(2 * np.pi * iteration / self.max_iterations)
            
            for i in range(self.population_size):
                r = np.random.random()
                if r < 0.33:
                    target = best_position
                elif r < 0.66:
                    target = population[np.random.randint(0, self.population_size)]
                else:
                    target = np.random.uniform(lower_bound, upper_bound, dimensions)
                
                chaos_step = chaos_factor * (target - population[i])
                new_position = population[i] + 0.5 * chaos_step
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
            
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions