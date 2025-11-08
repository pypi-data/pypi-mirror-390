"""
GWO-WOA Hybrid Algorithm
========================
Combines Grey Wolf Optimizer (GWO) with Whale Optimization Algorithm (WOA)
- First half: GWO's hierarchical social structure
- Second half: WOA's bubble-net attacking mechanism
"""

import numpy as np
from ...base import BaseOptimizer

class GWO_WOA_Hybrid(BaseOptimizer):
    """
    Grey Wolf Optimizer + Whale Optimization Algorithm Hybrid
    
    Strengths:
    - GWO: Good exploitation through hierarchical social structure
    - WOA: Strong exploration with spiral updating
    - Hybrid: Balanced exploration-exploitation
    
    Parameters:
    -----------
    population_size : int, default=30
        Number of search agents
    max_iterations : int, default=100
        Maximum number of iterations
    """
    
    def __init__(self, population_size=30, max_iterations=100, **kwargs):
        super().__init__(population_size, max_iterations, **kwargs)
        self.algorithm_name = "GWO_WOA_Hybrid"
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Execute hybrid GWO-WOA optimization"""
        # Determine dimensions and bounds
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        # Initialize population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # GWO: Track alpha, beta, delta wolves
        sorted_indices = np.argsort(fitness)
        alpha_pos = population[sorted_indices[0]].copy()
        beta_pos = population[sorted_indices[1]].copy()
        delta_pos = population[sorted_indices[2]].copy()
        
        # Track best
        best_position = alpha_pos.copy()
        best_fitness = fitness[sorted_indices[0]]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            a = 2 - iteration * (2.0 / self.max_iterations_)  # Decreasing a
            
            # Determine which phase we're in
            if iteration < self.max_iterations_ // 2:
                # PHASE 1: GWO
                for i in range(self.population_size_):
                    for j in range(dimensions):
                        r1, r2 = np.random.rand(2)
                        A1 = 2 * a * r1 - a
                        C1 = 2 * r2
                        
                        D_alpha = abs(C1 * alpha_pos[j] - population[i, j])
                        X1 = alpha_pos[j] - A1 * D_alpha
                        
                        r1, r2 = np.random.rand(2)
                        A2 = 2 * a * r1 - a
                        C2 = 2 * r2
                        
                        D_beta = abs(C2 * beta_pos[j] - population[i, j])
                        X2 = beta_pos[j] - A2 * D_beta
                        
                        r1, r2 = np.random.rand(2)
                        A3 = 2 * a * r1 - a
                        C3 = 2 * r2
                        
                        D_delta = abs(C3 * delta_pos[j] - population[i, j])
                        X3 = delta_pos[j] - A3 * D_delta
                        
                        # Update position (average of three leaders)
                        population[i, j] = (X1 + X2 + X3) / 3.0
                
            else:
                # PHASE 2: WOA
                for i in range(self.population_size_):
                    r = np.random.rand()
                    A = 2 * a * np.random.rand() - a
                    C = 2 * np.random.rand()
                    b = 1  # Spiral shape parameter
                    l = np.random.uniform(-1, 1)
                    p = np.random.rand()
                    
                    if p < 0.5:
                        if abs(A) < 1:
                            # Encircling prey
                            D = abs(C * best_position - population[i])
                            population[i] = best_position - A * D
                        else:
                            # Search for prey (exploration)
                            rand_idx = np.random.randint(0, self.population_size_)
                            X_rand = population[rand_idx]
                            D = abs(C * X_rand - population[i])
                            population[i] = X_rand - A * D
                    else:
                        # Spiral updating position
                        D_prime = abs(best_position - population[i])
                        population[i] = D_prime * np.exp(b * l) * np.cos(2 * np.pi * l) + best_position
            
            # Apply bounds
            population = np.clip(population, bounds[0], bounds[1])
            
            # Evaluate fitness
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update leaders
            sorted_indices = np.argsort(fitness)
            alpha_pos = population[sorted_indices[0]].copy()
            beta_pos = population[sorted_indices[1]].copy()
            delta_pos = population[sorted_indices[2]].copy()
            
            # Update best
            if fitness[sorted_indices[0]] < best_fitness:
                best_fitness = fitness[sorted_indices[0]]
                best_position = population[sorted_indices[0]].copy()
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions

