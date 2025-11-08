"""
Squirrel Search Algorithm (SSA)
==============================

Squirrel Search Algorithm inspired by the dynamic foraging behavior
of flying squirrels.
"""

import numpy as np
from ..base import BaseOptimizer


class SquirrelSearchAlgorithm(BaseOptimizer):
    """
    Squirrel Search Algorithm (SSA)
    
    Bio-inspired algorithm based on the dynamic foraging behavior
    and gliding capability of flying squirrels.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Squirrel Search Algorithm"
        self.aliases = ["ssa_squirrel", "squirrel_search", "flying_squirrel"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Squirrel Search Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize squirrel population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Sort population based on fitness (find trees hierarchy)
        sorted_indices = np.argsort(fitness)
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        # Track best solution (hickory nut tree)
        hickory_tree = population[0].copy()
        hickory_fitness = fitness[0]
        
        # Track second best (oak tree)
        oak_tree = population[1].copy() if len(population) > 1 else hickory_tree.copy()
        
        # History tracking
        global_fitness = [hickory_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Algorithm parameters
        Pdp = 0.1  # Predator presence probability
        
        for iteration in range(self.max_iterations):
            # Seasonal monitoring condition
            seasonal_constant = np.sqrt(np.sum((hickory_tree - oak_tree) ** 2))
            Sc = np.random.random()
            
            # Update acorn nut positions
            n_acorn = len(population) // 2  # Half population on acorn trees
            
            for i in range(n_acorn):
                if Sc >= seasonal_constant:
                    # Normal condition - move towards hickory tree
                    population[i] = np.random.random() * (hickory_tree - population[i])
                else:
                    # Seasonal monitoring - random movement
                    population[i] = np.random.uniform(bounds[0], bounds[1], dimension)
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Update normal nut positions
            for i in range(n_acorn, len(population)):
                if Sc >= seasonal_constant:
                    # Move towards oak tree
                    population[i] = np.random.random() * (oak_tree - population[i])
                else:
                    # Random movement
                    population[i] = np.random.uniform(bounds[0], bounds[1], dimension)
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Flying squirrel gliding behavior
            for i in range(len(population)):
                if np.random.random() < Pdp:
                    # Predator detected - random gliding
                    gliding_distance = np.random.exponential(1.0)
                    gliding_direction = np.random.uniform(-1, 1, dimension)
                    gliding_direction = gliding_direction / np.linalg.norm(gliding_direction)
                    
                    population[i] = population[i] + gliding_distance * gliding_direction
                    population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Re-sort population (update tree hierarchy)
            sorted_indices = np.argsort(fitness)
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            # Update best solutions
            if fitness[0] < hickory_fitness:
                hickory_tree = population[0].copy()
                hickory_fitness = fitness[0]
            
            if len(population) > 1:
                oak_tree = population[1].copy()
            
            # Track progress
            global_fitness.append(hickory_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return hickory_tree, hickory_fitness, global_fitness, local_fitness, local_positions