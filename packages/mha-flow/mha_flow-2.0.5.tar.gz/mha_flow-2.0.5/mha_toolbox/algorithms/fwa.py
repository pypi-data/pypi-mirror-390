"""Firework Algorithm (FWA) - Tan (2010)"""
import numpy as np
import random
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class FireworkAlgorithm(BaseOptimizer):
    """Firework Algorithm - Tan (2010)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 m: int = 50, a: float = 0.04, b: float = 0.8):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.m = m  # Max number of sparks
        self.a = a
        self.b = b
        
        self.fireworks = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(fw) for fw in self.fireworks])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.fireworks[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            all_sparks = []
            all_fitness = []
            
            worst_fitness = np.max(self.fitness)
            best_fitness_iter = np.min(self.fitness)
            
            # Generate sparks for each firework
            for i in range(self.population_size):
                # Calculate number of sparks
                if worst_fitness != best_fitness_iter:
                    fitness_sum = np.sum(worst_fitness - self.fitness)
                    Si = int(self.m * (worst_fitness - self.fitness[i]) / (fitness_sum + 1e-10))
                else:
                    Si = int(self.m / self.population_size)
                
                Si = max(1, min(Si, self.m))
                
                # Calculate explosion amplitude
                if best_fitness_iter != worst_fitness:
                    fitness_diff_sum = np.sum(self.fitness - best_fitness_iter)
                    Ai = self.a * (self.bounds[:, 1] - self.bounds[:, 0]) * (self.fitness[i] - best_fitness_iter) / (fitness_diff_sum + 1e-10)
                else:
                    Ai = self.a * (self.bounds[:, 1] - self.bounds[:, 0])
                
                # Generate sparks
                for _ in range(Si):
                    spark = self.fireworks[i].copy()
                    
                    # Select random dimensions to modify
                    num_dims = random.randint(1, self.dimensions)
                    dims_to_modify = random.sample(range(self.dimensions), num_dims)
                    
                    for d in dims_to_modify:
                        spark[d] += Ai * np.random.uniform(-1, 1)
                    
                    # Clip to bounds
                    spark = np.clip(spark, self.bounds[:, 0], self.bounds[:, 1])
                    spark_fitness = self.objective_function(spark)
                    
                    all_sparks.append(spark)
                    all_fitness.append(spark_fitness)
                    
                    if spark_fitness < self.best_fitness:
                        self.best_solution = spark.copy()
                        self.best_fitness = spark_fitness
            
            # Select next generation (keep best individuals)
            combined_pop = np.vstack([self.fireworks, np.array(all_sparks)])
            combined_fitness = np.concatenate([self.fitness, np.array(all_fitness)])
            
            # Sort and select best
            sorted_indices = np.argsort(combined_fitness)
            self.fireworks = combined_pop[sorted_indices[:self.population_size]]
            self.fitness = combined_fitness[sorted_indices[:self.population_size]]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
