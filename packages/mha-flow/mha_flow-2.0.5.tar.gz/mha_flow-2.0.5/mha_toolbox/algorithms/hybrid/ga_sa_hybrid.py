"""
Genetic Algorithm - Simulated Annealing Hybrid (GA-SA)
=====================================================

Hybrid algorithm combining Genetic Algorithm and Simulated Annealing
for enhanced exploration and exploitation capabilities.
"""

import numpy as np
from ...base import BaseOptimizer


class GeneticSimulatedAnnealingHybrid(BaseOptimizer):
    """
    GA-SA Hybrid Algorithm
    
    Combines the population-based search of GA with the local search
    capabilities of Simulated Annealing for improved performance.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "GA-SA Hybrid"
        self.aliases = ["ga_sa", "genetic_annealing", "ga_sa_hybrid"]
        self.crossover_rate = 0.8
        self.mutation_rate = 0.1
        self.initial_temp = 100.0
        self.cooling_rate = 0.95
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the GA-SA Hybrid Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Initialize temperature for SA
        temperature = self.initial_temp
        
        for iteration in range(self.max_iterations):
            # GA Operations
            new_population = []
            
            # Selection, Crossover, and Mutation
            for _ in range(self.population_size // 2):
                # Tournament selection
                parent1 = self.tournament_selection(population, fitness)
                parent2 = self.tournament_selection(population, fitness)
                
                # Crossover
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if np.random.random() < self.mutation_rate:
                    child1 = self.mutate(child1, bounds)
                if np.random.random() < self.mutation_rate:
                    child2 = self.mutate(child2, bounds)
                
                new_population.extend([child1, child2])
            
            # Ensure exact population size
            if len(new_population) > self.population_size:
                new_population = new_population[:self.population_size]
            
            new_population = np.array(new_population)
            
            # SA Local Search on best individuals
            elite_count = self.population_size // 4  # Top 25% individuals
            sorted_indices = np.argsort(fitness)
            
            for i in range(elite_count):
                elite_idx = sorted_indices[i]
                elite_solution = new_population[elite_idx].copy()
                
                # SA local search
                improved_solution = self.simulated_annealing_local_search(
                    elite_solution, objective_function, bounds, temperature
                )
                new_population[elite_idx] = improved_solution
            
            # Update population
            population = new_population
            
            # Apply bounds
            population = np.clip(population, bounds[0], bounds[1])
            
            # Evaluate new population
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Cool down temperature
            temperature *= self.cooling_rate
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions
    
    def tournament_selection(self, population, fitness, tournament_size=3):
        """Tournament selection for parent selection"""
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = fitness[tournament_indices]
        winner_idx = tournament_indices[np.argmin(tournament_fitness)]
        return population[winner_idx].copy()
    
    def crossover(self, parent1, parent2):
        """Arithmetic crossover"""
        alpha = np.random.random()
        child1 = alpha * parent1 + (1 - alpha) * parent2
        child2 = (1 - alpha) * parent1 + alpha * parent2
        return child1, child2
    
    def mutate(self, individual, bounds):
        """Gaussian mutation"""
        mutation_strength = 0.1
        mutation = np.random.normal(0, mutation_strength, len(individual))
        mutated = individual + mutation
        return np.clip(mutated, bounds[0], bounds[1])
    
    def simulated_annealing_local_search(self, solution, objective_function, bounds, temperature):
        """Local search using simulated annealing"""
        current_solution = solution.copy()
        current_fitness = objective_function(current_solution)
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        # Local search iterations
        for _ in range(10):  # Limited local search
            # Generate neighbor
            step_size = 0.1 * (bounds[1] - bounds[0])
            neighbor = current_solution + np.random.normal(0, step_size, len(solution))
            neighbor = np.clip(neighbor, bounds[0], bounds[1])
            
            neighbor_fitness = objective_function(neighbor)
            
            # Accept or reject based on SA criteria
            if neighbor_fitness < current_fitness:
                current_solution = neighbor.copy()
                current_fitness = neighbor_fitness
                
                if neighbor_fitness < best_fitness:
                    best_solution = neighbor.copy()
                    best_fitness = neighbor_fitness
            else:
                # Accept worse solution with probability
                if temperature > 0:
                    delta = neighbor_fitness - current_fitness
                    probability = np.exp(-delta / temperature)
                    if np.random.random() < probability:
                        current_solution = neighbor.copy()
                        current_fitness = neighbor_fitness
        
        return best_solution