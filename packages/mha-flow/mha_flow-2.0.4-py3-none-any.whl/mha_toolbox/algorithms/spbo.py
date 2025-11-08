"""
Student Psychology Based Optimization (SPBO) Algorithm

A human behavior-inspired optimization algorithm based on the learning behavior
and psychology of students in educational environments.

Reference:
Das, B., Mukherjee, V., & Das, D. (2020). Student psychology based optimization 
algorithm: A new population based optimization algorithm for solving optimization problems. 
Advances in Engineering Software, 146, 102804.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class StudentPsychologyBasedOptimization(BaseOptimizer):
    """
    Student Psychology Based Optimization (SPBO) Algorithm
    
    A human behavior-inspired optimization algorithm based on student learning psychology.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of students in the class
    max_iterations : int, default=100
        Maximum number of learning sessions
    learning_rate : float, default=0.8
        Rate at which students learn from better performers
    curiosity_rate : float, default=0.3
        Rate of exploration due to student curiosity
    """
    
    aliases = ['spbo', 'student', 'psychology']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 learning_rate=0.8, curiosity_rate=0.3, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.learning_rate = learning_rate
        self.curiosity_rate = curiosity_rate
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.learning_rate_ = learning_rate
        self.curiosity_rate_ = curiosity_rate
        self.algorithm_name_ = "Student Psychology Based Optimization"
    
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
        # Initialize students (population)
        students = np.random.uniform(lower_bound, upper_bound, 
                                   (self.population_size, dimensions))
        fitness = np.array([objective_func(student) for student in students])
        
        # Initialize student characteristics
        motivation = np.random.uniform(0.5, 1.0, self.population_size)
        concentration = np.random.uniform(0.3, 1.0, self.population_size)
        study_time = np.zeros(self.population_size)
        
        best_idx = np.argmin(fitness)
        best_position = students[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [students.tolist()]
        for iteration in range(self.max_iterations):
            # Rank students by performance
            ranked_indices = np.argsort(fitness)
            
            for i in range(self.population_size):
                current_rank = np.where(ranked_indices == i)[0][0]
                
                # Learning from better students (best student is the teacher)
                if np.random.random() < self.learning_rate:
                    if current_rank > 0:  # Not the best student
                        # Learn from a better student
                        better_students = ranked_indices[:current_rank]
                        teacher_idx = np.random.choice(better_students)
                        
                        # Learning intensity based on motivation and concentration
                        learning_intensity = motivation[i] * concentration[i]
                        learning_direction = students[teacher_idx] - students[i]
                        
                        # Apply learning with some variation
                        learning_step = learning_intensity * learning_direction
                        variation = np.random.normal(0, 0.1, dimensions)
                        new_position = students[i] + learning_step + variation
                    else:
                        # Best student self-improves
                        self_improvement = np.random.normal(0, 0.05, dimensions)
                        new_position = students[i] + self_improvement
                    
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[i]:
                        students[i] = new_position
                        fitness[i] = new_fitness
                        motivation[i] = min(1.0, motivation[i] + 0.1)  # Success increases motivation
                        study_time[i] += 1
                    else:
                        motivation[i] = max(0.1, motivation[i] - 0.05)  # Failure decreases motivation
                
                # Curiosity-driven exploration
                if np.random.random() < self.curiosity_rate:
                    # Curious students explore new areas
                    curiosity_strength = np.random.uniform(0.1, 0.5)
                    exploration_direction = np.random.uniform(-1, 1, dimensions)
                    exploration_step = curiosity_strength * exploration_direction
                    
                    new_position = students[i] + exploration_step
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[i]:
                        students[i] = new_position
                        fitness[i] = new_fitness
                        concentration[i] = min(1.0, concentration[i] + 0.05)
                
                # Peer pressure and group study
                if np.random.random() < 0.4 and iteration > 10:
                    # Form study groups with nearby students (similar performance)
                    group_size = min(5, self.population_size // 10)
                    start_rank = max(0, current_rank - group_size // 2)
                    end_rank = min(self.population_size, start_rank + group_size)
                    
                    group_indices = ranked_indices[start_rank:end_rank]
                    if len(group_indices) > 1:
                        # Learn from group average
                        group_positions = students[group_indices]
                        group_center = np.mean(group_positions, axis=0)
                        
                        group_learning = 0.2 * (group_center - students[i])
                        new_position = students[i] + group_learning
                        new_position = np.clip(new_position, lower_bound, upper_bound)
                        new_fitness = objective_func(new_position)
                        
                        if new_fitness < fitness[i]:
                            students[i] = new_position
                            fitness[i] = new_fitness
                
                # Stress and burnout management
                if study_time[i] > 20:  # Student is getting tired
                    # Take a break (random reset with small probability)
                    if np.random.random() < 0.1:
                        students[i] = np.random.uniform(lower_bound, upper_bound, dimensions)
                        fitness[i] = objective_func(students[i])
                        study_time[i] = 0
                        motivation[i] = np.random.uniform(0.7, 1.0)  # Refreshed motivation
                        concentration[i] = np.random.uniform(0.7, 1.0)  # Refreshed concentration
            
            # Teacher intervention (global guidance)
            if iteration % 10 == 0:
                # Teacher helps struggling students
                worst_students = ranked_indices[-int(0.2 * self.population_size):]
                for student_idx in worst_students:
                    # Direct guidance towards best solution
                    guidance = 0.3 * (best_position - students[student_idx])
                    encouragement = np.random.normal(0, 0.1, dimensions)
                    
                    new_position = students[student_idx] + guidance + encouragement
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[student_idx]:
                        students[student_idx] = new_position
                        fitness[student_idx] = new_fitness
                        motivation[student_idx] += 0.2  # Teacher help boosts motivation
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = students[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(students.tolist())
            
            # Semester effects - periodic motivation and concentration updates
            if iteration % 25 == 0:
                # New semester - some motivation reset
                motivation = np.clip(motivation + np.random.normal(0, 0.1, self.population_size), 0.1, 1.0)
                concentration = np.clip(concentration + np.random.normal(0, 0.1, self.population_size), 0.1, 1.0)
            
            if hasattr(self, "verbose_") and self.verbose_:
                avg_motivation = np.mean(motivation)
                avg_concentration = np.mean(concentration)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Avg motivation: {avg_motivation:.3f}, Avg concentration: {avg_concentration:.3f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions