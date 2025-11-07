"""
Biogeography-Based Optimization (BBO)
====================================

Biogeography-Based Optimization inspired by the migration of species
between habitats.
"""

import numpy as np
from ..base import BaseOptimizer


class BiogeographyBasedOptimization(BaseOptimizer):
    """
    Biogeography-Based Optimization (BBO)
    
    Algorithm based on the geographical distribution of biological
    organisms and their migration patterns.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Biogeography-Based Optimization"
        self.aliases = ["bbo", "biogeography", "biogeography_optimization"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Biogeography-Based Optimization
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize habitat population
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        # Calculate immigration and emigration rates
        def calculate_rates(fit):
            # Normalize fitness
            fit_norm = (fit - np.min(fit)) / (np.max(fit) - np.min(fit) + 1e-10)
            # Immigration rate (lambda) - high for poor habitats
            lambda_rate = 1 - fit_norm
            # Emigration rate (mu) - high for good habitats
            mu_rate = fit_norm
            return lambda_rate, mu_rate
        
        for iteration in range(self.max_iterations):
            # Calculate migration rates
            lambda_rates, mu_rates = calculate_rates(fitness)
            
            # Migration (recombination)
            for i in range(self.population_size):
                if np.random.random() < lambda_rates[i]:
                    # Select emigrating habitat based on mu rates
                    probs = mu_rates / np.sum(mu_rates)
                    emigrating_idx = np.random.choice(self.population_size, p=probs)
                    
                    # Perform migration for random dimensions
                    for d in range(dimension):
                        if np.random.random() < 0.5:
                            population[i, d] = population[emigrating_idx, d]
            
            # Mutation
            mutation_rate = 0.01 * (1 - iteration / self.max_iterations)
            for i in range(self.population_size):
                if np.random.random() < mutation_rate:
                    mutation_dim = np.random.randint(0, dimension)
                    population[i, mutation_dim] = np.random.uniform(bounds[0], bounds[1])
            
            # Apply bounds
            population = np.clip(population, bounds[0], bounds[1])
            
            # Evaluate fitness
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions