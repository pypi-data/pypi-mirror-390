"""KH-PSO Hybrid: Krill Herd + PSO"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class KH_PSO_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 Nmax: float = 0.01, w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.Nmax = Nmax
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.krills = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.krills])
        self.velocities = np.zeros((population_size, dimensions))
        self.pbest = self.krills.copy()
        self.pbest_fitness = self.fitness.copy()
        best_idx = np.argmin(self.fitness)
        self.gbest = self.krills[best_idx].copy()
        self.gbest_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                K_worst_idx = np.argmax(self.fitness)
                K_best_idx = np.argmin(self.fitness)
                
                alpha_local = 0
                nn_count = 0
                for j in range(self.population_size):
                    if np.linalg.norm(self.krills[j] - self.krills[i]) < 0.2:
                        if self.fitness[j] < self.fitness[i]:
                            alpha_local += (self.fitness[j] - self.fitness[i]) / (self.fitness[K_worst_idx] - self.fitness[K_best_idx] + 1e-10) * (self.krills[j] - self.krills[i])
                            nn_count += 1
                
                if nn_count > 0:
                    alpha_local /= nn_count
                
                alpha_target = 2 * (self.fitness[K_best_idx] - self.fitness[i]) / (self.fitness[K_worst_idx] - self.fitness[K_best_idx] + 1e-10) * (self.krills[K_best_idx] - self.krills[i])
                
                alpha = alpha_local + alpha_target
                
                beta = 2 * (1 - iteration / self.max_iterations) * np.random.randn(self.dimensions)
                
                dX = self.Nmax * (alpha + beta)
                self.krills[i] += dX
                self.krills[i] = np.clip(self.krills[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.krills[i])
            
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    self.velocities[i] = (self.w * self.velocities[i] +
                                         self.c1 * np.random.rand() * (self.pbest[i] - self.krills[i]) +
                                         self.c2 * np.random.rand() * (self.gbest - self.krills[i]))
                    self.krills[i] += self.velocities[i]
                    self.krills[i] = np.clip(self.krills[i], self.bounds[:, 0], self.bounds[:, 1])
                    self.fitness[i] = self.objective_function(self.krills[i])
            
            for i in range(self.population_size):
                if self.fitness[i] < self.pbest_fitness[i]:
                    self.pbest[i] = self.krills[i].copy()
                    self.pbest_fitness[i] = self.fitness[i]
            
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.gbest_fitness:
                self.gbest = self.krills[best_idx].copy()
                self.gbest_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest, self.gbest_fitness, self.convergence_curve
