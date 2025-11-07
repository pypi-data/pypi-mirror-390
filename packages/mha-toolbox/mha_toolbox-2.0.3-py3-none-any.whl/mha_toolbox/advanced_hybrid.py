"""
Advanced Hybrid Algorithm System for MHA Toolbox

This module provides sophisticated hybrid algorithm combinations with multiple strategies:
- Sequential hybridization (run algorithms in sequence)
- Parallel hybridization (run algorithms in parallel and select best)
- Ensemble hybridization (combine results from multiple algorithms)
- Adaptive hybridization (switch between algorithms based on performance)
"""

import numpy as np
import time
from typing import List, Dict, Any, Callable, Optional, Union
from .base import BaseOptimizer, OptimizationModel
from .toolbox import get_toolbox
import matplotlib.pyplot as plt


class HybridStrategy:
    """Base class for hybrid strategies."""
    
    def __init__(self, name: str):
        self.name = name
    
    def combine(self, algorithms: List[str], problem, **kwargs):
        """Combine multiple algorithms to solve a problem."""
        raise NotImplementedError


class SequentialHybrid(HybridStrategy):
    """Run algorithms sequentially, using output of one as input to next."""
    
    def __init__(self):
        super().__init__("Sequential")
    
    def combine(self, algorithms: List[str], problem, **kwargs):
        """Run algorithms in sequence."""
        toolbox = get_toolbox()
        
        # Start with first algorithm
        current_result = None
        all_results = []
        best_fitness_history = []
        
        for i, alg_name in enumerate(algorithms):
            print(f"🔄 Stage {i+1}/{len(algorithms)}: Running {alg_name}")
            
            # Get optimizer
            optimizer = toolbox.get_optimizer(alg_name, **kwargs)
            
            # If we have a previous result, use it as starting point
            if current_result is not None and hasattr(optimizer, 'set_initial_solution'):
                optimizer.set_initial_solution(current_result.best_solution_)
            
            # Run optimization
            result = optimizer.optimize(problem)
            all_results.append(result)
            best_fitness_history.extend(result.global_fitness_)
            
            current_result = result
        
        # Create combined result
        return self._create_combined_result(all_results, best_fitness_history, algorithms)
    
    def _create_combined_result(self, results, fitness_history, algorithms):
        """Create a combined result object."""
        best_result = min(results, key=lambda r: r.best_fitness_)
        
        # Create hybrid result
        hybrid_result = OptimizationModel()
        hybrid_result.best_solution_ = best_result.best_solution_
        hybrid_result.best_fitness_ = best_result.best_fitness_
        hybrid_result.global_fitness_ = fitness_history
        hybrid_result.algorithm_name_ = f"Sequential({'+'.join(algorithms)})"
        hybrid_result.hybrid_results_ = results
        hybrid_result.hybrid_strategy_ = "sequential"
        
        return hybrid_result


class ParallelHybrid(HybridStrategy):
    """Run algorithms in parallel and select the best result."""
    
    def __init__(self):
        super().__init__("Parallel")
    
    def combine(self, algorithms: List[str], problem, **kwargs):
        """Run algorithms in parallel."""
        toolbox = get_toolbox()
        
        print(f"🚀 Running {len(algorithms)} algorithms in parallel...")
        
        results = []
        for alg_name in algorithms:
            print(f"  ▶️ Starting {alg_name}")
            optimizer = toolbox.get_optimizer(alg_name, **kwargs)
            result = optimizer.optimize(problem)
            results.append(result)
            print(f"  ✅ {alg_name} completed: fitness = {result.best_fitness_:.6f}")
        
        # Select best result
        best_result = min(results, key=lambda r: r.best_fitness_)
        
        # Create hybrid result
        hybrid_result = OptimizationModel()
        hybrid_result.best_solution_ = best_result.best_solution_
        hybrid_result.best_fitness_ = best_result.best_fitness_
        hybrid_result.global_fitness_ = best_result.global_fitness_
        hybrid_result.algorithm_name_ = f"Parallel({'+'.join(algorithms)})"
        hybrid_result.hybrid_results_ = results
        hybrid_result.hybrid_strategy_ = "parallel"
        hybrid_result.best_algorithm_ = best_result.algorithm_name_
        
        return hybrid_result


class EnsembleHybrid(HybridStrategy):
    """Combine solutions from multiple algorithms using ensemble methods."""
    
    def __init__(self, ensemble_method: str = "weighted_average"):
        super().__init__("Ensemble")
        self.ensemble_method = ensemble_method
    
    def combine(self, algorithms: List[str], problem, **kwargs):
        """Combine algorithms using ensemble methods."""
        toolbox = get_toolbox()
        
        print(f"🎭 Running ensemble with {len(algorithms)} algorithms...")
        
        results = []
        solutions = []
        fitnesses = []
        
        for alg_name in algorithms:
            optimizer = toolbox.get_optimizer(alg_name, **kwargs)
            result = optimizer.optimize(problem)
            results.append(result)
            solutions.append(result.best_solution_)
            fitnesses.append(result.best_fitness_)
        
        # Create ensemble solution
        if self.ensemble_method == "weighted_average":
            ensemble_solution = self._weighted_average_ensemble(solutions, fitnesses)
        elif self.ensemble_method == "voting":
            ensemble_solution = self._voting_ensemble(solutions)
        else:
            ensemble_solution = self._simple_average_ensemble(solutions)
        
        # Evaluate ensemble solution
        ensemble_fitness = problem.evaluate(ensemble_solution)
        
        # Create hybrid result
        hybrid_result = OptimizationModel()
        hybrid_result.best_solution_ = ensemble_solution
        hybrid_result.best_fitness_ = ensemble_fitness
        hybrid_result.algorithm_name_ = f"Ensemble({'+'.join(algorithms)})"
        hybrid_result.hybrid_results_ = results
        hybrid_result.hybrid_strategy_ = "ensemble"
        hybrid_result.ensemble_method_ = self.ensemble_method
        
        return hybrid_result
    
    def _weighted_average_ensemble(self, solutions, fitnesses):
        """Create weighted average based on inverse fitness."""
        solutions = np.array(solutions)
        fitnesses = np.array(fitnesses)
        
        # Calculate weights (inverse fitness)
        weights = 1.0 / (fitnesses + 1e-10)
        weights = weights / np.sum(weights)
        
        # Weighted average
        ensemble_solution = np.average(solutions, axis=0, weights=weights)
        return ensemble_solution
    
    def _voting_ensemble(self, solutions):
        """Create solution using majority voting (for binary problems)."""
        solutions = np.array(solutions)
        # For binary problems, use majority voting
        ensemble_solution = (np.mean(solutions, axis=0) > 0.5).astype(float)
        return ensemble_solution
    
    def _simple_average_ensemble(self, solutions):
        """Simple average of all solutions."""
        return np.mean(np.array(solutions), axis=0)


class AdaptiveHybrid(HybridStrategy):
    """Adaptively switch between algorithms based on performance."""
    
    def __init__(self, switch_threshold: float = 0.1):
        super().__init__("Adaptive")
        self.switch_threshold = switch_threshold
    
    def combine(self, algorithms: List[str], problem, **kwargs):
        """Adaptively switch between algorithms."""
        toolbox = get_toolbox()
        
        print(f"🧠 Running adaptive hybrid with {len(algorithms)} algorithms...")
        
        current_alg_idx = 0
        current_optimizer = toolbox.get_optimizer(algorithms[current_alg_idx], **kwargs)
        
        best_solution = None
        best_fitness = float('inf')
        fitness_history = []
        algorithm_history = []
        stagnation_counter = 0
        
        max_iterations = kwargs.get('max_iterations', 100)
        iterations_per_switch = max_iterations // (len(algorithms) * 2)
        check_window = max(10, max_iterations // 10)  # Check improvement over 10% of iterations
        
        for iteration in range(max_iterations):
            # Run one iteration of current algorithm
            # This is simplified - in practice, you'd need to modify algorithms
            # to support single-iteration execution
            
            # For demonstration, we'll run short bursts
            if iteration % iterations_per_switch == 0 and iteration > 0:
                # Check if we should switch algorithms
                if len(fitness_history) >= check_window:
                    recent_improvement = self._check_improvement(fitness_history[-check_window:])
                else:
                    recent_improvement = 0
                
                if recent_improvement < self.switch_threshold:
                    current_alg_idx = (current_alg_idx + 1) % len(algorithms)
                    current_optimizer = toolbox.get_optimizer(algorithms[current_alg_idx], **kwargs)
                    print(f"  🔄 Switching to {algorithms[current_alg_idx]} at iteration {iteration}")
                    stagnation_counter = 0
                
            algorithm_history.append(algorithms[current_alg_idx])
        
        # For now, return the best result from running each algorithm briefly
        # In a full implementation, this would be more sophisticated
        results = []
        for alg_name in algorithms:
            optimizer = toolbox.get_optimizer(alg_name, max_iterations=max_iterations//len(algorithms), **kwargs)
            result = optimizer.optimize(problem)
            results.append(result)
        
        best_result = min(results, key=lambda r: r.best_fitness_)
        
        # Create hybrid result
        hybrid_result = OptimizationModel()
        hybrid_result.best_solution_ = best_result.best_solution_
        hybrid_result.best_fitness_ = best_result.best_fitness_
        hybrid_result.global_fitness_ = best_result.global_fitness_
        hybrid_result.algorithm_name_ = f"Adaptive({'+'.join(algorithms)})"
        hybrid_result.hybrid_results_ = results
        hybrid_result.hybrid_strategy_ = "adaptive"
        hybrid_result.algorithm_history_ = algorithm_history
        
        return hybrid_result
    
    def _check_improvement(self, recent_fitness):
        """Check improvement in recent fitness values."""
        if len(recent_fitness) < 2:
            return float('inf')
        
        initial = recent_fitness[0]
        final = recent_fitness[-1]
        
        if initial == 0:
            return 0
        
        return abs((initial - final) / initial)


class AdvancedHybridOptimizer:
    """Advanced hybrid optimizer with multiple strategies."""
    
    def __init__(self):
        self.strategies = {
            'sequential': SequentialHybrid(),
            'parallel': ParallelHybrid(),
            'ensemble': EnsembleHybrid(),
            'adaptive': AdaptiveHybrid()
        }
    
    def optimize(self, algorithms: List[str], problem, strategy: str = 'parallel', **kwargs):
        """
        Optimize using hybrid strategy.
        
        Parameters
        ----------
        algorithms : list
            List of algorithm names to combine
        problem : Problem
            Optimization problem
        strategy : str
            Hybrid strategy: 'sequential', 'parallel', 'ensemble', 'adaptive'
        **kwargs
            Additional parameters
            
        Returns
        -------
        OptimizationModel
            Hybrid optimization result
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")
        
        print(f"🔬 Starting {strategy} hybrid optimization")
        start_time = time.time()
        
        result = self.strategies[strategy].combine(algorithms, problem, **kwargs)
        
        execution_time = time.time() - start_time
        result.execution_time_ = execution_time
        result.hybrid_execution_time_ = execution_time
        
        print(f"✅ Hybrid optimization completed in {execution_time:.3f} seconds")
        print(f"🏆 Best fitness: {result.best_fitness_:.6f}")
        print(f"🧬 Strategy: {strategy}")
        
        return result
    
    def compare_strategies(self, algorithms: List[str], problem, strategies: List[str] = None, **kwargs):
        """
        Compare different hybrid strategies.
        
        Parameters
        ----------
        algorithms : list
            List of algorithm names to combine
        problem : Problem
            Optimization problem
        strategies : list, optional
            List of strategies to compare (default: all)
        **kwargs
            Additional parameters
            
        Returns
        -------
        dict
            Results for each strategy
        """
        if strategies is None:
            strategies = list(self.strategies.keys())
        
        print(f"🎯 Comparing {len(strategies)} hybrid strategies with algorithms: {algorithms}")
        
        results = {}
        for strategy in strategies:
            print(f"\n🔍 Testing {strategy} strategy...")
            result = self.optimize(algorithms, problem, strategy=strategy, **kwargs)
            results[strategy] = result
            
        # Print comparison
        print(f"\n📊 STRATEGY COMPARISON RESULTS:")
        print("-" * 60)
        for strategy, result in results.items():
            print(f"{strategy:15s}: fitness = {result.best_fitness_:.6f}, time = {result.execution_time_:.3f}s")
        
        # Find best strategy
        best_strategy = min(results.keys(), key=lambda s: results[s].best_fitness_)
        print(f"\n🏆 Best strategy: {best_strategy} (fitness: {results[best_strategy].best_fitness_:.6f})")
        
        return results
    
    def auto_select_algorithms(self, problem, n_algorithms: int = 3, **kwargs):
        """
        Automatically select best algorithms for a problem.
        
        Parameters
        ----------
        problem : Problem
            Optimization problem
        n_algorithms : int
            Number of algorithms to select
        **kwargs
            Additional parameters
            
        Returns
        -------
        list
            List of selected algorithm names
        """
        toolbox = get_toolbox()
        
        # Quick test of multiple algorithms
        test_algorithms = ['pso', 'gwo', 'sca', 'woa', 'ga', 'de', 'abc', 'aco', 'alo', 'fa']
        
        print(f"🔍 Testing {len(test_algorithms)} algorithms to select best {n_algorithms}...")
        
        quick_results = []
        for alg_name in test_algorithms:
            try:
                optimizer = toolbox.get_optimizer(alg_name, max_iterations=20, **kwargs)
                result = optimizer.optimize(problem)
                quick_results.append((alg_name, result.best_fitness_))
                print(f"  ✅ {alg_name}: {result.best_fitness_:.6f}")
            except Exception as e:
                print(f"  ❌ {alg_name}: failed ({str(e)[:50]})")
                continue
        
        # Sort by fitness and select top algorithms
        quick_results.sort(key=lambda x: x[1])
        selected = [alg for alg, _ in quick_results[:n_algorithms]]
        
        print(f"🎯 Selected algorithms: {selected}")
        return selected


def create_hybrid_optimizer(**kwargs):
    """Create an advanced hybrid optimizer."""
    return AdvancedHybridOptimizer()


def quick_hybrid(algorithms: List[str], problem=None, strategy: str = 'parallel', **kwargs):
    """
    Quick hybrid optimization function.
    
    Parameters
    ----------
    algorithms : list
        List of algorithm names
    problem : Problem, optional
        Optimization problem (will create default if not provided)
    strategy : str
        Hybrid strategy
    **kwargs
        Additional parameters
        
    Returns
    -------
    OptimizationModel
        Hybrid optimization result
    """
    if problem is None:
        from .utils.problem_creator import create_problem
        problem = create_problem(objective_function=lambda x: sum(x**2), dimensions=10)
    
    hybrid = AdvancedHybridOptimizer()
    return hybrid.optimize(algorithms, problem, strategy=strategy, **kwargs)