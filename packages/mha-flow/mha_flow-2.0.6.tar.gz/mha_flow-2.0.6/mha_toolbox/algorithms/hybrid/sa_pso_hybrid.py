"""
SA-PSO Hybrid Algorithm
Combines Simulated Annealing with Particle Swarm Optimization
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class SA_PSO_Hybrid(BaseOptimizer):
    """
    Hybrid algorithm combining Simulated Annealing and Particle Swarm Optimization
    
    Parameters
    ----------
    pop_size : int
        Population size
    max_iter : int
        Maximum number of iterations
    T0 : float
        Initial temperature (SA component)
    Tf : float
        Final temperature (SA component)
    w : float
        Inertia weight (PSO component)
    c1 : float
        Cognitive parameter (PSO component)
    c2 : float
        Social parameter (PSO component)
    """
    
    def __init__(self, pop_size=50, max_iter=100, T0=100.0, Tf=0.01, w=0.7, c1=1.5, c2=1.5, **kwargs):
        super().__init__(pop_size, max_iter, **kwargs)
        self.T0 = T0
        self.Tf = Tf
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Execute the SA-PSO hybrid optimization"""
        # Determine dimensions and bounds
        if X is not None:
            dim = X.shape[1]
            lb = np.zeros(dim)
            ub = np.ones(dim)
        else:
            dim = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dim), np.ones(dim)))
            lb = bounds[0] if isinstance(bounds[0], np.ndarray) else np.ones(dim) * bounds[0]
            ub = bounds[1] if isinstance(bounds[1], np.ndarray) else np.ones(dim) * bounds[1]
        
        # Initialize population
        population = np.random.uniform(lb, ub, (self.population_size_, dim))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # PSO components
        velocity = np.random.uniform(-1, 1, (self.population_size_, dim))
        pbest = population.copy()
        pbest_fitness = fitness.copy()
        
        # Best solution
        best_idx = np.argmin(fitness)
        gbest = population[best_idx].copy()
        gbest_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            # Calculate temperature for SA component
            T = self.T0 * ((self.Tf / self.T0) ** (iteration / self.max_iterations_))
            
            for i in range(self.population_size_):
                # PSO phase
                r1, r2 = np.random.rand(2)
                velocity[i] = (self.w * velocity[i] + 
                              self.c1 * r1 * (pbest[i] - population[i]) +
                              self.c2 * r2 * (gbest - population[i]))
                
                new_pos = population[i] + velocity[i]
                new_pos = np.clip(new_pos, lb, ub)
                
                # Evaluate new position
                new_fitness = objective_function(new_pos)
                
                # SA acceptance criterion
                delta_E = new_fitness - fitness[i]
                if delta_E < 0 or np.random.rand() < np.exp(-delta_E / T):
                    population[i] = new_pos
                    fitness[i] = new_fitness
                    
                    # Update personal best
                    if fitness[i] < pbest_fitness[i]:
                        pbest[i] = population[i].copy()
                        pbest_fitness[i] = fitness[i]
                        
                    # Update global best
                    if fitness[i] < gbest_fitness:
                        gbest = population[i].copy()
                        gbest_fitness = fitness[i]
            
            global_fitness.append(gbest_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
            
        return gbest, gbest_fitness, global_fitness, local_fitness, local_positions
