"""
GWO-MFO Hybrid Algorithm
=========================

Hybrid combining Grey Wolf Optimizer (GWO) and Moth-Flame Optimization (MFO).
This hybrid leverages the social hierarchy of GWO with the spiral search of MFO
for improved exploration and exploitation balance.

Strategy:
---------
1. Population is split: 60% GWO wolves, 40% MFO moths
2. GWO wolves follow alpha, beta, delta hierarchy
3. MFO moths perform spiral search around best positions (flames)
4. Information sharing: best positions become flames for MFO
5. Adaptive switching based on iteration progress
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class GWO_MFO_Hybrid(BaseOptimizer):
    """
    GWO-MFO Hybrid Algorithm
    
    Combines the hunting strategy of Grey Wolves with the spiral 
    search mechanism of Moth-Flame Optimization.
    
    Parameters
    ----------
    population_size : int, default=30
        Total number of search agents
    max_iterations : int, default=100
        Maximum number of iterations
    gwo_ratio : float, default=0.6
        Ratio of GWO agents (0.6 = 60% GWO, 40% MFO)
    b : float, default=1.0
        Spiral constant for MFO component
        
    Examples
    --------
    >>> from mha_toolbox.algorithms.hybrid.gwo_mfo_hybrid import GWO_MFO_Hybrid
    >>> optimizer = GWO_MFO_Hybrid(population_size=30, max_iterations=100)
    >>> model = optimizer.fit(X, y, objective_function=knn_fitness)
    """
    
    def __init__(self, population_size=30, max_iterations=100, gwo_ratio=0.6, b=1.0, **kwargs):
        super().__init__(**kwargs)
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.gwo_ratio = gwo_ratio
        self.b = b  # Spiral constant for MFO
        self.algorithm_name_ = "GWO_MFO_Hybrid"
        
        # Split population
        self.n_gwo = int(population_size * gwo_ratio)
        self.n_mfo = population_size - self.n_gwo
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Core hybrid optimization logic
        
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
        
        # Initialize all agents
        positions = np.random.uniform(
            self.lower_bound_,
            self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate fitness
        fitness = np.array([objective_function(pos) for pos in positions])
        
        # Sort by fitness to identify GWO leaders
        sorted_indices = np.argsort(fitness)
        
        # GWO leaders (alpha, beta, delta)
        alpha_pos = positions[sorted_indices[0]].copy()
        alpha_score = fitness[sorted_indices[0]]
        
        beta_pos = positions[sorted_indices[1]].copy() if len(sorted_indices) > 1 else alpha_pos.copy()
        beta_score = fitness[sorted_indices[1]] if len(sorted_indices) > 1 else alpha_score
        
        delta_pos = positions[sorted_indices[2]].copy() if len(sorted_indices) > 2 else beta_pos.copy()
        delta_score = fitness[sorted_indices[2]] if len(sorted_indices) > 2 else beta_score
        
        # MFO flames (top positions)
        n_flames = min(5, self.population_size_)
        flames = positions[sorted_indices[:n_flames]].copy()
        flame_fitness = fitness[sorted_indices[:n_flames]].copy()
        
        # Best overall
        best_position = alpha_pos.copy()
        best_fitness = alpha_score
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            # Linearly decrease 'a' from 2 to 0 (GWO)
            a = 2 - iteration * (2.0 / self.max_iterations_)
            
            iter_fitness = []
            iter_positions = []
            
            # Update GWO agents (first n_gwo agents)
            for i in range(self.n_gwo):
                for j in range(self.dimensions_):
                    # Calculate distances to alpha, beta, delta
                    r1, r2 = np.random.rand(), np.random.rand()
                    A1 = 2 * a * r1 - a
                    C1 = 2 * r2
                    D_alpha = abs(C1 * alpha_pos[j] - positions[i, j])
                    X1 = alpha_pos[j] - A1 * D_alpha
                    
                    r1, r2 = np.random.rand(), np.random.rand()
                    A2 = 2 * a * r1 - a
                    C2 = 2 * r2
                    D_beta = abs(C2 * beta_pos[j] - positions[i, j])
                    X2 = beta_pos[j] - A2 * D_beta
                    
                    r1, r2 = np.random.rand(), np.random.rand()
                    A3 = 2 * a * r1 - a
                    C3 = 2 * r2
                    D_delta = abs(C3 * delta_pos[j] - positions[i, j])
                    X3 = delta_pos[j] - A3 * D_delta
                    
                    # Update position (average of three leaders)
                    positions[i, j] = (X1 + X2 + X3) / 3.0
                
                # Boundary check
                positions[i] = np.clip(positions[i], self.lower_bound_, self.upper_bound_)
            
            # Update MFO agents (remaining agents)
            flame_no = max(1, round(len(flames) - iteration * ((len(flames) - 1) / self.max_iterations_)))
            
            for i in range(self.n_gwo, self.population_size_):
                for j in range(self.dimensions_):
                    # Select flame
                    flame_idx = min(i - self.n_gwo, flame_no - 1)
                    if flame_idx >= len(flames):
                        flame_idx = 0
                    
                    distance_to_flame = abs(flames[flame_idx, j] - positions[i, j])
                    
                    # Convergence constant
                    a_mfo = -1 + iteration * ((-1) / self.max_iterations_)
                    
                    # Spiral parameters
                    r = (a_mfo - 1) * np.random.rand() + 1
                    t = (a_mfo - 1) * np.random.rand() + a_mfo
                    
                    # Spiral update
                    positions[i, j] = (
                        distance_to_flame * np.exp(self.b * t) * np.cos(t * 2 * np.pi) + 
                        flames[flame_idx, j]
                    )
                
                # Boundary check
                positions[i] = np.clip(positions[i], self.lower_bound_, self.upper_bound_)
            
            # Evaluate all agents
            fitness = np.array([objective_function(pos) for pos in positions])
            
            iter_fitness = fitness.tolist()
            iter_positions = [pos.copy() for pos in positions]
            
            # Update GWO leaders
            for i in range(self.population_size_):
                if fitness[i] < alpha_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = alpha_score
                    beta_pos = alpha_pos.copy()
                    alpha_score = fitness[i]
                    alpha_pos = positions[i].copy()
                elif fitness[i] < beta_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = fitness[i]
                    beta_pos = positions[i].copy()
                elif fitness[i] < delta_score:
                    delta_score = fitness[i]
                    delta_pos = positions[i].copy()
            
            # Update flames (best positions for MFO)
            sorted_indices = np.argsort(fitness)
            n_flames = min(5, self.population_size_)
            flames = positions[sorted_indices[:n_flames]].copy()
            flame_fitness = fitness[sorted_indices[:n_flames]].copy()
            
            # Update best overall
            if alpha_score < best_fitness:
                best_position = alpha_pos.copy()
                best_fitness = alpha_score
            
            # Convergence tracking
            global_fitness.append(best_fitness)
            local_fitness.append(iter_fitness)
            local_positions.append(iter_positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions


# Aliases
GWO_MFO = GWO_MFO_Hybrid
GWOMFO = GWO_MFO_Hybrid
