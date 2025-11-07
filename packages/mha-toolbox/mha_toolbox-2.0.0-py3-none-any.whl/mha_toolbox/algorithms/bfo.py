"""Bacterial Foraging Optimization (BFO) - Passino (2002)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class BacterialForagingOptimization(BaseOptimizer):
    """Bacterial Foraging Optimization - Passino (2002)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 Nc: int = 4, Ns: int = 4, Nre: int = 4, Ned: int = 2, C: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.Nc = Nc  # Chemotactic steps
        self.Ns = Ns  # Swim length
        self.Nre = Nre  # Reproduction steps
        self.Ned = Ned  # Elimination-dispersal steps
        self.C = C  # Step size
        
        self.bacteria = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(b) for b in self.bacteria])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.bacteria[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Chemotaxis loop
            for i in range(self.population_size):
                # Tumble: generate random direction
                delta = np.random.randn(self.dimensions)
                delta_norm = np.linalg.norm(delta)
                if delta_norm > 1e-10:
                    delta = delta / delta_norm
                else:
                    delta = np.random.randn(self.dimensions)
                    delta = delta / (np.linalg.norm(delta) + 1e-10)
                
                # Move bacterium
                self.bacteria[i] = self.bacteria[i] + self.C * delta
                self.bacteria[i] = np.clip(self.bacteria[i], self.bounds[:, 0], self.bounds[:, 1])
                
                new_fitness = self.objective_function(self.bacteria[i])
                
                # Swim if fitness improves
                if new_fitness < self.fitness[i]:
                    for swim_step in range(self.Ns):
                        self.bacteria[i] = self.bacteria[i] + self.C * delta
                        self.bacteria[i] = np.clip(self.bacteria[i], self.bounds[:, 0], self.bounds[:, 1])
                        swim_fitness = self.objective_function(self.bacteria[i])
                        
                        if swim_fitness < new_fitness:
                            new_fitness = swim_fitness
                        else:
                            break
                
                self.fitness[i] = new_fitness
                
                if self.fitness[i] < self.best_fitness:
                    self.best_solution = self.bacteria[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
