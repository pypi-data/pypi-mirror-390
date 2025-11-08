"""
Antlion Optimizer (ALO)
======================

Antlion Optimizer inspired by the hunting mechanism of antlions
in nature and their interaction with ants.
"""

import numpy as np
from ..base import BaseOptimizer


class AntlionOptimizer(BaseOptimizer):
    """
    Antlion Optimizer (ALO)
    
    Bio-inspired algorithm based on the hunting behavior of antlions
    and the random walk of ants.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Antlion Optimizer"
        self.aliases = ["alo_new", "antlion_optimizer", "antlion_new"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Antlion Optimizer
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize ants and antlions
        ants = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        antlions = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        
        # Evaluate fitness
        ant_fitness = np.array([objective_function(ant) for ant in ants])
        antlion_fitness = np.array([objective_function(antlion) for antlion in antlions])
        
        # Track elite antlion (best solution)
        elite_idx = np.argmin(antlion_fitness)
        elite_antlion = antlions[elite_idx].copy()
        elite_fitness = antlion_fitness[elite_idx]
        
        # History tracking
        global_fitness = [elite_fitness]
        local_fitness = [ant_fitness.copy()]
        local_positions = [ants.copy()]
        
        for iteration in range(self.max_iterations):
            # Sort antlions based on fitness
            sorted_indices = np.argsort(antlion_fitness)
            antlions = antlions[sorted_indices]
            antlion_fitness = antlion_fitness[sorted_indices]
            
            # Update ants positions
            for i in range(self.population_size):
                # Select antlion using roulette wheel
                antlion_idx = self.roulette_wheel_selection(antlion_fitness)
                selected_antlion = antlions[antlion_idx]
                
                # Random walk around selected antlion
                c = 2 * np.exp(iteration / self.max_iterations)  # Spiral constant
                I = 1 - iteration / self.max_iterations  # Intensity of exploitation
                
                # Random walk bounds
                lb = selected_antlion - I * (bounds[1] - bounds[0]) / 2
                ub = selected_antlion + I * (bounds[1] - bounds[0]) / 2
                
                # Ensure bounds are within original bounds
                lb = np.maximum(lb, bounds[0])
                ub = np.minimum(ub, bounds[1])
                
                # Random walk
                ant_walk = self.random_walk(dimension, self.max_iterations, lb, ub)
                ants[i] = ant_walk[iteration]
                
                # Random walk around elite
                elite_lb = elite_antlion - I * (bounds[1] - bounds[0]) / 2
                elite_ub = elite_antlion + I * (bounds[1] - bounds[0]) / 2
                elite_lb = np.maximum(elite_lb, bounds[0])
                elite_ub = np.minimum(elite_ub, bounds[1])
                
                elite_walk = self.random_walk(dimension, self.max_iterations, elite_lb, elite_ub)
                
                # Combine walks
                ants[i] = (ants[i] + elite_walk[iteration]) / 2
                
                # Apply bounds
                ants[i] = np.clip(ants[i], bounds[0], bounds[1])
            
            # Evaluate ants
            ant_fitness = np.array([objective_function(ant) for ant in ants])
            
            # Replace antlions with better ants
            for i in range(self.population_size):
                if ant_fitness[i] < antlion_fitness[i]:
                    antlions[i] = ants[i].copy()
                    antlion_fitness[i] = ant_fitness[i]
            
            # Update elite antlion
            current_best_idx = np.argmin(antlion_fitness)
            if antlion_fitness[current_best_idx] < elite_fitness:
                elite_antlion = antlions[current_best_idx].copy()
                elite_fitness = antlion_fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(elite_fitness)
            local_fitness.append(ant_fitness.copy())
            local_positions.append(ants.copy())
        
        return elite_antlion, elite_fitness, global_fitness, local_fitness, local_positions
    
    def roulette_wheel_selection(self, fitness):
        """Roulette wheel selection for antlion selection"""
        # Convert to maximization problem
        max_fitness = np.max(fitness)
        weights = max_fitness - fitness + 1e-10
        
        # Calculate probabilities
        probabilities = weights / np.sum(weights)
        
        # Select based on probabilities
        cumulative_prob = np.cumsum(probabilities)
        random_value = np.random.random()
        
        for i, cum_prob in enumerate(cumulative_prob):
            if random_value <= cum_prob:
                return i
        
        return len(fitness) - 1
    
    def random_walk(self, dimension, max_iter, lb, ub):
        """Generate random walk for ant movement"""
        walk = np.zeros((max_iter, dimension))
        walk[0] = np.random.uniform(lb, ub)
        
        for i in range(1, max_iter):
            step = np.random.choice([-1, 1], dimension) * np.random.random(dimension)
            walk[i] = walk[i-1] + step
            walk[i] = np.clip(walk[i], lb, ub)
        
        return walk