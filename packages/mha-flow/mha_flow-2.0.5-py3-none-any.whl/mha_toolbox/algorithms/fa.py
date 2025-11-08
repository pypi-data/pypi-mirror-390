"""
Firefly Algorithm (FA)

Based on: Yang, X. S. (2009). Firefly algorithms for multimodal optimization.
In International symposium on stochastic algorithms (pp. 169-178).
"""

import numpy as np
from ..base import BaseOptimizer


class FireflyAlgorithm(BaseOptimizer):
    """
    Firefly Algorithm (FA)
    
    FA is inspired by the flashing behavior of fireflies. The algorithm
    is based on the assumption that all fireflies are unisex and they
    are attracted to other fireflies regardless of their sex.
    
    Parameters
    ----------
    alpha : float, default=0.2
        Randomization parameter
    beta_0 : float, default=1.0
        Attractiveness at distance r=0
    gamma : float, default=1.0
        Light absorption coefficient
    """
    
    aliases = ["fa", "firefly", "firefly_algorithm"]
    
    def __init__(self, alpha=0.2, beta_0=1.0, gamma=1.0, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.beta_0 = beta_0
        self.gamma = gamma
        self.algorithm_name = "FA"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        fitness = np.array([objective_function(ind) for ind in population])
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(self.population_size_):
                for j in range(self.population_size_):
                    if fitness[j] < fitness[i]:
                        r = np.linalg.norm(population[i] - population[j])
                        beta = self.beta_0 * np.exp(-self.gamma * r**2)
                        population[i] += beta * (population[j] - population[i]) + \
                                       self.alpha * (np.random.random(self.dimensions_) - 0.5)
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                fitness[i] = objective_function(population[i])
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            best_idx = np.argmin(fitness)
            global_fitness.append(fitness[best_idx])
            local_fitness.append(fitnesses)
            local_positions.append(positions)
            self.alpha *= 0.98
        best_idx = np.argmin(fitness)
        return population[best_idx], fitness[best_idx], global_fitness, local_fitness, local_positions
