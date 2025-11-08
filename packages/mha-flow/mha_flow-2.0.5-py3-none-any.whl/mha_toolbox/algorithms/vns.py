"""
Variable Neighborhood Search (VNS) Algorithm

A local search metaheuristic that systematically changes neighborhood
structures to escape from local optima.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class VariableNeighborhoodSearch(BaseOptimizer):
    """Variable Neighborhood Search (VNS) Algorithm"""
    
    aliases = ['vns', 'neighborhood', 'local_search']
    
    def __init__(self, population_size=1, max_iterations=100, k_max=5, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = max(1, population_size)
        self.max_iterations = max_iterations
        self.k_max = k_max
        self.population_size_ = self.population_size
        self.max_iterations_ = max_iterations
        self.k_max_ = k_max
        self.algorithm_name_ = "Variable Neighborhood Search"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the VNS optimization algorithm
        """
        # Use trailing underscore attributes
        if X is not None:
            dimensions = X.shape[1]
            lower_bound = np.zeros(dimensions)
            upper_bound = np.ones(dimensions)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                raise ValueError("Dimensions must be specified")
            dimensions = self.dimensions_
            lower_bound = self.lower_bound_
            upper_bound = self.upper_bound_
            
        objective_func = objective_function
        # Initialize solution
        current_solution = np.random.uniform(lower_bound, upper_bound, dimensions)
        current_fitness = objective_func(current_solution)
        
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness_history = [current_fitness]
        local_positions = [current_solution.tolist()]
        
        for iteration in range(self.max_iterations):
            k = 1
            while k <= self.k_max:
                # Shaking phase - generate solution in k-th neighborhood
                neighborhood_size = k * 0.1
                perturbation = np.random.normal(0, neighborhood_size, dimensions)
                shaken_solution = current_solution + perturbation
                shaken_solution = np.clip(shaken_solution, lower_bound, upper_bound)
                
                # Local search phase
                local_solution = self._local_search(shaken_solution, objective_func, 
                                                  lower_bound, upper_bound, k)
                local_fitness = objective_func(local_solution)
                
                # Move or not
                if local_fitness < current_fitness:
                    current_solution = local_solution
                    current_fitness = local_fitness
                    k = 1  # Restart with first neighborhood
                    
                    if local_fitness < best_fitness:
                        best_solution = local_solution.copy()
                        best_fitness = local_fitness
                else:
                    k += 1  # Try next neighborhood
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness_history.append(best_fitness)
            local_positions.append(best_solution.tolist())
        
        return best_solution, best_fitness, global_fitness, local_fitness_history, local_positions
    
    def _local_search(self, solution, objective_func, lower_bound, upper_bound, k):
        """Perform local search around given solution"""
        current = solution.copy()
        current_fitness = objective_func(current)
        
        # Number of local search steps
        local_steps = 20 // k
        
        for _ in range(local_steps):
            # Generate neighbor
            step_size = 0.05 / k
            neighbor = current + np.random.normal(0, step_size, len(current))
            neighbor = np.clip(neighbor, lower_bound, upper_bound)
            neighbor_fitness = objective_func(neighbor)
            
            if neighbor_fitness < current_fitness:
                current = neighbor
                current_fitness = neighbor_fitness
        
        return current