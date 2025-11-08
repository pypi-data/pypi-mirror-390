"""
CS-GA Hybrid: Cuckoo Search + Genetic Algorithm
===============================================

Best for: Engineering design and constrained optimization
Combines Lévy flight exploration with genetic operations
"""

import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer


class CS_GA_Hybrid(BaseOptimizer):
    """
    CS-GA Hybrid: Cuckoo Search + Genetic Algorithm
    
    Parameters:
    -----------
    pa : float
        Probability of abandoning worst nests (0-1)
    beta : float
        Lévy flight parameter
    crossover_rate, mutation_rate : float
        GA parameters
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 pa: float = 0.25, beta: float = 1.5,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.pa = pa
        self.beta = beta
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        # Initialize nests (solutions)
        self.nests = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                      (population_size, dimensions))
        self.fitness = np.array([objective_function(nest) for nest in self.nests])
        
        # Best nest
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_nest = self.nests[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def _levy_flight(self, size):
        """Generate Lévy flight step using Mantegna's algorithm"""
        sigma = (np.math.gamma(1 + self.beta) * np.sin(np.pi * self.beta / 2) /
                (np.math.gamma((1 + self.beta) / 2) * self.beta * 
                 2**((self.beta - 1) / 2)))**(1 / self.beta)
        
        u = np.random.normal(0, sigma, size)
        v = np.random.normal(0, 1, size)
        step = u / np.abs(v)**(1 / self.beta)
        
        return step
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run CS-GA hybrid optimization"""
        for iteration in range(self.max_iterations):
            # Cuckoo Search phase - Lévy flights
            for i in range(self.population_size):
                # Generate new solution via Lévy flight
                step_size = 0.01 * self._levy_flight(self.dimensions)
                new_nest = self.nests[i] + step_size * (self.nests[i] - self.gbest_nest)
                new_nest = np.clip(new_nest, self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate new nest
                new_fitness = self.objective_function(new_nest)
                
                # Random nest selection for comparison
                j = np.random.randint(0, self.population_size)
                
                # Replace if better
                if new_fitness < self.fitness[j]:
                    self.nests[j] = new_nest
                    self.fitness[j] = new_fitness
            
            # Abandon worst nests (discovery rate pa)
            n_abandon = int(self.pa * self.population_size)
            worst_indices = np.argsort(self.fitness)[-n_abandon:]
            
            for idx in worst_indices:
                # Replace with random solution
                self.nests[idx] = np.random.uniform(self.bounds[:, 0], 
                                                    self.bounds[:, 1], 
                                                    self.dimensions)
                self.fitness[idx] = self.objective_function(self.nests[idx])
            
            # GA phase - apply every 5 iterations
            if iteration % 5 == 0:
                # Selection using fitness-proportionate (roulette wheel)
                fitness_inv = 1.0 / (self.fitness + 1e-10)
                probs = fitness_inv / np.sum(fitness_inv)
                
                # Crossover
                for _ in range(self.population_size // 4):
                    if np.random.random() < self.crossover_rate:
                        # Select two parents
                        parents = np.random.choice(self.population_size, 2, 
                                                  p=probs, replace=False)
                        
                        # Single-point crossover
                        crossover_point = np.random.randint(1, self.dimensions)
                        
                        offspring = self.nests[parents[0]].copy()
                        offspring[crossover_point:] = self.nests[parents[1]][crossover_point:]
                        
                        # Evaluate offspring
                        offspring_fitness = self.objective_function(offspring)
                        
                        # Replace worst individual if offspring is better
                        worst_idx = np.argmax(self.fitness)
                        if offspring_fitness < self.fitness[worst_idx]:
                            self.nests[worst_idx] = offspring
                            self.fitness[worst_idx] = offspring_fitness
                
                # Mutation
                for i in range(self.population_size):
                    if np.random.random() < self.mutation_rate:
                        # Gaussian mutation on random dimension
                        mutation_idx = np.random.randint(0, self.dimensions)
                        self.nests[i][mutation_idx] = np.random.uniform(
                            self.bounds[mutation_idx, 0],
                            self.bounds[mutation_idx, 1]
                        )
                        self.fitness[i] = self.objective_function(self.nests[i])
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_idx = current_best_idx
                self.gbest_nest = self.nests[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_nest, self.gbest_fitness, self.convergence_curve
