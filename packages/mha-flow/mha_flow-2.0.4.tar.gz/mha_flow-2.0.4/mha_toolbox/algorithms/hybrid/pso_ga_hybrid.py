"""
PSO-GA Hybrid Algorithm

A hybrid algorithm combining Particle Swarm Optimization and Genetic Algorithm.
"""

import numpy as np
from ...base import BaseOptimizer


class PSO_GA_Hybrid(BaseOptimizer):
    """
    PSO-GA Hybrid Algorithm
    
    This algorithm combines the exploration capability of PSO with the exploitation
    capability of GA by alternating between PSO updates and genetic operations.
    
    Parameters
    ----------
    w : float, default=0.9
        PSO inertia weight
    c1 : float, default=2.0
        PSO cognitive coefficient
    c2 : float, default=2.0
        PSO social coefficient
    crossover_rate : float, default=0.8
        GA crossover probability
    mutation_rate : float, default=0.1
        GA mutation probability
    hybrid_rate : int, default=10
        Number of PSO iterations before applying GA operations
    """
    
    aliases = ["pso_ga", "pso_ga_hybrid", "hybrid_pso_ga"]
    
    def __init__(self, w=0.9, c1=2.0, c2=2.0, crossover_rate=0.8, mutation_rate=0.1, hybrid_rate=10, **kwargs):
        super().__init__(**kwargs)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.hybrid_rate = hybrid_rate
        self.algorithm_name = "PSO_GA_Hybrid"
    
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
        
        # Initialize particles
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Initialize velocities for PSO
        velocity = np.random.uniform(-1, 1, (self.population_size_, self.dimensions_))
        
        # Initialize personal bests
        personal_best = population.copy()
        personal_best_fitness = np.array([objective_function(ind) for ind in population])
        
        # Find global best
        global_best_idx = np.argmin(personal_best_fitness)
        global_best = personal_best[global_best_idx].copy()
        global_best_fitness = personal_best_fitness[global_best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # PSO Update Phase
            for i in range(self.population_size_):
                r1, r2 = np.random.random(2)
                
                # Update velocity
                velocity[i] = (self.w * velocity[i] + 
                             self.c1 * r1 * (personal_best[i] - population[i]) +
                             self.c2 * r2 * (global_best - population[i]))
                
                # Update position
                population[i] = population[i] + velocity[i]
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                
                # Evaluate fitness
                fitness = objective_function(population[i])
                
                # Update personal best
                if fitness < personal_best_fitness[i]:
                    personal_best[i] = population[i].copy()
                    personal_best_fitness[i] = fitness
                    
                    # Update global best
                    if fitness < global_best_fitness:
                        global_best = population[i].copy()
                        global_best_fitness = fitness
                
                fitnesses.append(fitness)
                positions.append(population[i].copy())
            
            # Apply GA operations every hybrid_rate iterations
            if iteration % self.hybrid_rate == 0 and iteration > 0:
                population = self._apply_genetic_operations(population, personal_best_fitness, objective_function)
                
                # Re-evaluate fitness after genetic operations
                for i in range(self.population_size_):
                    fitness = objective_function(population[i])
                    
                    # Update personal best
                    if fitness < personal_best_fitness[i]:
                        personal_best[i] = population[i].copy()
                        personal_best_fitness[i] = fitness
                        
                        # Update global best
                        if fitness < global_best_fitness:
                            global_best = population[i].copy()
                            global_best_fitness = fitness
            
            global_fitness.append(global_best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return global_best, global_best_fitness, global_fitness, local_fitness, local_positions
    
    def _apply_genetic_operations(self, population, fitness, objective_function):
        """Apply genetic algorithm operations"""
        new_population = []
        
        for _ in range(self.population_size_):
            # Tournament selection
            parent1 = self._tournament_selection(population, fitness)
            parent2 = self._tournament_selection(population, fitness)
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()
            
            # Mutation
            if np.random.random() < self.mutation_rate:
                child = self._mutate(child)
            
            new_population.append(child)
        
        return np.array(new_population)
    
    def _tournament_selection(self, population, fitness, tournament_size=3):
        """Tournament selection"""
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        best_idx = tournament_indices[np.argmin([fitness[i] for i in tournament_indices])]
        return population[best_idx].copy()
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        crossover_point = np.random.randint(1, len(parent1))
        child = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        return child
    
    def _mutate(self, individual):
        """Gaussian mutation"""
        mutation_point = np.random.randint(0, len(individual))
        individual[mutation_point] = np.random.uniform(self.lower_bound_[mutation_point], 
                                                      self.upper_bound_[mutation_point])
        return individual