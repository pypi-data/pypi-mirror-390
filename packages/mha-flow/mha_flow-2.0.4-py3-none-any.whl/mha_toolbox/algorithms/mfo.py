"""
Moth-Flame Optimization (MFO) Algorithm
========================================

Paper: Mirjalili, S. (2015). Moth-flame optimization algorithm: A novel 
       nature-inspired heuristic paradigm. Knowledge-based systems, 89, 228-249.

The MFO algorithm mimics the navigation method of moths in nature called 
transverse orientation. Moths fly in the night by maintaining a fixed angle 
with respect to the moon, a very effective mechanism for travelling in a 
straight line for long distances. However, when the source of light is close 
(such as a flame), maintaining a similar angle leads to a spiral flying path.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class MFO(BaseOptimizer):
    """
    Moth-Flame Optimization (MFO)
    
    A nature-inspired algorithm based on moth navigation behavior.
    Moths are attracted to flames (best solutions) in a spiral manner.
    
    Parameters
    ----------
    population_size : int, default=30
        Number of moths (search agents)
    max_iterations : int, default=100
        Maximum number of iterations
    b : float, default=1.0
        Constant for defining spiral shape (typically 1.0)
    
    Examples
    --------
    >>> from mha_toolbox.algorithms.mfo import MFO
    >>> optimizer = MFO(population_size=30, max_iterations=100)
    >>> model = optimizer.fit(X, y, objective_function=knn_fitness)
    """
    
    def __init__(self, population_size=30, max_iterations=100, b=1.0, **kwargs):
        super().__init__(**kwargs)
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.b = b  # Spiral constant
        self.algorithm_name_ = "MothFlameOptimization"
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Core MFO optimization logic
        
        Returns
        -------
        tuple
            (best_solution, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Set dimensions and bounds
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
        
        # Initialize moths randomly in search space
        Moths = np.random.uniform(
            self.lower_bound_, 
            self.upper_bound_, 
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial moths
        Fitness_moths = np.array([objective_function(moth) for moth in Moths])
        
        # Initialize flames as copy of moths
        Flames = Moths.copy()
        Fitness_flames = Fitness_moths.copy()
        
        # Sort flames by fitness
        sorted_indices = np.argsort(Fitness_flames)
        Flames = Flames[sorted_indices]
        Fitness_flames = Fitness_flames[sorted_indices]
        
        # Track best solution
        best_position = Flames[0].copy()
        best_fitness = Fitness_flames[0]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        # Main optimization loop
        for iteration in range(self.max_iterations_):
            # Number of flames (decreases over iterations)
            flame_no = round(self.population_size_ - iteration * ((self.population_size_ - 1) / self.max_iterations_))
            
            iter_fitness = []
            iter_positions = []
            
            # Update moths
            for i in range(self.population_size_):
                for j in range(self.dimensions_):
                    # Distance to corresponding flame
                    if i < flame_no:
                        distance_to_flame = abs(Flames[i, j] - Moths[i, j])
                    else:
                        distance_to_flame = abs(Flames[0, j] - Moths[i, j])
                    
                    # Convergence constant (decreases linearly from -1 to -2)
                    a = -1 + iteration * ((-1) / self.max_iterations_)
                    
                    # Random parameters for spiral
                    r = (a - 1) * np.random.rand() + 1
                    t = (a - 1) * np.random.rand() + a
                    
                    # Update moth position using logarithmic spiral
                    if i < flame_no:
                        Moths[i, j] = (
                            distance_to_flame * np.exp(self.b * t) * np.cos(t * 2 * np.pi) + 
                            Flames[i, j]
                        )
                    else:
                        Moths[i, j] = (
                            distance_to_flame * np.exp(self.b * t) * np.cos(t * 2 * np.pi) + 
                            Flames[0, j]
                        )
                
                # Boundary check
                Moths[i] = np.clip(Moths[i], self.lower_bound_, self.upper_bound_)
            
            # Evaluate new moth positions
            Fitness_moths = np.array([objective_function(moth) for moth in Moths])
            
            # Track for this iteration
            iter_fitness = Fitness_moths.tolist()
            iter_positions = [moth.copy() for moth in Moths]
            
            # Update flames: merge moths and flames, sort, and keep best
            all_positions = np.vstack((Moths, Flames))
            all_fitness = np.concatenate((Fitness_moths, Fitness_flames))
            
            # Sort by fitness
            sorted_indices = np.argsort(all_fitness)
            all_positions = all_positions[sorted_indices]
            all_fitness = all_fitness[sorted_indices]
            
            # Keep top flames
            Flames = all_positions[:self.population_size_].copy()
            Fitness_flames = all_fitness[:self.population_size_].copy()
            
            # Update best solution
            if Fitness_flames[0] < best_fitness:
                best_position = Flames[0].copy()
                best_fitness = Fitness_flames[0]
            
            # Store convergence
            global_fitness.append(best_fitness)
            local_fitness.append(iter_fitness)
            local_positions.append(iter_positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions


# Alias for convenience
MothFlameOptimization = MFO
