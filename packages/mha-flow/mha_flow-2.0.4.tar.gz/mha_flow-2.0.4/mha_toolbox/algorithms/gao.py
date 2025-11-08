"""
Giant Armadillo Optimization (GAO)
=================================

Giant Armadillo Optimization inspired by the foraging and
survival behavior of giant armadillos.
"""

import numpy as np
from ..base import BaseOptimizer


class GiantArmadilloOptimization(BaseOptimizer):
    """
    Giant Armadillo Optimization (GAO)
    
    Bio-inspired algorithm based on the foraging, digging,
    and survival strategies of giant armadillos.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Giant Armadillo Optimization"
        self.aliases = ["gao", "armadillo", "giant_armadillo_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Giant Armadillo Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize armadillo population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update control parameter
            C = 2 * (1 - iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # Foraging behavior
                if np.random.random() < 0.5:
                    # Exploration phase - digging for food
                    r1 = np.random.random()
                    r2 = np.random.random()
                    
                    # Random armadillo position
                    k = np.random.randint(0, self.population_size)
                    
                    population[i] = population[i] + C * r1 * (population[k] - r2 * population[i])
                else:
                    # Exploitation phase - moving towards best food source
                    r3 = np.random.random()
                    
                    population[i] = best_position + C * r3 * (best_position - population[i])
                
                # Defense mechanism - random escape if threatened
                if np.random.random() < 0.1:  # 10% chance of threat
                    escape_direction = np.random.uniform(-1, 1, dimension)
                    population[i] = population[i] + escape_direction * C
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions