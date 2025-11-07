"""DA-GA Hybrid: Dragonfly Algorithm + GA"""
import numpy as np
from typing import Callable, Tuple
from mha_toolbox.base import BaseOptimizer

class DA_GA_Hybrid(BaseOptimizer):
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.dragonflies = np.random.uniform(bounds[:, 0], bounds[:, 1], (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.dragonflies])
        self.velocities = np.zeros((population_size, dimensions))
        best_idx = np.argmin(self.fitness)
        self.food_pos = self.dragonflies[best_idx].copy()
        self.food_fitness = self.fitness[best_idx]
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            w = 0.9 - iteration * 0.5 / self.max_iterations
            
            for i in range(self.population_size):
                S = -np.sum([self.dragonflies[j] - self.dragonflies[i] for j in range(self.population_size) if j != i], axis=0)
                A = np.mean(self.velocities, axis=0) - self.velocities[i]
                C = np.mean(self.dragonflies, axis=0) - self.dragonflies[i]
                F = self.food_pos - self.dragonflies[i]
                
                self.velocities[i] = w * self.velocities[i] + 2*S + 2*A + 2*C + 2*F
                self.dragonflies[i] += self.velocities[i]
                self.dragonflies[i] = np.clip(self.dragonflies[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.dragonflies[i])
            
            if iteration % 5 == 0:
                for i in range(0, self.population_size-1, 2):
                    if np.random.rand() < self.crossover_rate:
                        alpha = np.random.rand()
                        offspring1 = alpha * self.dragonflies[i] + (1-alpha) * self.dragonflies[i+1]
                        offspring2 = (1-alpha) * self.dragonflies[i] + alpha * self.dragonflies[i+1]
                        offspring1 = np.clip(offspring1, self.bounds[:, 0], self.bounds[:, 1])
                        offspring2 = np.clip(offspring2, self.bounds[:, 0], self.bounds[:, 1])
                        
                        fit1, fit2 = self.objective_function(offspring1), self.objective_function(offspring2)
                        if fit1 < self.fitness[i]:
                            self.dragonflies[i], self.fitness[i] = offspring1, fit1
                        if fit2 < self.fitness[i+1]:
                            self.dragonflies[i+1], self.fitness[i+1] = offspring2, fit2
            
            best_idx = np.argmin(self.fitness)
            if self.fitness[best_idx] < self.food_fitness:
                self.food_pos = self.dragonflies[best_idx].copy()
                self.food_fitness = self.fitness[best_idx]
            
            self.convergence_curve.append(self.food_fitness)
        
        return self.food_pos, self.food_fitness, self.convergence_curve
