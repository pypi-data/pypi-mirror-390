"""
Pathfinder Algorithm (PFA)

Based on: Yapici, H., & Cetinkaya, N. (2019). A new meta-heuristic optimizer: 
Pathfinder algorithm.
"""

import numpy as np
from ..base import BaseOptimizer


class PathfinderAlgorithm(BaseOptimizer):
    """
    Pathfinder Algorithm (PFA)
    
    PFA is inspired by the movement of a swarm following a pathfinder to
    reach a target. It models the behavior of animals following a leader.
    """
    
    aliases = ["pfa", "pathfinder"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "PathfinderAlgorithm"
    
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
        
        # Find pathfinder (best solution)
        pathfinder_idx = np.argmin(fitness)
        pathfinder = population[pathfinder_idx].copy()
        pathfinder_fitness = fitness[pathfinder_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Update parameters
            alpha = 2 - 2 * iteration / self.max_iterations_  # Decreasing factor
            beta = 1 - iteration / self.max_iterations_       # Decreasing factor
            
            for i in range(self.population_size_):
                if i == pathfinder_idx:
                    # Pathfinder updates position randomly
                    epsilon = np.random.random()
                    if epsilon < 0.5:
                        new_position = population[i] + alpha * np.random.randn(self.dimensions_)
                    else:
                        new_position = (self.upper_bound_ + self.lower_bound_) / 2 + beta * np.random.randn(self.dimensions_)
                else:
                    # Other members follow pathfinder
                    A = 2 * alpha * np.random.random() - alpha
                    C = 2 * np.random.random()
                    
                    if abs(A) < 1:
                        # Exploitation (follow pathfinder closely)
                        D = abs(C * pathfinder - population[i])
                        new_position = pathfinder - A * D
                    else:
                        # Exploration (search randomly)
                        random_member = population[np.random.randint(0, self.population_size_)]
                        D = abs(C * random_member - population[i])
                        new_position = random_member - A * D
                
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
                    
                    # Update pathfinder if necessary
                    if new_fitness < pathfinder_fitness:
                        pathfinder = new_position.copy()
                        pathfinder_fitness = new_fitness
                        pathfinder_idx = i
            
            global_fitness.append(pathfinder_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return pathfinder, pathfinder_fitness, global_fitness, local_fitness, local_positions