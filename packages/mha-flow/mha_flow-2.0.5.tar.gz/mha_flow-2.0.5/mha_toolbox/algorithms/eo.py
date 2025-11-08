"""
Equilibrium Optimizer (EO) Algorithm

A physics-inspired optimization algorithm based on control volume mass balance
used to estimate both dynamic and equilibrium states.

Reference:
Faramarzi, A., Heidarinejad, M., Stephens, B., & Mirjalili, S. (2020). 
Equilibrium optimizer: A novel optimization algorithm. 
Knowledge-Based Systems, 191, 105190.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class EquilibriumOptimizer(BaseOptimizer):
    """
    Equilibrium Optimizer (EO) Algorithm
    
    A physics-inspired optimization algorithm based on mass balance equations.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of particles in the system
    max_iterations : int, default=100
        Maximum number of iterations
    a1 : float, default=2.0
        Exploitation parameter
    a2 : float, default=1.0
        Exploration parameter
    GP : float, default=0.5
        Generation probability for equilibrium pool
    """
    
    aliases = ['eo', 'equilibrium', 'mass_balance']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 a1=2.0, a2=1.0, GP=0.5, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.a1 = a1
        self.a2 = a2
        self.GP = GP
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.a1_ = a1
        self.a2_ = a2
        self.GP_ = GP
        self.algorithm_name_ = "Equilibrium Optimizer"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the optimization algorithm
        """
        # Use trailing underscore attributes
        if X is not None:
            dimensions = X.shape[1]
            lower_bound = np.zeros(dimensions)
            upper_bound = np.ones(dimensions)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                raise ValueError("Dimensions must be specified")
            dimensions = self.dimensions_
            lower_bound = self.lower_bound_
            upper_bound = self.upper_bound_
            
        objective_func = objective_function
        # Initialize particles (concentration)
        particles = np.random.uniform(lower_bound, upper_bound, 
                                    (self.population_size, dimensions))
        fitness = np.array([objective_func(particle) for particle in particles])
        
        best_idx = np.argmin(fitness)
        best_position = particles[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [particles.tolist()]
        for iteration in range(self.max_iterations):
            # Calculate time parameter t
            t = (1 - iteration / self.max_iterations) ** (self.a2 * iteration / self.max_iterations)
            
            # Form equilibrium pool
            equilibrium_pool = []
            
            # Sort particles by fitness
            sorted_indices = np.argsort(fitness)
            
            # Add best 4 particles to equilibrium pool
            for i in range(min(4, len(sorted_indices))):
                equilibrium_pool.append(particles[sorted_indices[i]].copy())
            
            # Add equilibrium candidate (average of best particles)
            if len(equilibrium_pool) > 0:
                equilibrium_candidate = np.mean(equilibrium_pool, axis=0)
                equilibrium_pool.append(equilibrium_candidate)
            
            # Update each particle
            for i in range(self.population_size):
                # Select equilibrium state randomly from pool
                if equilibrium_pool:
                    Ceq_idx = np.random.randint(0, len(equilibrium_pool))
                    Ceq = equilibrium_pool[Ceq_idx]
                else:
                    Ceq = best_position
                
                # Calculate lambda (turnover rate)
                lambda_val = np.random.uniform(0, 1, dimensions)
                
                # Calculate r vector
                r = np.random.uniform(0, 1, dimensions)
                
                # Calculate F (exponential term)
                F = self.a1 * np.sign(r - 0.5) * (np.exp(-lambda_val * t) - 1)
                
                # Generation rate G
                G = self.GP * np.random.uniform(0, 1, dimensions)
                
                # Update particle concentration
                if np.random.random() < 0.5:
                    # Exploitation phase
                    new_position = Ceq + (particles[i] - Ceq) * F + \
                                 G * (lambda_val * (best_position - particles[i]))
                else:
                    # Exploration phase
                    new_position = Ceq + (particles[i] - Ceq) * F + \
                                 G * lambda_val * np.random.uniform(-1, 1, dimensions)
                
                # Memory saving - keep track of previous position
                prev_position = particles[i].copy()
                
                # Boundary handling
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                # Update if better
                if new_fitness < fitness[i]:
                    particles[i] = new_position
                    fitness[i] = new_fitness
                else:
                    # Apply memory mechanism
                    if iteration > 0.7 * self.max_iterations:
                        # In later stages, use memory to avoid getting stuck
                        memory_position = 0.5 * (prev_position + particles[i])
                        memory_position = np.clip(memory_position, lower_bound, upper_bound)
                        memory_fitness = objective_func(memory_position)
                        
                        if memory_fitness < fitness[i]:
                            particles[i] = memory_position
                            fitness[i] = memory_fitness
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = particles[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(particles.tolist())
            
            # Equilibrium state adjustment
            if iteration % 20 == 0:
                # Check if system reached equilibrium (convergence)
                fitness_std = np.std(fitness)
                if fitness_std < 1e-6:
                    # System at equilibrium - introduce perturbation
                    perturbation_indices = np.random.choice(self.population_size, 
                                                          size=max(1, self.population_size // 10),
                                                          replace=False)
                    for idx in perturbation_indices:
                        perturbation = np.random.normal(0, 0.1, dimensions)
                        particles[idx] += perturbation
                        particles[idx] = np.clip(particles[idx], lower_bound, upper_bound)
                        fitness[idx] = objective_func(particles[idx])
            
            # Dynamic parameter adjustment
            if iteration > 0.8 * self.max_iterations:
                # Increase exploitation in final phase
                self.a1 *= 1.01
                self.GP *= 0.99
            
            if hasattr(self, "verbose_") and self.verbose_:
                avg_fitness = np.mean(fitness)
                fitness_std = np.std(fitness)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Avg fitness: {avg_fitness:.6f}, Std: {fitness_std:.6f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions