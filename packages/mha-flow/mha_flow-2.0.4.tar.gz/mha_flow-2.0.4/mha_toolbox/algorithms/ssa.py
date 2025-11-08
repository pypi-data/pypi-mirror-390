"""
Salp Swarm Algorithm (SSA)

Based on: Mirjalili, S., Gandomi, A. H., Mirjalili, S. Z., Saremi, S., Faris, H., 
& Mirjalili, S. M. (2017). Salp swarm algorithm: A bio-inspired optimizer for 
engineering design problems.
"""

import numpy as np
from ..base import BaseOptimizer


class SalpSwarmAlgorithm(BaseOptimizer):
    """
    Salp Swarm Algorithm (SSA)
    
    SSA is inspired by the swarming behavior of salps in oceans. Salps form
    chains where the leader guides the chain towards food sources.
    """
    
    aliases = ["ssa_salp", "salp_swarm", "salp"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "SalpSwarmAlgorithm"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        if X is not None:
            self.dimensions_ = X.shape[1]
            self.lower_bound_ = np.zeros(self.dimensions_)
            self.upper_bound_ = np.ones(self.dimensions_)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                self.dimensions_ = kwargs.get('dimensions', 10)
            if not hasattr(self, 'lower_bound_') or self.lower_bound_ is None:
                lb = kwargs.get('lower_bound', kwargs.get('lb', -10.0))
                self.lower_bound_ = np.full(self.dimensions_, lb) if np.isscalar(lb) else np.array(lb)
            if not hasattr(self, 'upper_bound_') or self.upper_bound_ is None:
                ub = kwargs.get('upper_bound', kwargs.get('ub', 10.0))
                self.upper_bound_ = np.full(self.dimensions_, ub) if np.isscalar(ub) else np.array(ub)
        
        # Initialize salp population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find food source (best solution)
        food_idx = np.argmin(fitness)
        food_source = population[food_idx].copy()
        food_fitness = fitness[food_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update c1 parameter
            c1 = 2 * np.exp(-(4 * iteration / self.max_iterations_) ** 2)
            
            # Divide population into leaders and followers
            leader_count = self.population_size_ // 2
            
            for i in range(self.population_size_):
                if i < leader_count:  # Leader salps
                    # Update position of leader salps
                    for j in range(self.dimensions_):
                        c2 = np.random.random()
                        c3 = np.random.random()
                        
                        if c3 < 0.5:
                            new_position_j = food_source[j] + c1 * ((self.upper_bound_[j] - self.lower_bound_[j]) * c2 + self.lower_bound_[j])
                        else:
                            new_position_j = food_source[j] - c1 * ((self.upper_bound_[j] - self.lower_bound_[j]) * c2 + self.lower_bound_[j])
                        
                        population[i][j] = new_position_j
                
                else:  # Follower salps
                    # Followers follow the salp in front of them
                    population[i] = (population[i] + population[i-1]) / 2
                
                # Boundary checking
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(population[i])
                fitnesses.append(new_fitness)
                positions.append(population[i].copy())
                
                # Update fitness
                fitness[i] = new_fitness
                
                # Update food source if better
                if new_fitness < food_fitness:
                    food_source = population[i].copy()
                    food_fitness = new_fitness
            
            global_fitness.append(food_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return food_source, food_fitness, global_fitness, local_fitness, local_positions