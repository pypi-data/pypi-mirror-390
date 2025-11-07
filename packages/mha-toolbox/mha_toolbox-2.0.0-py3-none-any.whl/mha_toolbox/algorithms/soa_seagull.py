"""
Seagull Optimization Algorithm (SOA)
===================================

Seagull Optimization Algorithm inspired by the natural behavior
of seagulls during migration and foraging.
"""

import numpy as np
from ..base import BaseOptimizer


class SeagullOptimizationAlgorithm(BaseOptimizer):
    """
    Seagull Optimization Algorithm (SOA)
    
    Bio-inspired algorithm based on the migration and attacking behaviors
    of seagulls in nature.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Seagull Optimization Algorithm"
        self.aliases = ["soa", "seagull", "seagull_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Seagull Optimization Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize seagull population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update A and fc parameters
            A = 2 - 2 * iteration / self.max_iterations  # Linearly decreases from 2 to 0
            fc = 2 * (iteration / self.max_iterations) ** 2  # Spiral behavior control
            
            for i in range(self.population_size):
                # Migration behavior - variable A controls exploration/exploitation
                if A >= 1:
                    # Exploration phase
                    if np.random.random() >= 0.5:
                        # Update position without attacking behavior
                        Cs = A * population[i]
                        Ds = abs(Cs + np.random.random() * best_position - population[i])
                        population[i] = (np.random.random() - 0.5) * 2 * Ds
                    else:
                        # Random search
                        population[i] = np.random.random() * (bounds[1] - bounds[0]) + bounds[0]
                else:
                    # Exploitation phase - attacking behavior
                    Ms = fc * np.spiral_movement()  # Spiral movement function
                    population[i] = Ms * best_position
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions
    
    def spiral_movement(self):
        """Generate spiral movement pattern for seagull attacking behavior"""
        # Simplified spiral movement implementation
        theta = np.random.random() * 2 * np.pi
        r = theta
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = r * theta
        return np.array([x, y, z])

# Add spiral movement as numpy function extension
np.spiral_movement = lambda: SeagullOptimizationAlgorithm().spiral_movement()[:2]  # Use only x, y components