"""
Artificial Bee Colony Algorithm (ABC)

Based on: Karaboga, D. (2005). An idea based on honey bee swarm for numerical optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class ArtificialBeeColony(BaseOptimizer):
    """
    Artificial Bee Colony Algorithm (ABC)
    
    ABC is inspired by the foraging behavior of honey bee colonies.
    It consists of employed bees, onlooker bees, and scout bees.
    
    Parameters
    ----------
    limit : int, default=100
        Maximum number of trials for abandoning a food source
    """
    
    aliases = ["abc", "artificial_bee_colony", "bee_colony"]
    
    def __init__(self, limit=100, **kwargs):
        super().__init__(**kwargs)
        self.limit = limit
        self.algorithm_name = "ABC"
    
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
        
        # Number of food sources = half of population
        num_sources = self.population_size_ // 2
        
        # Initialize food sources
        food_sources = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (num_sources, self.dimensions_)
        )
        
        # Evaluate initial food sources
        fitness = np.array([objective_function(source) for source in food_sources])
        
        # Initialize trial counters
        trials = np.zeros(num_sources)
        
        # Find initial best
        best_idx = np.argmin(fitness)
        best_position = food_sources[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Employed bees phase
            for i in range(num_sources):
                # Choose a random dimension
                j = np.random.randint(0, self.dimensions_)
                
                # Choose a random neighbor (different from current)
                k = np.random.randint(0, num_sources)
                while k == i:
                    k = np.random.randint(0, num_sources)
                
                # Generate new solution
                phi = np.random.uniform(-1, 1)
                new_source = food_sources[i].copy()
                new_source[j] = food_sources[i][j] + phi * (food_sources[i][j] - food_sources[k][j])
                
                # Ensure bounds
                new_source = np.clip(new_source, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new source
                new_fitness = objective_function(new_source)
                
                # Greedy selection
                if new_fitness < fitness[i]:
                    food_sources[i] = new_source.copy()
                    fitness[i] = new_fitness
                    trials[i] = 0
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_source.copy()
                        best_fitness = new_fitness
                else:
                    trials[i] += 1
            
            # Calculate probabilities for onlooker bees
            fitness_values = 1.0 / (1.0 + fitness)  # Convert to positive values
            probabilities = fitness_values / np.sum(fitness_values)
            
            # Onlooker bees phase
            for _ in range(num_sources):
                # Select food source based on probability
                i = np.random.choice(num_sources, p=probabilities)
                
                # Choose a random dimension
                j = np.random.randint(0, self.dimensions_)
                
                # Choose a random neighbor
                k = np.random.randint(0, num_sources)
                while k == i:
                    k = np.random.randint(0, num_sources)
                
                # Generate new solution
                phi = np.random.uniform(-1, 1)
                new_source = food_sources[i].copy()
                new_source[j] = food_sources[i][j] + phi * (food_sources[i][j] - food_sources[k][j])
                
                # Ensure bounds
                new_source = np.clip(new_source, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new source
                new_fitness = objective_function(new_source)
                
                # Greedy selection
                if new_fitness < fitness[i]:
                    food_sources[i] = new_source.copy()
                    fitness[i] = new_fitness
                    trials[i] = 0
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_source.copy()
                        best_fitness = new_fitness
                else:
                    trials[i] += 1
            
            # Scout bees phase
            for i in range(num_sources):
                if trials[i] > self.limit:
                    # Generate new random food source
                    food_sources[i] = np.random.uniform(
                        self.lower_bound_, self.upper_bound_, self.dimensions_
                    )
                    fitness[i] = objective_function(food_sources[i])
                    trials[i] = 0
                    
                    # Update global best if necessary
                    if fitness[i] < best_fitness:
                        best_position = food_sources[i].copy()
                        best_fitness = fitness[i]
            
            # Collect data for this iteration
            for i in range(num_sources):
                fitnesses.append(fitness[i])
                positions.append(food_sources[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions