"""
Sailfish Optimizer (SFO)
=======================

Sailfish Optimizer inspired by the hunting behavior of sailfish in the ocean.
"""

import numpy as np
from ..base import BaseOptimizer


class SailfishOptimizer(BaseOptimizer):
    """
    Sailfish Optimizer (SFO)
    
    Bio-inspired algorithm based on the group hunting behavior of sailfish.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Sailfish Optimizer"
        self.aliases = ["sfo", "sailfish", "sailfish_optimizer"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Sailfish Optimizer
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize sailfish and sardines
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Attack coefficient
            A = 4 - 4 * (iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # Sailfish attack behavior
                r1 = np.random.random()
                r2 = np.random.random()
                
                if i < self.population_size // 2:
                    # Sailfish group
                    if r1 < 0.5:
                        population[i] = best_position - A * (r2 * (best_position + population[i]) / 2 - population[i])
                    else:
                        k = np.random.randint(0, self.population_size)
                        population[i] = population[i] + A * (population[k] - population[i])
                else:
                    # Sardine group
                    population[i] = best_position + A * np.random.randn(dimension)
                
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            current_best_idx = np.argmin(fitness)
            
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions