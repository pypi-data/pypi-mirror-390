"""
Particle Swarm Optimization (PSO) Algorithm

Based on: Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization.
"""

import numpy as np
from ..base import BaseOptimizer


class ParticleSwarmOptimization(BaseOptimizer):
    """
    Particle Swarm Optimization (PSO) Algorithm
    
    PSO is inspired by the social behavior of bird flocking or fish schooling.
    Each particle represents a potential solution and moves through the search space
    influenced by its own best position and the global best position.
    
    Parameters
    ----------
    w : float, default=0.9
        Inertia weight controlling the influence of previous velocity
    c1 : float, default=2.0
        Acceleration coefficient for personal best (cognitive component)
    c2 : float, default=2.0
        Acceleration coefficient for global best (social component)
    """
    
    def __init__(self, *args, w=0.9, c1=2.0, c2=2.0, verbose=True, mode=True, population_size=30, max_iterations=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.w_ = w
        self.c1_ = c1
        self.c2_ = c2
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = verbose
        self.mode_ = mode
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.algorithm_name_ = "ParticleSwarmOptimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        # Use trailing underscore attributes
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
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        velocity = np.random.uniform(-1, 1, (self.population_size_, self.dimensions_))
        personal_best = population.copy()
        personal_best_fitness = np.array([objective_function(ind) for ind in population])
        global_best_idx = np.argmin(personal_best_fitness)
        global_best = personal_best[global_best_idx].copy()
        global_best_fitness = personal_best_fitness[global_best_idx]
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(self.population_size_):
                r1, r2 = np.random.random(2)
                velocity[i] = (self.w_ * velocity[i] + 
                             self.c1_ * r1 * (personal_best[i] - population[i]) +
                             self.c2_ * r2 * (global_best - population[i]))
                population[i] += velocity[i]
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                fitness = objective_function(population[i])
                fitnesses.append(fitness)
                positions.append(population[i].copy())
                if fitness < personal_best_fitness[i]:
                    personal_best[i] = population[i].copy()
                    personal_best_fitness[i] = fitness
                    if fitness < global_best_fitness:
                        global_best = population[i].copy()
                        global_best_fitness = fitness
            global_fitness.append(global_best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        return global_best, global_best_fitness, global_fitness, local_fitness, local_positions
