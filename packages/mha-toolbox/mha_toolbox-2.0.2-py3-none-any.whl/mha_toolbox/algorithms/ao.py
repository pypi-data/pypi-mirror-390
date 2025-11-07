"""
Aquila Optimizer (AO)

Based on: Abualigah, L., Yousri, D., Abd Elaziz, M., Ewees, A. A., Al-qaness, M. A., & Gandomi, A. H. (2021). 
Aquila optimizer: a novel meta-heuristic optimization algorithm. Computers & Industrial Engineering, 157, 107250.
"""

import numpy as np
import math
from ..base import BaseOptimizer


class AquilaOptimizer(BaseOptimizer):
    """
    Aquila Optimizer implementation.
    
    The Aquila Optimizer is inspired by the hunting behavior of Aquila eagles.
    """
    
    def __init__(self, population_size=30, max_iter=100, **kwargs):
        super().__init__(population_size, max_iter, **kwargs)
        self.name = "Aquila Optimizer"
        self.short_name = "AO"
        
    def _optimize(self, objective_function, **kwargs):
        """
        Core optimization logic for Aquila Optimizer.
        
        Args:
            objective_function: Function to optimize
            
        Returns:
            Tuple of (best_solution, best_fitness, global_fitness, local_fitness, local_positions)
        """
        # Initialize population
        population = self._initialize_population()
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best solution
        best_idx = np.argmin(fitness)
        global_best_position = population[best_idx].copy()
        global_best_fitness = fitness[best_idx]
        
        # Track convergence
        global_fitness = [global_best_fitness]
        local_fitness = []
        local_positions = []
        
        # Main optimization loop
        for iteration in range(self.max_iterations_):
            # Update using different hunting strategies
            for i in range(self.population_size_):
                # Strategy selection based on iteration
                t = iteration / self.max_iterations_
                
                if t <= 2/3:  # Exploration phase
                    if np.random.random() < 0.5:
                        # Expanded exploration (X1)
                        X1 = self._expanded_exploration(global_best_position, population[i], t)
                        population[i] = np.clip(X1, self.lower_bound_, self.upper_bound_)
                    else:
                        # Narrowed exploration (X2)
                        X2 = self._narrowed_exploration(global_best_position, population[i], t)
                        population[i] = np.clip(X2, self.lower_bound_, self.upper_bound_)
                else:  # Exploitation phase
                    if np.random.random() < 0.5:
                        # Expanded exploitation (X3)
                        X3 = self._expanded_exploitation(global_best_position, population[i], t)
                        population[i] = np.clip(X3, self.lower_bound_, self.upper_bound_)
                    else:
                        # Narrowed exploitation (X4)
                        X4 = self._narrowed_exploitation(global_best_position, population[i], t)
                        population[i] = np.clip(X4, self.lower_bound_, self.upper_bound_)
            
            # Evaluate new population
            fitness = np.array([objective_function(ind) for ind in population])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < global_best_fitness:
                global_best_fitness = fitness[current_best_idx]
                global_best_position = population[current_best_idx].copy()
            
            # Track progress
            global_fitness.append(global_best_fitness)
            local_fitness.append(np.mean(fitness))
            local_positions.append(population.copy())
            
        return global_best_position, global_best_fitness, global_fitness, local_fitness, local_positions
    
    def _expanded_exploration(self, best_position, current_position, t):
        """Expanded exploration strategy (X1)."""
        X_M = self._calculate_mean_position()
        r1, r2 = np.random.random(), np.random.random()
        
        # Levy flight
        levy = self._levy_flight(self.dimensions_)
        
        if np.random.random() < 0.5:
            return best_position * (1 - t) + X_M * levy
        else:
            return best_position * levy + r1 * ((current_position + best_position) / 2) + r2 * levy
    
    def _narrowed_exploration(self, best_position, current_position, t):
        """Narrowed exploration strategy (X2)."""
        r1, r2 = np.random.random(), np.random.random()
        
        # Levy flight
        levy = self._levy_flight(self.dimensions_)
        
        return best_position * levy + r1 * current_position + r2 * levy
    
    def _expanded_exploitation(self, best_position, current_position, t):
        """Expanded exploitation strategy (X3)."""
        r1, r2 = np.random.random(), np.random.random()
        
        # Quality function
        QF = t**((2 * np.random.random() - 1))
        
        return (best_position - current_position) * QF + r1 * ((self._uniform_random() + self._uniform_random()) / 2) + r2 * self._levy_flight(self.dimensions_)
    
    def _narrowed_exploitation(self, best_position, current_position, t):
        """Narrowed exploitation strategy (X4)."""
        r1, r2 = np.random.random(), np.random.random()
        
        # Quality function
        QF = t**((2 * np.random.random() - 1))
        
        G1 = 2 * r1 - 1
        G2 = 2 * (1 - t)
        
        return QF * best_position - G1 * current_position * np.random.random() - G2 * self._levy_flight(self.dimensions_)
    
    def _calculate_mean_position(self):
        """Calculate mean position of current population."""
        return np.mean(self.population, axis=0)
    
    def _levy_flight(self, dimensions):
        """Generate Levy flight."""
        beta = 1.5
        sigma = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (math.gamma((1 + beta) / 2) * beta * (2**((beta - 1) / 2))))**(1 / beta)
        
        u = np.random.normal(0, sigma, dimensions)
        v = np.random.normal(0, 1, dimensions)
        
        return u / (np.abs(v)**(1 / beta))
    
    def _uniform_random(self):
        """Generate uniform random vector."""
        return np.random.uniform(self.lower_bound_, self.upper_bound_)
    
    def _initialize_population(self):
        """Initialize population within bounds."""
        population = []
        for _ in range(self.population_size_):
            individual = np.random.uniform(self.lower_bound_, self.upper_bound_, self.dimensions_)
            population.append(individual)
        
        self.population = np.array(population)
        return self.population
