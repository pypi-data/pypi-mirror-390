"""
Simulated Annealing (SA) Algorithm

A classical optimization algorithm inspired by the annealing process in metallurgy,
where controlled cooling allows the material to reach a low-energy state.

Reference:
Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983). 
Optimization by simulated annealing. Science, 220(4598), 671-680.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class SimulatedAnnealing(BaseOptimizer):
    """
    Simulated Annealing (SA) Algorithm
    
    A classical optimization algorithm based on the metallurgical annealing process.
    
    Parameters
    ----------
    population_size : int, default=1
        Number of solutions (typically 1 for traditional SA)
    max_iterations : int, default=1000
        Maximum number of iterations
    initial_temperature : float, default=100.0
        Initial temperature for annealing
    cooling_rate : float, default=0.95
        Cooling rate (alpha)
    min_temperature : float, default=0.01
        Minimum temperature threshold
    """
    
    aliases = ['sa', 'annealing', 'simulated']
    
    def __init__(self, population_size=1, max_iterations=1000, 
                 initial_temperature=100.0, cooling_rate=0.95, min_temperature=0.01, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = max(1, population_size)  # SA typically uses 1 solution
        self.max_iterations = max_iterations
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        
        # Set trailing underscore attributes
        self.population_size_ = self.population_size
        self.max_iterations_ = max_iterations
        self.initial_temperature_ = initial_temperature
        self.cooling_rate_ = cooling_rate
        self.min_temperature_ = min_temperature
        self.algorithm_name_ = "Simulated Annealing"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the optimization algorithm
        """
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
            
        objective_func = objective_function
        if self.population_size == 1:
            return self._single_sa(objective_func, dimensions, lower_bound, upper_bound)
        else:
            return self._population_sa(objective_func, dimensions, lower_bound, upper_bound)
    
    def _single_sa(self, objective_func, dimensions, lower_bound, upper_bound):
        """Traditional single-solution Simulated Annealing"""
        # Initialize solution
        current_solution = np.random.uniform(lower_bound, upper_bound, dimensions)
        current_fitness = objective_func(current_solution)
        
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [current_fitness]
        local_positions = [current_solution.tolist()]
        
        temperature = self.initial_temperature
        
        for iteration in range(self.max_iterations):
            if temperature < self.min_temperature:
                break
            
            # Generate neighbor solution
            step_size = temperature / self.initial_temperature * 0.1
            perturbation = np.random.normal(0, step_size, dimensions)
            new_solution = current_solution + perturbation
            
            # Boundary handling
            new_solution = np.clip(new_solution, lower_bound, upper_bound)
            new_fitness = objective_func(new_solution)
            
            # Accept or reject new solution
            if new_fitness < current_fitness:
                # Better solution - always accept
                current_solution = new_solution
                current_fitness = new_fitness
                
                if new_fitness < best_fitness:
                    best_solution = new_solution.copy()
                    best_fitness = new_fitness
            else:
                # Worse solution - accept with probability
                delta = new_fitness - current_fitness
                probability = np.exp(-delta / temperature)
                
                if np.random.random() < probability:
                    current_solution = new_solution
                    current_fitness = new_fitness
            
            # Cool down
            temperature *= self.cooling_rate
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(current_fitness)
            local_positions.append(current_solution.tolist())
            
            if hasattr(self, 'verbose_') and self.verbose_ and iteration % 100 == 0:
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Temperature = {temperature:.6f}")
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions
    
    def _population_sa(self, objective_func, dimensions, lower_bound, upper_bound):
        """Population-based Simulated Annealing"""
        # Initialize population
        population = np.random.uniform(lower_bound, upper_bound, 
                                     (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        temperatures = np.full(self.population_size, self.initial_temperature)
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                if temperatures[i] < self.min_temperature:
                    continue
                
                # Generate neighbor solution
                step_size = temperatures[i] / self.initial_temperature * 0.1
                perturbation = np.random.normal(0, step_size, dimensions)
                new_solution = population[i] + perturbation
                
                # Boundary handling
                new_solution = np.clip(new_solution, lower_bound, upper_bound)
                new_fitness = objective_func(new_solution)
                
                # Accept or reject new solution
                if new_fitness < fitness[i]:
                    # Better solution - always accept
                    population[i] = new_solution
                    fitness[i] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_solution = new_solution.copy()
                        best_fitness = new_fitness
                else:
                    # Worse solution - accept with probability
                    delta = new_fitness - fitness[i]
                    probability = np.exp(-delta / temperatures[i])
                    
                    if np.random.random() < probability:
                        population[i] = new_solution
                        fitness[i] = new_fitness
                
                # Cool down individual temperature
                temperatures[i] *= self.cooling_rate
            
            # Reheat some solutions to maintain diversity
            if iteration % 50 == 0:
                cold_solutions = np.where(temperatures < self.min_temperature)[0]
                if len(cold_solutions) > 0:
                    reheat_count = min(len(cold_solutions), self.population_size // 10)
                    reheat_indices = np.random.choice(cold_solutions, reheat_count, replace=False)
                    temperatures[reheat_indices] = self.initial_temperature * 0.1
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
            
            if hasattr(self, 'verbose_') and self.verbose_ and iteration % 100 == 0:
                avg_temp = np.mean(temperatures[temperatures >= self.min_temperature])
                active_solutions = np.sum(temperatures >= self.min_temperature)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Avg temp = {avg_temp:.6f}, Active solutions = {active_solutions}")
        
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions