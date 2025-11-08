"""
Wind Driven Optimization (WDO) Algorithm

A physics-inspired optimization algorithm based on the motion of air particles
in the atmosphere under wind forces.

Reference:
Bayraktar, Z., Komurcu, M., Bossard, J. A., & Werner, D. H. (2013). 
The wind driven optimization technique and its application in electromagnetics. 
IEEE transactions on antennas and propagation, 61(5), 2745-2757.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class WindDrivenOptimization(BaseOptimizer):
    """
    Wind Driven Optimization (WDO) Algorithm
    
    A physics-inspired optimization algorithm based on atmospheric wind motion.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of air parcels
    max_iterations : int, default=100
        Maximum number of iterations
    pressure_constant : float, default=0.4
        Pressure constant
    gravity_constant : float, default=0.4
        Gravitational constant
    """
    
    aliases = ['wdo', 'wind', 'atmosphere']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 pressure_constant=0.4, gravity_constant=0.4, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.pressure_constant = pressure_constant
        self.gravity_constant = gravity_constant
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.pressure_constant_ = pressure_constant
        self.gravity_constant_ = gravity_constant
        self.algorithm_name_ = "Wind Driven Optimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the optimization algorithm
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
        # Initialize air parcels
        air_parcels = np.random.uniform(lower_bound, upper_bound, 
                                      (self.population_size, dimensions))
        fitness = np.array([objective_func(parcel) for parcel in air_parcels])
        velocities = np.random.uniform(-0.1, 0.1, (self.population_size, dimensions))
        
        best_idx = np.argmin(fitness)
        best_position = air_parcels[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [air_parcels.tolist()]
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Calculate ranking-based velocity update
                ranked_positions = np.argsort(fitness)
                rank = np.where(ranked_positions == i)[0][0] + 1
                
                # Pressure gradient force
                pressure_force = -self.pressure_constant * np.random.random() * \
                               (air_parcels[i] - best_position)
                
                # Gravitational force
                gravity_force = self.gravity_constant * (best_position - air_parcels[i])
                
                # Coriolis force (perpendicular deflection)
                coriolis_constant = 2 * 0.1  # Simplified Coriolis parameter
                if dimensions >= 2:
                    coriolis_force = np.zeros(dimensions)
                    coriolis_force[0] = coriolis_constant * velocities[i, 1] if dimensions > 1 else 0
                    coriolis_force[1] = -coriolis_constant * velocities[i, 0] if dimensions > 1 else 0
                else:
                    coriolis_force = np.zeros(dimensions)
                
                # Friction force
                friction_constant = 0.01
                friction_force = -friction_constant * velocities[i]
                
                # Update velocity
                total_force = pressure_force + gravity_force + coriolis_force + friction_force
                velocities[i] += total_force
                
                # Velocity damping based on rank
                damping_factor = 1 - rank / self.population_size
                velocities[i] *= damping_factor
                
                # Update position
                new_position = air_parcels[i] + velocities[i]
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                if new_fitness < fitness[i]:
                    air_parcels[i] = new_position
                    fitness[i] = new_fitness
                else:
                    # Reduce velocity if no improvement
                    velocities[i] *= 0.9
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = air_parcels[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(air_parcels.tolist())
            
            if hasattr(self, "verbose_") and self.verbose_:
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions