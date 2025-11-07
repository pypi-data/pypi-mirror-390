"""
Ant Lion Optimizer (ALO)

Based on: Mirjalili, S. (2015). The ant lion optimizer. 
Advances in Engineering Software, 83, 80-98.
"""

import numpy as np
from ..base import BaseOptimizer


class AntLionOptimizer(BaseOptimizer):
    """
    Ant Lion Optimizer (ALO)
    
    ALO mimics the hunting mechanism of antlions in nature. Antlions create
    conical pits in sand to trap ants. The algorithm uses random walks of
    ants, interactions with antlions, and elite selection.
    """
    
    aliases = ["alo", "antlion", "ant_lion"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "AntLionOptimizer"
    
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
        
        # Initialize antlions (population)
        antlions = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Initialize ants
        ants = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Evaluate initial population
        antlion_fitness = np.array([objective_function(al) for al in antlions])
        
        # Find elite (best antlion)
        elite_idx = np.argmin(antlion_fitness)
        elite = antlions[elite_idx].copy()
        elite_fitness = antlion_fitness[elite_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            # Calculate radius of random walks
            I = 1  # Intensity ratio
            w = 2 * np.exp(-2 * iteration / self.max_iterations_)  # Weight
            
            for i in range(self.population_size_):
                # Select antlion using roulette wheel
                antlion_idx = self._roulette_wheel_selection(1.0 / (antlion_fitness + 1e-10))
                
                # Random walk towards selected antlion
                RA = self._random_walk(self.dimensions_, self.max_iterations_, 
                                     antlions[antlion_idx], w)
                
                # Random walk towards elite
                RE = self._random_walk(self.dimensions_, self.max_iterations_, 
                                     elite, w)
                
                # Update ant position (weighted average)
                ants[i] = (RA + RE) / 2.0
                ants[i] = np.clip(ants[i], self.lower_bound_, self.upper_bound_)
                
                # Evaluate ant
                fitness = objective_function(ants[i])
                fitnesses.append(fitness)
                positions.append(ants[i].copy())
                
                # Replace antlion if ant is better
                if fitness < antlion_fitness[i]:
                    antlions[i] = ants[i].copy()
                    antlion_fitness[i] = fitness
                    
                    # Update elite if necessary
                    if fitness < elite_fitness:
                        elite = ants[i].copy()
                        elite_fitness = fitness
            
            global_fitness.append(elite_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return elite, elite_fitness, global_fitness, local_fitness, local_positions
    
    def _roulette_wheel_selection(self, weights):
        """Roulette wheel selection based on weights."""
        total = np.sum(weights)
        if total == 0:
            return np.random.randint(0, len(weights))
        r = np.random.random() * total
        cumsum = 0
        for i, w in enumerate(weights):
            cumsum += w
            if cumsum >= r:
                return i
        return len(weights) - 1
    
    def _random_walk(self, dimensions, max_iter, center, w):
        """Generate random walk around center position."""
        # Simplified random walk implementation
        walk = np.random.randn(dimensions) * w
        return center + walk