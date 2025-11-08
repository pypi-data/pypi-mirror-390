"""
Water Cycle Algorithm (WCA)

A nature-inspired optimization algorithm based on the water cycle process
including evaporation, condensation, and precipitation.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class WaterCycleAlgorithm(BaseOptimizer):
    """Water Cycle Algorithm (WCA)"""
    
    aliases = ['wca', 'water_cycle', 'hydrological']
    
    def __init__(self, population_size=50, max_iterations=100, n_rivers=4, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.n_rivers = n_rivers
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.n_rivers_ = n_rivers
        self.algorithm_name_ = "Water Cycle Algorithm"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the WCA optimization algorithm
        """
        # Use trailing underscore attributes
        if X is not None:
            dimensions = X.shape[1]
            lower_bound = np.zeros(dimensions)
            upper_bound = np.ones(dimensions)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                raise ValueError("Dimensions must be specified")
            dimensions = self.dimensions_
            lower_bound = self.lower_bound_
            upper_bound = self.upper_bound_
            
        objective_func = objective_function
        population = np.random.uniform(lower_bound, upper_bound, (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # Sort by fitness
        sorted_indices = np.argsort(fitness)
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        # Best solution is the sea
        sea = population[0].copy()
        sea_fitness = fitness[0]
        
        # Initialize tracking for history
        global_fitness = [sea_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        
        # Next best are rivers
        rivers = population[1:self.n_rivers+1].copy()
        river_fitness = fitness[1:self.n_rivers+1].copy()
        
        # Rest are streams
        streams = population[self.n_rivers+1:].copy()
        stream_fitness = fitness[self.n_rivers+1:].copy()
        
        for iteration in range(self.max_iterations):
            # Streams flow to rivers and sea
            for i in range(len(streams)):
                if i < len(rivers):
                    target = rivers[i % len(rivers)]
                else:
                    target = sea
                
                # Flow towards target
                direction = target - streams[i]
                flow_rate = np.random.uniform(0.1, 0.9)
                new_position = streams[i] + flow_rate * direction
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                if new_fitness < stream_fitness[i]:
                    streams[i] = new_position
                    stream_fitness[i] = new_fitness
            
            # Rivers flow to sea
            for i in range(len(rivers)):
                direction = sea - rivers[i]
                flow_rate = np.random.uniform(0.3, 0.7)
                new_position = rivers[i] + flow_rate * direction
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                if new_fitness < river_fitness[i]:
                    rivers[i] = new_position
                    river_fitness[i] = new_fitness
                    
                    # River may become better than sea
                    if new_fitness < sea_fitness:
                        sea, rivers[i] = rivers[i].copy(), sea.copy()
                        sea_fitness, river_fitness[i] = river_fitness[i], sea_fitness
            
            # Evaporation and precipitation
            if iteration % 10 == 0:
                # Some streams evaporate and precipitate randomly
                evaporation_rate = 0.1
                n_evaporate = max(1, int(evaporation_rate * len(streams)))
                evaporate_indices = np.random.choice(len(streams), n_evaporate, replace=False)
                
                for idx in evaporate_indices:
                    streams[idx] = np.random.uniform(lower_bound, upper_bound, dimensions)
                    stream_fitness[idx] = objective_func(streams[idx])
            
            # Track progress
            # Combine all populations for tracking
            all_populations = np.vstack([sea.reshape(1, -1), rivers, streams])
            all_fitness = np.concatenate([[sea_fitness], river_fitness, stream_fitness])
            global_fitness.append(sea_fitness)
            local_fitness.append(all_fitness.tolist())
            local_positions.append(all_populations.tolist())
        
        return sea, sea_fitness, global_fitness, local_fitness, local_positions