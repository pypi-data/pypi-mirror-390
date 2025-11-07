"""Big Bang-Big Crunch Algorithm (BB-BC) - Erol (2006)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class BigBangBigCrunchAlgorithm(BaseOptimizer):
    """Big Bang-Big Crunch Algorithm - Erol (2006)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        
        self.best_solution = None
        self.best_fitness = float('inf')
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        # Initialize with random solution
        center_of_mass = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], self.dimensions)
        
        for iteration in range(self.max_iterations):
            # Big Bang: Generate random candidates around center of mass
            candidates = []
            fitness_values = []
            
            # Generate population
            for i in range(self.population_size):
                if iteration == 0:
                    # Initial random generation
                    candidate = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], self.dimensions)
                else:
                    # Generate around center of mass with decreasing variance
                    std = (self.bounds[:, 1] - self.bounds[:, 0]) * (1 - iteration / self.max_iterations)
                    candidate = center_of_mass + np.random.normal(0, std, self.dimensions)
                    candidate = np.clip(candidate, self.bounds[:, 0], self.bounds[:, 1])
                
                candidates.append(candidate)
                fitness_values.append(self.objective_function(candidate))
            
            candidates = np.array(candidates)
            fitness_values = np.array(fitness_values)
            
            # Find best candidate
            best_idx = np.argmin(fitness_values)
            if fitness_values[best_idx] < self.best_fitness:
                self.best_solution = candidates[best_idx].copy()
                self.best_fitness = fitness_values[best_idx]
            
            # Big Crunch: Calculate center of mass
            # Weighted by inverse of fitness (better solutions have more weight)
            weights = 1.0 / (fitness_values + 1e-10)
            total_weight = np.sum(weights)
            
            center_of_mass = np.zeros(self.dimensions)
            for i in range(self.population_size):
                center_of_mass += candidates[i] * weights[i]
            center_of_mass /= total_weight
            
            # Ensure center of mass is within bounds
            center_of_mass = np.clip(center_of_mass, self.bounds[:, 0], self.bounds[:, 1])
            
            # Evaluate center of mass
            center_fitness = self.objective_function(center_of_mass)
            if center_fitness < self.best_fitness:
                self.best_solution = center_of_mass.copy()
                self.best_fitness = center_fitness
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
