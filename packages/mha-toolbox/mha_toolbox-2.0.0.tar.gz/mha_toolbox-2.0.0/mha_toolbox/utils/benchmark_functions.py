"""
Benchmark functions for testing optimization algorithms.

This module provides a collection of well-known benchmark functions
used in optimization research.
"""

import numpy as np
from typing import Callable, Dict, Any

def get_benchmark_function(function_name: str) -> Callable:
    """
    Get a benchmark function by name.
    
    Parameters
    ----------
    function_name : str
        Name of the benchmark function
        
    Returns
    -------
    callable
        Benchmark function
    """
    
    functions = {
        'sphere': sphere,
        'rastrigin': rastrigin,
        'rosenbrock': rosenbrock,
        'ackley': ackley,
        'griewank': griewank,
        'schwefel': schwefel,
        'levy': levy,
        'zakharov': zakharov,
        'dixon_price': dixon_price,
        'sum_squares': sum_squares
    }
    
    if function_name not in functions:
        available = ', '.join(functions.keys())
        raise ValueError(f"Function '{function_name}' not available. Choose from: {available}")
    
    return functions[function_name]

def list_benchmark_functions() -> list:
    """
    List all available benchmark functions.
    
    Returns
    -------
    list
        List of function names
    """
    return [
        'sphere', 'rastrigin', 'rosenbrock', 'ackley', 
        'griewank', 'schwefel', 'levy', 'zakharov', 
        'dixon_price', 'sum_squares'
    ]

def get_function_info(function_name: str) -> Dict[str, Any]:
    """
    Get information about a benchmark function.
    
    Parameters
    ----------
    function_name : str
        Name of the function
        
    Returns
    -------
    dict
        Function information including bounds, global minimum, etc.
    """
    
    info = {
        'sphere': {
            'description': 'Sphere function: f(x) = sum(x_i^2)',
            'bounds': (-100, 100),
            'global_minimum': 0.0,
            'global_optimum': 'zeros vector',
            'properties': ['unimodal', 'separable', 'convex']
        },
        'rastrigin': {
            'description': 'Rastrigin function: highly multimodal',
            'bounds': (-5.12, 5.12),
            'global_minimum': 0.0,
            'global_optimum': 'zeros vector',
            'properties': ['multimodal', 'separable', 'scalable']
        },
        'rosenbrock': {
            'description': 'Rosenbrock function: valley-shaped, non-convex',
            'bounds': (-30, 30),
            'global_minimum': 0.0,
            'global_optimum': 'ones vector',
            'properties': ['unimodal', 'non-separable', 'non-convex']
        },
        'ackley': {
            'description': 'Ackley function: highly multimodal',
            'bounds': (-32.768, 32.768),
            'global_minimum': 0.0,
            'global_optimum': 'zeros vector',
            'properties': ['multimodal', 'non-separable']
        },
        'griewank': {
            'description': 'Griewank function: multimodal with product term',
            'bounds': (-600, 600),
            'global_minimum': 0.0,
            'global_optimum': 'zeros vector',
            'properties': ['multimodal', 'non-separable']
        },
        'schwefel': {
            'description': 'Schwefel function: multimodal with deep local minima',
            'bounds': (-500, 500),
            'global_minimum': 0.0,
            'global_optimum': '[420.9687, 420.9687, ...]',
            'properties': ['multimodal', 'separable', 'deceptive']
        }
    }
    
    return info.get(function_name, {'description': 'Information not available'})

# Benchmark function implementations

def sphere(x):
    """
    Sphere function: f(x) = sum(x_i^2)
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    return np.sum(x**2)

def rastrigin(x):
    """
    Rastrigin function: highly multimodal
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    A = 10
    n = len(x)
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))

def rosenbrock(x):
    """
    Rosenbrock function: valley-shaped
    Global minimum: 0 at x = [1, 1, ..., 1]
    """
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

def ackley(x):
    """
    Ackley function: highly multimodal
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    a, b, c = 20, 0.2, 2 * np.pi
    n = len(x)
    
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(c * x))
    
    return -a * np.exp(-b * np.sqrt(sum1 / n)) - np.exp(sum2 / n) + a + np.e

def griewank(x):
    """
    Griewank function: multimodal
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    sum_term = np.sum(x**2) / 4000
    prod_term = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return 1 + sum_term - prod_term

def schwefel(x):
    """
    Schwefel function: multimodal, deceptive
    Global minimum: 0 at x = [420.9687, 420.9687, ..., 420.9687]
    """
    return 418.9829 * len(x) - np.sum(x * np.sin(np.sqrt(np.abs(x))))

def levy(x):
    """
    Levy function: multimodal
    Global minimum: 0 at x = [1, 1, ..., 1]
    """
    w = 1 + (x - 1) / 4
    
    term1 = np.sin(np.pi * w[0])**2
    term2 = np.sum((w[:-1] - 1)**2 * (1 + 10 * np.sin(np.pi * w[:-1] + 1)**2))
    term3 = (w[-1] - 1)**2 * (1 + np.sin(2 * np.pi * w[-1])**2)
    
    return term1 + term2 + term3

def zakharov(x):
    """
    Zakharov function: unimodal
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    sum1 = np.sum(x**2)
    sum2 = np.sum(0.5 * np.arange(1, len(x) + 1) * x)
    return sum1 + sum2**2 + sum2**4

def dixon_price(x):
    """
    Dixon-Price function: unimodal
    Global minimum: 0 at x_i = 2^(-(2^i-2)/2^i)
    """
    n = len(x)
    term1 = (x[0] - 1)**2
    term2 = np.sum(np.arange(2, n + 1) * (2 * x[1:]**2 - x[:-1])**2)
    return term1 + term2

def sum_squares(x):
    """
    Sum of Squares function: unimodal
    Global minimum: 0 at x = [0, 0, ..., 0]
    """
    return np.sum(np.arange(1, len(x) + 1) * x**2)

# Multi-objective benchmark functions

def zdt1(x):
    """
    ZDT1 multi-objective function
    """
    f1 = x[0]
    g = 1 + 9 * np.sum(x[1:]) / (len(x) - 1)
    h = 1 - np.sqrt(f1 / g)
    f2 = g * h
    return [f1, f2]

def zdt2(x):
    """
    ZDT2 multi-objective function
    """
    f1 = x[0]
    g = 1 + 9 * np.sum(x[1:]) / (len(x) - 1)
    h = 1 - (f1 / g)**2
    f2 = g * h
    return [f1, f2]

# Constrained benchmark functions

def constrained_sphere(x):
    """
    Constrained sphere function with constraint g(x) = sum(x) - 1 <= 0
    """
    objective = np.sum(x**2)
    constraint = np.sum(x) - 1
    
    # Penalty method for constraint handling
    penalty = max(0, constraint)**2 * 1000
    
    return objective + penalty

def create_shifted_function(base_function, shift_vector):
    """
    Create a shifted version of a benchmark function.
    
    Parameters
    ----------
    base_function : callable
        Original benchmark function
    shift_vector : array-like
        Vector to shift the function by
        
    Returns
    -------
    callable
        Shifted function
    """
    def shifted_function(x):
        return base_function(x - shift_vector)
    
    return shifted_function

def create_rotated_function(base_function, rotation_matrix):
    """
    Create a rotated version of a benchmark function.
    
    Parameters
    ----------
    base_function : callable
        Original benchmark function
    rotation_matrix : array-like
        Rotation matrix
        
    Returns
    -------
    callable
        Rotated function
    """
    def rotated_function(x):
        return base_function(rotation_matrix @ x)
    
    return rotated_function