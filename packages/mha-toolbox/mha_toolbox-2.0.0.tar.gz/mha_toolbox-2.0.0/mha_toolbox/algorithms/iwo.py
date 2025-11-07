"""Invasive Weed Optimization (IWO) - Mehrabian (2006)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class InvasiveWeedOptimization(BaseOptimizer):
    """Invasive Weed Optimization - Mehrabian (2006)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 max_pop: int = 50, Smax: int = 5, Smin: int = 0):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.max_pop = max_pop
        self.Smax = Smax
        self.Smin = Smin
        
        self.weeds = [np.random.uniform(bounds[:, 0], bounds[:, 1], dimensions) for _ in range(population_size)]
        self.fitness = [objective_function(w) for w in self.weeds]
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.weeds[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Calculate fitness statistics
            worst_fitness = max(self.fitness)
            best_fitness_iter = min(self.fitness)
            
            new_weeds = []
            new_fitness = []
            
            # Reproduction: each weed produces seeds
            for i in range(len(self.weeds)):
                # Calculate number of seeds based on fitness
                if worst_fitness != best_fitness_iter:
                    ratio = (self.fitness[i] - worst_fitness) / (best_fitness_iter - worst_fitness)
                else:
                    ratio = 0.5
                
                # Better weeds produce more seeds
                num_seeds = int(self.Smin + (self.Smax - self.Smin) * (1 - ratio))
                num_seeds = max(1, num_seeds)
                
                # Standard deviation decreases over iterations (adaptive dispersal)
                sigma = ((self.max_iterations - iteration) / self.max_iterations) ** 3
                sigma = sigma * (self.bounds[:, 1] - self.bounds[:, 0])
                
                # Produce seeds
                for _ in range(num_seeds):
                    seed = self.weeds[i] + np.random.normal(0, sigma, self.dimensions)
                    seed = np.clip(seed, self.bounds[:, 0], self.bounds[:, 1])
                    seed_fitness = self.objective_function(seed)
                    
                    new_weeds.append(seed)
                    new_fitness.append(seed_fitness)
                    
                    if seed_fitness < self.best_fitness:
                        self.best_solution = seed.copy()
                        self.best_fitness = seed_fitness
            
            # Combine parent and offspring populations
            self.weeds.extend(new_weeds)
            self.fitness.extend(new_fitness)
            
            # Competitive exclusion: keep only max_pop best weeds
            if len(self.weeds) > self.max_pop:
                sorted_indices = np.argsort(self.fitness)
                self.weeds = [self.weeds[i] for i in sorted_indices[:self.max_pop]]
                self.fitness = [self.fitness[i] for i in sorted_indices[:self.max_pop]]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
