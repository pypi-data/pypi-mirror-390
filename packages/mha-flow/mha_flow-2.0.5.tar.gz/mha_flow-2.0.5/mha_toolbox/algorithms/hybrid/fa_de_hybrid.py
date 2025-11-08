"""
FA-DE Hybrid: Firefly Algorithm + Differential Evolution
========================================================

Best for: Continuous multimodal optimization problems
Combines light-based attraction with differential mutation
"""

import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer


class FA_DE_Hybrid(BaseOptimizer):
    """
    FA-DE Hybrid: Firefly Algorithm + Differential Evolution
    
    Parameters:
    -----------
    population_size : int
        Number of fireflies
    max_iterations : int
        Maximum number of iterations
    alpha : float
        Randomization parameter
    beta0 : float
        Attractiveness at r=0
    gamma : float
        Light absorption coefficient
    F, CR : float
        DE scaling factor and crossover rate
    """
    
    def __init__(self, population_size=50, max_iterations=100,
                 alpha=0.2, beta0=1.0, gamma=1.0, F=0.8, CR=0.9):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "FA-DE Hybrid"
        self.aliases = ["fa_de", "fa_de_hybrid", "firefly_differential"]
        self.alpha = alpha
        self.beta0 = beta0
        self.gamma = gamma
        self.F = F
        self.CR = CR
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Internal optimization method following BaseOptimizer interface"""
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        # Initialize fireflies
        positions = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        fitness = np.array([objective_function(ind) for ind in positions])
        light_intensity = 1.0 / (1.0 + fitness)
        
        # Best solution
        gbest_idx = np.argmin(fitness)
        gbest_position = positions[gbest_idx].copy()
        gbest_fitness = fitness[gbest_idx]
        
        global_fitness = [gbest_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [positions.copy()]
        
        for iteration in range(self.max_iterations_):
            # Firefly phase - light-based movement
            for i in range(self.population_size_):
                for j in range(self.population_size_):
                    if light_intensity[j] > light_intensity[i]:
                        # Calculate Euclidean distance
                        r = np.linalg.norm(positions[i] - positions[j])
                        
                        # Attractiveness decreases exponentially with distance
                        beta = self.beta0 * np.exp(-self.gamma * r**2)
                        
                        # Move firefly i towards brighter firefly j
                        random_vector = np.random.random(dimensions) - 0.5
                        positions[i] += (beta * (positions[j] - positions[i]) +
                                        self.alpha * random_vector)
                        
                        # Boundary constraint
                        positions[i] = np.clip(positions[i], bounds[0], bounds[1])
                
                # Evaluate new position
                fitness[i] = objective_function(positions[i])
                light_intensity[i] = 1.0 / (1.0 + fitness[i])
            
            # DE phase - apply differential evolution every 4 iterations
            if iteration % 4 == 0:
                for i in range(self.population_size_):
                    # Select three random distinct individuals
                    indices = [j for j in range(self.population_size_) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    
                    # DE mutation: v = x_a + F * (x_b - x_c)
                    mutant = positions[a] + self.F * (positions[b] - positions[c])
                    mutant = np.clip(mutant, bounds[0], bounds[1])
                    
                    # DE crossover: binomial crossover
                    trial = np.where(np.random.random(dimensions) < self.CR,
                                   mutant, positions[i])
                    
                    # Evaluate trial solution
                    trial_fitness = objective_function(trial)
                    
                    # Greedy selection
                    if trial_fitness < fitness[i]:
                        positions[i] = trial
                        fitness[i] = trial_fitness
                        light_intensity[i] = 1.0 / (1.0 + trial_fitness)
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < gbest_fitness:
                gbest_idx = current_best_idx
                gbest_position = positions[current_best_idx].copy()
                gbest_fitness = fitness[current_best_idx]
            
            # Adaptive alpha reduction (cooling schedule)
            self.alpha *= 0.97
            
            global_fitness.append(gbest_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(positions.copy())
        
        return gbest_position, gbest_fitness, global_fitness, local_fitness, local_positions

