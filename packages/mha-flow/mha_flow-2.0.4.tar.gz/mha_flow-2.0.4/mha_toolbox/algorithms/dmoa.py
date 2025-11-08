"""
Dwarf Mongoose Optimization Algorithm (DMOA)
===========================================

Dwarf Mongoose Optimization Algorithm inspired by the foraging and
scouting behavior of dwarf mongooses.
"""

import numpy as np
from ..base import BaseOptimizer


class DwarfMongooseOptimization(BaseOptimizer):
    """
    Dwarf Mongoose Optimization Algorithm (DMOA)
    
    Bio-inspired algorithm based on the cooperative foraging behavior
    and social structure of dwarf mongoose colonies.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Dwarf Mongoose Optimization Algorithm"
        self.aliases = ["dmoa", "dwarf_mongoose", "mongoose_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Dwarf Mongoose Optimization Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize mongoose population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track alpha mongoose (best)
        alpha_idx = np.argmin(fitness)
        alpha_position = population[alpha_idx].copy()
        alpha_fitness = fitness[alpha_idx]
        
        # History tracking
        global_fitness = [alpha_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update control parameter
            CF = (1 - iteration / self.max_iterations) ** (2 * iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # Foraging behavior
                if np.random.random() < 0.5:
                    # Foraging-led approach
                    r1 = np.random.random()
                    r2 = np.random.random()
                    
                    if np.random.random() < 0.5:
                        # Babysitting (exploitation)
                        population[i] = population[i] + CF * (r1 * alpha_position - r2 * population[i])
                    else:
                        # Scout behavior (exploration)
                        k = np.random.randint(0, self.population_size)
                        population[i] = population[i] + CF * (r1 * population[k] - r2 * population[i])
                else:
                    # Sleeping mound behavior
                    r3 = np.random.random()
                    r4 = np.random.random()
                    
                    population[i] = alpha_position + r3 * (r4 - 0.5) * 2 * CF * alpha_position
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update alpha mongoose
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < alpha_fitness:
                alpha_position = population[current_best_idx].copy()
                alpha_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(alpha_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return alpha_position, alpha_fitness, global_fitness, local_fitness, local_positions