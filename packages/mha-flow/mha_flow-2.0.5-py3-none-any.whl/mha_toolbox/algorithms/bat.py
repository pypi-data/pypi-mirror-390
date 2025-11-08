"""
Bat Algorithm (BA)

Based on: Yang, X. S. (2010). A new metaheuristic bat-inspired algorithm.
"""

import numpy as np
from ..base import BaseOptimizer


class BatAlgorithm(BaseOptimizer):
    """
    Bat Algorithm (BA)
    
    BA is inspired by the echolocation behavior of bats.
    Bats use echolocation to detect prey, avoid obstacles, and locate roosts.
    
    Parameters
    ----------
    A : float, default=0.5
        Loudness (typically between 0 and 2)
    r : float, default=0.5
        Pulse emission rate (typically between 0 and 1)
    Qmin : float, default=0
        Minimum frequency
    Qmax : float, default=2
        Maximum frequency
    alpha : float, default=0.9
        Loudness reduction factor
    gamma : float, default=0.9
        Pulse rate increase factor
    """
    
    aliases = ["ba", "bat", "bat_algorithm"]
    
    def __init__(self, A=0.5, r=0.5, Qmin=0, Qmax=2, alpha=0.9, gamma=0.9, **kwargs):
        super().__init__(**kwargs)
        self.A = A
        self.r = r
        self.Qmin = Qmin
        self.Qmax = Qmax
        self.alpha = alpha
        self.gamma = gamma
        self.algorithm_name = "BA"
    
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
        
        # Initialize bat population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Initialize velocities
        velocity = np.zeros((self.population_size_, self.dimensions_))
        
        # Initialize frequencies
        frequency = np.zeros(self.population_size_)
        
        # Initialize pulse rates and loudness
        pulse_rates = np.full(self.population_size_, self.r)
        loudness = np.full(self.population_size_, self.A)
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find initial best
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            for i in range(self.population_size_):
                # Update frequency
                frequency[i] = self.Qmin + (self.Qmax - self.Qmin) * np.random.random()
                
                # Update velocity
                velocity[i] = velocity[i] + (population[i] - best_position) * frequency[i]
                
                # Update position
                new_position = population[i] + velocity[i]
                
                # Apply random walk for local search
                if np.random.random() > pulse_rates[i]:
                    # Generate local solution around best solution
                    new_position = best_position + 0.1 * np.random.randn(self.dimensions_)
                
                # Ensure bounds
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(new_position)
                
                # Accept new solution
                if np.random.random() < loudness[i] and new_fitness < fitness[i]:
                    population[i] = new_position.copy()
                    fitness[i] = new_fitness
                    
                    # Increase pulse rate and decrease loudness
                    pulse_rates[i] = self.r * (1 - np.exp(-self.gamma * iteration))
                    loudness[i] = self.alpha * loudness[i]
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_position.copy()
                        best_fitness = new_fitness
                
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions