"""
Grey Wolf Optimizer (GWO)

Based on: Mirjalili, S., Mirjalili, S. M., & Lewis, A. (2014). 
Grey wolf optimizer. Advances in engineering software, 69, 46-61.
"""

import numpy as np
from ..base import BaseOptimizer


class GreyWolfOptimizer(BaseOptimizer):
    """
    Grey Wolf Optimizer (GWO)
    
    GWO mimics the leadership hierarchy and hunting mechanism of grey wolves.
    The algorithm simulates the social behavior of grey wolves including alpha,
    beta, delta, and omega wolves.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        alpha_pos = np.zeros(self.dimensions_)
        beta_pos = np.zeros(self.dimensions_)
        delta_pos = np.zeros(self.dimensions_)
        alpha_score = float('inf')
        beta_score = float('inf')
        delta_score = float('inf')
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            for i in range(len(population)):
                population[i] = np.clip(population[i], self.lower_bound_, self.upper_bound_)
                fitness = objective_function(population[i])
                fitnesses.append(fitness)
                positions.append(population[i].copy())
                if fitness < alpha_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = alpha_score
                    beta_pos = alpha_pos.copy()
                    alpha_score = fitness
                    alpha_pos = population[i].copy()
                if fitness > alpha_score and fitness < beta_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = fitness
                    beta_pos = population[i].copy()
                if fitness > alpha_score and fitness > beta_score and fitness < delta_score:
                    delta_score = fitness
                    delta_pos = population[i].copy()
            global_fitness.append(alpha_score)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
            a = 2 - iteration * (2.0 / self.max_iterations_)
            for i in range(len(population)):
                for j in range(self.dimensions_):
                    r1 = np.random.random()
                    r2 = np.random.random()
                    A1 = 2 * a * r1 - a
                    C1 = 2 * r2
                    D_alpha = abs(C1 * alpha_pos[j] - population[i][j])
                    X1 = alpha_pos[j] - A1 * D_alpha
                    r1 = np.random.random()
                    r2 = np.random.random()
                    A2 = 2 * a * r1 - a
                    C2 = 2 * r2
                    D_beta = abs(C2 * beta_pos[j] - population[i][j])
                    X2 = beta_pos[j] - A2 * D_beta
                    r1 = np.random.random()
                    r2 = np.random.random()
                    A3 = 2 * a * r1 - a
                    C3 = 2 * r2
                    D_delta = abs(C3 * delta_pos[j] - population[i][j])
                    X3 = delta_pos[j] - A3 * D_delta
                    population[i][j] = (X1 + X2 + X3) / 3
        return alpha_pos, alpha_score, global_fitness, local_fitness, local_positions
