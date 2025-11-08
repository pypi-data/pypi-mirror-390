"""
Krill Herd Algorithm (KH)
========================

Krill Herd Algorithm inspired by the herding behavior of krill swarms.
"""

import numpy as np
from ..base import BaseOptimizer


class KrillHerdAlgorithm(BaseOptimizer):
    """Krill Herd Algorithm (KH)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Krill Herd Algorithm"
        self.aliases = ["kh", "krill_herd", "krill_algorithm"]
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        velocity = np.zeros((self.population_size, dimension))
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Motion induced by other krill
                alpha = 0
                for j in range(self.population_size):
                    if i != j:
                        dist = np.linalg.norm(population[i] - population[j])
                        if dist > 0:
                            alpha += (fitness[j] - fitness[i]) / dist * (population[j] - population[i])
                
                # Motion induced by foraging
                beta = 2 * (1 - iteration / self.max_iterations) * (best_position - population[i])
                
                # Physical diffusion
                delta = np.random.randn(dimension) * 0.01
                
                # Update position
                velocity[i] = 0.9 * velocity[i] + 0.1 * (alpha + beta + delta)
                population[i] = population[i] + velocity[i]
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions