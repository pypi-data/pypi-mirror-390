"""
Symbiotic Organisms Search (SOS)
===============================

Symbiotic Organisms Search inspired by the symbiotic interactions
between organisms in an ecosystem.
"""

import numpy as np
from ..base import BaseOptimizer


class SymbioticOrganismsSearch(BaseOptimizer):
    """
    Symbiotic Organisms Search (SOS)
    
    Algorithm based on mutualism, commensalism, and parasitism
    symbiotic relationships in nature.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Symbiotic Organisms Search"
        self.aliases = ["sos", "symbiotic", "symbiotic_organisms"]
    
    def _optimize(self, objective_function, bounds, dimension):
        """
        Execute the Symbiotic Organisms Search
        
        Args:
            objective_function: Function to optimize
            bounds: Search space bounds
            dimension: Problem dimension
            
        Returns:
            Tuple containing (best_position, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize ecosystem
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Select random organism for interaction
                j = i
                while j == i:
                    j = np.random.randint(0, self.population_size)
                
                # Phase 1: Mutualism
                mutual_vector = (population[i] + population[j]) / 2
                BF1 = np.random.choice([1, 2])  # Benefit factor 1
                BF2 = np.random.choice([1, 2])  # Benefit factor 2
                
                new_i = population[i] + np.random.random() * (best_position - mutual_vector * BF1)
                new_j = population[j] + np.random.random() * (best_position - mutual_vector * BF2)
                
                new_i = np.clip(new_i, bounds[0], bounds[1])
                new_j = np.clip(new_j, bounds[0], bounds[1])
                
                new_fitness_i = objective_function(new_i)
                new_fitness_j = objective_function(new_j)
                
                if new_fitness_i < fitness[i]:
                    population[i] = new_i
                    fitness[i] = new_fitness_i
                
                if new_fitness_j < fitness[j]:
                    population[j] = new_j
                    fitness[j] = new_fitness_j
                
                # Phase 2: Commensalism
                k = i
                while k == i or k == j:
                    k = np.random.randint(0, self.population_size)
                
                new_i = population[i] + np.random.uniform(-1, 1) * (best_position - population[k])
                new_i = np.clip(new_i, bounds[0], bounds[1])
                
                new_fitness_i = objective_function(new_i)
                if new_fitness_i < fitness[i]:
                    population[i] = new_i
                    fitness[i] = new_fitness_i
                
                # Phase 3: Parasitism
                parasite = population[i].copy()
                # Randomly modify some dimensions
                parasite_dims = np.random.choice(dimension, size=max(1, dimension // 2), replace=False)
                parasite[parasite_dims] = np.random.uniform(bounds[0], bounds[1], len(parasite_dims))
                
                parasite_fitness = objective_function(parasite)
                if parasite_fitness < fitness[j]:
                    population[j] = parasite
                    fitness[j] = parasite_fitness
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions