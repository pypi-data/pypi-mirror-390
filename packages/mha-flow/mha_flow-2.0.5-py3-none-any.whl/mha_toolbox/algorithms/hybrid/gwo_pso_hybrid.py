"""
GWO-PSO Hybrid (Grey Wolf Optimizer - Particle Swarm Optimization)
=================================================================

Hybrid combining GWO's hierarchy with PSO's velocity-based movement.
"""

import numpy as np
from ...base import BaseOptimizer


class GWO_PSO_Hybrid(BaseOptimizer):
    """GWO-PSO Hybrid combining wolf pack hierarchy with particle swarm"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "GWO-PSO Hybrid"
        self.aliases = ["gwo_pso", "gwo_pso_hybrid", "wolf_swarm"]
        self.w = 0.7
        self.c1 = 1.5
        self.c2 = 1.5
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        velocity = np.random.uniform(-1, 1, (self.population_size_, dimensions))
        fitness = np.array([objective_function(ind) for ind in population])
        
        personal_best = population.copy()
        personal_best_fitness = fitness.copy()
        
        sorted_idx = np.argsort(fitness)
        alpha = population[sorted_idx[0]].copy()
        beta = population[sorted_idx[1]].copy()
        delta = population[sorted_idx[2]].copy()
        alpha_fitness = fitness[sorted_idx[0]]
        
        global_fitness = [alpha_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations_):
            a = 2 - 2 * (iteration / self.max_iterations_)
            w_adaptive = self.w * (1 - iteration / self.max_iterations_)
            
            for i in range(self.population_size_):
                # GWO position update
                r1, r2 = np.random.random(2)
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                D_alpha = np.abs(C1 * alpha - population[i])
                X1 = alpha - A1 * D_alpha
                
                r1, r2 = np.random.random(2)
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                D_beta = np.abs(C2 * beta - population[i])
                X2 = beta - A2 * D_beta
                
                r1, r2 = np.random.random(2)
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                D_delta = np.abs(C3 * delta - population[i])
                X3 = delta - A3 * D_delta
                
                gwo_position = (X1 + X2 + X3) / 3
                
                # PSO velocity and position update
                r1, r2 = np.random.random(2)
                velocity[i] = (w_adaptive * velocity[i] + 
                              self.c1 * r1 * (personal_best[i] - population[i]) +
                              self.c2 * r2 * (alpha - population[i]))
                pso_position = population[i] + velocity[i]
                
                # Hybrid: blend both strategies
                population[i] = 0.5 * gwo_position + 0.5 * pso_position
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            
            for i in range(self.population_size_):
                if fitness[i] < personal_best_fitness[i]:
                    personal_best[i] = population[i].copy()
                    personal_best_fitness[i] = fitness[i]
            
            sorted_idx = np.argsort(fitness)
            if fitness[sorted_idx[0]] < alpha_fitness:
                alpha = population[sorted_idx[0]].copy()
                alpha_fitness = fitness[sorted_idx[0]]
            beta = population[sorted_idx[1]].copy()
            delta = population[sorted_idx[2]].copy()
            
            global_fitness.append(alpha_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return alpha, alpha_fitness, global_fitness, local_fitness, local_positions