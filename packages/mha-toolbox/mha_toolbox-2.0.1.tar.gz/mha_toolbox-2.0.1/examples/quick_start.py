"""
MHA Toolbox - Quick Start Examples
==================================

This script demonstrates how to use the MHA Toolbox library with various algorithms
and visualizations. Run this after installing: pip install mha-toolbox
"""

import numpy as np
import matplotlib.pyplot as plt
from mha_toolbox.algorithms import PSO, GWO, WOA, GA, DE

print("="*70)
print("MHA Toolbox - Quick Start Examples")
print("="*70)

# Example 1: Simple Optimization
print("\n[Example 1] Simple Optimization with PSO")
print("-" * 50)

def sphere_function(x):
    """Simple sphere function: f(x) = sum(x^2)"""
    return np.sum(x**2)

bounds = np.array([[-10, 10]] * 5)  # 5 dimensions
pso = PSO(objective_func=sphere_function, bounds=bounds, n_particles=30, max_iter=100)

print("Running PSO optimization...")
best_position, best_fitness = pso.optimize()

print(f"✓ Optimization complete!")
print(f"  Best fitness: {best_fitness:.6e}")
print(f"  Best position: {best_position}")

# Example 2: Compare Multiple Algorithms
print("\n[Example 2] Algorithm Comparison")
print("-" * 50)

def rastrigin_function(x):
    """Rastrigin function - multimodal benchmark"""
    A = 10
    n = len(x)
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))

bounds = np.array([[-5.12, 5.12]] * 10)

algorithms = {
    'PSO': PSO(rastrigin_function, bounds, n_particles=40, max_iter=150),
    'GWO': GWO(rastrigin_function, bounds, n_wolves=40, max_iter=150),
    'WOA': WOA(rastrigin_function, bounds, n_whales=40, max_iter=150),
    'GA': GA(rastrigin_function, bounds, pop_size=40, max_iter=150),
    'DE': DE(rastrigin_function, bounds, pop_size=40, max_iter=150)
}

results = {}
print("Running 5 algorithms on Rastrigin function...")

for name, algo in algorithms.items():
    print(f"  Running {name}...", end=" ")
    best_pos, best_fit = algo.optimize()
    results[name] = best_fit
    print(f"fitness = {best_fit:.6f}")

best_algorithm = min(results, key=results.get)
print(f"\n✓ Best algorithm: {best_algorithm} with fitness {results[best_algorithm]:.6f}")

# Example 3: Visualization
print("\n[Example 3] Convergence Visualization")
print("-" * 50)

def ackley_function(x):
    """Ackley function - complex multimodal benchmark"""
    a, b, c = 20, 0.2, 2 * np.pi
    d = len(x)
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(c * x))
    return -a * np.exp(-b * np.sqrt(sum1/d)) - np.exp(sum2/d) + a + np.e

bounds = np.array([[-5, 5]] * 10)

# Track convergence
print("Running algorithms with tracking...")
convergence_data = {}

for algo_name in ['PSO', 'GWO', 'WOA']:
    if algo_name == 'PSO':
        algo = PSO(ackley_function, bounds, n_particles=50, max_iter=100)
    elif algo_name == 'GWO':
        algo = GWO(ackley_function, bounds, n_wolves=50, max_iter=100)
    else:  # WOA
        algo = WOA(ackley_function, bounds, n_whales=50, max_iter=100)
    
    best_pos, best_fit = algo.optimize()
    
    # Store convergence history if available
    if hasattr(algo, 'fitness_history'):
        convergence_data[algo_name] = algo.fitness_history
        print(f"  {algo_name}: final fitness = {best_fit:.6f}")

# Create visualization
print("\n✓ Creating convergence plot...")
plt.figure(figsize=(12, 6))

for algo_name, history in convergence_data.items():
    plt.plot(history, label=algo_name, linewidth=2)

plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Best Fitness', fontsize=12)
plt.title('Algorithm Convergence Comparison on Ackley Function', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.yscale('log')  # Log scale for better visualization
plt.tight_layout()

# Save plot
plt.savefig('convergence_comparison.png', dpi=150, bbox_inches='tight')
print("  Plot saved as 'convergence_comparison.png'")
plt.show()

# Example 4: Hybrid Algorithms
print("\n[Example 4] Using Hybrid Algorithms")
print("-" * 50)

try:
    from mha_toolbox.algorithms.hybrid import GWO_PSO_Hybrid, WOA_GA_Hybrid
    
    print("Running hybrid algorithms...")
    
    # GWO-PSO Hybrid
    hybrid1 = GWO_PSO_Hybrid(objective_func=sphere_function, bounds=bounds, n_agents=40, max_iter=100)
    h1_pos, h1_fit = hybrid1.optimize()
    print(f"  GWO-PSO Hybrid: fitness = {h1_fit:.6e}")
    
    # WOA-GA Hybrid  
    hybrid2 = WOA_GA_Hybrid(objective_func=sphere_function, bounds=bounds, n_agents=40, max_iter=100)
    h2_pos, h2_fit = hybrid2.optimize()
    print(f"  WOA-GA Hybrid: fitness = {h2_fit:.6e}")
    
    print("\n✓ Hybrid algorithms work great for complex problems!")
    
except ImportError as e:
    print(f"  Note: Hybrid algorithms may need different initialization")
    print(f"  Check USER_GUIDE.md for details")

# Summary
print("\n" + "="*70)
print("Summary")
print("="*70)
print(f"""
✓ Example 1: PSO optimization completed
✓ Example 2: Compared 5 algorithms
✓ Example 3: Generated convergence plot
✓ Example 4: Tested hybrid algorithms

Next Steps:
1. Open 'convergence_comparison.png' to see the visualization
2. Try the web interface: run 'mha-web' or 'streamlit run mha_toolbox_pro_ultimate.py'
3. Read USER_GUIDE.md for more examples
4. Experiment with different benchmark functions and algorithms

Available algorithms: 95+ individual + 9 hybrids = 104 total!

Popular algorithms to try:
  - PSO, GWO, WOA, GA, DE (shown above)
  - SMA, SSA, FA, BA, ACO
  - GSK, LCA, WHO, SAR, and many more!

Happy Optimizing! 🚀
""")
print("="*70)
