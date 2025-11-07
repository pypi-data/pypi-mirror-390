"""
Advanced Hybrid Metaheuristic Algorithms
========================================

15+ Hybrid algorithms combining strengths of multiple optimization techniques.
Each hybrid is designed for specific problem types with configurable parameters.
"""

import numpy as np
from typing import Callable, Dict, Tuple, Optional
import copy


class PSO_GA_Hybrid:
    """
    PSO-GA Hybrid: Combines Particle Swarm Optimization with Genetic Algorithm
    Best for: Balanced exploration and exploitation
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 w_min: float = 0.4, w_max: float = 0.9, c1: float = 2.0, c2: float = 2.0,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        """
        Initialize PSO-GA Hybrid
        
        Parameters:
        -----------
        w_min, w_max : float
            Inertia weight bounds for PSO
        c1, c2 : float
            Cognitive and social coefficients
        crossover_rate : float
            Probability of crossover (0-1)
        mutation_rate : float
            Probability of mutation (0-1)
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w_min = w_min
        self.w_max = w_max
        self.c1 = c1
        self.c2 = c2
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        # Initialize population and velocities
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        # Personal best
        self.pbest_positions = self.positions.copy()
        self.pbest_fitness = self.fitness.copy()
        
        # Global best
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            # Adaptive inertia weight
            w = self.w_max - (self.w_max - self.w_min) * iteration / self.max_iterations
            
            # PSO Update
            for i in range(self.population_size):
                r1, r2 = np.random.random(2)
                
                # Update velocity
                self.velocities[i] = (w * self.velocities[i] +
                                     self.c1 * r1 * (self.pbest_positions[i] - self.positions[i]) +
                                     self.c2 * r2 * (self.gbest_position - self.positions[i]))
                
                # Update position
                self.positions[i] += self.velocities[i]
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate
                self.fitness[i] = self.objective_function(self.positions[i])
                
                # Update personal best
                if self.fitness[i] < self.pbest_fitness[i]:
                    self.pbest_positions[i] = self.positions[i].copy()
                    self.pbest_fitness[i] = self.fitness[i]
            
            # GA Operations (every 5 iterations)
            if iteration % 5 == 0:
                self._genetic_operations()
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_position, self.gbest_fitness, self.convergence_curve
    
    def _genetic_operations(self):
        """Apply genetic algorithm operations"""
        # Selection (tournament)
        selected = []
        for _ in range(self.population_size // 2):
            idx1, idx2 = np.random.choice(self.population_size, 2, replace=False)
            winner = idx1 if self.fitness[idx1] < self.fitness[idx2] else idx2
            selected.append(self.positions[winner].copy())
        
        # Crossover
        offspring = []
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected) and np.random.random() < self.crossover_rate:
                # Two-point crossover
                point1, point2 = sorted(np.random.choice(self.dimensions, 2, replace=False))
                child1, child2 = selected[i].copy(), selected[i+1].copy()
                child1[point1:point2], child2[point1:point2] = child2[point1:point2], child1[point1:point2]
                offspring.extend([child1, child2])
            else:
                offspring.extend([selected[i].copy()])
                if i + 1 < len(selected):
                    offspring.extend([selected[i+1].copy()])
        
        # Mutation
        for ind in offspring:
            if np.random.random() < self.mutation_rate:
                mutation_idx = np.random.randint(self.dimensions)
                ind[mutation_idx] = np.random.uniform(self.bounds[mutation_idx, 0], 
                                                     self.bounds[mutation_idx, 1])
        
        # Replace worst individuals
        worst_indices = np.argsort(self.fitness)[-len(offspring):]
        for idx, new_ind in zip(worst_indices, offspring):
            self.positions[idx] = new_ind
            self.fitness[idx] = self.objective_function(new_ind)


class GWO_PSO_Hybrid:
    """
    GWO-PSO Hybrid: Grey Wolf Optimizer with PSO velocity updates
    Best for: Complex multimodal landscapes
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 c1: float = 2.0, c2: float = 2.0):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.c1 = c1
        self.c2 = c2
        
        # Initialize
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.zeros((population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        # Alpha, Beta, Delta (top 3 wolves)
        sorted_indices = np.argsort(self.fitness)
        self.alpha_pos = self.positions[sorted_indices[0]].copy()
        self.alpha_score = self.fitness[sorted_indices[0]]
        self.beta_pos = self.positions[sorted_indices[1]].copy()
        self.beta_score = self.fitness[sorted_indices[1]]
        self.delta_pos = self.positions[sorted_indices[2]].copy()
        self.delta_score = self.fitness[sorted_indices[2]]
        
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            a = 2 - 2 * iteration / self.max_iterations  # Linearly decreasing from 2 to 0
            
            for i in range(self.population_size):
                # GWO position update
                r1, r2 = np.random.random(2)
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                
                D_alpha = np.abs(C1 * self.alpha_pos - self.positions[i])
                X1 = self.alpha_pos - A1 * D_alpha
                
                r1, r2 = np.random.random(2)
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                
                D_beta = np.abs(C2 * self.beta_pos - self.positions[i])
                X2 = self.beta_pos - A2 * D_beta
                
                r1, r2 = np.random.random(2)
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                
                D_delta = np.abs(C3 * self.delta_pos - self.positions[i])
                X3 = self.delta_pos - A3 * D_delta
                
                # PSO-like velocity update
                r1, r2 = np.random.random(2)
                self.velocities[i] = (0.5 * self.velocities[i] +
                                     self.c1 * r1 * (self.alpha_pos - self.positions[i]) +
                                     self.c2 * r2 * ((X1 + X2 + X3) / 3 - self.positions[i]))
                
                # Update position (combination of GWO and PSO)
                self.positions[i] = 0.7 * (X1 + X2 + X3) / 3 + 0.3 * (self.positions[i] + self.velocities[i])
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate
                self.fitness[i] = self.objective_function(self.positions[i])
            
            # Update alpha, beta, delta
            sorted_indices = np.argsort(self.fitness)
            if self.fitness[sorted_indices[0]] < self.alpha_score:
                self.alpha_pos = self.positions[sorted_indices[0]].copy()
                self.alpha_score = self.fitness[sorted_indices[0]]
            if self.fitness[sorted_indices[1]] < self.beta_score:
                self.beta_pos = self.positions[sorted_indices[1]].copy()
                self.beta_score = self.fitness[sorted_indices[1]]
            if self.fitness[sorted_indices[2]] < self.delta_score:
                self.delta_pos = self.positions[sorted_indices[2]].copy()
                self.delta_score = self.fitness[sorted_indices[2]]
            
            self.convergence_curve.append(self.alpha_score)
        
        return self.alpha_pos, self.alpha_score, self.convergence_curve


class DE_PSO_Hybrid:
    """
    DE-PSO Hybrid: Differential Evolution with PSO exploration
    Best for: High-dimensional continuous optimization
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 F: float = 0.8, CR: float = 0.9, w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F  # Differential weight
        self.CR = CR  # Crossover probability
        self.w = w  # Inertia weight
        self.c1 = c1  # Cognitive coefficient
        self.c2 = c2  # Social coefficient
        
        # Initialize
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        self.best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
        
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # DE mutation
                indices = [idx for idx in range(self.population_size) if idx != i]
                a, b, c = self.positions[np.random.choice(indices, 3, replace=False)]
                mutant = a + self.F * (b - c)
                mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                
                # DE crossover
                trial = np.copy(self.positions[i])
                j_rand = np.random.randint(self.dimensions)
                for j in range(self.dimensions):
                    if np.random.random() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                
                # PSO-inspired velocity update
                r1, r2 = np.random.random(2)
                self.velocities[i] = (self.w * self.velocities[i] +
                                     self.c1 * r1 * (self.best_position - self.positions[i]) +
                                     self.c2 * r2 * (trial - self.positions[i]))
                
                # Combine DE and PSO
                candidate = 0.7 * trial + 0.3 * (self.positions[i] + self.velocities[i])
                candidate = np.clip(candidate, self.bounds[:, 0], self.bounds[:, 1])
                
                # Selection
                candidate_fitness = self.objective_function(candidate)
                if candidate_fitness < self.fitness[i]:
                    self.positions[i] = candidate
                    self.fitness[i] = candidate_fitness
                    
                    if candidate_fitness < self.best_fitness:
                        self.best_position = candidate.copy()
                        self.best_fitness = candidate_fitness
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_position, self.best_fitness, self.convergence_curve


# I'll create more hybrid algorithms in a continuation...
# For brevity, here are class stubs for the remaining 12 hybrids:

class SA_GA_Hybrid:
    """
    SA-GA Hybrid: Simulated Annealing + Genetic Algorithm
    Best for: Combinatorial optimization with escape from local optima
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 initial_temp: float = 100.0, cooling_rate: float = 0.95,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        # Initialize population
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        self.best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
        
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        temperature = self.initial_temp
        
        for iteration in range(self.max_iterations):
            # Genetic Algorithm operations
            if iteration % 3 == 0:
                self._genetic_operations()
            
            # Simulated Annealing for each solution
            for i in range(self.population_size):
                # Generate neighbor
                neighbor = self.positions[i] + np.random.randn(self.dimensions) * temperature * 0.1
                neighbor = np.clip(neighbor, self.bounds[:, 0], self.bounds[:, 1])
                
                neighbor_fitness = self.objective_function(neighbor)
                
                # Metropolis acceptance criterion
                delta = neighbor_fitness - self.fitness[i]
                if delta < 0 or np.random.random() < np.exp(-delta / temperature):
                    self.positions[i] = neighbor
                    self.fitness[i] = neighbor_fitness
                    
                    if neighbor_fitness < self.best_fitness:
                        self.best_position = neighbor.copy()
                        self.best_fitness = neighbor_fitness
            
            # Cool down
            temperature *= self.cooling_rate
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_position, self.best_fitness, self.convergence_curve
    
    def _genetic_operations(self):
        """Apply GA operations"""
        # Tournament selection
        selected = []
        for _ in range(self.population_size // 2):
            idx1, idx2 = np.random.choice(self.population_size, 2, replace=False)
            winner = idx1 if self.fitness[idx1] < self.fitness[idx2] else idx2
            selected.append(self.positions[winner].copy())
        
        # Crossover and mutation
        offspring = []
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected) and np.random.random() < self.crossover_rate:
                point = np.random.randint(1, self.dimensions)
                child1, child2 = selected[i].copy(), selected[i+1].copy()
                child1[point:], child2[point:] = child2[point:], child1[point:]
                offspring.extend([child1, child2])
            else:
                offspring.append(selected[i].copy())
                if i + 1 < len(selected):
                    offspring.append(selected[i+1].copy())
        
        for ind in offspring:
            if np.random.random() < self.mutation_rate:
                idx = np.random.randint(self.dimensions)
                ind[idx] = np.random.uniform(self.bounds[idx, 0], self.bounds[idx, 1])
        
        # Replace worst
        worst_indices = np.argsort(self.fitness)[-len(offspring):]
        for idx, new_ind in zip(worst_indices, offspring):
            self.positions[idx] = new_ind
            self.fitness[idx] = self.objective_function(new_ind)


class WOA_GA_Hybrid:
    """
    WOA-GA Hybrid: Whale Optimization Algorithm + Genetic Algorithm
    Best for: Feature selection and exploration-intensive problems
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 crossover_rate: float = 0.7, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        self.best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
        
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            a = 2 - 2 * iteration / self.max_iterations
            
            for i in range(self.population_size):
                r = np.random.random()
                A = 2 * a * r - a
                C = 2 * r
                l = np.random.uniform(-1, 1)
                p = np.random.random()
                
                if p < 0.5:
                    if np.abs(A) < 1:
                        # Encircling prey
                        D = np.abs(C * self.best_position - self.positions[i])
                        self.positions[i] = self.best_position - A * D
                    else:
                        # Search for prey
                        rand_idx = np.random.randint(self.population_size)
                        X_rand = self.positions[rand_idx]
                        D = np.abs(C * X_rand - self.positions[i])
                        self.positions[i] = X_rand - A * D
                else:
                    # Spiral updating
                    D_prime = np.abs(self.best_position - self.positions[i])
                    self.positions[i] = D_prime * np.exp(l) * np.cos(2 * np.pi * l) + self.best_position
                
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.positions[i])
                
                if self.fitness[i] < self.best_fitness:
                    self.best_position = self.positions[i].copy()
                    self.best_fitness = self.fitness[i]
            
            # GA operations every 5 iterations
            if iteration % 5 == 0:
                self._genetic_operations()
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_position, self.best_fitness, self.convergence_curve
    
    def _genetic_operations(self):
        """Apply genetic operations"""
        selected = []
        for _ in range(self.population_size // 2):
            idx1, idx2 = np.random.choice(self.population_size, 2, replace=False)
            winner = idx1 if self.fitness[idx1] < self.fitness[idx2] else idx2
            selected.append(self.positions[winner].copy())
        
        offspring = []
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected) and np.random.random() < self.crossover_rate:
                alpha = np.random.random(self.dimensions)
                child1 = alpha * selected[i] + (1 - alpha) * selected[i+1]
                child2 = alpha * selected[i+1] + (1 - alpha) * selected[i]
                offspring.extend([child1, child2])
            else:
                offspring.append(selected[i].copy())
        
        for ind in offspring:
            if np.random.random() < self.mutation_rate:
                idx = np.random.randint(self.dimensions)
                ind[idx] = np.random.uniform(self.bounds[idx, 0], self.bounds[idx, 1])
        
        worst_indices = np.argsort(self.fitness)[-len(offspring):]
        for idx, new_ind in zip(worst_indices, offspring):
            self.positions[idx] = new_ind
            self.fitness[idx] = self.objective_function(new_ind)


