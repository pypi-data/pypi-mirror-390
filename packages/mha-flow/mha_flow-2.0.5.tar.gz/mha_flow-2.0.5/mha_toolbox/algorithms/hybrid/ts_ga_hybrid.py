"""TS-GA Hybrid: Tabu Search + GA"""
import numpy as np
from typing import Callable, Tuple
from collections import deque
from mha_toolbox.base import BaseOptimizer

class TS_GA_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 tabu_size: int = 20, crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.tabu_size = tabu_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.population = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.population])
        self.tabu_list = deque(maxlen=tabu_size)
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.population[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def is_tabu(self, solution: np.ndarray, threshold: float = 0.01) -> bool:
        for tabu_sol in self.tabu_list:
            if np.linalg.norm(solution - tabu_sol) < threshold:
                return True
        return False
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                step_size = 0.1 * (1 - iteration / self.max_iterations)
                
                for _ in range(5):
                    neighbor = self.population[i] + step_size * np.random.randn(self.dimensions)
                    neighbor = np.clip(neighbor, self.bounds[:, 0], self.bounds[:, 1])
                    
                    if not self.is_tabu(neighbor):
                        neighbor_fitness = self.objective_function(neighbor)
                        
                        if neighbor_fitness < self.fitness[i]:
                            self.population[i] = neighbor
                            self.fitness[i] = neighbor_fitness
                            self.tabu_list.append(neighbor.copy())
                            break
            
            if iteration % 5 == 0:
                sorted_idx = np.argsort(self.fitness)
                elite_size = self.population_size // 4
                elites = self.population[sorted_idx[:elite_size]].copy()
                
                new_population = elites.copy()
                
                while len(new_population) < self.population_size:
                    if np.random.rand() < self.crossover_rate and len(new_population) < self.population_size - 1:
                        parent1, parent2 = elites[np.random.choice(elite_size, 2, replace=False)]
                        alpha = np.random.rand()
                        offspring1 = alpha * parent1 + (1-alpha) * parent2
                        offspring2 = (1-alpha) * parent1 + alpha * parent2
                        new_population = np.vstack([new_population, offspring1, offspring2])
                    else:
                        parent = elites[np.random.randint(elite_size)]
                        offspring = parent.copy()
                        if np.random.rand() < self.mutation_rate:
                            mut_dim = np.random.randint(self.dimensions)
                            offspring[mut_dim] = np.random.uniform(self.bounds[mut_dim, 0], self.bounds[mut_dim, 1])
                        new_population = np.vstack([new_population, offspring])
                
                self.population = new_population[:self.population_size]
                self.fitness = np.array([self.objective_function(ind) for ind in self.population])
            
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.best_fitness:
                self.best_solution = self.population[best_idx].copy()
                self.best_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
