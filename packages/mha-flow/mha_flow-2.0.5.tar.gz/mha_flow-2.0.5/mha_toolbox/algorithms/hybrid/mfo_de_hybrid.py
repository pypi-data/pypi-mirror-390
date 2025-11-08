"""MFO-DE Hybrid: Moth-Flame Optimization + DE"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class MFO_DE_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 b: float = 1.0, F: float = 0.8, CR: float = 0.9):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.b = b
        self.F = F
        self.CR = CR
        
        self.moths = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.moths])
        sorted_indices = np.argsort(self.fitness)
        self.flames = self.moths[sorted_indices].copy()
        self.flame_fitness = self.fitness[sorted_indices].copy()
        self.gbest = self.flames[0].copy()
        self.gbest_fitness = self.flame_fitness[0]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            flame_no = int(self.population_size - iteration * ((self.population_size - 1) / self.max_iterations))
            
            for i in range(self.population_size):
                flame_idx = min(i, flame_no - 1)
                t = np.random.uniform(-1, 1)
                distance = abs(self.flames[flame_idx] - self.moths[i])
                mfo_pos = distance * np.exp(self.b * t) * np.cos(2 * np.pi * t) + self.flames[flame_idx]
                
                indices = [idx for idx in range(self.population_size) if idx != i]
                a, b, c = np.random.choice(indices, 3, replace=False)
                mutant = self.moths[a] + self.F * (self.moths[b] - self.moths[c])
                
                trial = np.where(np.random.rand(self.dimensions) < self.CR, mutant, mfo_pos)
                trial = np.clip(trial, self.bounds[:, 0], self.bounds[:, 1])
                
                trial_fitness = self.objective_function(trial)
                if trial_fitness < self.fitness[i]:
                    self.moths[i] = trial
                    self.fitness[i] = trial_fitness
            
            combined = np.vstack((self.flames, self.moths))
            combined_fitness = np.hstack((self.flame_fitness, self.fitness))
            sorted_indices = np.argsort(combined_fitness)
            self.flames = combined[sorted_indices[:self.population_size]].copy()
            self.flame_fitness = combined_fitness[sorted_indices[:self.population_size]].copy()
            self.gbest = self.flames[0].copy()
            self.gbest_fitness = self.flame_fitness[0]
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest, self.gbest_fitness, self.convergence_curve
