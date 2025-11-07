"""
Coyote Optimization Algorithm (COA)

Based on: Pierezan, J., & Coelho, L. D. S. (2018). Coyote optimization algorithm: 
a new metaheuristic for global optimization problems.
"""

import numpy as np
from ..base import BaseOptimizer


class CoyoteOptimizationAlgorithm(BaseOptimizer):
    """
    Coyote Optimization Algorithm (COA)
    
    COA is inspired by the social organization and pack hunting behavior of coyotes.
    It uses pack formation, leadership hierarchy, and cooperative hunting strategies.
    """
    
    aliases = ["coa", "coyote", "coyote_optimization"]
    
    def __init__(self, *args, n_packs=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_packs_ = n_packs
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "CoyoteOptimizationAlgorithm"
    
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
        
        # Initialize coyote population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Calculate pack size
        pack_size = self.population_size_ // self.n_packs_
        
        # Organize into packs
        packs = [population[i*pack_size:(i+1)*pack_size] for i in range(self.n_packs_)]
        if len(population) % self.n_packs_ > 0:
            packs[-1] = np.vstack([packs[-1], population[self.n_packs_*pack_size:]])
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        
        # Find global best (alpha coyote)
        best_idx = np.argmin(fitness)
        global_best = population[best_idx].copy()
        global_best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            new_population = []
            
            for pack_idx, pack in enumerate(packs):
                pack_fitness = np.array([objective_function(coyote) for coyote in pack])
                
                # Find pack alpha (leader)
                alpha_idx = np.argmin(pack_fitness)
                alpha = pack[alpha_idx].copy()
                
                # Update each coyote in the pack
                for i, coyote in enumerate(pack):
                    # Social interaction with alpha
                    r1, r2 = np.random.random(2)
                    
                    # Birth of new coyote (combination of two random coyotes)
                    if len(pack) > 1:
                        cr1, cr2 = np.random.choice(len(pack), 2, replace=False)
                        r = np.random.random(self.dimensions_)
                        pup = np.where(r < 0.5, pack[cr1], pack[cr2])
                        
                        # Add random perturbation
                        if np.random.random() < 0.005:  # Birth rate
                            pup += np.random.randn(self.dimensions_) * 0.1
                        
                        pup = np.clip(pup, self.lower_bound_, self.upper_bound_)
                        new_position = pup
                    else:
                        # Random movement if pack too small
                        new_position = coyote + np.random.randn(self.dimensions_) * 0.1
                        new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                    
                    new_fitness = objective_function(new_position)
                    fitnesses.append(new_fitness)
                    positions.append(new_position.copy())
                    
                    # Update global best
                    if new_fitness < global_best_fitness:
                        global_best = new_position.copy()
                        global_best_fitness = new_fitness
                    
                    new_population.append(new_position)
            
            # Update population
            population = np.array(new_population)
            
            # Re-organize packs (migration)
            if iteration % 10 == 0:  # Migration every 10 iterations
                indices = np.random.permutation(len(population))
                population = population[indices]
                packs = [population[i*pack_size:(i+1)*pack_size] for i in range(self.n_packs_)]
                if len(population) % self.n_packs_ > 0:
                    packs[-1] = np.vstack([packs[-1], population[self.n_packs_*pack_size:]])
            
            global_fitness.append(global_best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return global_best, global_best_fitness, global_fitness, local_fitness, local_positions