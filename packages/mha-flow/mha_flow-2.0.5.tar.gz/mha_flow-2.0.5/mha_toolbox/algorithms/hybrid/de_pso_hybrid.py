"""
Differential Evolution - Particle Swarm Optimization Hybrid (DE-PSO)
====================================================================

Hybrid algorithm combining Differential Evolution and Particle Swarm Optimization
for enhanced global and local search capabilities.
"""

import numpy as np
from ...base import BaseOptimizer


class DifferentialEvolutionPSOHybrid(BaseOptimizer):
    """
    DE-PSO Hybrid Algorithm
    
    Combines the differential mutation of DE with the velocity-based
    movement of PSO for improved optimization performance.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "DE-PSO Hybrid"
        self.aliases = ["de_pso", "differential_pso", "de_pso_hybrid"]
        self.F = 0.5  # DE scaling factor
        self.CR = 0.9  # DE crossover rate
        self.w = 0.7  # PSO inertia weight
        self.c1 = 1.5  # PSO cognitive parameter
        self.c2 = 1.5  # PSO social parameter
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the DE-PSO Hybrid Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize population and velocities
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        velocities = np.random.uniform(-1, 1, (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Initialize personal best positions
        personal_best = population.copy()
        personal_best_fitness = fitness.copy()
        
        # Track global best solution
        best_idx = np.argmin(fitness)
        global_best = population[best_idx].copy()
        global_best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [global_best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Adaptive parameters
            w_adaptive = self.w * (1 - iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # DE Mutation
                # Select three random individuals different from current
                candidates = list(range(self.population_size))
                candidates.remove(i)
                a, b, c = np.random.choice(candidates, 3, replace=False)
                
                # Mutant vector
                mutant = population[a] + self.F * (population[b] - population[c])
                mutant = np.clip(mutant, bounds[0], bounds[1])
                
                # DE Crossover
                trial = population[i].copy()
                crossover_points = np.random.random(dimension) < self.CR
                trial[crossover_points] = mutant[crossover_points]
                
                # Ensure at least one parameter is from mutant
                if not np.any(crossover_points):
                    trial[np.random.randint(dimension)] = mutant[np.random.randint(dimension)]
                
                # PSO Velocity Update
                r1, r2 = np.random.random(2)
                velocities[i] = (w_adaptive * velocities[i] + 
                                self.c1 * r1 * (personal_best[i] - population[i]) +
                                self.c2 * r2 * (global_best - population[i]))
                
                # PSO Position Update
                pso_position = population[i] + velocities[i]
                pso_position = np.clip(pso_position, bounds[0], bounds[1])
                
                # Hybrid Selection: Choose better between DE trial and PSO position
                trial_fitness = objective_function(trial)
                pso_fitness = objective_function(pso_position)
                
                if trial_fitness < pso_fitness:
                    new_position = trial
                    new_fitness = trial_fitness
                else:
                    new_position = pso_position
                    new_fitness = pso_fitness
                
                # Selection: Replace if better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
                    
                    # Update personal best
                    if new_fitness < personal_best_fitness[i]:
                        personal_best[i] = new_position.copy()
                        personal_best_fitness[i] = new_fitness
                        
                        # Update global best
                        if new_fitness < global_best_fitness:
                            global_best = new_position.copy()
                            global_best_fitness = new_fitness
            
            # Track progress
            global_fitness.append(global_best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return global_best, global_best_fitness, global_fitness, local_fitness, local_positions