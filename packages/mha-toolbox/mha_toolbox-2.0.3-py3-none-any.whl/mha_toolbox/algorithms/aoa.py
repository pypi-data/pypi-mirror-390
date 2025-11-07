"""
Archimedes Optimization Algorithm (AOA)

A physics-inspired optimization algorithm based on Archimedes' principle
of buoyancy and fluid mechanics.

Reference:
Hashim, F. A., Hussain, K., Houssein, E. H., Mabrouk, M. S., & Al-Atabany, W. (2021). 
Archimedes optimization algorithm: a new metaheuristic algorithm for solving optimization problems. 
Applied Intelligence, 51(3), 1531-1551.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class ArchimedesOptimizationAlgorithm(BaseOptimizer):
    """
    Archimedes Optimization Algorithm (AOA)
    
    A physics-inspired optimization algorithm based on Archimedes' principle.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of objects in the fluid
    max_iterations : int, default=100
        Maximum number of iterations
    acceleration_factor : float, default=2.0
        Acceleration factor for object movement
    """
    
    aliases = ['aoa', 'archimedes', 'buoyancy']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 acceleration_factor=2.0, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.acceleration_factor = acceleration_factor
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.acceleration_factor_ = acceleration_factor
        self.algorithm_name_ = "Archimedes Optimization Algorithm"
    
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
        # Initialize objects in fluid
        objects = np.random.uniform(lower_bound, upper_bound, 
                                  (self.population_size, dimensions))
        fitness = np.array([objective_func(obj) for obj in objects])
        
        # Initialize physical properties
        densities = np.random.uniform(0.5, 2.0, self.population_size)
        volumes = np.random.uniform(0.1, 1.0, self.population_size)
        accelerations = np.zeros((self.population_size, dimensions))
        
        best_idx = np.argmin(fitness)
        best_position = objects[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [objects.tolist()]
        # Fluid density (environment)
        fluid_density = 1.0
        
        for iteration in range(self.max_iterations):
            # Calculate transfer operator T
            T = np.exp((iteration - self.max_iterations) / self.max_iterations)
            
            for i in range(self.population_size):
                # Calculate material density function (MR)
                density_factor = np.random.uniform(0.9, 1.1)
                material_density = densities[i] * density_factor
                
                # Archimedes force calculation
                if material_density > fluid_density:
                    # Object sinks - exploitation phase
                    # Calculate acceleration due to Archimedes principle
                    buoyant_force = fluid_density * volumes[i]  # Simplified
                    weight = material_density * volumes[i]
                    net_force = weight - buoyant_force
                    
                    # Movement towards best solution (sinking towards bottom)
                    direction_to_best = best_position - objects[i]
                    acceleration_magnitude = net_force / material_density
                    accelerations[i] = acceleration_magnitude * T * direction_to_best
                    
                    # Update position with physics-based movement
                    new_position = objects[i] + accelerations[i] + \
                                 0.5 * accelerations[i] * T**2
                
                else:
                    # Object floats - exploration phase
                    # Random movement due to buoyancy
                    buoyant_force = fluid_density * volumes[i]
                    weight = material_density * volumes[i]
                    net_upward_force = buoyant_force - weight
                    
                    # Random exploration movement
                    random_direction = np.random.uniform(-1, 1, dimensions)
                    acceleration_magnitude = net_upward_force / fluid_density
                    accelerations[i] = acceleration_magnitude * random_direction
                    
                    # Update position with buoyant movement
                    new_position = objects[i] + accelerations[i] * T + \
                                 np.random.normal(0, 0.1, dimensions)
                
                # Boundary handling
                new_position = np.clip(new_position, lower_bound, upper_bound)
                new_fitness = objective_func(new_position)
                
                # Update if better
                if new_fitness < fitness[i]:
                    objects[i] = new_position
                    fitness[i] = new_fitness
                
                # Collision with other objects
                if np.random.random() < 0.3:
                    # Select random object for collision
                    collision_idx = np.random.randint(0, self.population_size)
                    if collision_idx != i:
                        # Elastic collision - exchange of momentum
                        mass_i = material_density * volumes[i]
                        mass_j = densities[collision_idx] * volumes[collision_idx]
                        
                        # Simplified collision dynamics
                        velocity_exchange = (mass_j / (mass_i + mass_j)) * \
                                          (objects[collision_idx] - objects[i])
                        
                        collision_position = objects[i] + 0.5 * velocity_exchange
                        collision_position = np.clip(collision_position, lower_bound, upper_bound)
                        collision_fitness = objective_func(collision_position)
                        
                        if collision_fitness < fitness[i]:
                            objects[i] = collision_position
                            fitness[i] = collision_fitness
            
            # Fluid dynamics - update fluid properties
            if iteration % 10 == 0:
                # Fluid density changes with temperature/pressure
                fluid_density *= np.random.uniform(0.95, 1.05)
                fluid_density = np.clip(fluid_density, 0.5, 2.0)
                
                # Some objects may change density due to dissolution/precipitation
                change_indices = np.random.choice(self.population_size, 
                                                size=max(1, self.population_size // 10), 
                                                replace=False)
                for idx in change_indices:
                    densities[idx] *= np.random.uniform(0.9, 1.1)
                    densities[idx] = np.clip(densities[idx], 0.1, 3.0)
            
            # Convection currents - global mixing
            if iteration % 15 == 0:
                # Create convection currents that mix the fluid
                for i in range(self.population_size):
                    if np.random.random() < 0.2:
                        # Object caught in convection current
                        current_strength = np.random.uniform(0.1, 0.3)
                        current_direction = np.random.uniform(-1, 1, dimensions)
                        
                        convection_position = objects[i] + current_strength * current_direction
                        convection_position = np.clip(convection_position, lower_bound, upper_bound)
                        convection_fitness = objective_func(convection_position)
                        
                        if convection_fitness < fitness[i]:
                            objects[i] = convection_position
                            fitness[i] = convection_fitness
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = objects[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(objects.tolist())
            
            # Adaptive acceleration factor
            self.acceleration_factor *= 0.998
            
            if hasattr(self, "verbose_") and self.verbose_:
                avg_density = np.mean(densities)
                floating_count = np.sum(densities < fluid_density)
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Floating objects: {floating_count}, Fluid density: {fluid_density:.3f}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions