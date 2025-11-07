"""
Differential Evolution (DE)

Based on: Storn, R., & Price, K. (1997). Differential evolution–a simple and 
efficient heuristic for global optimization over continuous spaces.
"""

import numpy as np
from ..base import BaseOptimizer


class DifferentialEvolution(BaseOptimizer):
    """
    Differential Evolution (DE)
    
    DE is a population-based optimization algorithm that uses vector differences
    for perturbing the vector population. It includes mutation, crossover, and
    selection operations.
    
    Parameters
    ----------
    F : float, default=0.5
        Differential weight (scaling factor)
    CR : float, default=0.7
        Crossover probability
    strategy : str, default='rand/1/bin'
        DE strategy to use
    """
    
    aliases = ["de", "differential", "differential_evolution"]
    
    def __init__(self, F=0.5, CR=0.7, strategy='rand/1/bin', **kwargs):
        super().__init__(**kwargs)
        self.F = F
        self.CR = CR
        self.strategy = strategy
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        fitness = np.array([objective_function(ind) for ind in population])
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(self.population_size_):
                if self.strategy == 'rand/1/bin':
                    candidates = list(range(self.population_size_))
                    candidates.remove(i)
                    r1, r2, r3 = np.random.choice(candidates, 3, replace=False)
                    mutant = population[r1] + self.F * (population[r2] - population[r3])
                elif self.strategy == 'best/1/bin':
                    best_idx = np.argmin(fitness)
                    candidates = list(range(self.population_size_))
                    candidates.remove(i)
                    r1, r2 = np.random.choice(candidates, 2, replace=False)
                    mutant = population[best_idx] + self.F * (population[r1] - population[r2])
                mutant = np.clip(mutant, self.lower_bound_, self.upper_bound_)
                trial = population[i].copy()
                j_rand = np.random.randint(0, self.dimensions_)
                for j in range(self.dimensions_):
                    if np.random.random() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                trial_fitness = objective_function(trial)
                if trial_fitness < fitness[i]:
                    population[i] = trial
                    fitness[i] = trial_fitness
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            best_fitness = np.min(fitness)
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        best_idx = np.argmin(fitness)
        return population[best_idx], fitness[best_idx], global_fitness, local_fitness, local_positions
