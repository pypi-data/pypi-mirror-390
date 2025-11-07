"""
Marine Predators Algorithm (MPA)
===============================

Marine Predators Algorithm inspired by the foraging strategies
of marine predators in ocean.
"""

import numpy as np
from ..base import BaseOptimizer


class MarinePredatorsAlgorithm(BaseOptimizer):
    """Marine Predators Algorithm (MPA)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
        self.algorithm_name = "Marine Predators Algorithm"
        self.aliases = ["mpa", "marine_predators", "marine_algorithm"]
    
    def _optimize(self, objective_function, bounds, dimension):
        # Initialize prey and predators
        prey = np.random.uniform(bounds[0], bounds[1], (self.population_size, dimension))
        predators = prey.copy()
        
        fitness_prey = np.array([objective_function(ind) for ind in prey])
        elite_idx = np.argmin(fitness_prey)
        elite = prey[elite_idx].copy()
        elite_fitness = fitness_prey[elite_idx]
        
        global_fitness = [elite_fitness]
        local_fitness = [fitness_prey.copy()]
        local_positions = [prey.copy()]
        
        for iteration in range(self.max_iterations):
            CF = (1 - iteration / self.max_iterations) ** (2 * iteration / self.max_iterations)
            
            for i in range(self.population_size):
                r = np.random.random()
                
                if iteration < self.max_iterations / 3:
                    # Phase 1: High-velocity ratio - Exploration
                    if r < 0.5:
                        prey[i] = prey[i] + CF * (elite - prey[i]) * np.random.random()
                    else:
                        k = np.random.randint(0, self.population_size)
                        prey[i] = prey[i] + CF * (prey[k] - prey[i]) * np.random.random()
                elif iteration < 2 * self.max_iterations / 3:
                    # Phase 2: Unit-velocity ratio - Transition
                    if r < 0.5:
                        prey[i] = elite + CF * (elite - prey[i]) * np.random.random()
                    else:
                        prey[i] = CF * elite + (1 - CF) * prey[i]
                else:
                    # Phase 3: Low-velocity ratio - Exploitation
                    prey[i] = CF * elite + (1 - CF) * prey[i]
                
                prey[i] = np.clip(prey[i], bounds[0], bounds[1])
            
            fitness_prey = np.array([objective_function(ind) for ind in prey])
            current_best_idx = np.argmin(fitness_prey)
            if fitness_prey[current_best_idx] < elite_fitness:
                elite = prey[current_best_idx].copy()
                elite_fitness = fitness_prey[current_best_idx]
            
            global_fitness.append(elite_fitness)
            local_fitness.append(fitness_prey.copy())
            local_positions.append(prey.copy())
        
        return elite, elite_fitness, global_fitness, local_fitness, local_positions