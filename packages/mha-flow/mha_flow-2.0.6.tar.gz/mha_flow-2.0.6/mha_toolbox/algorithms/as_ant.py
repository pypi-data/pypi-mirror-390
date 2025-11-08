"""
Ant System (AS)
==============

Ant System - the original ant colony optimization algorithm inspired
by the foraging behavior of ants.
"""

import numpy as np
from ..base import BaseOptimizer


class AntSystem(BaseOptimizer):
    """
    Ant System (AS)
    
    The original ant colony optimization algorithm based on the
    pheromone trail laying behavior of ants.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Ant System"
        self.aliases = ["as", "ant_system", "ant_colony_system"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Ant System
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize ant population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Initialize pheromone matrix
        pheromone = np.ones((self.population_size, dimension))
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Pheromone parameters
        rho = 0.5  # Evaporation rate
        Q = 1.0    # Pheromone deposit factor
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Construct solution based on pheromone trails
                for d in range(dimension):
                    # Probability based on pheromone
                    prob = pheromone[i, d] / (np.sum(pheromone[i]) + 1e-10)
                    
                    # Move towards areas with higher pheromone
                    if np.random.random() < prob:
                        population[i, d] = population[i, d] + np.random.uniform(-1, 1) * (bounds[1] - bounds[0]) * 0.1
                    else:
                        population[i, d] = best_position[d] + np.random.randn() * 0.1
                
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate fitness
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update pheromone trails
            # Evaporation
            pheromone = (1 - rho) * pheromone
            
            # Deposit pheromone
            for i in range(self.population_size):
                delta_pheromone = Q / (fitness[i] + 1e-10)
                pheromone[i] += delta_pheromone
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions