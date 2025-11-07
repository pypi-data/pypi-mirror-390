"""
Grasshopper Optimization Algorithm (GOA)

Based on: Saremi, S., Mirjalili, S., & Lewis, A. (2017). Grasshopper optimization algorithm.
"""

import numpy as np
from ..base import BaseOptimizer


class GrasshopperOptimizationAlgorithm(BaseOptimizer):
    """
    Grasshopper Optimization Algorithm (GOA)
    
    GOA is inspired by the behavior of grasshopper swarms in nature.
    Grasshoppers exhibit both repulsion and attraction forces.
    
    Parameters
    ----------
    cmax : float, default=1
        Maximum value of coefficient c
    cmin : float, default=0.00001
        Minimum value of coefficient c
    """
    
    aliases = ["goa", "grasshopper", "grasshopper_optimization"]
    
    def __init__(self, cmax=1, cmin=0.00001, **kwargs):
        super().__init__(**kwargs)
        self.cmax = cmax
        self.cmin = cmin
        self.algorithm_name = "GOA"
    
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
        
        # Initialize grasshopper population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find initial target (best solution)
        target_idx = np.argmin(fitness)
        target_position = population[target_idx].copy()
        target_fitness = fitness[target_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Calculate coefficient c
            c = self.cmax - iteration * ((self.cmax - self.cmin) / self.max_iterations_)
            
            for i in range(self.population_size_):
                S = np.zeros(self.dimensions_)
                
                for j in range(self.population_size_):
                    if i != j:
                        # Calculate distance
                        distance = np.linalg.norm(population[i] - population[j])
                        
                        # Avoid division by zero
                        distance = max(distance, 1e-10)
                        
                        # Calculate unit vector
                        direction = (population[j] - population[i]) / distance
                        
                        # Social forces function
                        s = self._s_function(distance)
                        
                        S += s * direction
                
                # Update position
                population[i] = c * S + target_position
                
                # Ensure bounds
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                
                # Evaluate fitness
                fitness[i] = objective_function(population[i])
                
                # Update target
                if fitness[i] < target_fitness:
                    target_position = population[i].copy()
                    target_fitness = fitness[i]
                
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(target_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return target_position, target_fitness, global_fitness, local_fitness, local_positions
    
    def _s_function(self, r):
        """Social forces function"""
        f = 0.5
        l = 1.5
        return f * np.exp(-r/l) - np.exp(-r)