"""
Wildebeest Herd Optimization (WHO)
=================================

Wildebeest Herd Optimization inspired by the migration and
herding behavior of wildebeest populations.
"""

import numpy as np
from ..base import BaseOptimizer


class WildebeestHerdOptimization(BaseOptimizer):
    """
    Wildebeest Herd Optimization (WHO)
    
    Algorithm based on the collective migration behavior
    and herd dynamics of wildebeest.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Wildebeest Herd Optimization"
        self.aliases = ["who", "wildebeest", "wildebeest_herd"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Wildebeest Herd Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize wildebeest herd
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        velocity = np.zeros((self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Migration coefficient
            w = 0.9 - 0.5 * (iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # Herding behavior - follow the best position
                r1 = np.random.random()
                r2 = np.random.random()
                
                # Social influence from herd leader
                social_influence = r1 * (best_position - population[i])
                
                # Random exploration
                exploration = r2 * np.random.uniform(-1, 1, dimension)
                
                # Update velocity and position
                velocity[i] = w * velocity[i] + social_influence + exploration
                population[i] = population[i] + velocity[i]
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate fitness
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions