"""
Hunger Games Search (HGS)
========================

Hunger Games Search inspired by the cooperative and competitive
behaviors in hunger games.
"""

import numpy as np
from ..base import BaseOptimizer


class HungerGamesSearch(BaseOptimizer):
    """
    Hunger Games Search (HGS)
    
    Algorithm based on the cooperation and competition behaviors
    during hunger games for survival.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Hunger Games Search"
        self.aliases = ["hgs", "hunger_games", "hunger_games_search"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Hunger Games Search
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize population
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
            # Calculate hunger value for each individual
            shrink = 2 * (1 - iteration / self.max_iterations)
            
            # Sort population by fitness
            sorted_indices = np.argsort(fitness)
            sorted_population = population[sorted_indices]
            sorted_fitness = fitness[sorted_indices]
            
            # Calculate hunger for each individual
            hunger = np.zeros(self.population_size)
            for i in range(self.population_size):
                if i == 0:
                    hunger[i] = 0  # Best individual has no hunger
                else:
                    hunger[i] = (sorted_fitness[i] - sorted_fitness[0]) / (sorted_fitness[-1] - sorted_fitness[0] + 1e-10)
            
            for i in range(self.population_size):
                # Update position based on hunger games rules
                r = np.random.random()
                
                if r < shrink:
                    # Exploitation: Move towards better solution
                    better_idx = np.random.randint(0, max(1, i))
                    worse_idx = np.random.randint(i + 1, self.population_size) if i < self.population_size - 1 else i
                    
                    E = np.random.random() * 2 * shrink
                    
                    population[sorted_indices[i]] = (sorted_population[better_idx] + 
                                                    E * (sorted_population[better_idx] - sorted_population[worse_idx]))
                else:
                    # Exploration: Random search
                    W1 = hunger[i] * (self.population_size / (i + 1))
                    W2 = (1 - np.exp(-abs(hunger[i] - np.mean(hunger)))) * np.random.random() * 2
                    
                    if np.random.random() < 0.5:
                        population[sorted_indices[i]] = (sorted_population[0] * (1 - W1 * np.random.random()) + 
                                                        W2 * np.random.randn(dimension))
                    else:
                        population[sorted_indices[i]] = (sorted_population[0] * (1 + W1 * np.random.random()) + 
                                                        W2 * np.random.randn(dimension))
                
                # Apply bounds
                population[sorted_indices[i]] = np.clip(population[sorted_indices[i]], bounds[0], bounds[1])
            
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