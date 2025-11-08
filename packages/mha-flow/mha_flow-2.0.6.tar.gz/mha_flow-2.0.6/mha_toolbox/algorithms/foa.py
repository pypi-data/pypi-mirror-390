"""
Fruit Fly Optimization Algorithm (FOA)
=====================================

Fruit Fly Optimization Algorithm inspired by the food finding behavior
of fruit flies using osphresis and vision.
"""

import numpy as np
from ..base import BaseOptimizer


class FruitFlyOptimization(BaseOptimizer):
    """
    Fruit Fly Optimization Algorithm (FOA)
    
    Bio-inspired algorithm based on the foraging behavior of fruit flies
    using their keen osphresis and sensitive vision.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Fruit Fly Optimization Algorithm"
        self.aliases = ["foa", "fruitfly", "fruit_fly_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Fruit Fly Optimization Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize swarm position
        swarm_position = np.random.uniform(bounds[0], bounds[1], dimension)
        best_fitness = objective_function(swarm_position)
        best_position = swarm_position.copy()
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [np.array([best_fitness] * self.population_size)]
        local_positions = [np.tile(swarm_position, (self.population_size, 1))]
        
        for iteration in range(self.max_iterations):
            # Generate fruit fly swarm around the swarm location
            population = np.zeros((self.population_size, dimension))
            fitness = np.zeros(self.population_size)
            
            for i in range(self.population_size):
                # Random flight direction and distance using osphresis
                random_flight = np.random.uniform(-1, 1, dimension)
                
                # Update position
                population[i] = swarm_position + random_flight
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
                
                # Calculate smell concentration (distance to origin)
                distance = np.sqrt(np.sum(population[i] ** 2))
                
                # Smell concentration judgment value (reciprocal of distance)
                if distance == 0:
                    S = 1e10
                else:
                    S = 1.0 / distance
                
                # Find fitness using vision
                fitness[i] = objective_function(population[i])
            
            # Find the fruit fly with best smell concentration
            best_idx = np.argmin(fitness)
            
            # Update swarm position if better
            if fitness[best_idx] < best_fitness:
                best_position = population[best_idx].copy()
                best_fitness = fitness[best_idx]
                swarm_position = best_position.copy()
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions