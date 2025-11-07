"""
Bat Algorithm (BA)

Based on: Yang, X. S. (2010). A new metaheuristic bat-inspired algorithm.
In Nature inspired cooperative strategies for optimization (pp. 65-74).
"""

import numpy as np
from ..base import BaseOptimizer


class BatAlgorithm(BaseOptimizer):
    """
    Bat Algorithm (BA)
    
    BA is inspired by the echolocation behavior of microbats. The algorithm
    uses the idealized behavior of microbats to perform optimization.
    
    Parameters
    ----------
    A : float, default=0.5
        Loudness (constant or decreasing)
    r : float, default=0.5
        Pulse rate (constant or increasing)
    f_min : float, default=0.0
        Minimum frequency
    f_max : float, default=2.0
        Maximum frequency
    """
    
    aliases = ["ba", "bat", "bat_algorithm"]
    
    def __init__(self, A=0.5, r=0.5, f_min=0.0, f_max=2.0, **kwargs):
        super().__init__(**kwargs)
        self.A = A
        self.r = r
        self.f_min = f_min
        self.f_max = f_max
        self.algorithm_name = "BA"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        velocity = np.zeros((self.population_size_, self.dimensions_))
        frequency = np.zeros(self.population_size_)
        A = np.full(self.population_size_, self.A)
        r = np.full(self.population_size_, self.r)
        fitness = np.array([objective_function(ind) for ind in population])
        best_idx = np.argmin(fitness)
        best_bat = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(self.population_size_):
                frequency[i] = self.f_min + (self.f_max - self.f_min) * np.random.random()
                velocity[i] += (population[i] - best_bat) * frequency[i]
                new_position = population[i] + velocity[i]
                if np.random.random() > r[i]:
                    new_position = best_bat + 0.001 * np.random.randn(self.dimensions_)
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                new_fitness = objective_function(new_position)
                if new_fitness < fitness[i] and np.random.random() < A[i]:
                    population[i] = new_position.copy()
                    fitness[i] = new_fitness
                    A[i] *= 0.9
                    r[i] = self.r * (1 - np.exp(-0.9 * iteration))
                    if new_fitness < best_fitness:
                        best_bat = new_position.copy()
                        best_fitness = new_fitness
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        return best_bat, best_fitness, global_fitness, local_fitness, local_positions
