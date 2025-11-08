"""
SSA-DE Hybrid: Salp Swarm Algorithm + Differential Evolution
=============================================================

Best for: Constrained optimization and balance exploration/exploitation
Combines salp chain movement with DE mutation
"""

import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer


class SSA_DE_Hybrid(BaseOptimizer):
    """SSA-DE Hybrid: Salp Swarm + DE"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 F: float = 0.8, CR: float = 0.9):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F
        self.CR = CR
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # SSA parameter c1: decreases exponentially
            c1 = 2 * np.exp(-(4 * iteration / self.max_iterations)**2)
            
            # SSA phase - salp chain formation
            for i in range(self.population_size):
                if i == 0:  # Leader salp
                    # Leader updates position towards food source
                    for j in range(self.dimensions):
                        c2 = np.random.random()
                        c3 = np.random.random()
                        
                        if c3 < 0.5:
                            self.positions[i, j] = self.gbest_position[j] + c1 * (
                                (self.bounds[j, 1] - self.bounds[j, 0]) * c2 + self.bounds[j, 0])
                        else:
                            self.positions[i, j] = self.gbest_position[j] - c1 * (
                                (self.bounds[j, 1] - self.bounds[j, 0]) * c2 + self.bounds[j, 0])
                else:  # Follower salps
                    # Followers follow the salp in front (Newton's law of motion)
                    self.positions[i] = 0.5 * (self.positions[i] + self.positions[i-1])
                
                # Boundary check
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate
                self.fitness[i] = self.objective_function(self.positions[i])
            
            # DE phase - apply every 3 iterations
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    # Select three random distinct individuals
                    indices = [j for j in range(self.population_size) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    
                    # DE mutation
                    mutant = self.positions[a] + self.F * (self.positions[b] - self.positions[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    
                    # DE crossover
                    trial = np.where(np.random.random(self.dimensions) < self.CR,
                                   mutant, self.positions[i])
                    
                    trial_fitness = self.objective_function(trial)
                    
                    # Selection
                    if trial_fitness < self.fitness[i]:
                        self.positions[i] = trial
                        self.fitness[i] = trial_fitness
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_position, self.gbest_fitness, self.convergence_curve
