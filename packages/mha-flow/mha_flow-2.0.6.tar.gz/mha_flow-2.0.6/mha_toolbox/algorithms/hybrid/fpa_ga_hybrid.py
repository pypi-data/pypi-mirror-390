"""FPA-GA Hybrid: Flower Pollination Algorithm + GA"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class FPA_GA_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 switch_prob: float = 0.8, crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.switch_prob = switch_prob
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.flowers = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.flowers])
        best_idx = np.argmin(self.fitness)
        self.best_flower = self.flowers[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def levy_flight(self, Lambda: float = 1.5) -> float:
        sigma = (np.math.gamma(1 + Lambda) * np.sin(np.pi * Lambda / 2) / 
                (np.math.gamma((1 + Lambda) / 2) * Lambda * 2**((Lambda - 1) / 2)))**(1 / Lambda)
        u = np.random.randn() * sigma
        v = np.random.randn()
        step = u / abs(v)**(1 / Lambda)
        return step
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                if np.random.rand() < self.switch_prob:
                    L = self.levy_flight()
                    dS = L * (self.flowers[i] - self.best_flower)
                    new_flower = self.flowers[i] + dS
                else:
                    j, k = np.random.choice(self.population_size, 2, replace=False)
                    epsilon = np.random.rand()
                    new_flower = self.flowers[i] + epsilon * (self.flowers[j] - self.flowers[k])
                
                new_flower = np.clip(new_flower, self.bounds[:, 0], self.bounds[:, 1])
                new_fitness = self.objective_function(new_flower)
                
                if new_fitness < self.fitness[i]:
                    self.flowers[i] = new_flower
                    self.fitness[i] = new_fitness
                    
                    if new_fitness < self.best_fitness:
                        self.best_flower = new_flower.copy()
                        self.best_fitness = new_fitness
            
            if iteration % 5 == 0:
                for i in range(0, self.population_size-1, 2):
                    if np.random.rand() < self.crossover_rate:
                        alpha = np.random.rand()
                        offspring1 = alpha * self.flowers[i] + (1-alpha) * self.flowers[i+1]
                        offspring2 = (1-alpha) * self.flowers[i] + alpha * self.flowers[i+1]
                        offspring1 = np.clip(offspring1, self.bounds[:, 0], self.bounds[:, 1])
                        offspring2 = np.clip(offspring2, self.bounds[:, 0], self.bounds[:, 1])
                        
                        fit1, fit2 = self.objective_function(offspring1), self.objective_function(offspring2)
                        if fit1 < self.fitness[i]:
                            self.flowers[i], self.fitness[i] = offspring1, fit1
                        if fit2 < self.fitness[i+1]:
                            self.flowers[i+1], self.fitness[i+1] = offspring2, fit2
                
                for i in range(self.population_size):
                    if np.random.rand() < self.mutation_rate:
                        mut_dim = np.random.randint(self.dimensions)
                        self.flowers[i][mut_dim] = np.random.uniform(self.bounds[mut_dim, 0], self.bounds[mut_dim, 1])
                        self.fitness[i] = self.objective_function(self.flowers[i])
            
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.best_fitness:
                self.best_flower = self.flowers[best_idx].copy()
                self.best_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_flower, self.best_fitness, self.convergence_curve
