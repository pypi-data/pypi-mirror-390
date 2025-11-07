"""
Culture Algorithm (CA)
=====================

Culture Algorithm inspired by human cultural evolution and
social learning mechanisms.
"""

import numpy as np
from ..base import BaseOptimizer


class CultureAlgorithm(BaseOptimizer):
    """
    Culture Algorithm (CA)
    
    Algorithm based on cultural evolution, belief space,
    and population space interactions.
    """
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Culture Algorithm"
        self.aliases = ["ca", "culture", "culture_algorithm"]
    
    def _optimize(self, objective_function, bounds, dimension):
        population = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Belief space (cultural knowledge)
        belief_space = {
            'situational': population[np.argmin(fitness)].copy(),
            'normative': np.array([bounds[0], bounds[1]]).T
        }
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness, local_fitness, local_positions = [best_fitness], [fitness.copy()], [population.copy()]
        
        for iteration in range(self.max_iterations):
            # Update population based on belief space
            for i in range(self.population_size):
                if np.random.random() < 0.5:
                    # Influenced by situational knowledge
                    population[i] = belief_space['situational'] + np.random.randn(dimension) * (1 - iteration / self.max_iterations)
                else:
                    # Influenced by normative knowledge
                    for d in range(dimension):
                        population[i, d] = np.random.uniform(belief_space['normative'][d, 0], belief_space['normative'][d, 1])
                
                population[i] = np.clip(population[i], bounds[0], bounds[1])
            
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update belief space
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < objective_function(belief_space['situational']):
                belief_space['situational'] = population[current_best_idx].copy()
            
            # Update normative knowledge
            top_indices = np.argsort(fitness)[:max(2, self.population_size // 5)]
            for d in range(dimension):
                belief_space['normative'][d, 0] = np.min(population[top_indices, d])
                belief_space['normative'][d, 1] = np.max(population[top_indices, d])
            
            if fitness[current_best_idx] < best_fitness:
                best_position, best_fitness = population[current_best_idx].copy(), fitness[current_best_idx]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.copy())
            local_positions.append(population.copy())
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions