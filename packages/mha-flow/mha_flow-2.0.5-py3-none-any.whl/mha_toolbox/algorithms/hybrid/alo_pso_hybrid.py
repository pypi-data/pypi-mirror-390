"""
ALO-PSO Hybrid: Ant Lion Optimizer + PSO
========================================

Best for: Trap-prone landscapes and local optima avoidance
Combines ant lion trapping behavior with PSO velocity updates
"""

import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer


class ALO_PSO_Hybrid(BaseOptimizer):
    """
    ALO-PSO Hybrid: Ant Lion Optimizer + PSO
    
    Parameters:
    -----------
    w, c1, c2 : float
        PSO inertia weight and cognitive/social coefficients
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # Initialize ants and antlions
        self.ants = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                     (population_size, dimensions))
        self.antlions = self.ants.copy()
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        
        self.ant_fitness = np.array([objective_function(ant) for ant in self.ants])
        self.antlion_fitness = self.ant_fitness.copy()
        
        # Elite antlion (best solution)
        self.elite_idx = np.argmin(self.antlion_fitness)
        self.elite = self.antlions[self.elite_idx].copy()
        self.elite_fitness = self.antlion_fitness[self.elite_idx]
        
        # Personal best for PSO
        self.pbest = self.ants.copy()
        self.pbest_fitness = self.ant_fitness.copy()
        self.convergence_curve = []
        
    def _random_walk(self, antlion_pos, iteration):
        """Perform random walk around antlion with adaptive bounds"""
        # Convergence factor
        c = iteration / self.max_iterations
        
        # Adaptive bounds shrinking towards antlion
        lb = self.bounds[:, 0] * (1 - c) + antlion_pos * c
        ub = self.bounds[:, 1] * (1 - c) + antlion_pos * c
        
        # Random walk: cumulative sum of random steps
        walk = np.cumsum(2 * (np.random.random(self.dimensions) > 0.5) - 1)
        
        # Normalize walk to fit within adaptive bounds
        walk = (walk - walk.min()) / (walk.max() - walk.min() + 1e-10)
        walk = walk * (ub - lb) + lb
        
        return walk
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run ALO-PSO hybrid optimization"""
        for iteration in range(self.max_iterations):
            # ALO phase - ant movement guided by antlions
            for i in range(self.population_size):
                # Roulette wheel selection of antlion (better fitness = higher probability)
                fitness_inv = 1.0 / (self.antlion_fitness + 1e-10)
                probs = fitness_inv / np.sum(fitness_inv)
                selected_antlion_idx = np.random.choice(self.population_size, p=probs)
                
                # Random walk around selected antlion
                RA = self._random_walk(self.antlions[selected_antlion_idx], iteration)
                
                # Random walk around elite
                RE = self._random_walk(self.elite, iteration)
                
                # Combine both random walks
                self.ants[i] = (RA + RE) / 2
                self.ants[i] = np.clip(self.ants[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate ant position
                self.ant_fitness[i] = self.objective_function(self.ants[i])
                
                # Ant catches antlion if fitter (antlion updates position)
                if self.ant_fitness[i] < self.antlion_fitness[i]:
                    self.antlions[i] = self.ants[i].copy()
                    self.antlion_fitness[i] = self.ant_fitness[i]
            
            # PSO phase - apply every 3 iterations for velocity guidance
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    r1, r2 = np.random.random(2)
                    
                    # PSO velocity update equation
                    self.velocities[i] = (self.w * self.velocities[i] +
                                        self.c1 * r1 * (self.pbest[i] - self.ants[i]) +
                                        self.c2 * r2 * (self.elite - self.ants[i]))
                    
                    # Update ant position using velocity
                    self.ants[i] += self.velocities[i]
                    self.ants[i] = np.clip(self.ants[i], self.bounds[:, 0], self.bounds[:, 1])
                    
                    # Re-evaluate
                    self.ant_fitness[i] = self.objective_function(self.ants[i])
                    
                    # Update personal best
                    if self.ant_fitness[i] < self.pbest_fitness[i]:
                        self.pbest[i] = self.ants[i].copy()
                        self.pbest_fitness[i] = self.ant_fitness[i]
            
            # Update elite (global best)
            current_best_idx = np.argmin(self.antlion_fitness)
            if self.antlion_fitness[current_best_idx] < self.elite_fitness:
                self.elite_idx = current_best_idx
                self.elite = self.antlions[current_best_idx].copy()
                self.elite_fitness = self.antlion_fitness[current_best_idx]
            
            self.convergence_curve.append(self.elite_fitness)
        
        return self.elite, self.elite_fitness, self.convergence_curve
