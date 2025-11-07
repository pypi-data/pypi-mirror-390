"""
weIghted meaN OF vectOrs (INNOV) Algorithm

A vector-based optimization algorithm that uses weighted means of vectors
to explore the search space.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class WeightedMeanOfVectors(BaseOptimizer):
    """weIghted meaN OF vectOrs (INNOV) Algorithm"""
    
    aliases = ['innov', 'weighted_mean', 'vectors']
    
    def __init__(self, population_size=50, max_iterations=100, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.algorithm_name_ = "weIghted meaN OF vectOrs"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the INNOV optimization algorithm
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
        population = np.random.uniform(lower_bound, upper_bound, (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        for iteration in range(self.max_iterations):
            weights = 1.0 / (fitness + 1e-10)  # Avoid division by zero
            weights = weights / np.sum(weights)  # Normalize weights
            
            for i in range(self.population_size):
                # Calculate weighted mean of random subset
                subset_size = min(5, self.population_size)
                subset_indices = np.random.choice(self.population_size, subset_size, replace=False)
                subset_weights = weights[subset_indices]
                subset_weights = subset_weights / np.sum(subset_weights)
                
                weighted_mean = np.sum(population[subset_indices] * subset_weights.reshape(-1, 1), axis=0)
                
                # Move towards weighted mean with innovation
                innovation_factor = np.random.uniform(0.1, 0.9)
                innovation_vector = np.random.normal(0, 0.1, dimensions)
                
                new_position = innovation_factor * weighted_mean + (1 - innovation_factor) * population[i]
                new_position += innovation_vector
                
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
            
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions