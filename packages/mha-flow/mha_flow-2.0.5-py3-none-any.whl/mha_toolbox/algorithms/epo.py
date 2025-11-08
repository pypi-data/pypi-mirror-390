"""
Emperor Penguin Optimizer (EPO)
==============================

Emperor Penguin Optimizer inspired by the huddling behavior
of emperor penguins in Antarctica.
"""

import numpy as np
from ..base import BaseOptimizer


class EmperorPenguinOptimizer(BaseOptimizer):
    """
    Emperor Penguin Optimizer (EPO)
    
    Bio-inspired algorithm based on the social behavior and
    huddling strategies of emperor penguins.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Emperor Penguin Optimizer"
        self.aliases = ["epo", "emperor_penguin", "penguin_optimizer"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Emperor Penguin Optimizer
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize penguin population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution (emperor penguin)
        best_idx = np.argmin(fitness)
        emperor_position = population[best_idx].copy()
        emperor_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [emperor_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Algorithm parameters
        T0 = -20  # Initial temperature
        Tmin = -60  # Minimum temperature
        
        for iteration in range(self.max_iterations):
            # Temperature decreases over time
            T = T0 - (T0 - Tmin) * (iteration / self.max_iterations)
            
            # Grid formation coefficient
            grid_coeff = np.abs(T) / 60  # Normalize temperature
            
            # Penguin grid formation and movement
            for i in range(self.population_size):
                # Determine penguin's role
                if fitness[i] == emperor_fitness:
                    # Emperor penguin stays in center
                    continue
                
                # Calculate distance to emperor
                distance_to_emperor = np.linalg.norm(population[i] - emperor_position)
                
                # Huddling behavior
                if distance_to_emperor > 1.0:  # Far from emperor
                    # Move towards emperor (center of huddle)
                    direction = emperor_position - population[i]
                    step_size = np.random.random() * grid_coeff
                    population[i] = population[i] + step_size * direction
                else:
                    # Close to emperor - maintain position with small random movement
                    population[i] = population[i] + np.random.uniform(-0.1, 0.1, dimension)
                
                # Wind effect (random disturbance)
                wind_effect = np.random.normal(0, 0.01, dimension)
                population[i] = population[i] + wind_effect
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update emperor penguin
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < emperor_fitness:
                emperor_position = population[current_best_idx].copy()
                emperor_fitness = fitness[current_best_idx]
            
            # Penguin migration (exploration phase)
            if iteration % 10 == 0:  # Every 10 iterations
                # Some penguins explore new areas
                num_explorers = max(1, self.population_size // 10)
                explorer_indices = np.random.choice(self.population_size, num_explorers, replace=False)
                
                for idx in explorer_indices:
                    population[idx] = np.random.uniform(bounds[0], bounds[1], dimension)
            
            # Track progress
            global_fitness.append(emperor_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return emperor_position, emperor_fitness, global_fitness, local_fitness, local_positions