"""
Coronavirus Herd Immunity Optimization (CHIO) Algorithm

A pandemic-inspired optimization algorithm based on the spread of coronavirus
and the development of herd immunity in populations.

Reference:
Al-Betar, M. A., Alyasseri, Z. A. A., Awadallah, M. A., & Abu Doush, I. (2021). 
Coronavirus herd immunity optimizer (CHIO). Neural Computing and Applications, 33(10), 5011-5042.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class CoronavirusHerdImmunityOptimization(BaseOptimizer):
    """
    Coronavirus Herd Immunity Optimization (CHIO) Algorithm
    
    A pandemic-inspired optimization algorithm simulating virus spread and immunity development.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of individuals in the population
    max_iterations : int, default=100
        Maximum number of iterations
    infection_rate : float, default=0.3
        Basic reproduction number for virus spread
    immunity_rate : float, default=0.1
        Rate at which individuals develop immunity
    recovery_rate : float, default=0.2
        Rate of recovery from infection
    mutation_rate : float, default=0.01
        Virus mutation rate
    """
    
    aliases = ['chio', 'coronavirus', 'herdimmunity']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 infection_rate=0.3, immunity_rate=0.1, recovery_rate=0.2,
                 mutation_rate=0.01, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.infection_rate = infection_rate
        self.immunity_rate = immunity_rate
        self.recovery_rate = recovery_rate
        self.mutation_rate = mutation_rate
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.infection_rate_ = infection_rate
        self.immunity_rate_ = immunity_rate
        self.recovery_rate_ = recovery_rate
        self.mutation_rate_ = mutation_rate
        self.algorithm_name_ = "Coronavirus Herd Immunity Optimization"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        """
        Execute the CHIO optimization algorithm
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
        # Initialize population
        population = np.random.uniform(lower_bound, upper_bound, 
                                     (self.population_size, dimensions))
        fitness = np.array([objective_func(ind) for ind in population])
        
        # Initialize health status: 0=susceptible, 1=infected, 2=recovered/immune
        health_status = np.zeros(self.population_size)
        
        # Initialize some infected individuals
        initial_infected = max(1, int(0.1 * self.population_size))
        infected_indices = np.random.choice(self.population_size, initial_infected, replace=False)
        health_status[infected_indices] = 1
        
        best_idx = np.argmin(fitness)
        best_position = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [population.tolist()]
        for iteration in range(self.max_iterations):
            new_population = population.copy()
            new_health_status = health_status.copy()
            
            for i in range(self.population_size):
                if health_status[i] == 0:  # Susceptible
                    # Check for infection from neighbors
                    for j in range(self.population_size):
                        if health_status[j] == 1 and i != j:  # Infected neighbor
                            distance = np.linalg.norm(population[i] - population[j])
                            infection_prob = self.infection_rate * np.exp(-distance)
                            
                            if np.random.random() < infection_prob:
                                new_health_status[i] = 1  # Become infected
                                # Move towards infected individual (virus spread)
                                direction = population[j] - population[i]
                                step_size = np.random.uniform(0.1, 0.3)
                                new_population[i] = population[i] + step_size * direction
                                break
                
                elif health_status[i] == 1:  # Infected
                    # Virus mutation and spread
                    if np.random.random() < self.mutation_rate:
                        mutation = np.random.normal(0, 0.1, dimensions)
                        new_population[i] = population[i] + mutation
                    
                    # Recovery process
                    if np.random.random() < self.recovery_rate:
                        new_health_status[i] = 2  # Become immune
                        # Immune individuals move towards best solution
                        direction = best_position - population[i]
                        step_size = np.random.uniform(0.2, 0.5)
                        new_population[i] = population[i] + step_size * direction
                
                elif health_status[i] == 2:  # Recovered/Immune
                    # Immune individuals help others by sharing information
                    if np.random.random() < self.immunity_rate:
                        # Help susceptible neighbors
                        for j in range(self.population_size):
                            if health_status[j] == 0:  # Susceptible
                                distance = np.linalg.norm(population[i] - population[j])
                                if distance < 1.0:  # Close enough to help
                                    direction = population[i] - population[j]
                                    step_size = np.random.uniform(0.1, 0.2)
                                    new_population[j] = population[j] + step_size * direction
                    
                    # Immune individuals continue optimizing
                    exploration = np.random.normal(0, 0.05, dimensions)
                    new_population[i] = population[i] + exploration
                
                # Boundary handling
                new_population[i] = np.clip(new_population[i], lower_bound, upper_bound)
            
            # Update population and fitness
            population = new_population
            health_status = new_health_status
            fitness = np.array([objective_func(ind) for ind in population])
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = population[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(population.tolist())
            
            # Herd immunity check
            immune_ratio = np.sum(health_status == 2) / self.population_size
            if immune_ratio > 0.7:  # Herd immunity achieved
                # Reset some immune to susceptible (waning immunity)
                immune_indices = np.where(health_status == 2)[0]
                reset_count = int(0.1 * len(immune_indices))
                if reset_count > 0:
                    reset_indices = np.random.choice(immune_indices, reset_count, replace=False)
                    health_status[reset_indices] = 0
            
            # Adaptive parameters
            self.infection_rate *= 0.995
            self.recovery_rate *= 1.002
            
            if hasattr(self, "verbose_") and self.verbose_:
                infected_count = np.sum(health_status == 1)
                immune_count = np.sum(health_status == 2)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Infected: {infected_count}, Immune: {immune_count}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions