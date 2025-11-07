"""
Sand Cat Swarm Optimization (SCSO)
=================================

Sand Cat Swarm Optimization inspired by the hunting behavior
of sand cats in desert environments.
"""

import numpy as np
from ..base import BaseOptimizer


class SandCatSwarmOptimization(BaseOptimizer):
    """
    Sand Cat Swarm Optimization (SCSO)
    
    Bio-inspired algorithm based on the hunting and survival
    strategies of sand cats in harsh desert conditions.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Sand Cat Swarm Optimization"
        self.aliases = ["scso", "sand_cat", "sandcat_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Sand Cat Swarm Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize sand cat population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Sensitivity range decreases over iterations
            r = 2 - 2 * (iteration / self.max_iterations)
            
            for i in range(self.population_size):
                # Roulette wheel selection of position
                rg = r * np.random.randn()
                
                if np.abs(rg) >= 1:
                    # Exploration: Search for prey
                    rand_pos = np.random.randint(0, self.population_size)
                    population[i] = np.random.random() * population[rand_pos]
                else:
                    # Exploitation: Attack prey
                    theta = np.random.random() * 360
                    r_val = rg * np.sin(np.radians(theta))
                    
                    population[i] = best_position - r_val * np.abs(2 * np.random.random() * best_position - population[i])
                
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