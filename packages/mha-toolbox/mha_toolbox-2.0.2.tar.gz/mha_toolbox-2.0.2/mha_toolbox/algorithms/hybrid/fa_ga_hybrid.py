"""
FA-GA Hybrid (Firefly Algorithm - Genetic Algorithm)
====================================================

Hybrid combining FA's light attraction with GA's evolutionary operators.
"""

import numpy as np
from ...base import BaseOptimizer


class FA_GA_Hybrid(BaseOptimizer):
    """FA-GA Hybrid combining firefly light attraction with genetic evolution"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "FA-GA Hybrid"
        self.aliases = ["fa_ga", "fa_ga_hybrid", "firefly_genetic"]
        self.alpha = 0.5
        self.beta0 = 1.0
        self.gamma = 1.0
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        light_intensity = 1.0 / (fitness + 1e-10)
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            alpha_adaptive = self.alpha * (1 - iteration / self.max_iterations)
            
            # FA phase - Light attraction
            for i in range(self.population_size):
                for j in range(self.population_size):
                    if light_intensity[j] > light_intensity[i]:
                        r = np.linalg.norm(population[i] - population[j])
                        beta = self.beta0 * np.exp(-self.gamma * r**2)
                        
                        epsilon = np.random.uniform(-0.5, 0.5, dimension)
                        population[i] = (population[i] + 
                                       beta * (population[j] - population[i]) + 
                                       alpha_adaptive * epsilon)
                        
                        population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            light_intensity = 1.0 / (fitness + 1e-10)
            
            # GA phase - Selection (Tournament)
            selected = []
            for _ in range(self.population_size):
                i1, i2 = np.random.choice(self.population_size, 2, replace=False)
                if fitness[i1] < fitness[i2]:
                    selected.append(population[i1].copy())
                else:
                    selected.append(population[i2].copy())
            selected = np.array(selected)
            
            # GA phase - Crossover
            offspring = []
            for i in range(0, self.population_size, 2):
                parent1 = selected[i]
                parent2 = selected[min(i+1, self.population_size-1)]
                
                if np.random.random() < self.crossover_rate:
                    # Uniform crossover
                    mask = np.random.random(dimension) < 0.5
                    child1 = np.where(mask, parent1, parent2)
                    child2 = np.where(mask, parent2, parent1)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                offspring.extend([child1, child2])
            
            offspring = np.array(offspring[:self.population_size])
            
            # GA phase - Mutation
            for i in range(self.population_size):
                if np.random.random() < self.mutation_rate:
                    mutation_mask = np.random.random(dimension) < 0.2
                    mutations = np.random.uniform(bounds[0], bounds[1], dimension)
                    offspring[i] = np.where(mutation_mask, mutations, offspring[i])
            
            # Hybrid: blend FA and GA populations
            population = 0.5 * population + 0.5 * offspring
            population = np.clip(population, bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            light_intensity = 1.0 / (fitness + 1e-10)
            
            best_idx = np.argmin(fitness)
            if fitness[best_idx] < best_fitness:
                best_position = population[best_idx].copy()
                best_fitness = fitness[best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions