"""Shuffled Frog Leaping Algorithm (SFLA) - Eusuff (2003)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class ShuffledFrogLeapingAlgorithm(BaseOptimizer):
    """Shuffled Frog Leaping Algorithm - Eusuff (2003)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100, num_memeplexes: int = 3):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.num_memeplexes = num_memeplexes
        
        self.frogs = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(f) for f in self.frogs])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.frogs[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Sort frogs by fitness
            sorted_indices = np.argsort(self.fitness)
            self.frogs = self.frogs[sorted_indices]
            self.fitness = self.fitness[sorted_indices]
            
            # Partition into memeplexes
            memeplex_size = self.population_size // self.num_memeplexes
            
            for m in range(self.num_memeplexes):
                start_idx = m * memeplex_size
                end_idx = start_idx + memeplex_size
                
                if end_idx > self.population_size:
                    end_idx = self.population_size
                
                memeplex = self.frogs[start_idx:end_idx].copy()
                memeplex_fitness = self.fitness[start_idx:end_idx].copy()
                
                # Find worst and best in memeplex
                worst_idx = np.argmax(memeplex_fitness)
                best_idx = np.argmin(memeplex_fitness)
                
                # Update worst frog towards local best
                new_frog = memeplex[worst_idx] + np.random.rand() * (memeplex[best_idx] - memeplex[worst_idx])
                new_frog = np.clip(new_frog, self.bounds[:, 0], self.bounds[:, 1])
                new_fitness = self.objective_function(new_frog)
                
                if new_fitness < memeplex_fitness[worst_idx]:
                    memeplex[worst_idx] = new_frog
                    memeplex_fitness[worst_idx] = new_fitness
                else:
                    # Try global best
                    new_frog = memeplex[worst_idx] + np.random.rand() * (self.best_solution - memeplex[worst_idx])
                    new_frog = np.clip(new_frog, self.bounds[:, 0], self.bounds[:, 1])
                    new_fitness = self.objective_function(new_frog)
                    
                    if new_fitness < memeplex_fitness[worst_idx]:
                        memeplex[worst_idx] = new_frog
                        memeplex_fitness[worst_idx] = new_fitness
                    else:
                        # Random jump
                        memeplex[worst_idx] = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], self.dimensions)
                        memeplex_fitness[worst_idx] = self.objective_function(memeplex[worst_idx])
                
                # Update main population
                self.frogs[start_idx:end_idx] = memeplex
                self.fitness[start_idx:end_idx] = memeplex_fitness
            
            # Update best solution
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.best_fitness:
                self.best_solution = self.frogs[best_idx].copy()
                self.best_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
