"""
Spotted Hyena Optimizer (SHO)
============================

Spotted Hyena Optimizer inspired by the hunting behavior
of spotted hyenas in nature.
"""

import numpy as np
from ..base import BaseOptimizer


class SpottedHyenaOptimizer(BaseOptimizer):
    """
    Spotted Hyena Optimizer (SHO)
    
    Bio-inspired algorithm based on the hunting behavior and
    social hierarchy of spotted hyenas.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Spotted Hyena Optimizer"
        self.aliases = ["sho", "spotted_hyena", "hyena_optimizer"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Spotted Hyena Optimizer
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize hyena population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Sort population and identify hierarchy
        sorted_indices = np.argsort(fitness)
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        # Track best solutions (hunting group)
        Ch = population[0].copy()  # Leader (best hyena)
        Bh = population[1].copy() if len(population) > 1 else Ch.copy()  # Beta hyena
        Dh = population[2].copy() if len(population) > 2 else Ch.copy()  # Delta hyena
        
        best_fitness = fitness[0]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update h parameter (decreases linearly)
            h = 5 - iteration * (5 / self.max_iterations)
            
            for i in range(self.population_size):
                # Calculate distances to leaders
                Dh_pos = abs(2 * np.random.random() * Ch - population[i])
                Dbh_pos = abs(2 * np.random.random() * Bh - population[i])
                Ddh_pos = abs(2 * np.random.random() * Dh - population[i])
                
                # Calculate B vectors
                B1 = 2 * h * np.random.random() - h
                B2 = 2 * h * np.random.random() - h
                B3 = 2 * h * np.random.random() - h
                
                # Update position based on leaders
                X1 = Ch - B1 * Dh_pos
                X2 = Bh - B2 * Dbh_pos
                X3 = Dh - B3 * Ddh_pos
                
                # Calculate new position as average
                population[i] = (X1 + X2 + X3) / 3
                
                # Apply bounds
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # Evaluate new positions
            fitness = np.array([objective_function(individual) for individual in population])
            
            # Update hierarchy
            sorted_indices = np.argsort(fitness)
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            # Update leaders
            Ch = population[0].copy()
            Bh = population[1].copy() if len(population) > 1 else Ch.copy()
            Dh = population[2].copy() if len(population) > 2 else Ch.copy()
            
            # Update best fitness
            best_fitness = fitness[0]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return Ch, best_fitness, global_fitness, local_fitness, local_positions