"""
Ant Colony Optimization (ACO)

Based on: Dorigo, M., & Gambardella, L. M. (1997). Ant colony system: 
a cooperative learning approach to the traveling salesman problem.
"""

import numpy as np
from ..base import BaseOptimizer


class AntColonyOptimization(BaseOptimizer):
    """
    Ant Colony Optimization (ACO) for continuous optimization
    
    ACO is inspired by the foraging behavior of ants. This implementation
    adapts ACO for continuous optimization problems using a solution
    construction mechanism based on probability distributions.
    
    Parameters
    ----------
    q : float, default=0.01
        Intensification parameter
    zeta : float, default=1.0
        Deviation-distance ratio parameter
    """
    
    aliases = ["aco", "ant_colony", "ant_colony_optimization"]
    
    def __init__(self, q=0.01, zeta=1.0, **kwargs):
        super().__init__(**kwargs)
        self.q = q
        self.zeta = zeta
        self.algorithm_name = "ACO"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        # Use trailing underscore attributes
        if X is not None:
            dimensions = X.shape[1]
            lower_bound = np.zeros(dimensions)
            upper_bound = np.ones(dimensions)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                raise ValueError("Dimensions must be specified")
            dimensions = self.dimensions_
            lower_bound = self.lower_bound_
            upper_bound = self.upper_bound_
            
        archive = []
        archive_size = self.population_size_
        for _ in range(archive_size):
            solution = np.random.uniform(lower_bound, upper_bound, dimensions)
            fitness = objective_function(solution)
            archive.append((solution, fitness))
        archive.sort(key=lambda x: x[1])
        global_fitness = []
        local_fitness = []
        local_positions = []
        for iteration in range(self.max_iterations_):
            new_solutions = []
            fitnesses = []
            positions = []
            for _ in range(self.population_size_):
                solution = self._construct_solution(archive, dimensions)
                solution = np.clip(solution, self.lower_bound_, self.upper_bound_)
                fitness = objective_function(solution)
                new_solutions.append((solution, fitness))
                fitnesses.append(fitness)
                positions.append(solution.copy())
            archive.extend(new_solutions)
            archive.sort(key=lambda x: x[1])
            archive = archive[:archive_size]
            global_fitness.append(archive[0][1])
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        best_solution, best_fitness = archive[0]
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions
    
    def _construct_solution(self, archive, dimensions):
        """Construct a solution using the solution archive"""
        solution = np.zeros(dimensions)
        
        # Calculate weights for archive solutions
        weights = []
        for i, (_, fitness) in enumerate(archive):
            weight = (1.0 / (len(archive) * self.q * np.sqrt(2 * np.pi))) * \
                    np.exp(-0.5 * ((i) / (self.q * len(archive)))**2)
            weights.append(weight)
        
        weights = np.array(weights)
        weights /= np.sum(weights)  # Normalize weights
        
        for j in range(self.dimensions):
            # Select archive solution based on weights
            selected_idx = np.random.choice(len(archive), p=weights)
            selected_solution = archive[selected_idx][0]
            
            # Calculate standard deviation
            sigma = self.zeta * np.sum([abs(sol[j] - selected_solution[j]) 
                                      for sol, _ in archive]) / (len(archive) - 1)
            
            # Generate component value
            if sigma > 0:
                solution[j] = np.random.normal(selected_solution[j], sigma)
            else:
                solution[j] = selected_solution[j]
        
        return solution
