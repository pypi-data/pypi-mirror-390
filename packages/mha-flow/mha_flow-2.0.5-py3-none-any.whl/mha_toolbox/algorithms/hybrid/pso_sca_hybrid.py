"""
PSO-SCA Hybrid Algorithm
========================
Combines Particle Swarm Optimization (PSO) with Sine Cosine Algorithm (SCA)
- First half: PSO's velocity-based movement
- Second half: SCA's sine/cosine position updates
"""

import numpy as np
from ...base import BaseOptimizer

class PSO_SCA_Hybrid(BaseOptimizer):
    """
    Particle Swarm Optimization + Sine Cosine Algorithm Hybrid
    
    Strengths:
    - PSO: Fast convergence with social learning
    - SCA: Mathematical exploration using sine/cosine
    - Hybrid: Balanced local-global search
    
    Parameters:
    -----------
    population_size : int, default=30
        Number of particles
    max_iterations : int, default=100
        Maximum number of iterations
    w : float, default=0.9
        Inertia weight (PSO phase)
    c1 : float, default=2.0
        Cognitive parameter (PSO phase)
    c2 : float, default=2.0
        Social parameter (PSO phase)
    a : float, default=2.0
        Constant for SCA
    """
    
    def __init__(self, population_size=30, max_iterations=100, 
                 w=0.9, c1=2.0, c2=2.0, a=2.0, **kwargs):
        super().__init__(population_size, max_iterations, **kwargs)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.a = a
        self.algorithm_name = "PSO_SCA_Hybrid"
        
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """Execute hybrid PSO-SCA optimization"""
        # Determine dimensions and bounds
        if X is not None:
            dimensions = X.shape[1]
            bounds = (np.zeros(dimensions), np.ones(dimensions))
        else:
            dimensions = kwargs.get('dimensions', 10)
            bounds = kwargs.get('bounds', (np.zeros(dimensions), np.ones(dimensions)))
        
        # Initialize particles
        particles = np.random.uniform(bounds[0], bounds[1], (self.population_size_, dimensions))
        velocities = np.random.uniform(-1, 1, (self.population_size_, dimensions))
        
        # Personal best
        personal_best = particles.copy()
        personal_best_fitness = np.array([objective_function(p) for p in particles])
        
        # Global best
        best_idx = np.argmin(personal_best_fitness)
        global_best = personal_best[best_idx].copy()
        global_best_fitness = personal_best_fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            # Linear decrease of w and a
            w = self.w - (iteration / self.max_iterations_) * (self.w - 0.4)
            a = self.a - (iteration / self.max_iterations_) * self.a
            
            if iteration < self.max_iterations_ // 2:
                # PHASE 1: PSO
                for i in range(self.population_size_):
                    # Update velocity
                    r1, r2 = np.random.rand(2)
                    cognitive = self.c1 * r1 * (personal_best[i] - particles[i])
                    social = self.c2 * r2 * (global_best - particles[i])
                    velocities[i] = w * velocities[i] + cognitive + social
                    
                    # Update position
                    particles[i] = particles[i] + velocities[i]
                    
            else:
                # PHASE 2: SCA
                for i in range(self.population_size_):
                    for j in range(dimensions):
                        r1 = a - iteration * (a / self.max_iterations_)
                        r2 = 2 * np.pi * np.random.rand()
                        r3 = 2 * np.random.rand()
                        r4 = np.random.rand()
                        
                        if r4 < 0.5:
                            # Sine component
                            particles[i, j] = particles[i, j] + r1 * np.sin(r2) * abs(
                                r3 * global_best[j] - particles[i, j]
                            )
                        else:
                            # Cosine component
                            particles[i, j] = particles[i, j] + r1 * np.cos(r2) * abs(
                                r3 * global_best[j] - particles[i, j]
                            )
            
            # Apply bounds
            particles = np.clip(particles, bounds[0], bounds[1])
            velocities = np.clip(velocities, -2, 2)
            
            # Evaluate fitness
            fitness = np.array([objective_function(p) for p in particles])
            
            # Update personal best
            better_mask = fitness < personal_best_fitness
            personal_best[better_mask] = particles[better_mask].copy()
            personal_best_fitness[better_mask] = fitness[better_mask]
            
            # Update global best
            best_idx = np.argmin(personal_best_fitness)
            if personal_best_fitness[best_idx] < global_best_fitness:
                global_best = personal_best[best_idx].copy()
                global_best_fitness = personal_best_fitness[best_idx]
            
            global_fitness.append(global_best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(particles.copy())
        
        return global_best, global_best_fitness, global_fitness, local_fitness, local_positions

