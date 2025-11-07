"""
Slime Mould Algorithm (SMA)

Based on: Li, S., Chen, H., Wang, M., Heidari, A. A., & Mirjalili, S. (2020). 
Slime mould algorithm: A new method for stochastic optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class SlimeMouldAlgorithm(BaseOptimizer):
    """
    Slime Mould Algorithm (SMA)
    
    SMA is inspired by the oscillation behavior of slime mould in nature.
    It mimics the contraction mode and the foraging behavior of slime mould.
    """
    
    aliases = ["sma", "slime", "slime_mould"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "SlimeMouldAlgorithm"
    
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
        
        # Initialize slime mould population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Sort population by fitness
        sorted_indices = np.argsort(fitness)
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        # Best slime mould
        best_solution = population[0].copy()
        best_fitness = fitness[0]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update parameters
            a = np.arctanh(1 - (iteration + 1) / self.max_iterations_)  # Nonlinear decreasing
            
            # Calculate condition and weights
            condition = np.random.random() < np.tanh(abs(fitness - best_fitness))
            
            # Calculate weights
            if iteration < self.max_iterations_ / 2:
                W = 1 + np.random.random() * np.log10((best_fitness - fitness) / (best_fitness - fitness[-1] + 1e-10) + 1)
            else:
                W = 1 - np.random.random() * np.log10((best_fitness - fitness) / (best_fitness - fitness[-1] + 1e-10) + 1)
            
            for i in range(self.population_size_):
                # Position update based on different conditions
                if i < self.population_size_ // 2:  # First half (high fitness)
                    if condition[i]:
                        # Random position
                        new_position = np.random.uniform(self.lower_bound_, self.upper_bound_)
                    else:
                        # Update position based on best solution
                        p = np.tanh(abs(fitness[i] - best_fitness))
                        vb = np.random.uniform(-a, a, self.dimensions_)
                        vc = np.random.uniform(-1, 1, self.dimensions_)
                        
                        if np.random.random() < p:
                            new_position = best_solution + vb
                        else:
                            new_position = vc
                else:  # Second half (lower fitness)
                    # Update position based on random positions
                    new_position = population[i] + np.random.randn(self.dimensions_) * (W[i] * population[np.random.randint(0, self.population_size_ // 2)] - population[np.random.randint(self.population_size_ // 2, self.population_size_)])
                
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
            
            # Sort population again
            sorted_indices = np.argsort(fitness)
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions