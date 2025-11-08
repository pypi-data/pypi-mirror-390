"""
Harris Hawks Optimization (HHO)

Based on: Heidari, A. A., et al. (2019). Harris hawks optimization: Algorithm and applications.
"""

import numpy as np
from ..base import BaseOptimizer


class HarrisHawksOptimization(BaseOptimizer):
    """
    Harris Hawks Optimization (HHO)
    
    HHO is inspired by the cooperative behavior and chasing styles of Harris' hawks.
    The algorithm mimics the surprise pounce of Harris' hawks when catching prey.
    
    Parameters
    ----------
    None (Parameter-free algorithm)
    """
    
    aliases = ["hho", "harris_hawks", "harris_hawks_optimization"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.algorithm_name = "HHO"
    
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
        
        # Initialize hawk population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find initial rabbit (best solution)
        rabbit_idx = np.argmin(fitness)
        rabbit_position = population[rabbit_idx].copy()
        rabbit_fitness = fitness[rabbit_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Calculate energy
            E0 = 2 * np.random.random() - 1  # Initial energy
            E = 2 * E0 * (1 - iteration / self.max_iterations_)  # Energy decreases over time
            
            for i in range(self.population_size_):
                if abs(E) >= 1:
                    # Exploration phase (|E| >= 1)
                    if np.random.random() >= 0.5:
                        # Perch based on other hawks
                        r1, r2, r3, r4 = np.random.random(4)
                        population[i] = (rabbit_position - 
                                       r1 * np.abs(rabbit_position - 2 * r2 * population[i]))
                    else:
                        # Perch on random locations
                        r1, r2 = np.random.random(2)
                        hawk_idx = np.random.randint(0, self.population_size_)
                        population[i] = (population[hawk_idx] - 
                                       r1 * np.abs(population[hawk_idx] - 2 * r2 * population[i]))
                
                else:
                    # Exploitation phase (|E| < 1)
                    r = np.random.random()
                    
                    if r >= 0.5 and abs(E) >= 0.5:
                        # Soft besiege
                        delta_X = rabbit_position - population[i]
                        population[i] = delta_X - E * np.abs(np.random.random() * rabbit_position - population[i])
                    
                    elif r >= 0.5 and abs(E) < 0.5:
                        # Hard besiege
                        population[i] = rabbit_position - E * np.abs(delta_X)
                    
                    elif r < 0.5 and abs(E) >= 0.5:
                        # Soft besiege with progressive rapid dives
                        S = np.random.random(self.dimensions_)
                        LF = self._levy_flight()
                        Y = rabbit_position - E * np.abs(np.random.random() * rabbit_position - population[i])
                        Z = Y + S * LF
                        
                        if objective_function(Y) < fitness[i]:
                            population[i] = Y
                        elif objective_function(Z) < fitness[i]:
                            population[i] = Z
                    
                    else:
                        # Hard besiege with progressive rapid dives
                        S = np.random.random(self.dimensions_)
                        LF = self._levy_flight()
                        Y = rabbit_position - E * np.abs(np.random.random() * rabbit_position - 2 * population[i])
                        Z = Y + S * LF
                        
                        if objective_function(Y) < fitness[i]:
                            population[i] = Y
                        elif objective_function(Z) < fitness[i]:
                            population[i] = Z
                
                # Ensure bounds
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                
                # Evaluate fitness
                fitness[i] = objective_function(population[i])
                
                # Update rabbit position
                if fitness[i] < rabbit_fitness:
                    rabbit_position = population[i].copy()
                    rabbit_fitness = fitness[i]
                
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(rabbit_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return rabbit_position, rabbit_fitness, global_fitness, local_fitness, local_positions
    
    def _levy_flight(self):
        """Generate Levy flight"""
        beta = 1.5
        sigma = (np.math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (np.math.gamma((1 + beta) / 2) * beta * (2 ** ((beta - 1) / 2)))) ** (1 / beta)
        
        u = np.random.randn(self.dimensions_) * sigma
        v = np.random.randn(self.dimensions_)
        
        return u / (np.abs(v) ** (1 / beta))