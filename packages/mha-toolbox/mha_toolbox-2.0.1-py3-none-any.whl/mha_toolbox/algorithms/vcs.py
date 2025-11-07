"""
Virus Colony Search (VCS) Algorithm

A bio-inspired optimization algorithm based on the behavior of viruses in host organisms.
The algorithm simulates virus replication, mutation, and host cell infection processes.

Reference:
Li, M. D., Zhao, H., Weng, X. W., & Han, T. (2016). A novel nature-inspired algorithm for optimization: Virus colony search. Advances in Engineering Software, 92, 65-88.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class VirusColonySearch(BaseOptimizer):
    """
    Virus Colony Search (VCS) Algorithm
    
    A bio-inspired optimization algorithm based on virus behavior in host organisms.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of virus individuals in the population
    max_iterations : int, default=100
        Maximum number of iterations
    infection_rate : float, default=0.3
        Rate of infection for host cells
    replication_rate : float, default=0.5
        Rate of virus replication
    mutation_rate : float, default=0.1
        Probability of mutation during replication
    host_resistance : float, default=0.2
        Resistance factor of host cells
    """
    
    aliases = ['vcs', 'virus', 'viruscolony']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 infection_rate=0.3, replication_rate=0.5, mutation_rate=0.1,
                 host_resistance=0.2, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.infection_rate = infection_rate
        self.replication_rate = replication_rate
        self.mutation_rate = mutation_rate
        self.host_resistance = host_resistance
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.infection_rate_ = infection_rate
        self.replication_rate_ = replication_rate
        self.mutation_rate_ = mutation_rate
        self.host_resistance_ = host_resistance
        self.algorithm_name_ = "Virus Colony Search"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the VCS optimization algorithm
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
        # Initialize virus population
        population = np.random.uniform(lower_bound, upper_bound, 
                                     (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # Initialize host cells (environmental factors)
        host_cells = np.random.uniform(lower_bound, upper_bound, 
                                     (self.population_size, dimensions))
        host_fitness = np.array([objective_func(cell) for cell in host_cells])
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Virus infection process
                if np.random.random() < self.infection_rate:
                    # Select random host cell
                    host_idx = np.random.randint(0, self.population_size)
                    
                    # Infection based on fitness difference
                    if fitness[i] < host_fitness[host_idx] * (1 + self.host_resistance):
                        # Virus infects host - update host cell
                        infection_factor = np.random.random()
                        host_cells[host_idx] = (infection_factor * population[i] + 
                                              (1 - infection_factor) * host_cells[host_idx])
                        host_fitness[host_idx] = objective_func(host_cells[host_idx])
                
                # Virus replication process
                if np.random.random() < self.replication_rate:
                    # Create offspring virus
                    parent = population[i].copy()
                    
                    # Mutation during replication
                    if np.random.random() < self.mutation_rate:
                        mutation_vector = np.random.normal(0, 0.1, dimensions)
                        offspring = parent + mutation_vector
                    else:
                        # Normal replication with slight variation
                        variation = np.random.uniform(-0.05, 0.05, dimensions)
                        offspring = parent + variation
                    
                    # Boundary handling
                    offspring = np.clip(offspring, lower_bound, upper_bound)
                    offspring_fitness = objective_func(offspring)
                    
                    # Selection between parent and offspring
                    if offspring_fitness < fitness[i]:
                        population[i] = offspring
                        fitness[i] = offspring_fitness
                
                # Host cell interaction
                best_host_idx = np.argmin(host_fitness)
                if host_fitness[best_host_idx] < fitness[i]:
                    # Virus learns from best host cell
                    learning_rate = 0.1
                    population[i] = (population[i] + 
                                   learning_rate * (host_cells[best_host_idx] - population[i]))
                    population[i] = np.clip(population[i], lower_bound, upper_bound)
                    fitness[i] = objective_func(population[i])
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
            
            # Adaptive parameters
            self.infection_rate *= 0.995
            self.replication_rate *= 0.998
            
            if hasattr(self, 'verbose_') and self.verbose_:
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions