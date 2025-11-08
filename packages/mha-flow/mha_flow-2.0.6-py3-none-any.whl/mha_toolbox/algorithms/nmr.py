"""
Naked Mole-Rat Algorithm (NMR)
=============================
"""
import numpy as np
from ..base import BaseOptimizer

class NakedMoleRatAlgorithm(BaseOptimizer):
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Naked Mole-Rat Algorithm"
        self.aliases = ["nmr", "naked_mole_rat", "mole_rat"]
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        global_fitness, local_fitness, local_positions = [best_fitness], [fitness.copy()], [population.copy()]
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                r = np.random.random()
                if r < 0.5:
                    population[i] = best_position + np.random.randn(dimension) * (1 - iteration / self.max_iterations)
                else:
                    k = np.random.randint(0, self.population_size)
                    population[i] = population[i] + np.random.random() * (population[k] - population[i])
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position, best_fitness = population[current_best_idx].copy(), fitness[current_best_idx]
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        return best_position, best_fitness, global_fitness, local_fitness, local_positions