"""
Whale Optimization Algorithm (WOA)

Based on: Mirjalili, S., & Lewis, A. (2016). The whale optimization algorithm. 
Advances in engineering software, 95, 51-67.
"""

import numpy as np
from ..base import BaseOptimizer


class WhaleOptimizationAlgorithm(BaseOptimizer):
    """
    Whale Optimization Algorithm (WOA)
    
    WOA mimics the social behavior of humpback whales and their bubble-net
    hunting strategy. The algorithm implements encircling prey, bubble-net
    attacking method, and search for prey.
    """
    
    aliases = ["woa", "whale", "whale_optimization"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        leader_pos = np.zeros(self.dimensions_)
        leader_score = float('inf')
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(len(population)):
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                fitness = objective_function(population[i])
                fitnesses.append(fitness)
                positions.append(population[i].copy())
                if fitness < leader_score:
                    leader_score = fitness
                    leader_pos = population[i].copy()
            global_fitness.append(leader_score)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
            a = 2 - iteration * (2.0 / self.max_iterations_)
            for i in range(len(population)):
                r1 = np.random.random()
                r2 = np.random.random()
                A = 2 * a * r1 - a
                C = 2 * r2
                b = 1
                l = np.random.uniform(-1, 1)
                p = np.random.random()
                for j in range(self.dimensions_):
                    if p < 0.5:
                        if abs(A) >= 1:
                            rand_leader_index = np.random.randint(0, len(population))
                            X_rand = population[rand_leader_index]
                            D_X_rand = abs(C * X_rand[j] - population[i][j])
                            population[i][j] = X_rand[j] - A * D_X_rand
                        elif abs(A) < 1:
                            D_Leader = abs(C * leader_pos[j] - population[i][j])
                            population[i][j] = leader_pos[j] - A * D_Leader
                    elif p >= 0.5:
                        distance2Leader = abs(leader_pos[j] - population[i][j])
                        population[i][j] = distance2Leader * np.exp(b * l) * np.cos(l * 2 * np.pi) + leader_pos[j]
        return leader_pos, leader_score, global_fitness, local_fitness, local_positions
