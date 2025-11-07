"""Black Hole Algorithm (BH) - Hatamlou (2013)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class BlackHoleAlgorithm(BaseOptimizer):
    """Black Hole Algorithm - Hatamlou (2013)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        
        self.stars = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(s) for s in self.stars])
        best_idx = np.argmin(self.fitness)
        self.black_hole = self.stars[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Calculate event horizon radius
            total_fitness = np.sum(self.fitness)
            if total_fitness > 0:
                event_horizon = self.best_fitness / total_fitness
            else:
                event_horizon = 0.01
            
            # Move stars towards black hole
            for i in range(self.population_size):
                # Move star towards black hole
                self.stars[i] = self.stars[i] + np.random.rand() * (self.black_hole - self.stars[i])
                self.stars[i] = np.clip(self.stars[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate fitness
                self.fitness[i] = self.objective_function(self.stars[i])
                
                # Check if star crosses event horizon
                distance = np.linalg.norm(self.stars[i] - self.black_hole)
                if distance < event_horizon:
                    # Generate new star at random position
                    self.stars[i] = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], self.dimensions)
                    self.fitness[i] = self.objective_function(self.stars[i])
                
                # Update black hole if better solution found
                if self.fitness[i] < self.best_fitness:
                    self.black_hole = self.stars[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.black_hole, self.best_fitness, self.convergence_curve
