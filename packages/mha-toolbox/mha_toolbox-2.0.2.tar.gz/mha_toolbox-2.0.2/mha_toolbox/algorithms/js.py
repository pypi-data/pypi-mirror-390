"""
Jellyfish Search Algorithm (JS)
==============================

Jellyfish Search Algorithm inspired by the behavior of jellyfish
in the ocean currents.
"""

import numpy as np
from ..base import BaseOptimizer


class JellyfishSearchAlgorithm(BaseOptimizer):
    """
    Jellyfish Search Algorithm (JS)
    
    Bio-inspired algorithm based on the behavior of jellyfish following
    ocean currents and swarm behaviors.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Jellyfish Search Algorithm"
        self.aliases = ["js", "jellyfish", "jellyfish_search"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Jellyfish Search Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize jellyfish population
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
        
        # Algorithm parameters
        c0 = 0.5  # Cognitive component
        beta = 3  # Distribution control parameter
        gamma = 0.1  # Motion control parameter
        
        for iteration in range(self.max_iterations):
            # Calculate time control function
            time_control = abs((2 * np.exp(np.random.random() * (1 - iteration / self.max_iterations))) - 1)
            
            for i in range(self.population_size):
                if time_control >= c0:
                    # Follow ocean current (passive motion)
                    if np.random.random() > (1 - c0):
                        # Move towards best location
                        population[i] = population[i] + np.random.random() * (best_position - beta * np.random.random() * population[i])
                    else:
                        # Random motion
                        population[i] = population[i] + gamma * np.random.random() * (bounds[1] - bounds[0]) * np.random.uniform(-1, 1, dimension)
                else:
                    # Active motion (swarm behavior)
                    if i > 0:
                        # Follow the jellyfish ahead
                        if fitness[i] > fitness[i-1]:
                            # Move towards better jellyfish
                            direction = population[i-1] - population[i]
                            population[i] = population[i] + np.random.random() * direction
                        else:
                            # Random exploration
                            population[i] = population[i] + (bounds[1] - bounds[0]) * np.random.uniform(-1, 1, dimension) * 0.1
                    else:
                        # First jellyfish moves randomly
                        population[i] = population[i] + (bounds[1] - bounds[0]) * np.random.uniform(-1, 1, dimension) * 0.1
                
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