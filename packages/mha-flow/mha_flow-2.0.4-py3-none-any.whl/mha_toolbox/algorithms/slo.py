"""
Sea Lion Optimization Algorithm (SLO)
====================================

Sea Lion Optimization Algorithm inspired by the social behavior
and hunting strategies of sea lions.
"""

import numpy as np
from ..base import BaseOptimizer


class SeaLionOptimization(BaseOptimizer):
    """
    Sea Lion Optimization Algorithm (SLO)
    
    Bio-inspired algorithm based on the social behavior, hunting,
    and territorial strategies of sea lions.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Sea Lion Optimization Algorithm"
        self.aliases = ["slo", "sea_lion", "sealion_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Sea Lion Optimization Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize sea lion population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution (leader sea lion)
        best_idx = np.argmin(fitness)
        leader_position = population[best_idx].copy()
        leader_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [leader_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update algorithm parameters
            c = 2 - 2 * iteration / self.max_iterations  # Decreases from 2 to 0
            SP_leader = np.random.uniform(0, 1)  # Leader's social parameter
            
            for i in range(self.population_size):
                # Hunting behavior (exploitation)
                if SP_leader >= 0.6:
                    # Sea lion follows the leader
                    A = 2 * c * np.random.random() - c  # Coefficient vector
                    D = abs(2 * np.random.random() * leader_position - population[i])
                    population[i] = leader_position - A * D
                
                # Searching behavior (exploration)
                else:
                    # Sea lion searches for new territory
                    if abs(A) >= 1:
                        # Search for new hunting ground
                        rand_sea_lion = population[np.random.randint(0, self.population_size)]
                        D_rand = abs(2 * np.random.random() * rand_sea_lion - population[i])
                        population[i] = rand_sea_lion - A * D_rand
                    else:
                        # Follow leader but with noise
                        D_leader = abs(2 * np.random.random() * leader_position - population[i])
                        population[i] = leader_position - A * D_leader
                
                # Apply territorial behavior (bounds constraint)
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update leader sea lion
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < leader_fitness:
                leader_position = population[current_best_idx].copy()
                leader_fitness = fitness[current_best_idx]
            
            # Mating behavior (genetic diversity)
            if iteration % 15 == 0:  # Every 15 iterations
                # Select parents for mating
                num_offspring = self.population_size // 4
                for _ in range(num_offspring):
                    parent1_idx = np.random.randint(0, self.population_size)
                    parent2_idx = np.random.randint(0, self.population_size)
                    
                    # Create offspring through crossover
                    alpha = np.random.random()
                    offspring = alpha * population[parent1_idx] + (1 - alpha) * population[parent2_idx]
                    offspring = np.clip(offspring, bounds[0], bounds[1])
                    
                    # Replace worst individual if offspring is better
                    worst_idx = np.argmax(fitness)
                    offspring_fitness = objective_function(offspring)
                    if offspring_fitness < fitness[worst_idx]:
                        population[worst_idx] = offspring
                        fitness[worst_idx] = offspring_fitness
            
            # Track progress
            global_fitness.append(leader_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return leader_position, leader_fitness, global_fitness, local_fitness, local_positions