"""
Elephant Herding Optimization (EHO)
==================================

Elephant Herding Optimization inspired by the herding behavior
of elephants in nature.
"""

import numpy as np
from ..base import BaseOptimizer


class ElephantHerdingOptimization(BaseOptimizer):
    """
    Elephant Herding Optimization (EHO)
    
    Bio-inspired algorithm based on the herding behavior of elephants,
    including clan formation and separation behaviors.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Elephant Herding Optimization"
        self.aliases = ["eho", "elephant_herding", "elephant_optimization"]
        self.n_clans = 5  # Number of clans
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Elephant Herding Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize elephant population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Divide elephants into clans
        clan_size = self.population_size // self.n_clans
        clans = []
        clan_fitness = []
        
        for i in range(self.n_clans):
            start_idx = i * clan_size
            end_idx = start_idx + clan_size if i < self.n_clans - 1 else self.population_size
            clans.append(population[start_idx:end_idx])
            clan_fitness.append(fitness[start_idx:end_idx])
        
        # Track best solution
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            alpha = 0.5  # Scale factor
            beta = 0.1   # Influence of best elephant
            
            # Update each clan
            for clan_idx in range(len(clans)):
                clan = clans[clan_idx]
                clan_fit = clan_fitness[clan_idx]
                
                # Find matriarch (best elephant in clan)
                matriarch_idx = np.argmin(clan_fit)
                matriarch = clan[matriarch_idx]
                
                # Update clan center
                clan_center = np.mean(clan, axis=0)
                
                # Update each elephant in clan
                for i in range(len(clan)):
                    if i == matriarch_idx:
                        # Update matriarch position
                        clan[i] = beta * clan_center
                    else:
                        # Update other elephants
                        clan[i] = clan[i] + alpha * (matriarch - clan[i]) * np.random.random()
                    
                    # Apply bounds
                    clan[i] = np.clip(clan[i], bounds[0], bounds[1])
                
                # Evaluate updated clan
                clan_fitness[clan_idx] = np.array([objective_function(elephant) for elephant in clan])
            
            # Separating operator - worst elephant in each clan is replaced
            for clan_idx in range(len(clans)):
                clan = clans[clan_idx]
                clan_fit = clan_fitness[clan_idx]
                
                # Find worst elephant in clan
                worst_idx = np.argmax(clan_fit)
                
                # Replace worst elephant with new random elephant
                clan[worst_idx] = bounds[0] + np.random.random(dimension) * (bounds[1] - bounds[0])
                clan_fitness[clan_idx][worst_idx] = objective_function(clan[worst_idx])
            
            # Combine all clans back to population
            population = np.vstack(clans)
            fitness = np.concatenate(clan_fitness)
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions