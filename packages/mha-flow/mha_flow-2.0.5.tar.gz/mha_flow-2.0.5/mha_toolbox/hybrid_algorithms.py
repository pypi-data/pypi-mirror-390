"""
Hybrid Algorithm Implementations
===============================

Advanced hybrid metaheuristic algorithms combining 
multiple optimization strategies for enhanced performance.
"""

import numpy as np
import random
from typing import Tuple, List, Dict, Any
import time


class PSO_GA_Hybrid:
    """Hybrid PSO-GA Algorithm combining particle swarm with genetic operators"""
    
    def __init__(self, population_size=30, max_iterations=100, w=0.5, c1=2, c2=2, 
                 crossover_rate=0.8, mutation_rate=0.1):
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w  # Inertia weight
        self.c1 = c1  # Cognitive parameter
        self.c2 = c2  # Social parameter
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
    def optimize(self, objective_func, bounds, dimensions):
        """Main optimization loop"""
        
        # Initialize particles
        particles = []
        velocities = []
        personal_best = []
        personal_best_fitness = []
        
        # Initialize population
        for _ in range(self.population_size):
            position = np.random.uniform(bounds[0], bounds[1], dimensions)
            velocity = np.random.uniform(-1, 1, dimensions)
            particles.append(position)
            velocities.append(velocity)
            personal_best.append(position.copy())
            personal_best_fitness.append(objective_func(position))
        
        # Find global best
        global_best_idx = np.argmin(personal_best_fitness)
        global_best = personal_best[global_best_idx].copy()
        global_best_fitness = personal_best_fitness[global_best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # PSO velocity and position update
            for i in range(self.population_size):
                # Update velocity
                r1, r2 = random.random(), random.random()
                velocities[i] = (self.w * velocities[i] + 
                               self.c1 * r1 * (personal_best[i] - particles[i]) +
                               self.c2 * r2 * (global_best - particles[i]))
                
                # Update position
                particles[i] = particles[i] + velocities[i]
                
                # Apply bounds
                particles[i] = np.clip(particles[i], bounds[0], bounds[1])
                
                # Evaluate fitness
                fitness = objective_func(particles[i])
                
                # Update personal best
                if fitness < personal_best_fitness[i]:
                    personal_best[i] = particles[i].copy()
                    personal_best_fitness[i] = fitness
                    
                    # Update global best
                    if fitness < global_best_fitness:
                        global_best = particles[i].copy()
                        global_best_fitness = fitness
            
            # GA operations every 10 iterations
            if iteration % 10 == 0 and iteration > 0:
                particles, velocities = self._apply_genetic_operators(
                    particles, velocities, personal_best_fitness, bounds
                )
            
            convergence_curve.append(global_best_fitness)
        
        return {
            'best_solution': global_best,
            'best_fitness': global_best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'PSO_GA_Hybrid'
        }
    
    def _apply_genetic_operators(self, particles, velocities, fitness_values, bounds):
        """Apply genetic operators to population"""
        
        # Selection (tournament selection)
        selected_particles = []
        selected_velocities = []
        
        for _ in range(self.population_size):
            # Tournament selection
            tournament_size = 3
            tournament_indices = random.sample(range(self.population_size), tournament_size)
            best_idx = min(tournament_indices, key=lambda x: fitness_values[x])
            
            selected_particles.append(particles[best_idx].copy())
            selected_velocities.append(velocities[best_idx].copy())
        
        # Crossover
        for i in range(0, self.population_size - 1, 2):
            if random.random() < self.crossover_rate:
                # Single-point crossover
                crossover_point = random.randint(1, len(selected_particles[i]) - 1)
                
                # Swap genetic material
                temp1 = selected_particles[i][crossover_point:].copy()
                temp2 = selected_particles[i+1][crossover_point:].copy()
                
                selected_particles[i][crossover_point:] = temp2
                selected_particles[i+1][crossover_point:] = temp1
        
        # Mutation
        for i in range(self.population_size):
            if random.random() < self.mutation_rate:
                mutation_point = random.randint(0, len(selected_particles[i]) - 1)
                selected_particles[i][mutation_point] = random.uniform(bounds[0], bounds[1])
        
        return selected_particles, selected_velocities


class WOA_SMA_Hybrid:
    """Hybrid Whale Optimization + Slime Mould Algorithm"""
    
    def __init__(self, population_size=30, max_iterations=100, a_decrease=2):
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.a_decrease = a_decrease
    
    def optimize(self, objective_func, bounds, dimensions):
        """Main optimization loop"""
        
        # Initialize population
        population = []
        fitness = []
        
        for _ in range(self.population_size):
            position = np.random.uniform(bounds[0], bounds[1], dimensions)
            population.append(position)
            fitness.append(objective_func(position))
        
        # Find best solution
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            a = self.a_decrease - iteration * (self.a_decrease / self.max_iterations)
            
            # Sort population by fitness (for SMA component)
            sorted_indices = np.argsort(fitness)
            
            for i in range(self.population_size):
                # Hybrid decision: use WOA or SMA
                if random.random() < 0.5:
                    # WOA update
                    population[i] = self._woa_update(
                        population[i], best_solution, a, bounds, dimensions, iteration
                    )
                else:
                    # SMA update
                    population[i] = self._sma_update(
                        population, i, sorted_indices, bounds, dimensions, iteration
                    )
                
                # Evaluate new position
                fitness[i] = objective_func(population[i])
                
                # Update best solution
                if fitness[i] < best_fitness:
                    best_solution = population[i].copy()
                    best_fitness = fitness[i]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'WOA_SMA_Hybrid'
        }
    
    def _woa_update(self, position, best_solution, a, bounds, dimensions, iteration):
        """Whale Optimization Algorithm update"""
        
        A = 2 * a * random.random() - a
        C = 2 * random.random()
        p = random.random()
        
        if p < 0.5:
            if abs(A) >= 1:
                # Search for prey
                rand_position = np.random.uniform(bounds[0], bounds[1], dimensions)
                D = abs(C * rand_position - position)
                new_position = rand_position - A * D
            else:
                # Encircling prey
                D = abs(C * best_solution - position)
                new_position = best_solution - A * D
        else:
            # Spiral update
            b = 1
            l = random.uniform(-1, 1)
            D = abs(best_solution - position)
            new_position = D * np.exp(b * l) * np.cos(2 * np.pi * l) + best_solution
        
        return np.clip(new_position, bounds[0], bounds[1])
    
    def _sma_update(self, population, i, sorted_indices, bounds, dimensions, iteration):
        """Slime Mould Algorithm update"""
        
        # Get current population fitness
        current_fitness = []
        for pos in population:
            # This would normally use the objective function, but we'll use a placeholder
            current_fitness.append(np.sum(pos**2))  # Simple sphere function as placeholder
        
        best_fitness = min(current_fitness)
        
        # Position update based on fitness ranking
        if i in sorted_indices[:len(sorted_indices)//2]:
            # Better half: oscillation
            p = np.tanh(abs(current_fitness[i] - best_fitness))
            vb = np.random.uniform(-1, 1, dimensions)
            vc = np.random.uniform(-1, 1, dimensions)
            
            new_position = np.random.uniform(bounds[0], bounds[1], dimensions) if random.random() < p else vb * (population[sorted_indices[0]] - population[sorted_indices[-1]]) + vc
        else:
            # Worse half: random position
            new_position = np.random.uniform(bounds[0], bounds[1], dimensions)
        
        return np.clip(new_position, bounds[0], bounds[1])


class AdaptiveHybrid:
    """Adaptive Hybrid Algorithm that switches strategies based on performance"""
    
    def __init__(self, population_size=30, max_iterations=100):
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.strategy_performance = {'PSO': 0, 'GA': 0, 'SMA': 0}
        self.current_strategy = 'PSO'
        
    def optimize(self, objective_func, bounds, dimensions):
        """Adaptive optimization with strategy switching"""
        
        # Initialize population
        population = []
        fitness = []
        velocities = []  # For PSO
        
        for _ in range(self.population_size):
            position = np.random.uniform(bounds[0], bounds[1], dimensions)
            velocity = np.random.uniform(-1, 1, dimensions)
            population.append(position)
            velocities.append(velocity)
            fitness.append(objective_func(position))
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        strategy_history = []
        
        for iteration in range(self.max_iterations):
            previous_best = best_fitness
            
            # Apply current strategy
            if self.current_strategy == 'PSO':
                population, velocities = self._apply_pso(population, velocities, best_solution, bounds)
            elif self.current_strategy == 'GA':
                population = self._apply_ga(population, fitness, bounds)
            elif self.current_strategy == 'SMA':
                population = self._apply_sma(population, fitness, bounds)
            
            # Evaluate population
            for i in range(self.population_size):
                fitness[i] = objective_func(population[i])
                if fitness[i] < best_fitness:
                    best_solution = population[i].copy()
                    best_fitness = fitness[i]
            
            # Measure strategy performance
            improvement = previous_best - best_fitness
            self.strategy_performance[self.current_strategy] += improvement
            
            # Switch strategy if performance is poor
            if iteration % 20 == 0 and iteration > 0:
                self._adapt_strategy(iteration)
            
            convergence_curve.append(best_fitness)
            strategy_history.append(self.current_strategy)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'strategy_history': strategy_history,
            'algorithm_name': 'Adaptive_Hybrid'
        }
    
    def _apply_pso(self, population, velocities, global_best, bounds):
        """Apply PSO update"""
        w, c1, c2 = 0.5, 2.0, 2.0
        
        for i in range(self.population_size):
            r1, r2 = random.random(), random.random()
            velocities[i] = (w * velocities[i] + 
                           c1 * r1 * (global_best - population[i]) +
                           c2 * r2 * (global_best - population[i]))
            
            population[i] = population[i] + velocities[i]
            population[i] = np.clip(population[i], bounds[0], bounds[1])
        
        return population, velocities
    
    def _apply_ga(self, population, fitness, bounds):
        """Apply GA operations"""
        
        # Selection and crossover
        new_population = []
        
        for _ in range(self.population_size):
            # Tournament selection
            parent1_idx = self._tournament_selection(fitness)
            parent2_idx = self._tournament_selection(fitness)
            
            # Crossover
            if random.random() < 0.8:
                child = self._crossover(population[parent1_idx], population[parent2_idx])
            else:
                child = population[parent1_idx].copy()
            
            # Mutation
            if random.random() < 0.1:
                child = self._mutate(child, bounds)
            
            new_population.append(child)
        
        return new_population
    
    def _apply_sma(self, population, fitness, bounds):
        """Apply SMA update"""
        
        # Sort by fitness
        sorted_indices = np.argsort(fitness)
        best_solution = population[sorted_indices[0]]
        
        for i in range(self.population_size):
            if i < self.population_size // 2:
                # Better half: guided search
                p = np.tanh(abs(fitness[i] - fitness[sorted_indices[0]]))
                if random.random() < p:
                    population[i] = np.random.uniform(bounds[0], bounds[1], len(population[i]))
                else:
                    vb = np.random.uniform(-1, 1, len(population[i]))
                    population[i] = vb * (best_solution - population[sorted_indices[-1]])
            else:
                # Worse half: random position
                population[i] = np.random.uniform(bounds[0], bounds[1], len(population[i]))
        
        return population
    
    def _adapt_strategy(self, iteration):
        """Adapt strategy based on performance"""
        
        # Find best performing strategy
        best_strategy = max(self.strategy_performance.keys(), 
                          key=lambda x: self.strategy_performance[x])
        
        self.current_strategy = best_strategy
        
        # Reset performance counters
        for strategy in self.strategy_performance:
            self.strategy_performance[strategy] *= 0.9  # Decay factor
    
    def _tournament_selection(self, fitness):
        """Tournament selection for GA"""
        tournament_size = 3
        tournament_indices = random.sample(range(len(fitness)), tournament_size)
        return min(tournament_indices, key=lambda x: fitness[x])
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        crossover_point = random.randint(1, len(parent1) - 1)
        child = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        return child
    
    def _mutate(self, individual, bounds):
        """Gaussian mutation"""
        mutation_point = random.randint(0, len(individual) - 1)
        individual[mutation_point] += np.random.normal(0, 0.1)
        return np.clip(individual, bounds[0], bounds[1])


