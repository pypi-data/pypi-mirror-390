"""
Multi-Strategy Adaptive Hybrid Algorithm
=========================================
Combines 4 algorithms adaptively based on performance:
- PSO (Particle Swarm Optimization)
- GWO (Grey Wolf Optimizer)
- WOA (Whale Optimization Algorithm)
- SCA (Sine Cosine Algorithm)

The algorithm adapts which strategy to use based on improvement rate.
"""

import numpy as np
from ...base import BaseOptimizer

class Adaptive_Multi_Strategy_Hybrid(BaseOptimizer):
    """
    Adaptive Multi-Strategy Hybrid Algorithm (AMSHA)
    
    Dynamically switches between 4 metaheuristic strategies based on:
    - Recent improvement rate
    - Diversity of population
    - Current iteration phase
    
    Strategies:
    1. PSO: For fast convergence
    2. GWO: For exploitation
    3. WOA: For exploration
    4. SCA: For escaping local optima
    
    Parameters:
    -----------
    population_size : int, default=40
        Number of search agents
    max_iterations : int, default=100
        Maximum iterations
    switch_threshold : float, default=0.01
        Improvement threshold for strategy switching
    """
    
    def __init__(self, population_size=40, max_iterations=100, 
                 switch_threshold=0.01, **kwargs):
        super().__init__(population_size, max_iterations, **kwargs)
        self.switch_threshold = switch_threshold
        self.algorithm_name = "Adaptive_Multi_Strategy_Hybrid"
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Execute adaptive multi-strategy optimization"""
        # Determine dimensions and bounds
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        # Initialize population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        velocities = np.random.uniform(-1, 1, (self.population_size_, dimensions))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Personal and global best
        personal_best = population.copy()
        personal_best_fitness = fitness.copy()
        best_idx = np.argmin(fitness)
        global_best = population[best_idx].copy()
        global_best_fitness = fitness[best_idx]
        
        # Strategy performance tracking
        strategy_improvements = {
            'pso': [],
            'gwo': [],
            'woa': [],
            'sca': []
        }
        current_strategy = 'pso'
        stagnation_counter = 0
        prev_best = global_best_fitness
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations_):
            # Calculate diversity
            population = np.clip(population, bounds[0], bounds[1])
            diversity = np.mean(np.std(population, axis=0))
            diversity = np.mean(np.std(population, axis=0))
            
            # Calculate improvement rate
            improvement = prev_best - global_best_fitness
            improvement_rate = improvement / (abs(prev_best) + 1e-10)
            
            # Adaptive strategy selection
            if improvement_rate < self.switch_threshold:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
            
            # Switch strategy if stagnating
            if stagnation_counter > 5:
                # Choose best performing strategy
                avg_improvements = {
                    k: np.mean(v[-10:]) if v else 0 
                    for k, v in strategy_improvements.items()
                }
                current_strategy = max(avg_improvements, key=avg_improvements.get)
                stagnation_counter = 0
            
            # Store current best for comparison
            old_best = global_best_fitness
            
            # Execute selected strategy
            if current_strategy == 'pso':
                population, velocities = self._pso_update(
                    population, velocities, personal_best, global_best, iteration
                )
            elif current_strategy == 'gwo':
                population = self._gwo_update(population, fitness, iteration)
            elif current_strategy == 'woa':
                population = self._woa_update(population, global_best, iteration)
            else:  # sca
                population = self._sca_update(population, global_best, iteration)
            
            # Evaluate
            population = np.clip(population, bounds[0], bounds[1])
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update personal best
            better_mask = fitness < personal_best_fitness
            personal_best[better_mask] = population[better_mask].copy()
            personal_best_fitness[better_mask] = fitness[better_mask]
            
            # Update global best
            best_idx = np.argmin(personal_best_fitness)
            if personal_best_fitness[best_idx] < global_best_fitness:
                prev_best = global_best_fitness
                global_best = personal_best[best_idx].copy()
                global_best_fitness = personal_best_fitness[best_idx]
            
            # Track strategy performance
            strategy_improvement = old_best - global_best_fitness
            strategy_improvements[current_strategy].append(strategy_improvement)
            
            convergence_curve.append(global_best_fitness)
            
            if self.verbose_ and iteration % 10 == 0:
                print(f"Iter {iteration}: Strategy={current_strategy.upper()}, "
                      f"Fitness={global_best_fitness:.6f}, "
                      f"Diversity={diversity:.4f}")
        
        # Create local fitness and positions arrays for compatibility
        local_fitness = convergence_curve.copy()
        local_positions = population.copy()
        
        return global_best, global_best_fitness, convergence_curve, local_fitness, local_positions
    
    def _pso_update(self, population, velocities, personal_best, global_best, iteration):
        """PSO velocity-position update"""
        w = 0.9 - (iteration / self.max_iterations_) * 0.5
        c1, c2 = 2.0, 2.0
        
        for i in range(self.population_size_):
            r1, r2 = np.random.rand(2)
            cognitive = c1 * r1 * (personal_best[i] - population[i])
            social = c2 * r2 * (global_best - population[i])
            velocities[i] = w * velocities[i] + cognitive + social
            population[i] = population[i] + velocities[i]
        
        return population, velocities
    
    def _gwo_update(self, population, fitness, iteration):
        """GWO hierarchical update"""
        a = 2 - iteration * (2.0 / self.max_iterations_)
        sorted_indices = np.argsort(fitness)
        alpha = population[sorted_indices[0]]
        beta = population[sorted_indices[1]]
        delta = population[sorted_indices[2]]
        
        dimensions = population.shape[1]
        
        for i in range(self.population_size_):
            A1 = 2 * a * np.random.rand(dimensions) - a
            C1 = 2 * np.random.rand(dimensions)
            D_alpha = abs(C1 * alpha - population[i])
            X1 = alpha - A1 * D_alpha
            
            A2 = 2 * a * np.random.rand(dimensions) - a
            C2 = 2 * np.random.rand(dimensions)
            D_beta = abs(C2 * beta - population[i])
            X2 = beta - A2 * D_beta
            
            A3 = 2 * a * np.random.rand(dimensions) - a
            C3 = 2 * np.random.rand(dimensions)
            D_delta = abs(C3 * delta - population[i])
            X3 = delta - A3 * D_delta
            
            population[i] = (X1 + X2 + X3) / 3.0
        
        return population
    
    def _woa_update(self, population, global_best, iteration):
        """WOA spiral and encircling update"""
        a = 2 - iteration * (2.0 / self.max_iterations_)
        b = 1
        l = np.random.uniform(-1, 1)
        
        for i in range(self.population_size_):
            r = np.random.rand()
            A = 2 * a * r - a
            C = 2 * np.random.rand()
            p = np.random.rand()
            
            if p < 0.5:
                if abs(A) < 1:
                    D = abs(C * global_best - population[i])
                    population[i] = global_best - A * D
                else:
                    rand_idx = np.random.randint(0, self.population_size_)
                    X_rand = population[rand_idx]
                    D = abs(C * X_rand - population[i])
                    population[i] = X_rand - A * D
            else:
                D = abs(global_best - population[i])
                population[i] = D * np.exp(b * l) * np.cos(2 * np.pi * l) + global_best
        
        return population
    
    def _sca_update(self, population, global_best, iteration):
        """SCA sine-cosine update"""
        a = 2 - iteration * (2.0 / self.max_iterations_)
        dimensions = population.shape[1]
        
        for i in range(self.population_size_):
            r1 = a - iteration * (a / self.max_iterations_)
            r2 = 2 * np.pi * np.random.rand(dimensions)
            r3 = 2 * np.random.rand(dimensions)
            r4 = np.random.rand(dimensions)
            
            mask = r4 < 0.5
            population[i, mask] = population[i, mask] + r1 * np.sin(r2[mask]) * abs(
                r3[mask] * global_best[mask] - population[i, mask]
            )
            population[i, ~mask] = population[i, ~mask] + r1 * np.cos(r2[~mask]) * abs(
                r3[~mask] * global_best[~mask] - population[i, ~mask]
            )
        
        return population
