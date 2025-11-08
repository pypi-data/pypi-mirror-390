"""
Flower Pollination Algorithm (FPA)
=================================

Flower Pollination Algorithm inspired by the pollination process
of flowering plants.
"""

import numpy as np
from ..base import BaseOptimizer


class FlowerPollinationAlgorithm(BaseOptimizer):
    """
    Flower Pollination Algorithm (FPA)
    
    Bio-inspired algorithm based on the pollination process of flowers,
    including global and local pollination strategies.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Flower Pollination Algorithm"
        self.aliases = ["fpa", "flower_pollination", "pollination_algorithm"]
        self.p = 0.8  # Switch probability
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Flower Pollination Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize flower population
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
            for i in range(self.population_size):
                if np.random.random() < self.p:
                    # Global pollination (Levy flight)
                    L = self.levy_flight(dimension)
                    population[i] = population[i] + L * (population[i] - best_position)
                else:
                    # Local pollination
                    epsilon = np.random.random()
                    j = np.random.randint(0, self.population_size)
                    k = np.random.randint(0, self.population_size)
                    
                    population[i] = population[i] + epsilon * (population[j] - population[k])
                
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
    
    def levy_flight(self, dimension):
        """Generate Levy flight step"""
        beta = 1.5
        sigma = (np.math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (np.math.gamma((1 + beta) / 2) * beta * (2 ** ((beta - 1) / 2)))) ** (1 / beta)
        
        u = np.random.normal(0, sigma, dimension)
        v = np.random.normal(0, 1, dimension)
        
        step = u / (np.abs(v) ** (1 / beta))
        return step