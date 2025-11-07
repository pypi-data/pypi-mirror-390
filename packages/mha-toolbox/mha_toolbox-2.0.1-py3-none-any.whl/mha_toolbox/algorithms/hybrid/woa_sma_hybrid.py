"""
WOA-SMA Hybrid Algorithm

A hybrid algorithm combining Whale Optimization Algorithm and Slime Mould Algorithm.
"""

import numpy as np
from ...base import BaseOptimizer


class WOA_SMA_Hybrid(BaseOptimizer):
    """
    WOA-SMA Hybrid Algorithm
    
    This algorithm combines the exploration of WOA with the exploitation of SMA
    by using both algorithms alternately during the optimization process.
    
    Parameters
    ----------
    switch_prob : float, default=0.5
        Probability of using WOA vs SMA in each iteration
    """
    
    aliases = ["woa_sma", "woa_sma_hybrid", "hybrid_woa_sma"]
    
    def __init__(self, switch_prob=0.5, **kwargs):
        super().__init__(**kwargs)
        self.switch_prob = switch_prob
        self.algorithm_name = "WOA_SMA_Hybrid"
    
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
        
        # Initialize population
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
            
            # Decide which algorithm to use
            if np.random.random() < self.switch_prob:
                # Use WOA update
                a = 2 - iteration * (2 / self.max_iterations_)
                
                for i in range(self.population_size_):
                    r1, r2 = np.random.random(2)
                    A = 2 * a * r1 - a
                    C = 2 * r2
                    
                    p = np.random.random()
                    
                    if p < 0.5:
                        if abs(A) >= 1:
                            # Search for prey (exploration)
                            random_whale_idx = np.random.randint(0, self.population_size_)
                            D = abs(C * population[random_whale_idx] - population[i])
                            population[i] = population[random_whale_idx] - A * D
                        else:
                            # Encircling prey (exploitation)
                            D = abs(C * best_position - population[i])
                            population[i] = best_position - A * D
                    else:
                        # Spiral update
                        distance = abs(best_position - population[i])
                        b = 1
                        l = np.random.uniform(-1, 1)
                        population[i] = distance * np.exp(b * l) * np.cos(2 * np.pi * l) + best_position
                    
                    # Ensure bounds
                    population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                    
                    # Evaluate fitness
                    fitness[i] = objective_function(population[i])
                    
                    if fitness[i] < best_fitness:
                        best_position = population[i].copy()
                        best_fitness = fitness[i]
            
            else:
                # Use SMA update
                a = np.arctanh(-(iteration / self.max_iterations_) + 1)
                
                # Sort population by fitness
                sorted_indices = np.argsort(fitness)
                
                for i in range(self.population_size_):
                    if i < self.population_size_ // 2:
                        # Update position of the first half
                        r = np.random.random()
                        if r < a:
                            population[i] = np.random.uniform(self.lower_bound_, self.upper_bound_, self.dimensions_)
                        else:
                            p = np.tanh(abs(fitness[i] - best_fitness))
                            vb = np.random.uniform(-a, a, self.dimensions_)
                            vc = np.random.uniform(-1, 1, self.dimensions_)
                            
                            if np.random.random() < p:
                                population[i] = best_position + vb * (
                                    np.random.uniform(0, 1, self.dimensions_) * population[sorted_indices[0]] - 
                                    np.random.uniform(0, 1, self.dimensions_) * population[sorted_indices[1]]
                                )
                            else:
                                population[i] = vc * population[i]
                    else:
                        # Random position for the second half
                        population[i] = np.random.uniform(self.lower_bound_, self.upper_bound_, self.dimensions_)
                    
                    # Ensure bounds
                    population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                    
                    # Evaluate fitness
                    fitness[i] = objective_function(population[i])
                    
                    if fitness[i] < best_fitness:
                        best_position = population[i].copy()
                        best_fitness = fitness[i]
            
            # Collect data for this iteration
            for i in range(self.population_size_):
                fitnesses.append(fitness[i])
                positions.append(population[i].copy())
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions