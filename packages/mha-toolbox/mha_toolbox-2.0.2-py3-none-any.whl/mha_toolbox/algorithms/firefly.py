"""
Firefly Algorithm (FA)

Based on: Yang, X. S. (2008). Firefly algorithm for multimodal optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class FireflyAlgorithm(BaseOptimizer):
    """
    Firefly Algorithm (FA)
    
    FA is inspired by the flashing behavior of fireflies.
    Fireflies are attracted to other fireflies based on their brightness.
    
    Parameters
    ----------
    alpha : float, default=0.25
        Randomization parameter
    beta0 : float, default=1.0
        Attractiveness at distance r=0
    gamma : float, default=0.1
        Light absorption coefficient
    """
    
    aliases = ["fa", "firefly", "firefly_algorithm"]
    
    def __init__(self, alpha=0.25, beta0=1.0, gamma=0.1, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.beta0 = beta0
        self.gamma = gamma
        self.algorithm_name = "FA"
    
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
        
        # Initialize firefly population
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
            
            # Update alpha (optional: decrease over time)
            alpha = self.alpha * (0.97 ** iteration)
            
            for i in range(self.population_size_):
                for j in range(self.population_size_):
                    if fitness[j] < fitness[i]:  # j is brighter than i
                        # Calculate distance
                        r = np.linalg.norm(population[i] - population[j])
                        
                        # Calculate attractiveness
                        beta = self.beta0 * np.exp(-self.gamma * r**2)
                        
                        # Move firefly i towards j
                        population[i] = (population[i] + 
                                       beta * (population[j] - population[i]) +
                                       alpha * (np.random.random(self.dimensions_) - 0.5))
                        
                        # Ensure bounds
                        population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                        
                        # Evaluate new position
                        fitness[i] = objective_function(population[i])
                        
                        # Update global best
                        if fitness[i] < best_fitness:
                            best_position = population[i].copy()
                            best_fitness = fitness[i]
                
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions