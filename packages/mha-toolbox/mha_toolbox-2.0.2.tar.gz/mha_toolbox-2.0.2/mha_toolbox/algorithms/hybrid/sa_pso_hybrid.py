"""
SA-PSO Hybrid Algorithm
Combines Simulated Annealing with Particle Swarm Optimization
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class SA_PSO_Hybrid(BaseOptimizer):
    """
    Hybrid algorithm combining Simulated Annealing and Particle Swarm Optimization
    
    Parameters
    ----------
    pop_size : int
        Population size
    max_iter : int
        Maximum number of iterations
    T0 : float
        Initial temperature (SA component)
    Tf : float
        Final temperature (SA component)
    w : float
        Inertia weight (PSO component)
    c1 : float
        Cognitive parameter (PSO component)
    c2 : float
        Social parameter (PSO component)
    """
    
    def __init__(self, pop_size=50, max_iter=100, T0=100.0, Tf=0.01, w=0.7, c1=1.5, c2=1.5):
        super().__init__(pop_size, max_iter)
        self.T0 = T0
        self.Tf = Tf
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
    def optimize(self, objective_func, lower_bound, upper_bound, dim):
        """Execute the SA-PSO hybrid optimization"""
        lb = np.ones(dim) * lower_bound
        ub = np.ones(dim) * upper_bound
        
        # Initialize population
        population = np.random.uniform(lb, ub, (self.pop_size, dim))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # PSO components
        velocity = np.random.uniform(-1, 1, (self.pop_size, dim))
        pbest = population.copy()
        pbest_fitness = fitness.copy()
        
        # Best solution
        best_idx = np.argmin(fitness)
        gbest = population[best_idx].copy()
        gbest_fitness = fitness[best_idx]
        
        convergence_curve = np.zeros(self.max_iter)
        
        for iteration in range(self.max_iter):
            # Calculate temperature for SA component
            T = self.T0 * ((self.Tf / self.T0) ** (iteration / self.max_iter))
            
            for i in range(self.pop_size):
                # PSO phase
                r1, r2 = np.random.rand(2)
                velocity[i] = (self.w * velocity[i] + 
                              self.c1 * r1 * (pbest[i] - population[i]) +
                              self.c2 * r2 * (gbest - population[i]))
                
                new_pos = population[i] + velocity[i]
                new_pos = np.clip(new_pos, lb, ub)
                
                # Evaluate new position
                new_fitness = objective_func(new_pos)
                
                # SA acceptance criterion
                delta_E = new_fitness - fitness[i]
                if delta_E < 0 or np.random.rand() < np.exp(-delta_E / T):
                    population[i] = new_pos
                    fitness[i] = new_fitness
                    
                    # Update personal best
                    if fitness[i] < pbest_fitness[i]:
                        pbest[i] = population[i].copy()
                        pbest_fitness[i] = fitness[i]
                        
                    # Update global best
                    if fitness[i] < gbest_fitness:
                        gbest = population[i].copy()
                        gbest_fitness = fitness[i]
            
            convergence_curve[iteration] = gbest_fitness
            
        return gbest, gbest_fitness, convergence_curve
