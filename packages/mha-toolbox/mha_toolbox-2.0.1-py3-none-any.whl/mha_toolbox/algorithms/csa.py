"""
Capuchin Search Algorithm (CSA)

Based on: Braik, M. S. (2021). Capuchin search algorithm: A novel nature-inspired
metaheuristic optimization algorithm.
"""

import numpy as np
from ..base import BaseOptimizer


class CapuchinSearchAlgorithm(BaseOptimizer):
    """
    Capuchin Search Algorithm (CSA)
    
    CSA is inspired by the social behavior and movement patterns of capuchin monkeys.
    It models their jumping patterns, territorial behavior, and social interactions.
    """
    
    aliases = ["csa", "capuchin", "capuchin_search"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "CapuchinSearchAlgorithm"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        if X is not None:
            self.dimensions_ = X.shape[1]
            self.lower_bound_ = np.zeros(self.dimensions_)
            self.upper_bound_ = np.ones(self.dimensions_)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                self.dimensions_ = kwargs.get('dimensions', 10)
            if not hasattr(self, 'lower_bound_') or self.lower_bound_ is None:
                lb = kwargs.get('lower_bound', kwargs.get('lb', -10.0))
                self.lower_bound_ = np.full(self.dimensions_, lb) if np.isscalar(lb) else np.array(lb)
            if not hasattr(self, 'upper_bound_') or self.upper_bound_ is None:
                ub = kwargs.get('upper_bound', kwargs.get('ub', 10.0))
                self.upper_bound_ = np.full(self.dimensions_, ub) if np.isscalar(ub) else np.array(ub)
        
        # Initialize capuchin population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best capuchin (alpha)
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update parameters
            a = 2 - 2 * iteration / self.max_iterations_  # Decreasing factor
            
            for i in range(self.population_size_):
                # Phase 1: Jumping and moving
                if np.random.random() < 0.5:
                    # Long jump (exploration)
                    A = 2 * a * np.random.random() - a
                    C = 2 * np.random.random()
                    D = abs(C * best_solution - population[i])
                    new_position = best_solution - A * D
                else:
                    # Short jump (exploitation)
                    r1, r2 = np.random.randint(0, self.population_size_, 2)
                    while r1 == i:
                        r1 = np.random.randint(0, self.population_size_)
                    while r2 == i or r2 == r1:
                        r2 = np.random.randint(0, self.population_size_)
                    
                    new_position = population[i] + np.random.random() * (population[r1] - population[r2])
                
                # Phase 2: Territorial behavior
                if np.random.random() < 0.3:  # 30% chance of territorial behavior
                    new_position = population[i] + np.random.randn(self.dimensions_) * 0.1
                
                # Boundary checking
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(new_position)
                fitnesses.append(new_fitness)
                positions.append(new_position.copy())
                
                # Update if better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_solution = new_position.copy()
                        best_fitness = new_fitness
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions