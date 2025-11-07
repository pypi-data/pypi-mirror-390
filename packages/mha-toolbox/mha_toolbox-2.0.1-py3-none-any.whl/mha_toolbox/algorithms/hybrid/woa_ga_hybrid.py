"""
WOA-GA Hybrid (Whale Optimization Algorithm - Genetic Algorithm)
================================================================

Hybrid combining WOA's hunting behavior with GA's genetic operators.
"""

import numpy as np
from ...base import BaseOptimizer


class WOA_GA_Hybrid(BaseOptimizer):
    """WOA-GA Hybrid combining whale hunting with genetic operators"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "WOA-GA Hybrid"
        self.aliases = ["woa_ga", "woa_ga_hybrid", "whale_genetic"]
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
    
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
            a = 2 - 2 * (iteration / self.max_iterations)
            a2 = -1 + iteration * (-1 / self.max_iterations)
            
            # WOA phase
            for i in range(self.population_size):
                r = np.random.random()
                A = 2 * a * r - a
                C = 2 * r
                l = np.random.uniform(-1, 1)
                p = np.random.random()
                
                if p < 0.5:
                    if np.abs(A) < 1:
                        # Encircling prey
                        D = np.abs(C * best_position - population[i])
                        population[i] = best_position - A * D
                    else:
                        # Search for prey
                        rand_idx = np.random.randint(0, self.population_size)
                        X_rand = population[rand_idx]
                        D = np.abs(C * X_rand - population[i])
                        population[i] = X_rand - A * D
                else:
                    # Spiral updating position
                    D = np.abs(best_position - population[i])
                    population[i] = D * np.exp(l) * np.cos(2 * np.pi * l) + best_position
                
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # GA phase - Selection
            fitness = np.array([objective_function(ind) for ind in population])
            fitness_inv = 1.0 / (fitness + 1e-10)
            probabilities = fitness_inv / np.sum(fitness_inv)
            selected_idx = np.random.choice(self.population_size, self.population_size, p=probabilities)
            selected = population[selected_idx]
            
            # GA phase - Crossover
            offspring = []
            for i in range(0, self.population_size, 2):
                parent1 = selected[i]
                parent2 = selected[min(i+1, self.population_size-1)]
                
                if np.random.random() < self.crossover_rate:
                    crossover_point = np.random.randint(1, dimension)
                    child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
                    child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                offspring.extend([child1, child2])
            
            offspring = np.array(offspring[:self.population_size])
            
            # GA phase - Mutation
            for i in range(self.population_size):
                if np.random.random() < self.mutation_rate:
                    mutation_idx = np.random.randint(0, dimension)
                    offspring[i][mutation_idx] = np.random.uniform(bounds[0], bounds[1])
            
            # Hybrid: combine WOA and GA populations
            population = 0.6 * population + 0.4 * offspring
            population = np.clip(population, bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            best_idx = np.argmin(fitness)
            if fitness[best_idx] < best_fitness:
                best_position = population[best_idx].copy()
                best_fitness = fitness[best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions