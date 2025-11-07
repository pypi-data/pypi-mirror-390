"""Lightning Search Algorithm (LSA) - Shareef (2015)"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class LightningSearchAlgorithm(BaseOptimizer):
    """Lightning Search Algorithm - Shareef (2015)"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 30, max_iterations: int = 100, num_leaders: int = 3):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.num_leaders = num_leaders
        
        self.projectiles = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(p) for p in self.projectiles])
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.projectiles[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            # Stepped leader phase
            for i in range(self.population_size):
                # Create space leaders around each projectile
                for _ in range(self.num_leaders):
                    # Generate step with decreasing magnitude
                    step_size = 0.1 * (self.bounds[:, 1] - self.bounds[:, 0]) * (1 - iteration / self.max_iterations)
                    step = step_size * np.random.randn(self.dimensions)
                    
                    leader = self.projectiles[i] + step
                    leader = np.clip(leader, self.bounds[:, 0], self.bounds[:, 1])
                    leader_fitness = self.objective_function(leader)
                    
                    # Accept if better
                    if leader_fitness < self.fitness[i]:
                        self.projectiles[i] = leader
                        self.fitness[i] = leader_fitness
                        
                        if self.fitness[i] < self.best_fitness:
                            self.best_solution = self.projectiles[i].copy()
                            self.best_fitness = self.fitness[i]
            
            # Space leader propagation (move towards best solution)
            for i in range(self.population_size):
                self.projectiles[i] = self.projectiles[i] + np.random.rand() * (self.best_solution - self.projectiles[i])
                self.projectiles[i] = np.clip(self.projectiles[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.projectiles[i])
                
                if self.fitness[i] < self.best_fitness:
                    self.best_solution = self.projectiles[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_solution, self.best_fitness, self.convergence_curve
