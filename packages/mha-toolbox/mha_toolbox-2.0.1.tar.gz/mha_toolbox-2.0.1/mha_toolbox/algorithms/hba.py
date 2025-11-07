"""
Honey Badger Algorithm (HBA)
===========================

Honey Badger Algorithm inspired by the intelligent foraging behavior
of honey badgers.
"""

import numpy as np
from ..base import BaseOptimizer


class HoneyBadgerAlgorithm(BaseOptimizer):
    """
    Honey Badger Algorithm (HBA)
    
    Bio-inspired algorithm based on the dynamic foraging behavior
    and fearless characteristics of honey badgers.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Honey Badger Algorithm"
        self.aliases = ["hba", "honey_badger", "badger_algorithm"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Honey Badger Algorithm
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize badger population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Track best solution (prey)
        prey_idx = np.argmin(fitness)
        prey_position = population[prey_idx].copy()
        prey_fitness = fitness[prey_idx]
        
        # History tracking
        global_fitness = [prey_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update density factor
            alpha = 2 * np.exp(-iteration / self.max_iterations)
            
            # Update intensity
            I = np.random.rand() * (1 / (4 * np.pi * alpha ** 2))
            
            for i in range(self.population_size):
                r = np.random.random()
                
                if r < 0.5:
                    # Digging phase (exploration)
                    r3 = np.random.random()
                    r4 = np.random.random()
                    r5 = np.random.random()
                    
                    # Distance to prey
                    dist_to_prey = np.abs(prey_position - population[i])
                    
                    # Digging behavior
                    new_position = prey_position + r3 * alpha * I * dist_to_prey
                    
                    # Apply randomness
                    new_position = new_position + r4 * np.random.randn(dimension) - r5 * np.random.randn(dimension)
                    
                    population[i] = new_position
                else:
                    # Honey phase (exploitation)
                    r6 = np.random.random()
                    r7 = np.random.random()
                    
                    # Move towards prey
                    population[i] = prey_position + r6 * alpha * I * (prey_position - population[i])
                    
                    # Cardioid movement
                    if r7 < 0.5:
                        t = np.random.random() * 2 * np.pi
                        population[i] = population[i] + alpha * np.cos(t) * (1 + np.cos(t))
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update prey position (best solution)
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < prey_fitness:
                prey_position = population[current_best_idx].copy()
                prey_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(prey_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return prey_position, prey_fitness, global_fitness, local_fitness, local_positions