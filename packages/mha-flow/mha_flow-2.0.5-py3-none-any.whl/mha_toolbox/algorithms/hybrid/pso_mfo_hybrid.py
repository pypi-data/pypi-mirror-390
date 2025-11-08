"""
PSO-MFO Hybrid Algorithm
=========================

Hybrid combining Particle Swarm Optimization (PSO) and Moth-Flame Optimization (MFO).
This hybrid uses PSO's velocity-based movement with MFO's spiral search pattern
for enhanced exploration-exploitation balance.

Strategy:
---------
1. Particles maintain velocity (PSO) but also perform spiral search (MFO)
2. Adaptive switching: early iterations favor PSO exploration, later favor MFO exploitation
3. Best positions serve as both pbest/gbest (PSO) and flames (MFO)
4. Hybrid update equation combines both mechanisms
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class PSO_MFO_Hybrid(BaseOptimizer):
    """
    PSO-MFO Hybrid Algorithm
    
    Combines PSO's social learning with MFO's spiral search mechanism.
    
    Parameters
    ----------
    population_size : int, default=30
        Number of search agents (particles/moths)
    max_iterations : int, default=100
        Maximum number of iterations
    w : float, default=0.9
        Inertia weight for PSO (decreases linearly)
    c1 : float, default=2.0
        Cognitive coefficient (personal best)
    c2 : float, default=2.0
        Social coefficient (global best)
    b : float, default=1.0
        Spiral constant for MFO component
        
    Examples
    --------
    >>> from mha_toolbox.algorithms.hybrid.pso_mfo_hybrid import PSO_MFO_Hybrid
    >>> optimizer = PSO_MFO_Hybrid(population_size=30, max_iterations=100)
    >>> model = optimizer.fit(X, y, objective_function=knn_fitness)
    """
    
    def __init__(self, population_size=30, max_iterations=100, w=0.9, c1=2.0, c2=2.0, b=1.0, **kwargs):
        super().__init__(**kwargs)
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.w_max = w  # Maximum inertia weight
        self.w_min = 0.4  # Minimum inertia weight
        self.c1 = c1
        self.c2 = c2
        self.b = b  # Spiral constant
        self.algorithm_name_ = "PSO_MFO_Hybrid"
        
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
        
        # Positions
        positions = np.random.uniform(
            self.lower_bound_,
            self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Velocities (PSO component)
        velocity_range = (self.upper_bound_ - self.lower_bound_) * 0.1
        velocities = np.random.uniform(
            -velocity_range,
            velocity_range,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial positions
        fitness = np.array([objective_function(pos) for pos in positions])
        
        # Personal best (pbest) for each particle
        pbest_positions = positions.copy()
        pbest_fitness = fitness.copy()
        
        # Global best (gbest)
        best_idx = np.argmin(fitness)
        gbest_position = positions[best_idx].copy()
        gbest_fitness = fitness[best_idx]
        
        # Flames for MFO component (top 3 positions)
        sorted_indices = np.argsort(fitness)
        n_flames = min(3, self.population_size_)
        flames = positions[sorted_indices[:n_flames]].copy()
        flame_fitness = fitness[sorted_indices[:n_flames]].copy()
        
        # Best overall
        best_position = gbest_position.copy()
        best_fitness = gbest_fitness
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            # Adaptive inertia weight (decreases linearly)
            w = self.w_max - (self.w_max - self.w_min) * (iteration / self.max_iterations_)
            
            # Adaptive probability: favor PSO early, MFO later
            pso_prob = 1 - (iteration / self.max_iterations_)  # Decreases from 1 to 0
            
            iter_fitness = []
            iter_positions = []
            
            # Update each particle/moth
            for i in range(self.population_size_):
                if np.random.rand() < pso_prob:
                    # PSO UPDATE
                    r1, r2 = np.random.rand(self.dimensions_), np.random.rand(self.dimensions_)
                    
                    # Update velocity
                    cognitive = self.c1 * r1 * (pbest_positions[i] - positions[i])
                    social = self.c2 * r2 * (gbest_position - positions[i])
                    velocities[i] = w * velocities[i] + cognitive + social
                    
                    # Update position
                    positions[i] = positions[i] + velocities[i]
                else:
                    # MFO UPDATE (spiral search)
                    # Select flame based on rank
                    flame_idx = min(i, len(flames) - 1)
                    
                    for j in range(self.dimensions_):
                        distance_to_flame = abs(flames[flame_idx, j] - positions[i, j])
                        
                        # Convergence constant
                        a = -1 + iteration * ((-1) / self.max_iterations_)
                        
                        # Spiral parameters
                        r = (a - 1) * np.random.rand() + 1
                        t = (a - 1) * np.random.rand() + a
                        
                        # Spiral update
                        positions[i, j] = (
                            distance_to_flame * np.exp(self.b * t) * np.cos(t * 2 * np.pi) + 
                            flames[flame_idx, j]
                        )
                
                # Boundary check
                positions[i] = np.clip(positions[i], self.lower_bound_, self.upper_bound_)
                
                # Limit velocity
                max_velocity = (self.upper_bound_ - self.lower_bound_) * 0.2
                velocities[i] = np.clip(velocities[i], -max_velocity, max_velocity)
            
            # Evaluate all particles
            fitness = np.array([objective_function(pos) for pos in positions])
            
            iter_fitness = fitness.tolist()
            iter_positions = [pos.copy() for pos in positions]
            
            # Update personal best
            improved = fitness < pbest_fitness
            pbest_positions[improved] = positions[improved].copy()
            pbest_fitness[improved] = fitness[improved]
            
            # Update global best
            best_idx = np.argmin(fitness)
            if fitness[best_idx] < gbest_fitness:
                gbest_position = positions[best_idx].copy()
                gbest_fitness = fitness[best_idx]
            
            # Update flames (best positions for MFO component)
            sorted_indices = np.argsort(fitness)
            n_flames = min(3, self.population_size_)
            flames = positions[sorted_indices[:n_flames]].copy()
            flame_fitness = fitness[sorted_indices[:n_flames]].copy()
            
            # Update best overall
            if gbest_fitness < best_fitness:
                best_position = gbest_position.copy()
                best_fitness = gbest_fitness
            
            # Convergence tracking
            global_fitness.append(best_fitness)
            local_fitness.append(iter_fitness)
            local_positions.append(iter_positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions


# Aliases
PSO_MFO = PSO_MFO_Hybrid
PSOMFO = PSO_MFO_Hybrid
