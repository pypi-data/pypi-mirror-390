"""
Approximated Non-deterministic Tree Search (ANTS)

Based on: Colorni, A., Dorigo, M., & Maniezzo, V. (1991). 
Distributed optimization by ant colonies.
"""

import numpy as np
from ..base import BaseOptimizer


class ApproximatedNondeterministicTreeSearch(BaseOptimizer):
    """
    Approximated Non-deterministic Tree Search (ANTS)
    
    ANTS is an early ant colony optimization variant that uses probabilistic
    decision making and pheromone trail updates for optimization.
    """
    
    aliases = ["ants", "ant_tree_search", "nondeterministic_tree"]
    
    def __init__(self, *args, alpha=1.0, beta=2.0, evaporation_rate=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha_ = alpha  # Pheromone importance
        self.beta_ = beta   # Heuristic importance
        self.evaporation_rate_ = evaporation_rate
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "ApproximatedNondeterministicTreeSearch"
    
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
        
        # Initialize pheromone matrix (discretized search space)
        n_nodes = 50  # Number of nodes per dimension
        pheromone = np.ones((self.dimensions_, n_nodes))
        
        # Initialize ant population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best solution
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Generate new solutions using pheromone trails
            for i in range(self.population_size_):
                new_position = np.zeros(self.dimensions_)
                
                for j in range(self.dimensions_):
                    # Calculate probabilities based on pheromone trails
                    probabilities = pheromone[j] ** self.alpha_
                    probabilities = probabilities / np.sum(probabilities)
                    
                    # Select node based on probabilities
                    selected_node = np.random.choice(n_nodes, p=probabilities)
                    
                    # Convert node to actual value
                    new_position[j] = self.lower_bound_[j] + (selected_node / (n_nodes - 1)) * (self.upper_bound_[j] - self.lower_bound_[j])
                
                # Add small random perturbation
                new_position += np.random.randn(self.dimensions_) * 0.01 * (self.upper_bound_ - self.lower_bound_)
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(new_position)
                fitnesses.append(new_fitness)
                positions.append(new_position.copy())
                
                # Update if better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_solution = new_position.copy()
                        best_fitness = new_fitness
            
            # Update pheromone trails
            # Evaporation
            pheromone *= (1 - self.evaporation_rate_)
            
            # Reinforcement based on solution quality
            for i in range(self.population_size_):
                # Convert position to nodes
                for j in range(self.dimensions_):
                    node = int((population[i][j] - self.lower_bound_[j]) / (self.upper_bound_[j] - self.lower_bound_[j]) * (n_nodes - 1))
                    node = max(0, min(n_nodes - 1, node))
                    
                    # Update pheromone (higher for better solutions)
                    delta_pheromone = 1.0 / (1.0 + fitness[i])
                    pheromone[j][node] += delta_pheromone
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions