"""
ACO-PSO Hybrid Algorithm
Combines Ant Colony Optimization with Particle Swarm Optimization
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class ACO_PSO_Hybrid(BaseOptimizer):
    """
    Hybrid algorithm combining Ant Colony Optimization and Particle Swarm Optimization
    
    Parameters
    ----------
    pop_size : int
        Population size
    max_iter : int
        Maximum number of iterations
    alpha : float
        Pheromone importance (ACO component)
    beta : float
        Heuristic importance (ACO component)
    rho : float
        Evaporation rate (ACO component)
    w : float
        Inertia weight (PSO component)
    c1 : float
        Cognitive parameter (PSO component)
    c2 : float
        Social parameter (PSO component)
    """
    
    def __init__(self, population_size=50, max_iterations=100, alpha=1.0, beta=2.0, rho=0.5, 
                 w=0.7, c1=1.5, c2=1.5):
        super().__init__(population_size, max_iterations)
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.w = w
        self.c1 = c1
        self.c2 = c2
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Internal optimization method following BaseOptimizer interface"""
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        lb = bounds[0]
        ub = bounds[1]
        
        # Initialize population
        population = np.random.uniform(lb, ub, (self.population_size_, dimensions))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # PSO components
        velocity = np.random.uniform(-1, 1, (self.population_size_, dimensions))
        pbest = population.copy()
        pbest_fitness = fitness.copy()
        
        # ACO components - pheromone matrix
        pheromone = np.ones((self.population_size_, dimensions))
        
        # Best solution
        best_idx = np.argmin(fitness)
        gbest = population[best_idx].copy()
        gbest_fitness = fitness[best_idx]
        
        global_fitness = [gbest_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations_):
            for i in range(self.population_size_):
                # ACO phase: Update using pheromone trails
                if iteration > 0:
                    # Probabilistic selection based on pheromone
                    prob = (pheromone[i] ** self.alpha) * ((1.0 / (1.0 + np.abs(population[i] - gbest))) ** self.beta)
                    prob = prob / (np.sum(prob) + 1e-10)
                    
                    # Construct solution using pheromone guidance
                    aco_component = gbest + np.random.randn(dimensions) * prob * (ub - lb) * 0.1
                    aco_component = np.clip(aco_component, lb, ub)
                else:
                    aco_component = population[i]
                
                # PSO phase: Update velocity and position
                r1, r2 = np.random.rand(2)
                velocity[i] = (self.w * velocity[i] + 
                              self.c1 * r1 * (pbest[i] - population[i]) +
                              self.c2 * r2 * (gbest - population[i]))
                
                pso_component = population[i] + velocity[i]
                pso_component = np.clip(pso_component, lb, ub)
                
                # Hybrid: Combine ACO and PSO components
                hybrid_weight = 0.5 + 0.3 * np.cos(np.pi * iteration / self.max_iterations_)
                population[i] = hybrid_weight * aco_component + (1 - hybrid_weight) * pso_component
                population[i] = np.clip(population[i], lb, ub)
                
                # Evaluate fitness
                fitness[i] = objective_function(population[i])
                
                # Update personal best
                if fitness[i] < pbest_fitness[i]:
                    pbest[i] = population[i].copy()
                    pbest_fitness[i] = fitness[i]
                    
                # Update global best
                if fitness[i] < gbest_fitness:
                    gbest = population[i].copy()
                    gbest_fitness = fitness[i]
            
            # Update pheromone trails (ACO)
            pheromone *= (1 - self.rho)  # Evaporation
            for i in range(self.population_size_):
                if fitness[i] < np.percentile(fitness, 30):  # Top 30% deposit pheromone
                    pheromone[i] += 1.0 / (1.0 + fitness[i])
            
            global_fitness.append(gbest_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return gbest, gbest_fitness, global_fitness, local_fitness, local_positions

