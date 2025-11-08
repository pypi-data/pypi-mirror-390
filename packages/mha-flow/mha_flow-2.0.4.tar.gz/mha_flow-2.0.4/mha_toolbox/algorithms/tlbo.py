"""
Teaching-Learning-Based Optimization (TLBO)

Based on: Rao, R. V., Savsani, V. J., & Vakharia, D. P. (2011). Teaching-learning-based optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class TeachingLearningBasedOptimization(BaseOptimizer):
    """
    Teaching-Learning-Based Optimization (TLBO)
    
    TLBO is inspired by the teaching-learning process in a classroom.
    It consists of two phases: Teacher Phase and Learner Phase.
    
    Parameters
    ----------
    None (Parameter-free algorithm)
    """
    
    aliases = ["tlbo", "teaching_learning", "teaching_learning_based"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.algorithm_name = "TLBO"
    
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
        
        # Initialize population (learners)
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find initial best (teacher)
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Teacher Phase
            teacher = population[np.argmin(fitness)].copy()
            mean = np.mean(population, axis=0)
            
            for i in range(self.population_size_):
                # Teaching factor (1 or 2)
                TF = np.round(1 + np.random.random())
                
                # Generate new learner
                new_learner = population[i] + np.random.random() * (teacher - TF * mean)
                
                # Ensure bounds
                new_learner = np.clip(new_learner, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new learner
                new_fitness = objective_function(new_learner)
                
                # Accept if better
                if new_fitness < fitness[i]:
                    population[i] = new_learner.copy()
                    fitness[i] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_learner.copy()
                        best_fitness = new_fitness
            
            # Learner Phase
            for i in range(self.population_size_):
                # Select another random learner
                j = np.random.randint(0, self.population_size_)
                while j == i:
                    j = np.random.randint(0, self.population_size_)
                
                # Generate new learner based on interaction
                if fitness[i] < fitness[j]:
                    new_learner = population[i] + np.random.random() * (population[i] - population[j])
                else:
                    new_learner = population[i] + np.random.random() * (population[j] - population[i])
                
                # Ensure bounds
                new_learner = np.clip(new_learner, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new learner
                new_fitness = objective_function(new_learner)
                
                # Accept if better
                if new_fitness < fitness[i]:
                    population[i] = new_learner.copy()
                    fitness[i] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_learner.copy()
                        best_fitness = new_fitness
            
            # Collect data for this iteration
            for i in range(self.population_size_):
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions