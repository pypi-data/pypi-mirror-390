"""
POPMUSIC Algorithm
==================
"""

import numpy as np
from ..base import BaseOptimizer


class POPMUSIC(BaseOptimizer):
    """
    POPMUSIC Algorithm
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "POPMUSIC Algorithm"
        self.aliases = ["pm", "pm_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            C = 2 * (1 - iteration / self.max_iterations)
            
            for i in range(self.population_size):
                r = np.random.random()
                
                if r < 0.5:
                    # Exploration
                    k = np.random.randint(0, self.population_size)
                    population[i] = population[i] + C * np.random.random() * (best_position - population[k])
                else:
                    # Exploitation
                    population[i] = best_position + C * np.random.randn(dimension) * 0.1
                
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
