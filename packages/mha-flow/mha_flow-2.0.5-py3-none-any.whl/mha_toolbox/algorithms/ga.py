"""
Genetic Algorithm (GA)

Based on: Holland, J. H. (1992). Genetic algorithms. Scientific American, 267(1), 66-72.
"""

import numpy as np
from ..base import BaseOptimizer


class GeneticAlgorithm(BaseOptimizer):
    """
    Genetic Algorithm (GA)
    
    GA is inspired by the process of natural selection and genetics.
    Solutions evolve through selection, crossover, and mutation operations.
    
    Parameters
    ----------
    crossover_rate : float, default=0.8
        Probability of crossover between two parents
    mutation_rate : float, default=0.1
        Probability of mutation for each gene
    elite_rate : float, default=0.1
        Percentage of best individuals to keep in next generation
    """
    
    aliases = ["ga", "genetic", "genetic_algorithm"]
    
    def __init__(self, crossover_rate=0.8, mutation_rate=0.1, elite_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_rate = elite_rate
        self.algorithm_name = "GA"
    
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
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        global_fitness = []
        local_fitness = []
        local_positions = []
        elite_count = max(1, int(self.elite_rate * self.population_size_))
        for iteration in range(self.max_iterations_):
            fitness = np.array([objective_function(ind) for ind in population])
            sorted_indices = np.argsort(fitness)
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            global_fitness.append(fitness[0])
            local_fitness.append(fitness.tolist())
            local_positions.append([ind.copy() for ind in population])
            new_population = np.zeros_like(population)
            new_population[:elite_count] = population[:elite_count]
            for i in range(elite_count, self.population_size_):
                parent1 = self._tournament_selection(population, fitness)
                parent2 = self._tournament_selection(population, fitness)
                if np.random.random() < self.crossover_rate:
                    offspring = self._crossover(parent1, parent2)
                else:
                    offspring = parent1.copy()
                offspring = self._mutate(offspring)
                new_population[i] = offspring
            population = new_population
        final_fitness = np.array([objective_function(ind) for ind in population])
        best_idx = np.argmin(final_fitness)
        return population[best_idx], final_fitness[best_idx], global_fitness, local_fitness, local_positions
    
    def _tournament_selection(self, population, fitness, tournament_size=3):
        """Tournament selection"""
        # Ensure we have a valid population
        if len(population) == 0:
            raise ValueError("Population is empty")
        
        # Ensure tournament size doesn't exceed population size
        tournament_size = min(tournament_size, len(population))
        tournament_size = max(1, tournament_size)  # Ensure at least 1
        
        if tournament_size == 1:
            # If tournament size is 1, just return a random individual
            idx = np.random.randint(0, len(population))
            return population[idx].copy()
        
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = fitness[tournament_indices]
        winner_idx = tournament_indices[np.argmin(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        crossover_point = np.random.randint(1, len(parent1))
        offspring = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        return offspring
    
    def _mutate(self, individual):
        """Gaussian mutation"""
        for i in range(len(individual)):
            if np.random.random() < self.mutation_rate:
                if hasattr(self, 'upper_bound_') and hasattr(self, 'lower_bound_'):
                    # Handle both scalar and array bounds safely
                    if hasattr(self.upper_bound_, '__len__') and len(self.upper_bound_) > i:
                        ub = self.upper_bound_[i]
                    else:
                        ub = self.upper_bound_ if np.isscalar(self.upper_bound_) else self.upper_bound_[0]
                    
                    if hasattr(self.lower_bound_, '__len__') and len(self.lower_bound_) > i:
                        lb = self.lower_bound_[i]
                    else:
                        lb = self.lower_bound_ if np.isscalar(self.lower_bound_) else self.lower_bound_[0]
                        
                    mutation_range = abs(ub - lb)
                else:
                    mutation_range = 2.0
                    
                individual[i] += np.random.normal(0, 0.1 * mutation_range)
                
                if hasattr(self, 'upper_bound_') and hasattr(self, 'lower_bound_'):
                    if hasattr(self.upper_bound_, '__len__') and len(self.upper_bound_) > i:
                        ub = self.upper_bound_[i]
                    else:
                        ub = self.upper_bound_ if np.isscalar(self.upper_bound_) else self.upper_bound_[0]
                    
                    if hasattr(self.lower_bound_, '__len__') and len(self.lower_bound_) > i:
                        lb = self.lower_bound_[i]
                    else:
                        lb = self.lower_bound_ if np.isscalar(self.lower_bound_) else self.lower_bound_[0]
                        
                    individual[i] = np.clip(individual[i], lb, ub)
        return individual
