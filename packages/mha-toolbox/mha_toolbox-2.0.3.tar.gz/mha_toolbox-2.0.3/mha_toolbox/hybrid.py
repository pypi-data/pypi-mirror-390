"""
Hybrid Algorithm System for MHA Toolbox

This module provides support for combining 2-3 algorithms to create hybrid optimizers
that can leverage the strengths of multiple metaheuristic approaches.
"""

import numpy as np
import time
from datetime import datetime
import os

from .base import BaseOptimizer, OptimizationModel

class HybridOptimizationModel(OptimizationModel):
    """
    An extended OptimizationModel for hybrid algorithms.
    
    This class stores the overall result of the hybrid optimization, as well as
    a list of individual OptimizationModel objects for each component algorithm.
    """
    
    def __init__(self, individual_models, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.individual_models = individual_models
        self.algorithm_name = kwargs.get('algorithm_name', 'Hybrid')

    def summary(self):
        """
        Print a comprehensive summary of the hybrid optimization results.
        """
        super().summary()
        print("\n" + "="*60)
        print("🧩 Individual Algorithm Performance")
        print("="*60)
        
        sorted_models = sorted(self.individual_models, key=lambda m: m.best_fitness)
        
        for i, model in enumerate(sorted_models, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
            print(f"  {emoji} {i}. {model.algorithm_name:<20}: "
                  f"Fitness = {model.best_fitness:.6f}, "
                  f"Time = {model.execution_time:.2f}s")
        print("="*60)

    def save(self, base_filename=None, format='json'):
        """
        Save the hybrid result and the results of each individual algorithm.
        """
        if base_filename is None:
            # Save in hybrid algorithms directory
            subdir = 'results/hybrid_algorithms'
            os.makedirs(subdir, exist_ok=True)
            base_filename = f"{subdir}/hybrid_result_{self.algorithm_name.replace('+', '_')}_{datetime.now():%Y%m%d_%H%M%S}"
            
        # Save the main hybrid result
        super().save(filename=f"{base_filename}.{format}", format=format)
        
        # Save individual results in a sub-directory
        individual_results_dir = f"{base_filename}_components"
        try:
            if not os.path.exists(individual_results_dir):
                os.makedirs(individual_results_dir)
            
            for model in self.individual_models:
                model_filename = os.path.join(individual_results_dir, f"result_{model.algorithm_name}.{format}")
                model.save(filename=model_filename, format=format)
            
            print(f"Individual component results saved in '{individual_results_dir}/'")
        except Exception as e:
            print(f"Error saving individual results: {e}")


class HybridOptimizer(BaseOptimizer):
    """
    Hybrid optimizer that combines multiple algorithms sequentially.
    
    This class runs a sequence of algorithms, where each subsequent algorithm
    starts with the best solution found by the previous one.
    
    Supports flexible initialization:
    - HybridOptimizer(['PSO', 'SCA'], 50, 200) -> algorithms, pop_size=50, max_iter=200
    """
    
    def __init__(self, algorithms, *args, combination_mode='sequential', **kwargs):
        if not (2 <= len(algorithms) <= 3):
            raise ValueError("Hybrid optimizer requires 2 or 3 algorithms.")
            
        super().__init__(*args, **kwargs)
        self.algorithms = algorithms
        self.combination_mode = combination_mode # Currently only 'sequential' is fully supported
        self.algorithm_name = f"Hybrid_{'_then_'.join(algorithms)}"
        self.individual_models = []
        
    def _optimize(self, objective_function, X=None, y=None):
        """
        Hybrid optimization implementation.
        """
        if self.combination_mode == 'sequential':
            return self._sequential_optimization(objective_function, X, y)
        else:
            raise NotImplementedError(f"Combination mode '{self.combination_mode}' is not yet implemented.")
    
    def _sequential_optimization(self, objective_function, X, y):
        """Run algorithms sequentially, each using the best solution from the previous."""
        from mha_toolbox.toolbox import MHAToolbox
        toolbox = MHAToolbox()
        
        current_best_solution = None
        current_best_fitness = float('inf')
        full_convergence_curve = []
        
        # Divide iterations among algorithms
        iterations_per_alg = self.max_iterations // len(self.algorithms)
        if iterations_per_alg < 10:
            iterations_per_alg = 10 # Ensure at least a few iterations
        
        for i, alg_name in enumerate(self.algorithms):
            if self.verbose:
                print(f"\n🔄 Phase {i+1}/{len(self.algorithms)}: Running {alg_name} for {iterations_per_alg} iterations.")
            
            try:
                optimizer = toolbox.get_optimizer(
                    alg_name,
                    population_size=self.population_size,
                    max_iterations=iterations_per_alg,
                    lower_bound=self.lower_bound,
                    upper_bound=self.upper_bound,
                    dimensions=self.dimensions,
                    verbose=False,
                    **self.extra_params
                )
                
                # Seed the population of the next algorithm with the best solution from the previous one
                if current_best_solution is not None:
                    optimizer.seed_solution = current_best_solution
                
                # Run optimization for this phase
                alg_start_time = time.time()
                best_sol, best_fit, convergence = optimizer._optimize(objective_function, X=X, y=y)
                alg_exec_time = time.time() - alg_start_time
                
                # Create and store the model for this individual algorithm
                alg_model = optimizer._create_model(
                    best_sol, best_fit, convergence, alg_exec_time, X, y
                )
                self.individual_models.append(alg_model)
                
                # Update overall best solution
                current_best_solution = best_sol
                current_best_fitness = best_fit
                
                # Append to the full convergence curve
                full_convergence_curve.extend(convergence)
                
                if self.verbose:
                    print(f"   ✅ Phase complete. Best fitness so far: {current_best_fitness:.6f}")
                    
            except Exception as e:
                if self.verbose:
                    print(f"   ❌ Algorithm {alg_name} failed: {e}")
                # If one algorithm fails, we stop the sequence
                if not self.individual_models:
                    raise RuntimeError("Hybrid optimization failed as the first algorithm did not run.") from e
                break
        
        return current_best_solution, current_best_fitness, full_convergence_curve

    def _create_model(self, best_solution, best_fitness, convergence_curve, 
                      execution_time, X=None, y=None):
        """Create and return the HybridOptimizationModel object."""
        return HybridOptimizationModel(
            individual_models=self.individual_models,
            algorithm_name=self.algorithm_name,
            best_solution=best_solution,
            best_fitness=best_fitness,
            convergence_curve=convergence_curve,
            execution_time=execution_time,
            parameters=self.get_params(),
            problem_type=getattr(self, 'problem_type', 'unknown'),
            X_data=X,
            y_data=y
        )

def create_hybrid_optimizer(algorithms, *args, mode='sequential', **kwargs):
    """
    Factory function to create a hybrid optimizer.
    
    Parameters
    ----------
    algorithms : list
        List of 2-3 algorithm names to combine (e.g., ['PSO', 'GWO']).
    *args : tuple
        Positional arguments: population_size, max_iterations, dimensions
    mode : str
        The combination strategy. Currently, only 'sequential' is supported.
    **kwargs
        Additional parameters for the optimizer (e.g., population_size).
        
    Returns
    -------
    HybridOptimizer
        A configured hybrid optimizer instance.
        
    Example
    --------
    >>> # Flexible usage patterns:
    >>> hybrid = create_hybrid_optimizer(['PSO', 'GWO'], 50, 200)  # pop_size=50, max_iter=200
    >>> hybrid = create_hybrid_optimizer(['PSO', 'GWO'], population_size=50, max_iterations=200)
    """
    return HybridOptimizer(algorithms, *args, combination_mode=mode, **kwargs)
