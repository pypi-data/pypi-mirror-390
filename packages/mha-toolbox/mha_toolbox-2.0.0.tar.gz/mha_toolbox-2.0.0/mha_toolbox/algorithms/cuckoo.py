"""
Cuckoo Search Algorithm (CS)

Based on: Yang, X. S., & Deb, S. (2009). Cuckoo search via Lévy flights.
"""

import numpy as np
from ..base import BaseOptimizer
import math


class CuckooSearch(BaseOptimizer):
    """
    Cuckoo Search Algorithm (CS)
    
    CS is inspired by the brood parasitism of some cuckoo species.
    Cuckoos lay their eggs in the nests of other host birds.
    
    Parameters
    ----------
    pa : float, default=0.25
        Discovery rate of alien eggs/solutions
    beta : float, default=1.5
        Lévy flight parameter
    """
    
    aliases = ["cs", "cuckoo", "cuckoo_search"]
    
    def __init__(self, pa=0.25, beta=1.5, **kwargs):
        super().__init__(**kwargs)
        self.pa = pa
        self.beta = beta
        self.algorithm_name = "CS"
    
    def _levy_flight(self, dimensions):
        """Generate Lévy flight step"""
        sigma = (math.gamma(1 + self.beta) * np.sin(np.pi * self.beta / 2) / 
                (math.gamma((1 + self.beta) / 2) * self.beta * (2 ** ((self.beta - 1) / 2)))) ** (1 / self.beta)
        
        u = np.random.randn(dimensions) * sigma
        v = np.random.randn(dimensions)
        
        return u / (np.abs(v) ** (1 / self.beta))
    
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
        
        # Initialize nest population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find initial best
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Generate new solutions via Lévy flights
            for i in range(self.population_size_):
                # Lévy flight
                levy = self._levy_flight(self.dimensions_)
                step_size = 0.01 * levy
                
                # Generate new solution
                new_solution = population[i] + step_size
                new_solution = np.clip(new_solution, self.lower_bound_, self.upper_bound_)
                
                new_fitness = objective_function(new_solution)
                
                # Choose a random nest (not necessarily the best)
                j = np.random.randint(0, self.population_size_)
                
                # If new solution is better, replace
                if new_fitness < fitness[j]:
                    population[j] = new_solution.copy()
                    fitness[j] = new_fitness
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_position = new_solution.copy()
                        best_fitness = new_fitness
            
            # Abandon some nests and build new ones
            abandon_count = int(self.pa * self.population_size_)
            worst_indices = np.argsort(fitness)[-abandon_count:]
            
            for idx in worst_indices:
                # Generate new random solution
                population[idx] = np.random.uniform(
                    self.lower_bound_, self.upper_bound_, self.dimensions_
                )
                fitness[idx] = objective_function(population[idx])
                
                # Update global best if necessary
                if fitness[idx] < best_fitness:
                    best_position = population[idx].copy()
                    best_fitness = fitness[idx]
            
            for i in range(self.population_size_):
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions