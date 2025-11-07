"""
Charged System Search Algorithm (CSS)

Based on: Kaveh, A., & Talatahari, S. (2010). A novel heuristic optimization method: charged system search.
"""

import numpy as np
from ..base import BaseOptimizer


class ChargedSystemSearch(BaseOptimizer):
    """
    Charged System Search Algorithm (CSS)
    
    CSS is inspired by the Coulomb's law from electrostatics and the governing laws of motion.
    Charged particles (agents) attract or repel each other based on their fitness values.
    
    Parameters
    ----------
    kv : float, default=0.5
        Velocity coefficient
    ka : float, default=0.5
        Acceleration coefficient
    """
    
    aliases = ["css", "charged_system_search", "charged"]
    
    def __init__(self, kv=0.5, ka=0.5, **kwargs):
        super().__init__(**kwargs)
        self.kv = kv
        self.ka = ka
        self.algorithm_name = "CSS"
    
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
        
        # Initialize charged particles
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
            
            # Calculate charges
            worst_fitness = np.max(fitness)
            best_fitness_iter = np.min(fitness)
            
            if worst_fitness != best_fitness_iter:
                charges = (fitness - worst_fitness) / (best_fitness_iter - worst_fitness)
            else:
                charges = np.ones(self.population_size_)
            
            # Update positions
            for i in range(self.population_size_):
                force = np.zeros(self.dimensions_)
                
                for j in range(self.population_size_):
                    if i != j:
                        # Calculate distance
                        distance = np.linalg.norm(population[i] - population[j]) + 1e-10
                        
                        # Calculate force based on charges
                        if fitness[j] < fitness[i]:  # Attraction
                            force_direction = population[j] - population[i]
                        else:  # Repulsion
                            force_direction = population[i] - population[j]
                        
                        force += charges[j] * force_direction / (distance ** 2)
                
                # Update velocity
                velocity[i] = self.kv * velocity[i] + self.ka * force
                
                # Update position
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