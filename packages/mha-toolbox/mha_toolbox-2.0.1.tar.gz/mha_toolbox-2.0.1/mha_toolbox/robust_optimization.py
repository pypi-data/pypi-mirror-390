"""
Enhanced optimization utilities for handling large datasets and preventing timeouts
"""

import numpy as np
import time
import signal
import multiprocessing as mp
from functools import partial
from typing import Optional, Callable, Tuple, Union
import warnings

class TimeoutHandler:
    """Handle timeouts gracefully during optimization"""
    
    def __init__(self, timeout_seconds: Optional[float] = None):
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.original_handler = None
    
    def __enter__(self):
        if self.timeout_seconds is not None:
            self.start_time = time.time()
            # Set up timeout handler for Unix systems
            if hasattr(signal, 'SIGALRM'):
                self.original_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(int(self.timeout_seconds))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timeout_seconds is not None and hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Cancel the alarm
            if self.original_handler is not None:
                signal.signal(signal.SIGALRM, self.original_handler)
    
    def _timeout_handler(self, signum, frame):
        raise TimeoutError(f"Optimization timed out after {self.timeout_seconds} seconds")
    
    def check_timeout(self) -> bool:
        """Check if timeout has been exceeded (for manual checking)"""
        if self.timeout_seconds is not None and self.start_time is not None:
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout_seconds:
                return True
        return False

class LargeDatasetOptimizer:
    """Optimizations for handling large datasets efficiently"""
    
    @staticmethod
    def chunk_dataset(X: np.ndarray, y: np.ndarray, chunk_size: int = 10000) -> list:
        """Split large dataset into manageable chunks"""
        n_samples = len(X)
        chunks = []
        
        for i in range(0, n_samples, chunk_size):
            end_idx = min(i + chunk_size, n_samples)
            chunks.append((X[i:end_idx], y[i:end_idx]))
        
        return chunks
    
    @staticmethod
    def adaptive_batch_size(n_samples: int, n_features: int = None, memory_limit_gb: float = 2.0) -> int:
        """Calculate optimal batch size based on dataset size and memory"""
        # Estimate memory usage per sample (assuming 8 bytes per feature)
        features = n_features or 100  # Default assumption if not provided
        bytes_per_sample = features * 8
        samples_per_gb = (1024**3) / bytes_per_sample
        max_samples = int(memory_limit_gb * samples_per_gb)
        
        # Use smaller chunks for very large datasets
        if n_samples > 1000000:  # 1M+ samples
            return min(max_samples, 50000)
        elif n_samples > 100000:  # 100K+ samples
            return min(max_samples, 20000)
        else:
            return min(max_samples, n_samples)
    
    @staticmethod
    def parallel_fitness_evaluation(
        population: np.ndarray, 
        fitness_func: Callable,
        n_jobs: int = -1,
        timeout_per_eval: Optional[float] = None
    ) -> np.ndarray:
        """Evaluate fitness in parallel with optional timeout per evaluation"""
        
        if n_jobs == -1:
            n_jobs = min(mp.cpu_count(), len(population))
        elif n_jobs == 1:
            # Sequential evaluation with timeout
            fitness_values = []
            for individual in population:
                try:
                    with TimeoutHandler(timeout_per_eval):
                        fitness = fitness_func(individual)
                        fitness_values.append(fitness)
                except TimeoutError:
                    warnings.warn(f"Fitness evaluation timed out, using default value")
                    fitness_values.append(float('inf'))  # Worst possible fitness
            return np.array(fitness_values)
        
        # Parallel evaluation
        try:
            with mp.Pool(n_jobs) as pool:
                if timeout_per_eval:
                    # Apply timeout to each evaluation
                    fitness_values = pool.map_async(
                        partial(LargeDatasetOptimizer._safe_fitness_eval, 
                               fitness_func, timeout_per_eval),
                        population
                    ).get(timeout=timeout_per_eval * len(population))
                else:
                    fitness_values = pool.map(fitness_func, population)
            return np.array(fitness_values)
        except Exception as e:
            warnings.warn(f"Parallel evaluation failed: {e}. Falling back to sequential.")
            return LargeDatasetOptimizer.parallel_fitness_evaluation(
                population, fitness_func, n_jobs=1, timeout_per_eval=timeout_per_eval
            )
    
    @staticmethod
    def _safe_fitness_eval(fitness_func: Callable, timeout: Optional[float], individual) -> float:
        """Safely evaluate fitness with timeout"""
        try:
            with TimeoutHandler(timeout):
                return fitness_func(individual)
        except TimeoutError:
            return float('inf')  # Worst possible fitness for timed out evaluations

