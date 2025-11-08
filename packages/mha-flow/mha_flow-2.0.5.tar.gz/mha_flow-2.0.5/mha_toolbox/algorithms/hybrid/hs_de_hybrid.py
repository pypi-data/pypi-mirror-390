"""HS-DE Hybrid: Harmony Search + Differential Evolution"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class HS_DE_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 hmcr: float = 0.9, par: float = 0.3, bw: float = 0.01,
                 F: float = 0.8, CR: float = 0.9):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.hmcr = hmcr
        self.par = par
        self.bw = bw
        self.F = F
        self.CR = CR
        
        self.harmony_memory = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.harmony_memory])
        best_idx = np.argmin(self.fitness)
        self.best_harmony = self.harmony_memory[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            new_harmony = np.zeros(self.dimensions)
            
            for j in range(self.dimensions):
                if np.random.rand() < self.hmcr:
                    idx = np.random.randint(self.population_size)
                    new_harmony[j] = self.harmony_memory[idx, j]
                    
                    if np.random.rand() < self.par:
                        new_harmony[j] += self.bw * np.random.randn()
                else:
                    new_harmony[j] = np.random.uniform(self.bounds[j, 0], self.bounds[j, 1])
            
            new_harmony = np.clip(new_harmony, self.bounds[:, 0], self.bounds[:, 1])
            new_fitness = self.objective_function(new_harmony)
            
            worst_idx = np.argmax(self.fitness)
            if new_fitness < self.fitness[worst_idx]:
                self.harmony_memory[worst_idx] = new_harmony
                self.fitness[worst_idx] = new_fitness
            
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    idxs = [idx for idx in range(self.population_size) if idx != i]
                    a, b, c = np.random.choice(idxs, 3, replace=False)
                    
                    mutant = self.harmony_memory[a] + self.F * (self.harmony_memory[b] - self.harmony_memory[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    
                    trial = np.where(np.random.rand(self.dimensions) < self.CR, mutant, self.harmony_memory[i])
                    trial_fitness = self.objective_function(trial)
                    
                    if trial_fitness < self.fitness[i]:
                        self.harmony_memory[i] = trial
                        self.fitness[i] = trial_fitness
            
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.best_fitness:
                self.best_harmony = self.harmony_memory[best_idx].copy()
                self.best_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_harmony, self.best_fitness, self.convergence_curve