class BA_PSO_Hybrid:
    """
    BA-PSO Hybrid: Bat Algorithm + Particle Swarm Optimization
    Best for: Multimodal optimization with frequency tuning
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 freq_min: float = 0.0, freq_max: float = 2.0,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.zeros((population_size, dimensions))
        self.frequencies = np.zeros(population_size)
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        self.best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
        
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # BA: Update frequency
                self.frequencies[i] = self.freq_min + (self.freq_max - self.freq_min) * np.random.random()
                
                # BA: Update velocity and position
                self.velocities[i] += (self.positions[i] - self.best_position) * self.frequencies[i]
                
                # PSO: Add social and cognitive components
                r1, r2 = np.random.random(2)
                self.velocities[i] = (self.w * self.velocities[i] +
                                     self.c1 * r1 * (self.best_position - self.positions[i]) +
                                     self.c2 * r2 * (self.best_position - self.positions[i]))
                
                new_position = self.positions[i] + self.velocities[i]
                new_position = np.clip(new_position, self.bounds[:, 0], self.bounds[:, 1])
                
                new_fitness = self.objective_function(new_position)
                
                # Accept new solution
                if new_fitness < self.fitness[i]:
                    self.positions[i] = new_position
                    self.fitness[i] = new_fitness
                    
                    if new_fitness < self.best_fitness:
                        self.best_position = new_position.copy()
                        self.best_fitness = new_fitness
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_position, self.best_fitness, self.convergence_curve


class SCA_PSO_Hybrid:
    """
    SCA-PSO Hybrid: Sine Cosine Algorithm + PSO
    Best for: Mathematical function optimization with oscillation
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 a: float = 2.0, w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.a = a
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        self.best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
        
        self.convergence_curve = []
    
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run optimization"""
        for iteration in range(self.max_iterations):
            a = self.a - iteration * self.a / self.max_iterations
            
            for i in range(self.population_size):
                r1 = a * (2 * np.random.random() - 1)
                r2 = 2 * np.pi * np.random.random()
                r3 = 2 * np.random.random()
                r4 = np.random.random()
                
                # SCA update
                if r4 < 0.5:
                    # Sine update
                    sca_update = self.positions[i] + r1 * np.sin(r2) * np.abs(r3 * self.best_position - self.positions[i])
                else:
                    # Cosine update
                    sca_update = self.positions[i] + r1 * np.cos(r2) * np.abs(r3 * self.best_position - self.positions[i])
                
                # PSO velocity update
                r5, r6 = np.random.random(2)
                self.velocities[i] = (self.w * self.velocities[i] +
                                     self.c1 * r5 * (self.best_position - self.positions[i]) +
                                     self.c2 * r6 * (sca_update - self.positions[i]))
                
                # Combine SCA and PSO
                self.positions[i] = 0.6 * sca_update + 0.4 * (self.positions[i] + self.velocities[i])
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                
                self.fitness[i] = self.objective_function(self.positions[i])
                
                if self.fitness[i] < self.best_fitness:
                    self.best_position = self.positions[i].copy()
                    self.best_fitness = self.fitness[i]
            
            self.convergence_curve.append(self.best_fitness)
        
        return self.best_position, self.best_fitness, self.convergence_curve


# Remaining hybrids as stubs (can be implemented similarly)
class ACO_PSO_Hybrid:
    """
    ACO-PSO Hybrid: Combines Ant Colony Optimization with PSO
    Best for: Routing, graph problems, and continuous optimization
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 alpha: float = 1.0, beta: float = 2.0, evaporation: float = 0.5,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        """
        Parameters:
        -----------
        alpha : float
            Pheromone importance
        beta : float
            Heuristic importance  
        evaporation : float
            Pheromone evaporation rate (0-1)
        w, c1, c2 : float
            PSO parameters
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # Initialize
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.pheromone = np.ones((population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        
        # Best solutions
        self.pbest_positions = self.positions.copy()
        self.pbest_fitness = self.fitness.copy()
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run ACO-PSO hybrid optimization"""
        for iteration in range(self.max_iterations):
            # ACO phase - update pheromones
            self.pheromone *= (1 - self.evaporation)  # Evaporation
            
            for i in range(self.population_size):
                # Deposit pheromone based on solution quality
                pheromone_deposit = 1.0 / (1.0 + self.fitness[i])
                self.pheromone[i] += pheromone_deposit
                
                # ACO position update with pheromone guidance
                heuristic = 1.0 / (np.abs(self.positions[i] - self.gbest_position) + 1e-10)
                probability = (self.pheromone[i] ** self.alpha) * (heuristic ** self.beta)
                probability /= (np.sum(probability) + 1e-10)
                
                # Combine ACO and PSO
                r1, r2 = np.random.random(2)
                
                # PSO velocity update with ACO influence
                self.velocities[i] = (self.w * self.velocities[i] +
                                     self.c1 * r1 * (self.pbest_positions[i] - self.positions[i]) +
                                     self.c2 * r2 * (self.gbest_position - self.positions[i]) +
                                     0.3 * probability * (self.gbest_position - self.positions[i]))
                
                # Update position
                self.positions[i] += self.velocities[i]
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate
                self.fitness[i] = self.objective_function(self.positions[i])
                
                # Update personal best
                if self.fitness[i] < self.pbest_fitness[i]:
                    self.pbest_positions[i] = self.positions[i].copy()
                    self.pbest_fitness[i] = self.fitness[i]
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_idx = current_best_idx
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_position, self.gbest_fitness, self.convergence_curve

