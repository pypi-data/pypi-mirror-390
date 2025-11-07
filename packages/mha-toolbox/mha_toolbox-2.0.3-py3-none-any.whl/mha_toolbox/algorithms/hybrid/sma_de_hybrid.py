"""
SMA-DE Hybrid (Slime Mould Algorithm - Differential Evolution)
==============================================================

Hybrid combining SMA's biological foraging with DE's mutation strategies.
"""

import numpy as np
from ...base import BaseOptimizer


class SMA_DE_Hybrid(BaseOptimizer):
    """SMA-DE Hybrid combining slime mould foraging with differential evolution"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "SMA-DE Hybrid"
        self.aliases = ["sma_de", "sma_de_hybrid", "slime_differential"]
        self.z = 0.03
        self.F = 0.6
        self.CR = 0.9
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        sorted_idx = np.argsort(fitness)
        best_position = population[sorted_idx[0]].copy()
        best_fitness = fitness[sorted_idx[0]]
        worst_fitness = fitness[sorted_idx[-1]]
        
        global_fitness = [best_fitness]
        local_fitness = [fitness.copy()]
        local_positions = [population.copy()]
        
        for iteration in range(self.max_iterations):
            a = np.arctanh(-(iteration / self.max_iterations) + 1)
            b = 1 - (iteration / self.max_iterations)
            
            # SMA phase
            sorted_idx = np.argsort(fitness)
            fitness_normalized = (fitness - worst_fitness) / (best_fitness - worst_fitness + 1e-10)
            
            weights = np.zeros(self.population_size)
            for i in range(self.population_size):
                if i < self.population_size // 2:
                    weights[i] = 1 + np.random.random() * np.log10((best_fitness - fitness[i]) / 
                                                                    (best_fitness - worst_fitness + 1e-10) + 1)
                else:
                    weights[i] = 1 - np.random.random() * np.log10((best_fitness - fitness[i]) / 
                                                                    (best_fitness - worst_fitness + 1e-10) + 1)
            
            for i in range(self.population_size):
                r = np.random.random()
                
                if r < self.z:
                    population[i] = np.random.uniform(bounds[0], bounds[1], dimension)
                else:
                    p = np.tanh(fitness[i] / (fitness[sorted_idx[0]] + 1e-10))
                    vb = np.random.uniform(-a, a, dimension)
                    vc = np.random.uniform(-b, b, dimension)
                    
                    if np.random.random() < p:
                        rand_idx = np.random.randint(0, self.population_size)
                        population[i] = best_position + vb * (weights[i] * population[sorted_idx[0]] - 
                                                               population[rand_idx])
                    else:
                        population[i] = vc * population[i]
                
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            # DE phase - Mutation and Crossover
            for i in range(self.population_size):
                indices = list(range(self.population_size))
                indices.remove(i)
                a_idx, b_idx, c_idx = np.random.choice(indices, 3, replace=False)
                
                mutant = population[a_idx] + self.F * (population[b_idx] - population[c_idx])
                mutant = np.clip(mutant, bounds[0], bounds[1])
                
                trial = np.copy(population[i])
                j_rand = np.random.randint(0, dimension)
                for j in range(dimension):
                    if np.random.random() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                
                trial_fitness = objective_function(trial)
                if trial_fitness < fitness[i]:
                    population[i] = trial
                    fitness[i] = trial_fitness
            
            sorted_idx = np.argsort(fitness)
            if fitness[sorted_idx[0]] < best_fitness:
                best_position = population[sorted_idx[0]].copy()
                best_fitness = fitness[sorted_idx[0]]
            worst_fitness = fitness[sorted_idx[-1]]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions