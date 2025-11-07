"""
Enhanced visualization utilities for the MHA Toolbox.

This module provides comprehensive visualization functions for comparing algorithms,
plotting convergence curves, and analyzing optimization results.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Union, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

def plot_comparison(results: Union[Dict, List], 
                   title: str = "Algorithm Comparison",
                   save_path: Optional[str] = None,
                   show_convergence: bool = True,
                   show_statistics: bool = True):
    """
    Create comprehensive comparison plots for multiple optimization results.
    
    Parameters
    ----------
    results : dict or list
        Results from compare() function or list of OptimizationModel objects
    title : str, default="Algorithm Comparison"
        Main title for the plots
    save_path : str, optional
        Path to save the plot
    show_convergence : bool, default=True
        Whether to show convergence curves
    show_statistics : bool, default=True
        Whether to show statistical comparison
    """
    
    # Handle different input formats
    if isinstance(results, list):
        # Convert list to dict
        results_dict = {}
        for i, result in enumerate(results):
            if hasattr(result, 'algorithm_name'):
                results_dict[result.algorithm_name] = result
            else:
                results_dict[f'Algorithm_{i+1}'] = result
        results = results_dict
    
    n_algorithms = len(results)
    
    # Create subplot layout
    if show_convergence and show_statistics:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
    elif show_convergence or show_statistics:
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    else:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        axes = [ax]
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Colors for algorithms
    colors = plt.cm.Set3(np.linspace(0, 1, n_algorithms))
    
    # Plot 1: Convergence curves
    if show_convergence:
        ax = axes[0]
        for i, (alg_name, result) in enumerate(results.items()):
            if hasattr(result, 'convergence_curve'):
                ax.plot(result.convergence_curve, label=alg_name, 
                       color=colors[i], linewidth=2)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Best Fitness')
        ax.set_title('Convergence Curves')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
    
    # Plot 2: Final fitness comparison
    if len(axes) > 1:
        ax = axes[1]
        algorithm_names = list(results.keys())
        fitness_values = [result.best_fitness for result in results.values()]
        
        bars = ax.bar(algorithm_names, fitness_values, color=colors)
        ax.set_ylabel('Best Fitness')
        ax.set_title('Final Fitness Comparison')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, fitness_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.4f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
    
    plt.show()

def plot_convergence_multi(results: Union[Dict, List], 
                          title: str = "Convergence Comparison",
                          save_path: Optional[str] = None,
                          log_scale: bool = True):
    """
    Plot convergence curves for multiple algorithms.
    """
    
    if isinstance(results, list):
        results_dict = {}
        for i, result in enumerate(results):
            name = getattr(result, 'algorithm_name', f'Algorithm_{i+1}')
            results_dict[name] = result
        results = results_dict
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
    
    for i, (alg_name, result) in enumerate(results.items()):
        if hasattr(result, 'convergence_curve'):
            plt.plot(result.convergence_curve, label=alg_name, 
                    color=colors[i], linewidth=2)
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Fitness')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if log_scale:
        plt.yscale('log')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def plot_algorithm_comparison(results: Dict, 
                            title: str = "Algorithm Performance",
                            save_path: Optional[str] = None):
    """
    Create a performance comparison chart.
    """
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    algorithm_names = list(results.keys())
    colors = plt.cm.Set3(np.linspace(0, 1, len(algorithm_names)))
    
    # Fitness comparison
    ax1 = axes[0]
    fitness_values = [result.best_fitness for result in results.values()]
    bars1 = ax1.bar(algorithm_names, fitness_values, color=colors)
    ax1.set_ylabel('Best Fitness')
    ax1.set_title('Best Fitness')
    ax1.tick_params(axis='x', rotation=45)
    
    # Execution time comparison
    ax2 = axes[1]
    execution_times = [getattr(result, 'execution_time', 0) for result in results.values()]
    bars2 = ax2.bar(algorithm_names, execution_times, color=colors)
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Execution Time')
    ax2.tick_params(axis='x', rotation=45)
    
    # Convergence comparison
    ax3 = axes[2]
    for i, (alg_name, result) in enumerate(results.items()):
        if hasattr(result, 'convergence_curve'):
            ax3.plot(result.convergence_curve, label=alg_name, 
                    color=colors[i], linewidth=2)
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Best Fitness')
    ax3.set_title('Convergence')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# Convenience aliases
plot_convergence = plot_convergence_multi