class MemoryEfficientOperations:
    """Memory-efficient operations for large-scale optimization"""
    
    @staticmethod
    def streaming_statistics(data_stream, window_size: int = 1000):
        """Calculate streaming statistics without loading all data into memory"""
        count = 0
        mean = 0.0
        m2 = 0.0  # Sum of squares of differences from mean
        
        for chunk in data_stream:
            if hasattr(chunk, '__iter__'):
                for value in chunk:
                    count += 1
                    delta = value - mean
                    mean += delta / count
                    delta2 = value - mean
                    m2 += delta * delta2
            else:
                count += 1
                delta = chunk - mean
                mean += delta / count
                delta2 = chunk - mean
                m2 += delta * delta2
        
        variance = m2 / count if count > 0 else 0
        return {
            'mean': mean,
            'variance': variance,
            'std': np.sqrt(variance),
            'count': count
        }
    
    @staticmethod
    def efficient_convergence_tracking(fitness_history: list, check_interval: int = 10):
        """Memory-efficient convergence tracking"""
        if len(fitness_history) < check_interval:
            return False
        
        # Only check convergence every check_interval iterations
        if len(fitness_history) % check_interval != 0:
            return False
        
        # Check last few values for convergence
        recent_values = fitness_history[-check_interval:]
        improvement = abs(recent_values[0] - recent_values[-1])
        relative_improvement = improvement / (abs(recent_values[0]) + 1e-10)
        
        return relative_improvement < 1e-6  # Converged if improvement < 0.0001%

def optimize_for_large_dataset(
    optimizer_class,
    X: np.ndarray,
    y: np.ndarray,
    algorithm_params: dict = None,
    max_time_seconds: Optional[float] = None,
    chunk_size: Optional[int] = None,
    n_jobs: int = -1,
    memory_limit_gb: float = 2.0
):
    """
    Optimize algorithm parameters for large dataset handling
    
    Args:
        optimizer_class: The optimizer class to use
        X, y: Dataset
        algorithm_params: Parameters for the algorithm
        max_time_seconds: Maximum time allowed for optimization
        chunk_size: Size of data chunks (auto-calculated if None)
        n_jobs: Number of parallel jobs (-1 for all CPUs)
        memory_limit_gb: Memory limit in GB
    
    Returns:
        Optimized result with timeout and memory handling
    """
    algorithm_params = algorithm_params or {}
    
    # Auto-calculate chunk size if not provided
    if chunk_size is None:
        n_features = X.shape[1] if hasattr(X, 'shape') and len(X.shape) > 1 else 100
        chunk_size = LargeDatasetOptimizer.adaptive_batch_size(len(X), n_features, memory_limit_gb)
    
    # Adjust algorithm parameters for large datasets
    optimized_params = algorithm_params.copy()
    
    # Reduce population size for very large datasets to save memory
    if len(X) > 100000 and 'population_size' not in optimized_params:
        optimized_params['population_size'] = min(50, optimized_params.get('population_size', 30))
    
    # Reduce iterations if timeout is specified
    if max_time_seconds is not None and 'max_iterations' not in optimized_params:
        # Estimate iterations based on time budget
        estimated_time_per_iter = 0.1 * len(X) / 10000  # Rough estimate
        max_iters = max(10, int(max_time_seconds / estimated_time_per_iter * 0.8))  # 80% of time budget
        optimized_params['max_iterations'] = min(max_iters, optimized_params.get('max_iterations', 100))
    
    # Initialize optimizer
    optimizer = optimizer_class(**optimized_params)
    
    # Run optimization with timeout handling
    try:
        with TimeoutHandler(max_time_seconds):
            # For feature selection, use efficient batch processing
            if hasattr(optimizer, 'fit'):
                result = optimizer.fit(X, y)
            else:
                # For function optimization
                result = optimizer.optimize()
            
            return result
    
    except TimeoutError:
        warnings.warn(f"Optimization timed out after {max_time_seconds} seconds. Returning best result found so far.")
        # Return best result found so far
        if hasattr(optimizer, 'best_fitness_'):
            return optimizer
        else:
            raise TimeoutError("Optimization timed out and no partial results available")

class RobustOptimizer:
    """Wrapper for robust optimization with error handling and recovery"""
    
    def __init__(self, optimizer_class, **default_params):
        self.optimizer_class = optimizer_class
        self.default_params = default_params
    
    def optimize_with_fallback(self, X, y, primary_params=None, fallback_params=None):
        """Try optimization with primary parameters, fallback on failure"""
        primary_params = primary_params or {}
        fallback_params = fallback_params or self.default_params
        
        # Try primary optimization
        try:
            combined_params = {**self.default_params, **primary_params}
            return optimize_for_large_dataset(
                self.optimizer_class, X, y, combined_params
            )
        except Exception as e:
            warnings.warn(f"Primary optimization failed: {e}. Trying fallback parameters.")
            
            # Try fallback optimization
            try:
                combined_params = {**self.default_params, **fallback_params}
                # Use more conservative parameters for fallback
                combined_params.update({
                    'population_size': min(20, combined_params.get('population_size', 20)),
                    'max_iterations': min(50, combined_params.get('max_iterations', 50))
                })
                return optimize_for_large_dataset(
                    self.optimizer_class, X, y, combined_params
                )
            except Exception as e2:
                raise RuntimeError(f"Both primary and fallback optimization failed. Primary: {e}, Fallback: {e2}")