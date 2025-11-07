"""
Social Spider Algorithm (SSA)

Based on: Cuevas, E., Cienfuegos, M., Zaldívar, D., & Pérez-Cisneros, M. (2013). 
A swarm optimization algorithm inspired in the behavior of the social-spider.
"""

import numpy as np
from ..base import BaseOptimizer


class SocialSpiderAlgorithm(BaseOptimizer):
    """
    Social Spider Algorithm (SSA)
    
    SSA is inspired by the cooperative behavior of social spiders, including
    web construction, vibration sensing, and mating behavior.
    """
    
    aliases = ["ssa_spider", "social_spider", "spider"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions_ = None
        self.lower_bound_ = None
        self.upper_bound_ = None
        self.verbose_ = kwargs.get('verbose', True)
        self.mode_ = kwargs.get('mode', True)
        self.population_size_ = kwargs.get('population_size', 30)
        self.max_iterations_ = kwargs.get('max_iterations', 100)
        self.algorithm_name_ = "SocialSpiderAlgorithm"
    
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
        
        # Initialize spider population
        population = np.random.uniform(
            self.lower_bound_, self.upper_bound_,
            (self.population_size_, self.dimensions_)
        )
        
        # Assign genders (60% female, 40% male)
        n_females = int(0.6 * self.population_size_)
        genders = ['female'] * n_females + ['male'] * (self.population_size_ - n_females)
        np.random.shuffle(genders)
        
        # Evaluate initial population
        fitness = np.array([objective_function(ind) for ind in population])
        weights = (fitness - np.max(fitness)) / (np.min(fitness) - np.max(fitness) + 1e-10)
        
        # Find best and worst spiders
        best_idx = np.argmin(fitness)
        best_spider = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        global_fitness = []
        local_fitness = []
        local_positions = []
        
        for iteration in range(self.max_iterations_):
            fitnesses = []
            positions = []
            
            for i in range(self.population_size_):
                if genders[i] == 'female':
                    # Female spider movement
                    # Calculate vibrations from nearest females
                    distances = [np.linalg.norm(population[i] - population[j]) 
                               for j in range(self.population_size_) if genders[j] == 'female' and j != i]
                    
                    if distances:
                        nearest_idx = np.argmin(distances)
                        # Find the actual index of nearest female
                        female_indices = [j for j in range(self.population_size_) if genders[j] == 'female' and j != i]
                        nearest_female_idx = female_indices[nearest_idx]
                        
                        vibration_c = weights[nearest_female_idx] * np.exp(-distances[nearest_idx])
                        vibration_b = weights[best_idx] * np.exp(-np.linalg.norm(population[i] - best_spider))
                        
                        alpha = np.random.random()
                        beta = np.random.random()
                        delta = np.random.random() - 0.5
                        
                        new_position = (population[i] + 
                                      alpha * vibration_c * (population[nearest_female_idx] - population[i]) +
                                      beta * vibration_b * (best_spider - population[i]) +
                                      delta * (np.random.random(self.dimensions_) - 0.5))
                    else:
                        # If no other females, move randomly
                        new_position = population[i] + np.random.randn(self.dimensions_) * 0.1
                
                else:  # Male spider
                    # Male spider movement
                    male_indices = [j for j in range(self.population_size_) if genders[j] == 'male']
                    median_weight = np.median([weights[j] for j in male_indices])
                    
                    if weights[i] > median_weight:
                        # Dominant male - move towards nearest female
                        female_indices = [j for j in range(self.population_size_) if genders[j] == 'female']
                        if female_indices:
                            distances_to_females = [np.linalg.norm(population[i] - population[j]) for j in female_indices]
                            nearest_female_idx = female_indices[np.argmin(distances_to_females)]
                            
                            alpha = np.random.random()
                            new_position = population[i] + alpha * (population[nearest_female_idx] - population[i])
                        else:
                            new_position = population[i] + np.random.randn(self.dimensions_) * 0.1
                    else:
                        # Non-dominant male - move randomly
                        new_position = population[i] + np.random.randn(self.dimensions_) * 0.1
                
                # Boundary checking
                new_position = np.clip(new_position, self.lower_bound_, self.upper_bound_)
                
                # Evaluate new position
                new_fitness = objective_function(new_position)
                fitnesses.append(new_fitness)
                positions.append(new_position.copy())
                
                # Update if better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness
                    weights[i] = (new_fitness - np.max(fitness)) / (np.min(fitness) - np.max(fitness) + 1e-10)
                    
                    # Update global best
                    if new_fitness < best_fitness:
                        best_spider = new_position.copy()
                        best_fitness = new_fitness
                        best_idx = i
            
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions)
        
        return best_spider, best_fitness, global_fitness, local_fitness, local_positions