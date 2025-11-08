"""
Tuna Swarm Optimization (TSO)

Based on: Xie, L., Han, T., Zhou, H., Zhang, Z. R., Han, B., & Tang, A. (2021). 
Tuna swarm optimization: a novel swarm-based metaheuristic algorithm for global optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class TunaSwarmOptimization(BaseOptimizer):
    """
    Tuna Swarm Optimization (TSO)
    
    TSO is inspired by the cooperative foraging behavior of tunas, including
    spiral foraging and parabolic foraging behaviors.
    """
    
    aliases = ["tso", "tuna", "tuna_swarm"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "TunaSwarmOptimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        if X is not None:
            self.dimensions_ = X.shape[1]
            self.lower_bound_ = np.zeros(self.dimensions_)
            self.upper_bound_ = np.ones(self.dimensions_)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                self.dimensions_ = kwargs.get('dimensions', 10)
            if not hasattr(self, 'lower_bound_') or self.lower_bound_ is None:
                lb = kwargs.get('lower_bound', kwargs.get('lb', -10.0))
                self.lower_bound_ = np.full(self.dimensions_, lb) if np.isscalar(lb) else np.array(lb)
            if not hasattr(self, 'upper_bound_') or self.upper_bound_ is None:
                ub = kwargs.get('upper_bound', kwargs.get('ub', 10.0))
                self.upper_bound_ = np.full(self.dimensions_, ub) if np.isscalar(ub) else np.array(ub)
        
        # Initialize tuna population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best tuna
        best_idx = np.argmin(fitness)
        best_tuna = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update parameters
            a = 1 - iteration / self.max_iterations_  # Decreasing factor
            
            for i in range(self.population_size_):
                if np.random.random() < 0.5:
                    # Spiral foraging behavior
                    r = np.random.random()
                    theta = 2 * np.pi * np.random.random()
                    
                    # Calculate spiral movement
                    spiral_x = r * np.cos(theta)
                    spiral_y = r * np.sin(theta)
                    
                    # Update position using spiral
                    new_position = np.zeros(self.dimensions_)
                    for j in range(self.dimensions_):
                        if j % 2 == 0:
                            new_position[j] = population[i][j] + spiral_x * (best_tuna[j] - population[i][j])
                        else:
                            new_position[j] = population[i][j] + spiral_y * (best_tuna[j] - population[i][j])
                
                else:
                    # Parabolic foraging behavior
                    beta = 2 * a * np.random.random() - a
                    
                    # Select random tuna
                    random_idx = np.random.randint(0, self.population_size_)
                    while random_idx == i:
                        random_idx = np.random.randint(0, self.population_size_)
                    
                    # Parabolic movement
                    TF = np.random.randint(1, 3)  # Time factor (1 or 2)
                    new_position = population[i] + TF * beta * (best_tuna - population[random_idx])
                
                # Boundary checking
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(new_position)
                fitnesses.append(new_fitness)
                positions.append(new_position.copy())
                
                # Update if better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_tuna = new_position.copy()
                        best_fitness = new_fitness
                        best_idx = i
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_tuna, best_fitness, global_fitness, local_fitness, local_positions