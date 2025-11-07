"""
Forensic-Based Investigation Optimization (FBI) Algorithm

A human-based optimization algorithm inspired by the forensic investigation process
used by investigators to solve criminal cases.

Reference:
Chou, J. S., & Nguyen, N. M. (2020). FBI inspired meta-optimization. 
Applied Soft Computing, 93, 106339.
"""

import numpy as np
from mha_toolbox.base import BaseOptimizer


class ForensicBasedInvestigationOptimization(BaseOptimizer):
    """
    Forensic-Based Investigation Optimization (FBI) Algorithm
    
    A human-based optimization algorithm inspired by forensic investigation procedures.
    
    Parameters
    ----------
    population_size : int, default=50
        Number of investigators in the team
    max_iterations : int, default=100
        Maximum number of investigation rounds
    investigation_rate : float, default=0.8
        Rate of evidence investigation
    pursuit_rate : float, default=0.6
        Rate of suspect pursuit
    """
    
    aliases = ['fbi', 'forensic', 'investigation']
    
    def __init__(self, population_size=50, max_iterations=100, 
                 investigation_rate=0.8, pursuit_rate=0.6, **kwargs):
        super().__init__(population_size=population_size, max_iterations=max_iterations, **kwargs)
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.investigation_rate = investigation_rate
        self.pursuit_rate = pursuit_rate
        
        # Set trailing underscore attributes
        self.population_size_ = population_size
        self.max_iterations_ = max_iterations
        self.investigation_rate_ = investigation_rate
        self.pursuit_rate_ = pursuit_rate
        self.algorithm_name_ = "Forensic-Based Investigation Optimization"
    
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
        # Initialize investigators (population)
        investigators = np.random.uniform(lower_bound, upper_bound, 
                                        (self.population_size, dimensions))
        fitness = np.array([objective_func(inv) for inv in investigators])
        
        # Initialize evidence (best positions found so far)
        evidence_pool = []
        
        best_idx = np.argmin(fitness)
        best_position = investigators[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize tracking for history
        global_fitness = [best_fitness]
        local_fitness = [fitness.tolist()]
        local_positions = [investigators.tolist()]
        # Add initial best as first evidence
        evidence_pool.append(best_position.copy())
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Investigation phase - examine evidence
                if np.random.random() < self.investigation_rate and evidence_pool:
                    # Select random evidence to investigate
                    evidence_idx = np.random.randint(0, len(evidence_pool))
                    evidence = evidence_pool[evidence_idx]
                    
                    # Investigate around the evidence
                    investigation_radius = 0.1 * (1 - iteration / self.max_iterations)
                    investigation_vector = np.random.uniform(-investigation_radius, 
                                                          investigation_radius, dimensions)
                    new_position = evidence + investigation_vector
                    
                    # Boundary handling
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    # Update investigator if better evidence found
                    if new_fitness < fitness[i]:
                        investigators[i] = new_position
                        fitness[i] = new_fitness
                        
                        # Add new evidence to pool
                        evidence_pool.append(new_position.copy())
                
                # Pursuit phase - chase suspects
                if np.random.random() < self.pursuit_rate:
                    # Select target (worst performer as suspect)
                    worst_idx = np.argmax(fitness)
                    suspect_position = investigators[worst_idx]
                    
                    # Pursue the suspect
                    pursuit_direction = investigators[i] - suspect_position
                    pursuit_strength = np.random.uniform(0.1, 0.3)
                    new_position = investigators[i] + pursuit_strength * pursuit_direction
                    
                    # Add some randomness (unpredictable suspect behavior)
                    randomness = np.random.normal(0, 0.05, dimensions)
                    new_position += randomness
                    
                    # Boundary handling
                    new_position = np.clip(new_position, lower_bound, upper_bound)
                    new_fitness = objective_func(new_position)
                    
                    # Update if pursuit was successful
                    if new_fitness < fitness[i]:
                        investigators[i] = new_position
                        fitness[i] = new_fitness
                
                # Team collaboration - share information
                if iteration > 0 and np.random.random() < 0.3:
                    # Select random teammate
                    teammate_idx = np.random.randint(0, self.population_size)
                    if teammate_idx != i:
                        # Share information (crossover)
                        alpha = np.random.random()
                        shared_info = alpha * investigators[i] + (1 - alpha) * investigators[teammate_idx]
                        
                        # Test shared information
                        shared_info = np.clip(shared_info, lower_bound, upper_bound)
                        shared_fitness = objective_func(shared_info)
                        
                        # Update if shared information is better
                        if shared_fitness < fitness[i]:
                            investigators[i] = shared_info
                            fitness[i] = shared_fitness
            
            # Update global best
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_fitness:
                best_position = investigators[current_best_idx].copy()
                best_fitness = fitness[current_best_idx]
            
            # Track progress
            global_fitness.append(best_fitness)
            local_fitness.append(fitness.tolist())
            local_positions.append(investigators.tolist())
            
            # Add new best evidence to pool
            evidence_pool.append(best_position.copy())
            
            # Evidence management - keep only recent relevant evidence
            max_evidence = 10
            if len(evidence_pool) > max_evidence:
                # Keep only the best evidence
                evidence_fitness = [objective_func(ev) for ev in evidence_pool]
                best_evidence_indices = np.argsort(evidence_fitness)[:max_evidence]
                evidence_pool = [evidence_pool[idx] for idx in best_evidence_indices]
            
            # Case review - periodic reset of worst performers
            if iteration % 20 == 0 and iteration > 0:
                worst_performers = np.argsort(fitness)[-int(0.1 * self.population_size):]
                for idx in worst_performers:
                    investigators[idx] = np.random.uniform(lower_bound, upper_bound, dimensions)
                    fitness[idx] = objective_func(investigators[idx])
            
            if hasattr(self, "verbose_") and self.verbose_:
                print(f"Iteration {iteration + 1}: Best fitness = {best_fitness:.6f}, "
                      f"Evidence count: {len(evidence_pool)}")
        
        return best_position, best_fitness, global_fitness, local_fitness, local_positions