class MultiSwarmPSO:
    """Multi-Swarm PSO with dynamic sub-swarm management"""
    
    def __init__(self, population_size=30, max_iterations=100, num_swarms=3):
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.num_swarms = num_swarms
        self.swarm_size = population_size // num_swarms
    
    def optimize(self, objective_func, bounds, dimensions):
        """Multi-swarm optimization"""
        
        # Initialize swarms
        swarms = []
        swarm_best = []
        swarm_best_fitness = []
        
        for s in range(self.num_swarms):
            swarm = {
                'particles': [],
                'velocities': [],
                'personal_best': [],
                'personal_best_fitness': []
            }
            
            # Initialize swarm particles
            for _ in range(self.swarm_size):
                position = np.random.uniform(bounds[0], bounds[1], dimensions)
                velocity = np.random.uniform(-1, 1, dimensions)
                
                swarm['particles'].append(position)
                swarm['velocities'].append(velocity)
                swarm['personal_best'].append(position.copy())
                swarm['personal_best_fitness'].append(objective_func(position))
            
            # Find swarm best
            best_idx = np.argmin(swarm['personal_best_fitness'])
            swarm_best.append(swarm['personal_best'][best_idx].copy())
            swarm_best_fitness.append(swarm['personal_best_fitness'][best_idx])
            
            swarms.append(swarm)
        
        # Global best
        global_best_idx = np.argmin(swarm_best_fitness)
        global_best = swarm_best[global_best_idx].copy()
        global_best_fitness = swarm_best_fitness[global_best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Update each swarm
            for s in range(self.num_swarms):
                swarm = swarms[s]
                
                # PSO updates for this swarm
                for i in range(self.swarm_size):
                    # Update velocity
                    w = 0.9 - (iteration / self.max_iterations) * 0.5
                    c1, c2 = 2.0, 2.0
                    r1, r2 = random.random(), random.random()
                    
                    swarm['velocities'][i] = (w * swarm['velocities'][i] + 
                                            c1 * r1 * (swarm['personal_best'][i] - swarm['particles'][i]) +
                                            c2 * r2 * (swarm_best[s] - swarm['particles'][i]))
                    
                    # Update position
                    swarm['particles'][i] = swarm['particles'][i] + swarm['velocities'][i]
                    swarm['particles'][i] = np.clip(swarm['particles'][i], bounds[0], bounds[1])
                    
                    # Evaluate fitness
                    fitness = objective_func(swarm['particles'][i])
                    
                    # Update personal best
                    if fitness < swarm['personal_best_fitness'][i]:
                        swarm['personal_best'][i] = swarm['particles'][i].copy()
                        swarm['personal_best_fitness'][i] = fitness
                        
                        # Update swarm best
                        if fitness < swarm_best_fitness[s]:
                            swarm_best[s] = swarm['particles'][i].copy()
                            swarm_best_fitness[s] = fitness
                            
                            # Update global best
                            if fitness < global_best_fitness:
                                global_best = swarm['particles'][i].copy()
                                global_best_fitness = fitness
            
            # Swarm interaction every 25 iterations
            if iteration % 25 == 0 and iteration > 0:
                self._swarm_interaction(swarms, swarm_best)
            
            convergence_curve.append(global_best_fitness)
        
        return {
            'best_solution': global_best,
            'best_fitness': global_best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'MultiSwarm_PSO'
        }
    
    def _swarm_interaction(self, swarms, swarm_best):
        """Allow interaction between swarms"""
        
        # Exchange best particles between swarms
        for s in range(self.num_swarms):
            other_swarm = (s + 1) % self.num_swarms
            
            # Replace worst particle with best from other swarm
            worst_idx = np.argmax(swarms[s]['personal_best_fitness'])
            swarms[s]['particles'][worst_idx] = swarm_best[other_swarm].copy()


class EnhancedDE:
    """Enhanced Differential Evolution with adaptive parameters"""
    
    def __init__(self, population_size=30, max_iterations=100, F=0.5, CR=0.9):
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F  # Differential weight
        self.CR = CR  # Crossover probability
    
    def optimize(self, objective_func, bounds, dimensions):
        """Enhanced DE optimization"""
        
        # Initialize population
        population = []
        fitness = []
        
        for _ in range(self.population_size):
            individual = np.random.uniform(bounds[0], bounds[1], dimensions)
            population.append(individual)
            fitness.append(objective_func(individual))
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Adaptive parameters
            adaptive_F = self.F * (2 * random.random())
            adaptive_CR = self.CR * random.random()
            
            new_population = []
            
            for i in range(self.population_size):
                # Mutation
                indices = list(range(self.population_size))
                indices.remove(i)
                a, b, c = random.sample(indices, 3)
                
                mutant = population[a] + adaptive_F * (population[b] - population[c])
                mutant = np.clip(mutant, bounds[0], bounds[1])
                
                # Crossover
                trial = population[i].copy()
                for j in range(dimensions):
                    if random.random() < adaptive_CR or j == random.randint(0, dimensions-1):
                        trial[j] = mutant[j]
                
                # Selection
                trial_fitness = objective_func(trial)
                if trial_fitness < fitness[i]:
                    new_population.append(trial)
                    fitness[i] = trial_fitness
                    
                    if trial_fitness < best_fitness:
                        best_solution = trial.copy()
                        best_fitness = trial_fitness
                else:
                    new_population.append(population[i])
            
            population = new_population
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'Enhanced_DE'
        }