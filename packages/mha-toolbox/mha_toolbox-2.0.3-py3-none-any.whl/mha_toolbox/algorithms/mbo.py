"""
Monarch Butterfly Optimization (MBO)
===================================

Monarch Butterfly Optimization inspired by the migration behavior
of monarch butterflies.
"""

import numpy as np
from ..base import BaseOptimizer


class MonarchButterflyOptimization(BaseOptimizer):
    """
    Monarch Butterfly Optimization (MBO)
    
    Bio-inspired algorithm based on the migration behavior and
    population characteristics of monarch butterflies.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Monarch Butterfly Optimization"
        self.aliases = ["mbo", "monarch_butterfly", "butterfly_optimization"]
        self.migration_ratio = 5/12  # Ratio of migration
        self.p = 5/12  # Partition ratio
        self.period = 1.2  # Butterfly adjusting period
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Monarch Butterfly Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize butterfly population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(individual) for individual in population])
        
        # Divide population into subpopulations
        num_land1 = int(np.ceil(self.migration_ratio * self.population_size))
        num_land2 = self.population_size - num_land1
        
        # Track best solution
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # History tracking
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Sort population by fitness
            sorted_indices = np.argsort(fitness)
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            # Divide into two lands
            land1 = population[:num_land1]  # Better butterflies
            land2 = population[num_land1:]  # Other butterflies
            
            # Migration operator for Land 1
            for i in range(num_land1):
                if np.random.random() <= self.p:
                    # Migration operator
                    r1 = np.random.randint(0, num_land1)
                    r2 = np.random.randint(0, num_land1)
                    
                    land1[i] = land1[r1] + (land1[r2] - land1[i]) * np.random.random()
                else:
                    # Random walk
                    land1[i] = land1[i] + self.levy_flight(dimension) * (bounds[1] - bounds[0])
                
                # Apply bounds
                land1[i] = np.clip(land1[i], bounds[0], bounds[1])
            
            # Butterfly adjusting operator for Land 2
            for i in range(num_land2):
                if np.random.random() <= self.p:
                    # Butterfly adjusting operator
                    r1 = np.random.randint(0, num_land1)  # From Land 1
                    r2 = np.random.randint(0, num_land2)  # From Land 2
                    
                    land2[i] = land1[r1] + (land2[r2] - land2[i]) * np.random.random()
                else:
                    # Random walk with best position
                    land2[i] = best_position + self.levy_flight(dimension) * (bounds[1] - bounds[0])
                
                # Apply bounds
                land2[i] = np.clip(land2[i], bounds[0], bounds[1])
            
            # Combine populations
            population = np.vstack([land1, land2])
            
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
    
    def levy_flight(self, dimension):
        """Generate Levy flight step"""
        beta = 1.5
        sigma = (np.math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (np.math.gamma((1 + beta) / 2) * beta * (2 ** ((beta - 1) / 2)))) ** (1 / beta)
        
        u = np.random.normal(0, sigma, dimension)
        v = np.random.normal(0, 1, dimension)
        
        return u / (np.abs(v) ** (1 / beta))