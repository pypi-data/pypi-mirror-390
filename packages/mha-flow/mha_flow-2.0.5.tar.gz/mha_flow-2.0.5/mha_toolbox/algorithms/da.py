"""
Dragonfly Algorithm (DA)
=======================

Dragonfly Algorithm inspired by the static and dynamic swarming behaviors
of dragonflies in nature.
"""

import numpy as np
from ..base import BaseOptimizer


class DragonflyAlgorithm(BaseOptimizer):
    """
    Dragonfly Algorithm (DA)
    
    Bio-inspired algorithm based on the swarming behavior of dragonflies
    with separation, alignment, cohesion, food attraction, and enemy distraction.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Dragonfly Algorithm"
        self.aliases = ["da", "dragonfly", "dragonfly_algorithm"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Dragonfly Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize dragonfly population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        velocity = np.random.uniform(-1, 1, (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution (food source)
        best_idx = np.argmin(fitness)
        food_position = population[best_idx].copy()
        food_fitness = fitness[best_idx]
        
        # Track worst solution (enemy)
        worst_idx = np.argmax(fitness)
        enemy_position = population[worst_idx].copy()
        
        # History tracking
        global_fitness = [food_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Algorithm parameters
        w = 0.9  # Inertia weight
        c = 0.1  # Cognitive parameter
        
        for iteration in range(self.max_iterations):
            # Update weights
            s = 2 - iteration * (2 / self.max_iterations)  # Separation weight
            a = 2 - iteration * (2 / self.max_iterations)  # Alignment weight
            c_coh = 2 - iteration * (2 / self.max_iterations)  # Cohesion weight
            f = 2 * np.random.random()  # Food factor
            e = 1 + np.random.random()  # Enemy factor
            
            for i in range(self.population_size):
                # Calculate separation (S)
                S = np.zeros(dimension)
                for j in range(self.population_size):
                    if i != j:
                        distance = np.linalg.norm(population[i] - population[j])
                        if distance < 1.0:  # Radius threshold
                            S += population[i] - population[j]
                
                # Calculate alignment (A)
                A = np.zeros(dimension)
                neighbors = 0
                for j in range(self.population_size):
                    if i != j:
                        distance = np.linalg.norm(population[i] - population[j])
                        if distance < 2.0:  # Neighborhood radius
                            A += velocity[j]
                            neighbors += 1
                if neighbors > 0:
                    A = A / neighbors
                
                # Calculate cohesion (C)
                C = np.zeros(dimension)
                neighbors = 0
                for j in range(self.population_size):
                    if i != j:
                        distance = np.linalg.norm(population[i] - population[j])
                        if distance < 2.0:  # Neighborhood radius
                            C += population[j]
                            neighbors += 1
                if neighbors > 0:
                    C = C / neighbors - population[i]
                
                # Calculate food attraction (F)
                F = food_position - population[i]
                
                # Calculate enemy distraction (E)
                E = enemy_position + population[i]
                
                # Update velocity
                velocity[i] = (w * velocity[i] + 
                              s * S + 
                              a * A + 
                              c_coh * C + 
                              f * F + 
                              e * E)
                
                # Update position
                population[i] = population[i] + velocity[i]
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
                
                # Update velocity bounds
                velocity[i] = np.clip(velocity[i], -2, 2)
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update food position (best solution)
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < food_fitness:
                food_position = population[current_best_idx].copy()
                food_fitness = fitness[current_best_idx]
            
            # Update enemy position (worst solution)
            current_worst_idx = np.argmax(fitness)
            enemy_position = population[current_worst_idx].copy()
            
            # Track progress
            global_fitness.append(food_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return food_position, food_fitness, global_fitness, local_fitness, local_positions