class ABC_DE_Hybrid:
    """
    ABC-DE Hybrid: Artificial Bee Colony + Differential Evolution
    Best for: Numerical optimization with exploration-exploitation balance
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 limit: int = 20, F: float = 0.8, CR: float = 0.9):
        """
        Parameters:
        -----------
        limit : int
            Abandonment limit for scout bees
        F : float
            DE scaling factor
        CR : float
            DE crossover rate
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.limit = limit
        self.F = F
        self.CR = CR
        
        # Initialize
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        self.trial_counter = np.zeros(population_size)
        
        # Best solution
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run ABC-DE hybrid optimization"""
        for iteration in range(self.max_iterations):
            # Employed bee phase (ABC)
            for i in range(self.population_size):
                k = np.random.choice([j for j in range(self.population_size) if j != i])
                phi = np.random.uniform(-1, 1, self.dimensions)
                
                # ABC mutation
                candidate = self.positions[i] + phi * (self.positions[i] - self.positions[k])
                candidate = np.clip(candidate, self.bounds[:, 0], self.bounds[:, 1])
                
                candidate_fitness = self.objective_function(candidate)
                
                if candidate_fitness < self.fitness[i]:
                    self.positions[i] = candidate
                    self.fitness[i] = candidate_fitness
                    self.trial_counter[i] = 0
                else:
                    self.trial_counter[i] += 1
            
            # DE phase (every 3 iterations)
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    # Select three random distinct individuals
                    indices = [j for j in range(self.population_size) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    
                    # DE mutation
                    mutant = self.positions[a] + self.F * (self.positions[b] - self.positions[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    
                    # DE crossover
                    trial = np.where(np.random.random(self.dimensions) < self.CR, 
                                   mutant, self.positions[i])
                    
                    trial_fitness = self.objective_function(trial)
                    
                    if trial_fitness < self.fitness[i]:
                        self.positions[i] = trial
                        self.fitness[i] = trial_fitness
                        self.trial_counter[i] = 0
            
            # Scout bee phase
            for i in range(self.population_size):
                if self.trial_counter[i] >= self.limit:
                    self.positions[i] = np.random.uniform(self.bounds[:, 0], 
                                                         self.bounds[:, 1], 
                                                         self.dimensions)
                    self.fitness[i] = self.objective_function(self.positions[i])
                    self.trial_counter[i] = 0
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_idx = current_best_idx
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_position, self.gbest_fitness, self.convergence_curve

class FA_DE_Hybrid:
    """
    FA-DE Hybrid: Firefly Algorithm + Differential Evolution
    Best for: Continuous multimodal optimization problems
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 alpha: float = 0.2, beta0: float = 1.0, gamma: float = 1.0,
                 F: float = 0.8, CR: float = 0.9):
        """
        Parameters:
        -----------
        alpha : float
            Randomization parameter
        beta0 : float
            Attractiveness at r=0
        gamma : float
            Light absorption coefficient
        F, CR : float
            DE scaling factor and crossover rate
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta0 = beta0
        self.gamma = gamma
        self.F = F
        self.CR = CR
        
        # Initialize
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        self.light_intensity = 1.0 / (1.0 + self.fitness)
        
        # Best solution
        self.gbest_idx = np.argmax(self.light_intensity)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run FA-DE hybrid optimization"""
        for iteration in range(self.max_iterations):
            # Firefly phase
            for i in range(self.population_size):
                for j in range(self.population_size):
                    if self.light_intensity[j] > self.light_intensity[i]:
                        # Calculate distance
                        r = np.linalg.norm(self.positions[i] - self.positions[j])
                        
                        # Attractiveness decreases with distance
                        beta = self.beta0 * np.exp(-self.gamma * r**2)
                        
                        # Move towards brighter firefly
                        self.positions[i] += (beta * (self.positions[j] - self.positions[i]) +
                                            self.alpha * (np.random.random(self.dimensions) - 0.5))
                        
                        self.positions[i] = np.clip(self.positions[i], 
                                                   self.bounds[:, 0], 
                                                   self.bounds[:, 1])
                
                # Evaluate
                self.fitness[i] = self.objective_function(self.positions[i])
                self.light_intensity[i] = 1.0 / (1.0 + self.fitness[i])
            
            # DE phase (every 4 iterations)
            if iteration % 4 == 0:
                for i in range(self.population_size):
                    indices = [j for j in range(self.population_size) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    
                    # DE mutation and crossover
                    mutant = self.positions[a] + self.F * (self.positions[b] - self.positions[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    
                    trial = np.where(np.random.random(self.dimensions) < self.CR,
                                   mutant, self.positions[i])
                    
                    trial_fitness = self.objective_function(trial)
                    
                    if trial_fitness < self.fitness[i]:
                        self.positions[i] = trial
                        self.fitness[i] = trial_fitness
                        self.light_intensity[i] = 1.0 / (1.0 + trial_fitness)
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_idx = current_best_idx
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            # Reduce alpha over time
            self.alpha *= 0.97
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_position, self.gbest_fitness, self.convergence_curve

class CS_GA_Hybrid:
    """
    CS-GA Hybrid: Cuckoo Search + Genetic Algorithm
    Best for: Engineering design and constrained optimization
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 pa: float = 0.25, beta: float = 1.5,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        """
        Parameters:
        -----------
        pa : float
            Probability of abandoning worst nests (0-1)
        beta : float
            Lévy flight parameter
        crossover_rate, mutation_rate : float
            GA parameters
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.pa = pa
        self.beta = beta
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        # Initialize nests
        self.nests = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                      (population_size, dimensions))
        self.fitness = np.array([objective_function(nest) for nest in self.nests])
        
        # Best nest
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_nest = self.nests[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def _levy_flight(self, size):
        """Generate Lévy flight step"""
        sigma = (np.math.gamma(1 + self.beta) * np.sin(np.pi * self.beta / 2) /
                (np.math.gamma((1 + self.beta) / 2) * self.beta * 
                 2**((self.beta - 1) / 2)))**(1 / self.beta)
        u = np.random.normal(0, sigma, size)
        v = np.random.normal(0, 1, size)
        step = u / np.abs(v)**(1 / self.beta)
        return step
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run CS-GA hybrid optimization"""
        for iteration in range(self.max_iterations):
            # Cuckoo Search phase
            for i in range(self.population_size):
                # Lévy flight
                step_size = 0.01 * self._levy_flight(self.dimensions)
                new_nest = self.nests[i] + step_size * (self.nests[i] - self.gbest_nest)
                new_nest = np.clip(new_nest, self.bounds[:, 0], self.bounds[:, 1])
                
                # Random nest selection
                j = np.random.randint(0, self.population_size)
                new_fitness = self.objective_function(new_nest)
                
                if new_fitness < self.fitness[j]:
                    self.nests[j] = new_nest
                    self.fitness[j] = new_fitness
            
            # Abandon worst nests
            n_abandon = int(self.pa * self.population_size)
            worst_indices = np.argsort(self.fitness)[-n_abandon:]
            
            for idx in worst_indices:
                self.nests[idx] = np.random.uniform(self.bounds[:, 0], 
                                                    self.bounds[:, 1], 
                                                    self.dimensions)
                self.fitness[idx] = self.objective_function(self.nests[idx])
            
            # GA phase (every 5 iterations)
            if iteration % 5 == 0:
                # Selection
                fitness_inv = 1.0 / (self.fitness + 1e-10)
                probs = fitness_inv / np.sum(fitness_inv)
                
                # Crossover
                for _ in range(self.population_size // 4):
                    if np.random.random() < self.crossover_rate:
                        parents = np.random.choice(self.population_size, 2, p=probs, replace=False)
                        crossover_point = np.random.randint(1, self.dimensions)
                        
                        offspring = self.nests[parents[0]].copy()
                        offspring[crossover_point:] = self.nests[parents[1]][crossover_point:]
                        
                        offspring_fitness = self.objective_function(offspring)
                        worst_idx = np.argmax(self.fitness)
                        
                        if offspring_fitness < self.fitness[worst_idx]:
                            self.nests[worst_idx] = offspring
                            self.fitness[worst_idx] = offspring_fitness
                
                # Mutation
                for i in range(self.population_size):
                    if np.random.random() < self.mutation_rate:
                        mutation_idx = np.random.randint(0, self.dimensions)
                        self.nests[i][mutation_idx] = np.random.uniform(
                            self.bounds[mutation_idx, 0],
                            self.bounds[mutation_idx, 1]
                        )
                        self.fitness[i] = self.objective_function(self.nests[i])
            
            # Update global best
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_idx = current_best_idx
                self.gbest_nest = self.nests[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        
        return self.gbest_nest, self.gbest_fitness, self.convergence_curve

class ALO_PSO_Hybrid:
    """
    ALO-PSO Hybrid: Ant Lion Optimizer + PSO
    Best for: Trap-prone landscapes and local optima avoidance
    """
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # Initialize ants and antlions
        self.ants = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                     (population_size, dimensions))
        self.antlions = self.ants.copy()
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        
        self.ant_fitness = np.array([objective_function(ant) for ant in self.ants])
        self.antlion_fitness = self.ant_fitness.copy()
        
        # Elite antlion
        self.elite_idx = np.argmin(self.antlion_fitness)
        self.elite = self.antlions[self.elite_idx].copy()
        self.elite_fitness = self.antlion_fitness[self.elite_idx]
        
        # Personal best for PSO
        self.pbest = self.ants.copy()
        self.pbest_fitness = self.ant_fitness.copy()
        self.convergence_curve = []
        
    def _random_walk(self, antlion_pos, iteration):
        """Random walk around antlion"""
        # Adaptive bounds
        c = iteration / self.max_iterations
        lb = self.bounds[:, 0] * (1 - c) + antlion_pos * c
        ub = self.bounds[:, 1] * (1 - c) + antlion_pos * c
        
        walk = np.cumsum(2 * (np.random.random(self.dimensions) > 0.5) - 1)
        walk = (walk - walk.min()) / (walk.max() - walk.min() + 1e-10)
        walk = walk * (ub - lb) + lb
        
        return walk
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        """Run ALO-PSO hybrid optimization"""
        for iteration in range(self.max_iterations):
            # ALO phase
            for i in range(self.population_size):
                # Roulette wheel selection of antlion
                fitness_inv = 1.0 / (self.antlion_fitness + 1e-10)
                probs = fitness_inv / np.sum(fitness_inv)
                selected_antlion_idx = np.random.choice(self.population_size, p=probs)
                
                # Random walk around selected antlion and elite
                RA = self._random_walk(self.antlions[selected_antlion_idx], iteration)
                RE = self._random_walk(self.elite, iteration)
                
                # Combine walks
                self.ants[i] = (RA + RE) / 2
                self.ants[i] = np.clip(self.ants[i], self.bounds[:, 0], self.bounds[:, 1])
                
                # Evaluate
                self.ant_fitness[i] = self.objective_function(self.ants[i])
                
                # Replace antlion if ant is fitter
                if self.ant_fitness[i] < self.antlion_fitness[i]:
                    self.antlions[i] = self.ants[i].copy()
                    self.antlion_fitness[i] = self.ant_fitness[i]
            
            # PSO phase (every 3 iterations)
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    r1, r2 = np.random.random(2)
                    
                    # PSO velocity and position update
                    self.velocities[i] = (self.w * self.velocities[i] +
                                        self.c1 * r1 * (self.pbest[i] - self.ants[i]) +
                                        self.c2 * r2 * (self.elite - self.ants[i]))
                    
                    self.ants[i] += self.velocities[i]
                    self.ants[i] = np.clip(self.ants[i], self.bounds[:, 0], self.bounds[:, 1])
                    
                    self.ant_fitness[i] = self.objective_function(self.ants[i])
                    
                    # Update personal best
                    if self.ant_fitness[i] < self.pbest_fitness[i]:
                        self.pbest[i] = self.ants[i].copy()
                        self.pbest_fitness[i] = self.ant_fitness[i]
            
            # Update elite
            current_best_idx = np.argmin(self.antlion_fitness)
            if self.antlion_fitness[current_best_idx] < self.elite_fitness:
                self.elite_idx = current_best_idx
                self.elite = self.antlions[current_best_idx].copy()
                self.elite_fitness = self.antlion_fitness[current_best_idx]
            
            self.convergence_curve.append(self.elite_fitness)
        
        return self.elite, self.elite_fitness, self.convergence_curve

class SSA_DE_Hybrid:
    """SSA-DE Hybrid: Salp Swarm + DE - Best for constrained optimization"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 F: float = 0.8, CR: float = 0.9):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F
        self.CR = CR
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(ind) for ind in self.positions])
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_position = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            c1 = 2 * np.exp(-(4 * iteration / self.max_iterations)**2)
            
            # SSA phase - leader and followers
            for i in range(self.population_size):
                if i == 0:  # Leader
                    self.positions[i] = self.gbest_position + c1 * ((self.bounds[:, 1] - 
                                      self.bounds[:, 0]) * np.random.random(self.dimensions) + 
                                      self.bounds[:, 0])
                else:  # Followers
                    self.positions[i] = 0.5 * (self.positions[i] + self.positions[i-1])
                
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.positions[i])
            
            # DE phase
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    indices = [j for j in range(self.population_size) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    mutant = self.positions[a] + self.F * (self.positions[b] - self.positions[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    trial = np.where(np.random.random(self.dimensions) < self.CR, mutant, self.positions[i])
                    trial_fitness = self.objective_function(trial)
                    if trial_fitness < self.fitness[i]:
                        self.positions[i] = trial
                        self.fitness[i] = trial_fitness
            
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_position = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        return self.gbest_position, self.gbest_fitness, self.convergence_curve


class MVO_GA_Hybrid:
    """MVO-GA Hybrid: Multi-Verse Optimizer + GA"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 WEP_max: float = 1.0, WEP_min: float = 0.2,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.WEP_max = WEP_max
        self.WEP_min = WEP_min
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.universes = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.inflation_rates = np.array([objective_function(u) for u in self.universes])
        self.gbest_idx = np.argmin(self.inflation_rates)
        self.gbest_universe = self.universes[self.gbest_idx].copy()
        self.gbest_fitness = self.inflation_rates[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            WEP = self.WEP_max - iteration * ((self.WEP_max - self.WEP_min) / self.max_iterations)
            TDR = 1 - iteration**(1/6) / self.max_iterations**(1/6)
            
            # Normalize inflation rates
            sorted_indices = np.argsort(self.inflation_rates)
            normalized_rates = np.linspace(1, 0, self.population_size)[np.argsort(sorted_indices)]
            
            # MVO phase
            for i in range(self.population_size):
                for j in range(self.dimensions):
                    r1 = np.random.random()
                    if r1 < normalized_rates[i]:
                        white_hole_idx = self._roulette_wheel_selection(normalized_rates)
                        self.universes[i][j] = self.universes[white_hole_idx][j]
                    
                    r2 = np.random.random()
                    if r2 < WEP:
                        r3, r4 = np.random.random(2)
                        if r4 < 0.5:
                            self.universes[i][j] = self.gbest_universe[j] + TDR * ((self.bounds[j, 1] - 
                                                    self.bounds[j, 0]) * r3 + self.bounds[j, 0])
                        else:
                            self.universes[i][j] = self.gbest_universe[j] - TDR * ((self.bounds[j, 1] - 
                                                    self.bounds[j, 0]) * r3 + self.bounds[j, 0])
                
                self.universes[i] = np.clip(self.universes[i], self.bounds[:, 0], self.bounds[:, 1])
                self.inflation_rates[i] = self.objective_function(self.universes[i])
            
            # GA phase
            if iteration % 5 == 0:
                for _ in range(self.population_size // 4):
                    if np.random.random() < self.crossover_rate:
                        parents = np.random.choice(self.population_size, 2, replace=False)
                        cp = np.random.randint(1, self.dimensions)
                        offspring = self.universes[parents[0]].copy()
                        offspring[cp:] = self.universes[parents[1]][cp:]
                        offspring_fitness = self.objective_function(offspring)
                        worst_idx = np.argmax(self.inflation_rates)
                        if offspring_fitness < self.inflation_rates[worst_idx]:
                            self.universes[worst_idx] = offspring
                            self.inflation_rates[worst_idx] = offspring_fitness
            
            current_best_idx = np.argmin(self.inflation_rates)
            if self.inflation_rates[current_best_idx] < self.gbest_fitness:
                self.gbest_universe = self.universes[current_best_idx].copy()
                self.gbest_fitness = self.inflation_rates[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        return self.gbest_universe, self.gbest_fitness, self.convergence_curve
    
    def _roulette_wheel_selection(self, probabilities):
        cumsum = np.cumsum(probabilities)
        r = np.random.random() * cumsum[-1]
        return np.searchsorted(cumsum, r)


class HHO_DE_Hybrid:
    """HHO-DE Hybrid: Harris Hawks + DE"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 F: float = 0.8, CR: float = 0.9):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F
        self.CR = CR
        
        self.hawks = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                      (population_size, dimensions))
        self.fitness = np.array([objective_function(h) for h in self.hawks])
        self.rabbit_idx = np.argmin(self.fitness)
        self.rabbit_pos = self.hawks[self.rabbit_idx].copy()
        self.rabbit_fitness = self.fitness[self.rabbit_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            E0 = 2 * np.random.random() - 1
            E = 2 * E0 * (1 - iteration / self.max_iterations)
            
            for i in range(self.population_size):
                q = np.random.random()
                r = np.random.random()
                
                if abs(E) >= 1:  # Exploration
                    rand_idx = np.random.randint(0, self.population_size)
                    X_rand = self.hawks[rand_idx]
                    self.hawks[i] = X_rand - r * np.abs(X_rand - 2 * r * self.hawks[i])
                else:  # Exploitation
                    if r >= 0.5 and abs(E) >= 0.5:  # Soft besiege
                        self.hawks[i] = self.rabbit_pos - E * np.abs(self.rabbit_pos - self.hawks[i])
                    elif r >= 0.5 and abs(E) < 0.5:  # Hard besiege
                        self.hawks[i] = self.rabbit_pos - E * np.abs(self.rabbit_pos - self.hawks[i])
                    elif r < 0.5 and abs(E) >= 0.5:  # Soft besiege with progressive rapid dives
                        Y = self.rabbit_pos - E * np.abs(self.rabbit_pos - self.hawks[i])
                        Y = np.clip(Y, self.bounds[:, 0], self.bounds[:, 1])
                        if self.objective_function(Y) < self.fitness[i]:
                            self.hawks[i] = Y
                    else:  # Hard besiege with progressive rapid dives
                        Y = self.rabbit_pos - E * np.abs(self.rabbit_pos - np.mean(self.hawks, axis=0))
                        Y = np.clip(Y, self.bounds[:, 0], self.bounds[:, 1])
                        if self.objective_function(Y) < self.fitness[i]:
                            self.hawks[i] = Y
                
                self.hawks[i] = np.clip(self.hawks[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.hawks[i])
            
            # DE phase
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    indices = [j for j in range(self.population_size) if j != i]
                    a, b, c = np.random.choice(indices, 3, replace=False)
                    mutant = self.hawks[a] + self.F * (self.hawks[b] - self.hawks[c])
                    mutant = np.clip(mutant, self.bounds[:, 0], self.bounds[:, 1])
                    trial = np.where(np.random.random(self.dimensions) < self.CR, mutant, self.hawks[i])
                    trial_fitness = self.objective_function(trial)
                    if trial_fitness < self.fitness[i]:
                        self.hawks[i] = trial
                        self.fitness[i] = trial_fitness
            
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.rabbit_fitness:
                self.rabbit_pos = self.hawks[current_best_idx].copy()
                self.rabbit_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.rabbit_fitness)
        return self.rabbit_pos, self.rabbit_fitness, self.convergence_curve


class GTO_PSO_Hybrid:
    """GTO-PSO Hybrid: Gorilla Troops + PSO"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.gorillas = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                         (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.fitness = np.array([objective_function(g) for g in self.gorillas])
        self.silverback_idx = np.argmin(self.fitness)
        self.silverback_pos = self.gorillas[self.silverback_idx].copy()
        self.silverback_fitness = self.fitness[self.silverback_idx]
        self.pbest = self.gorillas.copy()
        self.pbest_fitness = self.fitness.copy()
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            C = 1 - iteration / self.max_iterations
            
            for i in range(self.population_size):
                if np.random.random() < 0.5:  # Exploration
                    r = np.random.random()
                    if r < 0.5:
                        Z = np.random.randint(-C, C, self.dimensions)
                        self.gorillas[i] = (self.bounds[:, 1] - self.bounds[:, 0]) * Z + self.bounds[:, 0]
                    else:
                        rand_idx = np.random.randint(0, self.population_size)
                        self.gorillas[i] = self.gorillas[rand_idx] + C * (2 * np.random.random(self.dimensions) - 1)
                else:  # Exploitation - follow silverback
                    M = np.mean(self.gorillas, axis=0)
                    L = C * np.random.random(self.dimensions)
                    self.gorillas[i] = L * M + (1 - L) * self.silverback_pos
                
                self.gorillas[i] = np.clip(self.gorillas[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.gorillas[i])
            
            # PSO phase
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    r1, r2 = np.random.random(2)
                    self.velocities[i] = (self.w * self.velocities[i] +
                                        self.c1 * r1 * (self.pbest[i] - self.gorillas[i]) +
                                        self.c2 * r2 * (self.silverback_pos - self.gorillas[i]))
                    self.gorillas[i] += self.velocities[i]
                    self.gorillas[i] = np.clip(self.gorillas[i], self.bounds[:, 0], self.bounds[:, 1])
                    self.fitness[i] = self.objective_function(self.gorillas[i])
                    if self.fitness[i] < self.pbest_fitness[i]:
                        self.pbest[i] = self.gorillas[i].copy()
                        self.pbest_fitness[i] = self.fitness[i]
            
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.silverback_fitness:
                self.silverback_pos = self.gorillas[current_best_idx].copy()
                self.silverback_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.silverback_fitness)
        return self.silverback_pos, self.silverback_fitness, self.convergence_curve


class AOA_GA_Hybrid:
    """AOA-GA Hybrid: Arithmetic Optimization + GA"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 alpha: float = 5.0, mu: float = 0.5,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.mu = mu
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.fitness = np.array([objective_function(p) for p in self.positions])
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_pos = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            MOA = 1 - iteration / self.max_iterations
            MOP = 1 - ((iteration + 1) / self.max_iterations) ** (1 / self.alpha)
            
            for i in range(self.population_size):
                for j in range(self.dimensions):
                    r1, r2, r3 = np.random.random(3)
                    
                    if r1 > MOA:  # Exploration
                        if r2 > 0.5:
                            self.positions[i][j] = self.gbest_pos[j] / (MOP + 1e-10) * ((self.bounds[j, 1] - 
                                                  self.bounds[j, 0]) * self.mu + self.bounds[j, 0])
                        else:
                            self.positions[i][j] = self.gbest_pos[j] * MOP * ((self.bounds[j, 1] - 
                                                  self.bounds[j, 0]) * self.mu + self.bounds[j, 0])
                    else:  # Exploitation
                        if r3 > 0.5:
                            self.positions[i][j] = self.gbest_pos[j] - MOP * ((self.bounds[j, 1] - 
                                                  self.bounds[j, 0]) * self.mu + self.bounds[j, 0])
                        else:
                            self.positions[i][j] = self.gbest_pos[j] + MOP * ((self.bounds[j, 1] - 
                                                  self.bounds[j, 0]) * self.mu + self.bounds[j, 0])
                
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.positions[i])
            
            # GA phase
            if iteration % 5 == 0:
                for _ in range(self.population_size // 4):
                    if np.random.random() < self.crossover_rate:
                        parents = np.random.choice(self.population_size, 2, replace=False)
                        cp = np.random.randint(1, self.dimensions)
                        offspring = self.positions[parents[0]].copy()
                        offspring[cp:] = self.positions[parents[1]][cp:]
                        offspring_fitness = self.objective_function(offspring)
                        worst_idx = np.argmax(self.fitness)
                        if offspring_fitness < self.fitness[worst_idx]:
                            self.positions[worst_idx] = offspring
                            self.fitness[worst_idx] = offspring_fitness
            
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_pos = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        return self.gbest_pos, self.gbest_fitness, self.convergence_curve


class RSA_PSO_Hybrid:
    """RSA-PSO Hybrid: Reptile Search + PSO"""
    
    def __init__(self, objective_function: Callable, dimensions: int, bounds: np.ndarray,
                 population_size: int = 50, max_iterations: int = 100,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                                          (population_size, dimensions))
        self.velocities = np.random.uniform(-1, 1, (population_size, dimensions))
        self.fitness = np.array([objective_function(p) for p in self.positions])
        self.gbest_idx = np.argmin(self.fitness)
        self.gbest_pos = self.positions[self.gbest_idx].copy()
        self.gbest_fitness = self.fitness[self.gbest_idx]
        self.pbest = self.positions.copy()
        self.pbest_fitness = self.fitness.copy()
        self.convergence_curve = []
        
    def optimize(self) -> Tuple[np.ndarray, float, list]:
        for iteration in range(self.max_iterations):
            beta = 2 * np.exp(-4 * iteration / self.max_iterations)
            
            for i in range(self.population_size):
                if np.random.random() < 0.5:  # Encircling
                    r = np.random.random()
                    rand_idx = np.random.randint(0, self.population_size)
                    if r < 0.5:
                        self.positions[i] = self.gbest_pos - beta * np.abs(2 * np.random.random(self.dimensions) * 
                                          self.gbest_pos - self.positions[i])
                    else:
                        self.positions[i] = self.positions[rand_idx] - beta * np.abs(2 * np.random.random(self.dimensions) * 
                                          self.positions[rand_idx] - self.positions[i])
                else:  # Hunting cooperation
                    ES = 2 * np.random.random(self.dimensions) - 1
                    self.positions[i] = self.gbest_pos - ES * np.abs(self.gbest_pos - self.positions[i])
                
                self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                self.fitness[i] = self.objective_function(self.positions[i])
            
            # PSO phase
            if iteration % 3 == 0:
                for i in range(self.population_size):
                    r1, r2 = np.random.random(2)
                    self.velocities[i] = (self.w * self.velocities[i] +
                                        self.c1 * r1 * (self.pbest[i] - self.positions[i]) +
                                        self.c2 * r2 * (self.gbest_pos - self.positions[i]))
                    self.positions[i] += self.velocities[i]
                    self.positions[i] = np.clip(self.positions[i], self.bounds[:, 0], self.bounds[:, 1])
                    self.fitness[i] = self.objective_function(self.positions[i])
                    if self.fitness[i] < self.pbest_fitness[i]:
                        self.pbest[i] = self.positions[i].copy()
                        self.pbest_fitness[i] = self.fitness[i]
            
            current_best_idx = np.argmin(self.fitness)
            if self.fitness[current_best_idx] < self.gbest_fitness:
                self.gbest_pos = self.positions[current_best_idx].copy()
                self.gbest_fitness = self.fitness[current_best_idx]
            
            self.convergence_curve.append(self.gbest_fitness)
        return self.gbest_pos, self.gbest_fitness, self.convergence_curve
