"""
Moth Search Algorithm (MSA)

Based on: Wang, G. G. (2018). Moth search algorithm: a bio-inspired metaheuristic 
algorithm for global optimization problems.
"""

import numpy as np
import math
from ..base import BaseOptimizer


class MothSearchAlgorithm(BaseOptimizer):
    """
    Moth Search Algorithm (MSA)
    
    MSA is inspired by the navigation method of moths in nature, including
    their movement patterns around light sources and Lévy flights.
    """
    
    aliases = ["msa", "moth", "moth_search"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "MothSearchAlgorithm"
    
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
        
        # Initialize moth population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find best moth (light source)
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Calculate scale parameter for Lévy flight
            scale = 1.0 / (iteration + 1)
            
            for i in range(self.population_size_):
                # Determine moth behavior
                if np.random.random() < 0.5:
                    # Spiral movement around light source
                    r = np.random.random()
                    theta = r * 2 * np.pi
                    new_position = best_solution + r * np.cos(theta) * (population[i] - best_solution)
                    new_position = new_position + r * np.sin(theta) * (population[i] - best_solution)
                else:
                    # Lévy flight for exploration
                    levy = self._levy_flight(self.dimensions_, scale)
                    new_position = population[i] + levy
                
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
    
    def _levy_flight(self, dimensions, scale=1.0):
        """Generate Lévy flight step."""
        # Simplified Lévy flight using normal distribution
        # In practice, you might want to use proper Lévy distribution
        sigma = (math.gamma(1 + 1.5) * np.sin(np.pi * 1.5 / 2) / 
                (math.gamma((1 + 1.5) / 2) * 1.5 * (2 ** ((1.5 - 1) / 2)))) ** (1 / 1.5)
        
        u = np.random.normal(0, sigma, dimensions)
        v = np.random.normal(0, 1, dimensions)
        
        step = u / (np.abs(v) ** (1 / 1.5))
        return scale * step