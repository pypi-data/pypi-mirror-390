"""
GWO-DE Hybrid Algorithm
Combines Grey Wolf Optimizer with Differential Evolution
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class GWO_DE_Hybrid(BaseOptimizer):
    """
    Hybrid algorithm combining Grey Wolf Optimizer and Differential Evolution
    
    Parameters
    ----------
    pop_size : int
        Population size
    max_iter : int
        Maximum number of iterations
    F : float
        Differential weight (DE component)
    CR : float
        Crossover probability (DE component)
    """
    
    def __init__(self, pop_size=50, max_iter=100, F=0.5, CR=0.9):
        super().__init__(pop_size, max_iter)
        self.F = F
        self.CR = CR
        
    def optimize(self, objective_func, lower_bound, upper_bound, dim):
        """Execute the GWO-DE hybrid optimization"""
        lb = np.ones(dim) * lower_bound
        ub = np.ones(dim) * upper_bound
        
        # Initialize population
        population = np.random.uniform(lb, ub, (self.pop_size, dim))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # Initialize alpha, beta, delta (top 3 wolves)
        sorted_indices = np.argsort(fitness)
        alpha_pos = population[sorted_indices[0]].copy()
        beta_pos = population[sorted_indices[1]].copy()
        delta_pos = population[sorted_indices[2]].copy()
        alpha_score = fitness[sorted_indices[0]]
        
        convergence_curve = np.zeros(self.max_iter)
        
        for iteration in range(self.max_iter):
            a = 2 - iteration * (2.0 / self.max_iter)  # Linearly decrease from 2 to 0
            
            for i in range(self.pop_size):
                # GWO phase
                for j in range(dim):
                    r1, r2 = np.random.rand(2)
                    A1 = 2 * a * r1 - a
                    C1 = 2 * r2
                    D_alpha = abs(C1 * alpha_pos[j] - population[i, j])
                    X1 = alpha_pos[j] - A1 * D_alpha
                    
                    r1, r2 = np.random.rand(2)
                    A2 = 2 * a * r1 - a
                    C2 = 2 * r2
                    D_beta = abs(C2 * beta_pos[j] - population[i, j])
                    X2 = beta_pos[j] - A2 * D_beta
                    
                    r1, r2 = np.random.rand(2)
                    A3 = 2 * a * r1 - a
                    C3 = 2 * r2
                    D_delta = abs(C3 * delta_pos[j] - population[i, j])
                    X3 = delta_pos[j] - A3 * D_delta
                    
                    population[i, j] = (X1 + X2 + X3) / 3
                
                # DE mutation and crossover
                indices = [idx for idx in range(self.pop_size) if idx != i]
                a_idx, b_idx, c_idx = np.random.choice(indices, 3, replace=False)
                
                mutant = population[a_idx] + self.F * (population[b_idx] - population[c_idx])
                mutant = np.clip(mutant, lb, ub)
                
                # Crossover
                cross_points = np.random.rand(dim) < self.CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, dim)] = True
                    
                trial = np.where(cross_points, mutant, population[i])
                trial = np.clip(trial, lb, ub)
                
                # Selection
                trial_fitness = objective_func(trial)
                if trial_fitness < fitness[i]:
                    population[i] = trial
                    fitness[i] = trial_fitness
            
            # Update alpha, beta, delta
            sorted_indices = np.argsort(fitness)
            alpha_pos = population[sorted_indices[0]].copy()
            beta_pos = population[sorted_indices[1]].copy()
            delta_pos = population[sorted_indices[2]].copy()
            alpha_score = fitness[sorted_indices[0]]
            
            convergence_curve[iteration] = alpha_score
            
        return alpha_pos, alpha_score, convergence_curve
