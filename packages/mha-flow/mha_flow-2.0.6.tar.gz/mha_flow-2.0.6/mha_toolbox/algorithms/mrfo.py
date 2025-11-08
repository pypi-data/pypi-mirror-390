"""
Manta Ray Foraging Optimization (MRFO)

Based on: Zhao, W., Zhang, Z., & Wang, L. (2020). Manta ray foraging optimization: 
An effective bio-inspired optimizer for engineering applications.
"""

import numpy as np
from ..base import BaseOptimizer


class MantaRayForagingOptimization(BaseOptimizer):
    """
    Manta Ray Foraging Optimization (MRFO)
    
    MRFO is inspired by the foraging behavior of manta rays, including
    chain foraging, cyclone foraging, and somersault foraging.
    """
    
    aliases = ["mrfo", "manta_ray", "manta"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "MantaRayForagingOptimization"
    
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
        
        # Initialize manta ray population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best manta ray
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update parameters
            beta = 2 * np.exp(np.random.random() * (self.max_iterations_ - iteration) / self.max_iterations_) * np.sin(2 * np.pi * np.random.random())
            
            # Sort population by fitness
            sorted_indices = np.argsort(fitness)
            
            for i in range(self.population_size_):
                if np.random.random() < 0.4:  # Chain foraging (40%)
                    if i == 0:  # First manta ray
                        new_position = population[i] + np.random.random(self.dimensions_) * (best_solution - population[i]) + beta * (best_solution - population[i])
                    else:  # Following manta rays
                        new_position = population[i] + np.random.random(self.dimensions_) * (population[sorted_indices[i-1]] - population[i]) + beta * (best_solution - population[i])
                
                elif np.random.random() < 0.7:  # Cyclone foraging (30%)
                    if i == 0:  # First manta ray
                        new_position = best_solution + np.random.random(self.dimensions_) * (best_solution - population[i]) + beta * (best_solution - population[i])
                    else:  # Following manta rays
                        new_position = best_solution + np.random.random(self.dimensions_) * (population[sorted_indices[i-1]] - population[i]) + beta * (best_solution - population[i])
                
                else:  # Somersault foraging (30%)
                    # Calculate center of mass
                    S = np.random.random() * population[i]
                    new_position = population[i] + 0.2 * (np.random.random(self.dimensions_) - 0.5) * 2 * S
                
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
                        best_solution = new_position.copy()
                        best_fitness = new_fitness
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions