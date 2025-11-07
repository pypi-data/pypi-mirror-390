"""
Gravitational Search Algorithm (GSA)

Based on: Rashedi, E., Nezamabadi-Pour, H., & Saryazdi, S. (2009). GSA: a gravitational search algorithm.
"""

import numpy as np
from ..base import BaseOptimizer


class GravitationalSearchAlgorithm(BaseOptimizer):
    """
    Gravitational Search Algorithm (GSA)
    
    GSA is inspired by the law of gravity and mass interactions.
    Agents are considered as objects with masses that attract each other.
    
    Parameters
    ----------
    G0 : float, default=100
        Initial gravitational constant
    alpha : float, default=20
        Decreasing rate of gravitational constant
    """
    
    aliases = ["gsa", "gravitational_search", "gravitational"]
    
    def __init__(self, G0=100, alpha=20, **kwargs):
        super().__init__(**kwargs)
        self.G0 = G0
        self.alpha = alpha
        self.algorithm_name = "GSA"
    
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
        
        # Initialize agents
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Initialize velocities
        velocity = np.zeros((self.population_size_, self.dimensions_))
        
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
            
            # Update gravitational constant
            G = self.G0 * np.exp(-self.alpha * iteration / self.max_iterations_)
            
            # Calculate masses
            worst_fitness = np.max(fitness)
            best_fitness_iter = np.min(fitness)
            
            if worst_fitness != best_fitness_iter:
                masses = (fitness - worst_fitness) / (best_fitness_iter - worst_fitness)
            else:
                masses = np.ones(self.population_size_)
            
            # Normalize masses
            masses = masses / np.sum(masses)
            
            # Calculate forces and accelerations
            for i in range(self.population_size_):
                force = np.zeros(self.dimensions_)
                
                for j in range(self.population_size_):
                    if i != j:
                        # Calculate Euclidean distance
                        R = np.linalg.norm(population[j] - population[i]) + 1e-10
                        
                        # Calculate force
                        force += np.random.random() * masses[j] * (population[j] - population[i]) / R
                
                # Calculate acceleration
                acceleration = force * G
                
                # Update velocity and position
                velocity[i] = np.random.random() * velocity[i] + acceleration
                population[i] = population[i] + velocity[i]
                
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