"""Artificial Fish Swarm Algorithm (AFSA)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class ArtificialFishSwarmAlgorithm(BaseOptimizer):
    """Artificial Fish Swarm Algorithm - Li (2002)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 visual: float = 0.3, step: float = 0.1, try_number: int = 10):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.visual = visual
        self.step = step
        self.try_number = try_number
        
        self.fish = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(f) for f in self.fish])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.fish[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def _find_neighbors(self, idx: int) -> int:
        """Find best neighbor within visual range"""
        neighbors = []
        for j in range(self.population_size):
            if j != idx and np.linalg.norm(self.fish[j] - self.fish[idx]) < self.visual:
                neighbors.append(j)
        if neighbors:
            return min(neighbors, key=lambda x: self.fitness[x])
        return idx
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Prey behavior: move towards best neighbor
                best_neighbor_idx = self._find_neighbors(i)
                
                if self.fitness[best_neighbor_idx] < self.fitness[i]:
                    direction = self.fish[best_neighbor_idx] - self.fish[i]
                    norm = np.linalg.norm(direction)
                    if norm > 1e-10:
                        self.fish[i] = self.fish[i] + self.step * direction / norm * np.random.rand()
                else:
                    # Random move if no better neighbor
                    self.fish[i] = self.fish[i] + self.step * np.random.uniform(-1, 1, self.dimensions)
                
                # Clip to bounds
                self.fish[i] = np.clip(self.fish[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.fish[i])
                
                if self.fitness[i] < self.best_fitness:
                    self.best_solution = self.fish[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
