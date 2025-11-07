"""Group Search Optimizer (GSO) - He (2009)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class GroupSearchOptimizer(BaseOptimizer):
    """Group Search Optimizer - He (2009)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100,
                 producer_ratio: float = 0.2, scrounger_ratio: float = 0.6):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.producer_ratio = producer_ratio
        self.scrounger_ratio = scrounger_ratio
        
        self.animals = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(a) for a in self.animals])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.animals[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        num_producers = max(1, int(self.population_size * self.producer_ratio))
        num_scroungers = int(self.population_size * self.scrounger_ratio)
        
        for iteration in range(self.max_iterations):
            # Sort by fitness
            sorted_indices = np.argsort(self.fitness)
            
            # Producer behavior (best individuals scan for better positions)
            for i in range(num_producers):
                idx = sorted_indices[i]
                
                # Generate scanning direction
                direction = np.random.randn(self.dimensions)
                direction_norm = np.linalg.norm(direction)
                if direction_norm > 1e-10:
                    direction = direction / direction_norm
                
                # Calculate step size
                step_size = 0.1 * (self.bounds[:, 1] - self.bounds[:, 0])
                new_animal = self.animals[idx] + step_size * direction
                new_animal = np.clip(new_animal, self.bounds[:, 0], self.bounds[:, 1])
                new_fitness = self.objective_function(new_animal)
                
                if new_fitness < self.fitness[idx]:
                    self.animals[idx] = new_animal
                    self.fitness[idx] = new_fitness
            
            # Scrounger behavior (follow the best producer)
            for i in range(num_scroungers):
                idx = sorted_indices[num_producers + i]
                self.animals[idx] = self.animals[idx] + np.random.rand() * (self.best_solution - self.animals[idx])
                self.animals[idx] = np.clip(self.animals[idx], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[idx] = self.objective_function(self.animals[idx])
            
            # Ranger behavior (random exploration)
            for i in range(num_producers + num_scroungers, self.population_size):
                self.animals[i] = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], self.dimensions)
                self.fitness[i] = self.objective_function(self.animals[i])
            
            # Update best solution
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.best_fitness:
                self.best_solution = self.animals[best_idx].copy()
                self.best_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
