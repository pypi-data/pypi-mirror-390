"""Central Force Optimization (CFO) - Formato (2007)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class CentralForceOptimization(BaseOptimizer):
    """Central Force Optimization - Formato (2007)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 alpha: float = 1.0, beta: float = 1.0):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta = beta
        
        self.probes = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(p) for p in self.probes])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.probes[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Calculate forces and move each probe
            for i in range(self.population_size):
                force = np.zeros(self.dimensions)
                
                # Calculate force from all other probes
                for j in range(self.population_size):
                    if i != j:
                        r = np.linalg.norm(self.probes[j] - self.probes[i]) + 1e-10
                        
                        # Attractive force if j is better, repulsive otherwise
                        if self.fitness[j] < self.fitness[i]:
                            direction = self.probes[j] - self.probes[i]
                            magnitude = self.alpha * (self.fitness[i] - self.fitness[j]) / (r ** self.beta)
                            force += magnitude * direction / r
                        else:
                            direction = self.probes[i] - self.probes[j]
                            magnitude = self.alpha * (self.fitness[j] - self.fitness[i]) / (r ** self.beta)
                            force += magnitude * direction / r
                
                # Adaptive step size (decreases over iterations)
                step_size = 0.1 * (self.bounds[:, 1] - self.bounds[:, 0]) / (iteration + 1)
                
                # Normalize force and apply step
                force_norm = np.linalg.norm(force)
                if force_norm > 1e-10:
                    self.probes[i] = self.probes[i] + step_size * force / force_norm
                
                # Clip to bounds
                self.probes[i] = np.clip(self.probes[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate fitness
                self.fitness[i] = self.objective_function(self.probes[i])
                
                if self.fitness[i] < self.best_fitness:
                    self.best_solution = self.probes[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
