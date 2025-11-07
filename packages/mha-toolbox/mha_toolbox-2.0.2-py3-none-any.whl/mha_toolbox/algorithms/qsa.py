"""
Queuing Search Algorithm (QSA)

A human-inspired optimization algorithm based on the queuing system behavior
where customers wait in line for service, inspired by queue theory.

Reference:
Zhang, J., Xiao, M., Gao, L., & Pan, Q. (2018). Queuing search algorithm: 
A novel metaheuristic algorithm for solving engineering optimization problems. 
Applied Mathematical Modelling, 63, 464-490.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class QueuingSearchAlgorithm(BaseOptimizer):
    """
    Queuing Search Algorithm (QSA)
    
    A human-inspired optimization algorithm based on queuing system behavior.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of customers in the queue
    max_iterations : int, default=100
        Maximum number of iterations
    service_rate : float, default=0.8
        Rate at which customers are served
    arrival_rate : float, default=0.3
        Rate at which new customers arrive
    """
    
    aliases = ['qsa', 'queuing', 'queue']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 service_rate=0.8, arrival_rate=0.3, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.service_rate = service_rate
        self.arrival_rate = arrival_rate
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.service_rate_ = service_rate
        self.arrival_rate_ = arrival_rate
        self.algorithm_name_ = "Queuing Search Algorithm"
    
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
        # Initialize queue (population)
        queue = np.random.uniform(lower_bound, upper_bound, 
                                (self.population_size, dimensions))
        fitness = np.array([objective_func(customer) for customer in queue])
        
        # Initialize service times and waiting times
        service_times = np.random.exponential(1.0 / self.service_rate, self.population_size)
        waiting_times = np.zeros(self.population_size)
        
        best_idx = np.argmin(fitness)
        best_position = queue[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [queue.tolist()]
        for iteration in range(self.max_iterations):
            # Service phase - customers being served move towards better positions
            for i in range(self.population_size):
                if np.random.random() < self.service_rate:
                    # Customer is being served - gets better service
                    if i == 0:  # First in queue gets best service
                        service_direction = best_position - queue[i]
                        service_quality = 0.8
                    else:
                        # Other customers get service based on queue position
                        service_target_idx = max(0, i - 1)  # Look to customer ahead
                        service_direction = queue[service_target_idx] - queue[i]
                        service_quality = 0.5 / (i + 1)  # Service quality decreases with position
                    
                    new_position = queue[i] + service_quality * service_direction
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[i]:
                        queue[i] = new_position
                        fitness[i] = new_fitness
                        waiting_times[i] = 0  # Reset waiting time after good service
                    else:
                        waiting_times[i] += 1  # Increase waiting time
            
            # Queue reorganization based on fitness (better customers move forward)
            if iteration % 5 == 0:
                sorted_indices = np.argsort(fitness)
                queue = queue[sorted_indices]
                fitness = fitness[sorted_indices]
                waiting_times = waiting_times[sorted_indices]
            
            # Arrival phase - new customers may join or leave
            for i in range(self.population_size):
                if np.random.random() < self.arrival_rate:
                    # New customer behavior - exploration
                    if waiting_times[i] > 5:  # If waited too long, become impatient
                        # Impatient customer moves randomly (exploration)
                        new_position = np.random.uniform(lower_bound, upper_bound, dimensions)
                    else:
                        # Patient customer waits and observes others
                        if i < self.population_size - 1:
                            # Learn from customer behind
                            learning_factor = np.random.uniform(0.1, 0.3)
                            direction = queue[i + 1] - queue[i]
                            new_position = queue[i] + learning_factor * direction
                        else:
                            # Last customer explores randomly
                            exploration = np.random.normal(0, 0.1, dimensions)
                            new_position = queue[i] + exploration
                    
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[i]:
                        queue[i] = new_position
                        fitness[i] = new_fitness
                        waiting_times[i] = 0
                    else:
                        waiting_times[i] += 1
            
            # Queue management - remove worst performers occasionally
            if iteration % 10 == 0:
                worst_customers = np.argsort(fitness)[-int(0.1 * self.population_size):]
                for idx in worst_customers:
                    if waiting_times[idx] > 10:  # Remove customers who waited too long
                        queue[idx] = np.random.uniform(lower_bound, upper_bound, dimensions)
                        fitness[idx] = objective_func(queue[idx])
                        waiting_times[idx] = 0
            
            # Server efficiency - occasionally provide premium service to best customers
            if iteration % 15 == 0:
                best_customers = np.argsort(fitness)[:int(0.2 * self.population_size)]
                for idx in best_customers:
                    premium_direction = best_position - queue[idx]
                    premium_service = 0.3 * premium_direction
                    new_position = queue[idx] + premium_service
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    if new_fitness < fitness[idx]:
                        queue[idx] = new_position
                        fitness[idx] = new_fitness
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = queue[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(queue.tolist())
            
            # Adaptive parameters
            self.service_rate = max(0.1, self.service_rate * 0.998)
            self.arrival_rate = min(0.5, self.arrival_rate * 1.001)
            
            if hasattr(self, "verbose_") and self.verbose_:
                avg_waiting = np.mean(waiting_times)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Avg waiting time: {avg_waiting:.2f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions