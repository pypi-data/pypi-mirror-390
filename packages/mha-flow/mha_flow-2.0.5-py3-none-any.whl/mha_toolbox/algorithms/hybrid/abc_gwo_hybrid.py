"""
ABC-GWO Hybrid Algorithm
========================
Combines Artificial Bee Colony (ABC) with Grey Wolf Optimizer (GWO)
- First half: ABC's employed & onlooker bee mechanism
- Second half: GWO's hierarchical hunting strategy
"""

import numpy as np
from ...base import BaseOptimizer

class ABC_GWO_Hybrid(BaseOptimizer):
    """
    Artificial Bee Colony + Grey Wolf Optimizer Hybrid
    
    Strengths:
    - ABC: Good exploration through multiple search strategies
    - GWO: Strong exploitation with leadership hierarchy
    - Hybrid: Comprehensive search space coverage
    
    Parameters:
    -----------
    population_size : int, default=30
        Number of bees/wolves
    max_iterations : int, default=100
        Maximum number of iterations
    limit : int, default=20
        Abandonment limit for ABC phase
    """
    
    def __init__(self, population_size=30, max_iterations=100, limit=20, **kwargs):
        super().__init__(population_size, max_iterations, **kwargs)
        self.limit = limit
        self.algorithm_name = "ABC_GWO_Hybrid"
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Execute hybrid ABC-GWO optimization"""
        # Determine dimensions and bounds
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        # Initialize population
        food_sources = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        fitness = np.array([objective_function(fs) for fs in food_sources])
        trials = np.zeros(self.population_size_)
        
        # Track best
        best_idx = np.argmin(fitness)
        best_position = food_sources[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            
            if iteration < self.max_iterations_ // 2:
                # PHASE 1: ABC Algorithm
                
                # Employed Bee Phase
                for i in range(self.population_size_):
                    # Select random neighbor
                    k = np.random.choice([x for x in range(self.population_size_) if x != i])
                    j = np.random.randint(0, dimensions)
                    
                    # Generate new solution
                    phi = np.random.uniform(-1, 1)
                    new_solution = food_sources[i].copy()
                    new_solution[j] = food_sources[i, j] + phi * (food_sources[i, j] - food_sources[k, j])
                    new_solution = np.clip(new_solution, bounds[0], bounds[1])
                    
                    # Evaluate
                    new_fitness = objective_function(new_solution)
                    
                    # Greedy selection
                    if new_fitness < fitness[i]:
                        food_sources[i] = new_solution
                        fitness[i] = new_fitness
                        trials[i] = 0
                    else:
                        trials[i] += 1
                
                # Onlooker Bee Phase
                prob = fitness.max() - fitness + 1e-10
                prob = prob / prob.sum()
                
                for i in range(self.population_size_):
                    # Roulette wheel selection
                    selected = np.random.choice(self.population_size_, p=prob)
                    
                    # Search around selected
                    k = np.random.choice([x for x in range(self.population_size_) if x != selected])
                    j = np.random.randint(0, dimensions)
                    
                    phi = np.random.uniform(-1, 1)
                    new_solution = food_sources[selected].copy()
                    new_solution[j] = food_sources[selected, j] + phi * (
                        food_sources[selected, j] - food_sources[k, j]
                    )
                    new_solution = np.clip(new_solution, bounds[0], bounds[1])
                    
                    new_fitness = objective_function(new_solution)
                    
                    if new_fitness < fitness[selected]:
                        food_sources[selected] = new_solution
                        fitness[selected] = new_fitness
                        trials[selected] = 0
                    else:
                        trials[selected] += 1
                
                # Scout Bee Phase
                for i in range(self.population_size_):
                    if trials[i] > self.limit:
                        food_sources[i] = np.random.uniform(bounds[0], bounds[1], dimensions)
                        fitness[i] = objective_function(food_sources[i])
                        trials[i] = 0
                        
            else:
                # PHASE 2: GWO Algorithm
                a = 2 - iteration * (2.0 / self.max_iterations_)
                
                # Sort and get leaders
                sorted_indices = np.argsort(fitness)
                alpha_pos = food_sources[sorted_indices[0]].copy()
                beta_pos = food_sources[sorted_indices[1]].copy()
                delta_pos = food_sources[sorted_indices[2]].copy()
                
                # Update positions
                for i in range(self.population_size_):
                    for j in range(dimensions):
                        r1, r2 = np.random.rand(2)
                        A1 = 2 * a * r1 - a
                        C1 = 2 * r2
                        D_alpha = abs(C1 * alpha_pos[j] - food_sources[i, j])
                        X1 = alpha_pos[j] - A1 * D_alpha
                        
                        r1, r2 = np.random.rand(2)
                        A2 = 2 * a * r1 - a
                        C2 = 2 * r2
                        D_beta = abs(C2 * beta_pos[j] - food_sources[i, j])
                        X2 = beta_pos[j] - A2 * D_beta
                        
                        r1, r2 = np.random.rand(2)
                        A3 = 2 * a * r1 - a
                        C3 = 2 * r2
                        D_delta = abs(C3 * delta_pos[j] - food_sources[i, j])
                        X3 = delta_pos[j] - A3 * D_delta
                        
                        food_sources[i, j] = (X1 + X2 + X3) / 3.0
                    
                    food_sources[i] = np.clip(food_sources[i], bounds[0], bounds[1])
                    fitness[i] = objective_function(food_sources[i])
            
            # Update best
            best_idx = np.argmin(fitness)
            if fitness[best_idx] < best_fitness:
                best_fitness = fitness[best_idx]
                best_position = food_sources[best_idx].copy()
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(food_sources.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions

