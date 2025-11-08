"""
Imperialist Competitive Algorithm (ICA)

A socio-politically inspired optimization algorithm based on the imperialistic competition
and the socio-political process of assimilation and revolution.

Reference:
Atashpaz-Gargari, E., & Lucas, C. (2007). Imperialist competitive algorithm: 
an algorithm for optimization inspired by imperialistic competition. 
In IEEE congress on evolutionary computation (pp. 4661-4667).
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class ImperialistCompetitiveAlgorithm(BaseOptimizer):
    """
    Imperialist Competitive Algorithm (ICA)
    
    A socio-politically inspired optimization algorithm based on imperialistic competition.
    
    Parameters
    ----------
    population_size : int, default=50
        Total number of countries (solutions)
    max_iterations : int, default=100
        Maximum number of decades
    n_imperialists : int, default=8
        Number of imperialist countries
    assimilation_rate : float, default=2.0
        Rate of colonies assimilation towards imperialists
    revolution_rate : float, default=0.3
        Probability of revolution in colonies
    """
    
    aliases = ['ica', 'imperialist', 'competitive']
    
    def __init__(self, population_size=50, max_iterations=100, n_imperialists=8,
                 assimilation_rate=2.0, revolution_rate=0.3, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.n_imperialists = min(n_imperialists, population_size // 2)
        self.assimilation_rate = assimilation_rate
        self.revolution_rate = revolution_rate
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.n_imperialists_ = self.n_imperialists
        self.assimilation_rate_ = assimilation_rate
        self.revolution_rate_ = revolution_rate
        self.algorithm_name_ = "Imperialist Competitive Algorithm"
    
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
        # Initialize countries (population)
        countries = np.random.uniform(lower_bound, upper_bound, 
                                    (self.population_size, dimensions))
        costs = np.array([objective_func(country) for country in countries])
        
        # Sort countries by cost (fitness)
        sorted_indices = np.argsort(costs)
        countries = countries[sorted_indices]
        costs = costs[sorted_indices]
        
        # Select imperialists (best countries)
        imperialists = countries[:self.n_imperialists].copy()
        imperialist_costs = costs[:self.n_imperialists].copy()
        
        # Remaining countries become colonies
        colonies = countries[self.n_imperialists:].copy()
        colony_costs = costs[self.n_imperialists:].copy()
        
        # Distribute colonies among imperialists based on their power
        if len(colonies) > 0:
            # Calculate normalized power of imperialists
            max_cost = np.max(imperialist_costs)
            normalized_costs = max_cost - imperialist_costs
            if np.sum(normalized_costs) == 0:
                probabilities = np.ones(self.n_imperialists) / self.n_imperialists
            else:
                probabilities = normalized_costs / np.sum(normalized_costs)
            
            # Assign colonies to imperialists
            empire_colonies = [[] for _ in range(self.n_imperialists)]
            for i in range(len(colonies)):
                empire_idx = np.random.choice(self.n_imperialists, p=probabilities)
                empire_colonies[empire_idx].append(i)
        else:
            empire_colonies = [[] for _ in range(self.n_imperialists)]
        
        best_position = imperialists[0].copy()
        best_fitness = imperialist_costs[0]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [imperialist_costs.tolist()]
        local_positions = [imperialists.tolist()]
        
        for iteration in range(self.max_iterations):
            # Assimilation: colonies move towards their imperialist
            for empire_idx in range(self.n_imperialists):
                for colony_idx in empire_colonies[empire_idx]:
                    # Assimilation movement
                    direction = imperialists[empire_idx] - colonies[colony_idx]
                    beta = np.random.uniform(0, self.assimilation_rate)
                    
                    # Add some deviation
                    theta = np.random.uniform(-np.pi/4, np.pi/4)
                    rotation_matrix = self._get_rotation_matrix(theta, dimensions)
                    
                    movement = beta * np.dot(rotation_matrix, direction.reshape(-1, 1)).flatten()
                    new_position = colonies[colony_idx] + movement
                    
                    # Boundary handling
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_cost = objective_func(new_position)
                    
                    # Revolution: random change with some probability
                    if np.random.random() < self.revolution_rate:
                        revolution_position = np.random.uniform(lower_bound, upper_bound, dimensions)
                        revolution_cost = objective_func(revolution_position)
                        
                        if revolution_cost < new_cost:
                            new_position = revolution_position
                            new_cost = revolution_cost
                    
                    # Update colony
                    colonies[colony_idx] = new_position
                    colony_costs[colony_idx] = new_cost
                    
                    # Check if colony becomes better than its imperialist
                    if new_cost < imperialist_costs[empire_idx]:
                        # Swap colony and imperialist
                        temp_pos = imperialists[empire_idx].copy()
                        temp_cost = imperialist_costs[empire_idx]
                        
                        imperialists[empire_idx] = new_position.copy()
                        imperialist_costs[empire_idx] = new_cost
                        
                        colonies[colony_idx] = temp_pos
                        colony_costs[colony_idx] = temp_cost
            
            # Imperialistic competition
            if len(colonies) > 0:
                # Calculate total power of each empire
                empire_powers = []
                for empire_idx in range(self.n_imperialists):
                    empire_cost = imperialist_costs[empire_idx]
                    if empire_colonies[empire_idx]:
                        colony_indices = empire_colonies[empire_idx]
                        mean_colony_cost = np.mean([colony_costs[i] for i in colony_indices])
                        empire_cost += 0.1 * mean_colony_cost  # Small influence of colonies
                    empire_powers.append(empire_cost)
                
                # Find weakest empire
                weakest_empire_idx = np.argmax(empire_powers)
                
                # If weakest empire has colonies, take one
                if empire_colonies[weakest_empire_idx]:
                    # Select weakest colony from weakest empire
                    colony_indices = empire_colonies[weakest_empire_idx]
                    colony_costs_in_empire = [colony_costs[i] for i in colony_indices]
                    weakest_colony_local_idx = np.argmax(colony_costs_in_empire)
                    weakest_colony_idx = colony_indices[weakest_colony_local_idx]
                    
                    # Remove colony from weakest empire
                    empire_colonies[weakest_empire_idx].remove(weakest_colony_idx)
                    
                    # Give colony to strongest empire
                    strongest_empire_idx = np.argmin(empire_powers)
                    empire_colonies[strongest_empire_idx].append(weakest_colony_idx)
            
            # Update global best
            current_best_idx = np.argmin(imperialist_costs)
            if imperialist_costs[current_best_idx] < best_fitness:
                best_position = imperialists[current_best_idx].copy()
                best_fitness = imperialist_costs[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(imperialist_costs.tolist())
            local_positions.append(imperialists.tolist())
            
            if hasattr(self, "verbose_") and self.verbose_:
                active_empires = sum(1 for empire in empire_colonies if empire)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Active empires: {active_empires}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions
    def _get_rotation_matrix(self, theta, dimensions):
        """Generate a rotation matrix for the given angle in 2D, extended to higher dimensions"""
        if dimensions == 1:
            return np.array([[1.0]])
        elif dimensions == 2:
            return np.array([[np.cos(theta), -np.sin(theta)],
                           [np.sin(theta), np.cos(theta)]])
        else:
            # For higher dimensions, create rotation in first two dimensions
            rotation = np.eye(dimensions)
            rotation[0, 0] = np.cos(theta)
            rotation[0, 1] = -np.sin(theta)
            rotation[1, 0] = np.sin(theta)
            rotation[1, 1] = np.cos(theta)
            return rotation