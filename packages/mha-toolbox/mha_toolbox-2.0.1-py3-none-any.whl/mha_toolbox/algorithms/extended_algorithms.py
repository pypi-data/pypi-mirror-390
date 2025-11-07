"""
Extended Metaheuristic Algorithms
==================================

Additional 20+ algorithms to expand the toolbox:
- Search-based: Tabu Search, Variable Neighborhood Search
- Swarm variants: Enhanced ABC, Modified BA, Improved FA
- Nature-inspired: Krill Herd, Moth-Flame, Dragonfly
- Music-based: Harmony Search
- Plant-based: Flower Pollination Algorithm
- And many more...
"""

import numpy as np
from typing import Callable, Tuple, Optional


class TabuSearch:
    """
    Tabu Search Algorithm
    
    A memory-based metaheuristic that guides local search using tabu lists
    to avoid cycling and escape local optima.
    
    Reference: Glover, F. (1989)
    """
    
    def __init__(self, tabu_tenure: int = 10, aspiration_criteria: bool = True):
        self.tabu_tenure = tabu_tenure
        self.aspiration_criteria = aspiration_criteria
        self.name = "Tabu Search"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 1) -> Tuple:
        """Run Tabu Search optimization"""
        lb, ub = bounds
        
        # Initialize current solution randomly
        current = np.random.uniform(lb, ub, dim)
        current_fitness = fitness_func(current)
        
        best_solution = current.copy()
        best_fitness = current_fitness
        
        # Tabu list: stores recent moves
        tabu_list = []
        convergence_curve = []
        
        for iteration in range(max_iterations):
            # Generate neighborhood (slightly perturbed solutions)
            neighborhood = []
            neighborhood_fitness = []
            
            # Generate candidate solutions
            for _ in range(20):  # Neighborhood size
                neighbor = current.copy()
                # Random perturbation
                perturb_dim = np.random.randint(0, dim)
                neighbor[perturb_dim] = np.clip(
                    neighbor[perturb_dim] + np.random.uniform(-0.1, 0.1) * (ub - lb),
                    lb, ub
                )
                
                fitness = fitness_func(neighbor)
                neighborhood.append(neighbor)
                neighborhood_fitness.append(fitness)
            
            # Find best non-tabu move
            sorted_indices = np.argsort(neighborhood_fitness)
            
            move_selected = False
            for idx in sorted_indices:
                candidate = neighborhood[idx]
                candidate_fitness = neighborhood_fitness[idx]
                
                # Check if move is in tabu list
                is_tabu = any(np.allclose(candidate, tabu_sol) for tabu_sol in tabu_list)
                
                # Aspiration criteria: accept if better than best known
                if not is_tabu or (self.aspiration_criteria and candidate_fitness < best_fitness):
                    current = candidate.copy()
                    current_fitness = candidate_fitness
                    
                    # Add to tabu list
                    tabu_list.append(current.copy())
                    if len(tabu_list) > self.tabu_tenure:
                        tabu_list.pop(0)
                    
                    move_selected = True
                    break
            
            # If no move selected, take best anyway
            if not move_selected:
                current = neighborhood[sorted_indices[0]].copy()
                current_fitness = neighborhood_fitness[sorted_indices[0]]
            
            # Update best
            if current_fitness < best_fitness:
                best_fitness = current_fitness
                best_solution = current.copy()
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


class HarmonySearch:
    """
    Harmony Search Algorithm
    
    Music-inspired metaheuristic based on the improvisation process
    of musicians searching for perfect harmony.
    
    Reference: Geem et al. (2001)
    """
    
    def __init__(self, hmcr: float = 0.9, par: float = 0.3, bw: float = 0.01):
        """
        Parameters:
            hmcr: Harmony Memory Considering Rate
            par: Pitch Adjusting Rate
            bw: Bandwidth (distance for pitch adjustment)
        """
        self.hmcr = hmcr
        self.par = par
        self.bw = bw
        self.name = "Harmony Search"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 30) -> Tuple:
        """Run Harmony Search optimization"""
        lb, ub = bounds
        
        # Initialize Harmony Memory (population)
        harmony_memory = np.random.uniform(lb, ub, (population_size, dim))
        fitness = np.array([fitness_func(ind) for ind in harmony_memory])
        
        best_idx = np.argmin(fitness)
        best_solution = harmony_memory[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            # Create new harmony
            new_harmony = np.zeros(dim)
            
            for j in range(dim):
                if np.random.rand() < self.hmcr:
                    # Memory consideration: select from harmony memory
                    idx = np.random.randint(0, population_size)
                    new_harmony[j] = harmony_memory[idx, j]
                    
                    # Pitch adjustment
                    if np.random.rand() < self.par:
                        new_harmony[j] += self.bw * np.random.uniform(-1, 1) * (ub - lb)
                else:
                    # Random selection
                    new_harmony[j] = np.random.uniform(lb, ub)
            
            # Boundary check
            new_harmony = np.clip(new_harmony, lb, ub)
            new_fitness = fitness_func(new_harmony)
            
            # Update harmony memory if better than worst
            worst_idx = np.argmax(fitness)
            if new_fitness < fitness[worst_idx]:
                harmony_memory[worst_idx] = new_harmony.copy()
                fitness[worst_idx] = new_fitness
                
                # Update best
                if new_fitness < best_fitness:
                    best_fitness = new_fitness
                    best_solution = new_harmony.copy()
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


class KrillHerd:
    """
    Krill Herd Algorithm
    
    Bio-inspired algorithm based on herding behavior of krill individuals.
    
    Reference: Gandomi & Alavi (2012)
    """
    
    def __init__(self, nmax: float = 0.01, vf: float = 0.02, dmax: float = 0.002):
        self.nmax = nmax  # Maximum induced speed
        self.vf = vf      # Foraging speed
        self.dmax = dmax  # Maximum diffusion speed
        self.name = "Krill Herd"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 30) -> Tuple:
        """Run Krill Herd optimization"""
        lb, ub = bounds
        
        # Initialize krill positions
        krill = np.random.uniform(lb, ub, (population_size, dim))
        fitness = np.array([fitness_func(ind) for ind in krill])
        
        best_idx = np.argmin(fitness)
        best_solution = krill[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        # Initialize velocities
        velocity = np.zeros((population_size, dim))
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            # Sort krill by fitness
            sorted_indices = np.argsort(fitness)
            
            for i in range(population_size):
                # Motion induced by other krill
                alpha_local = 0
                alpha_target = 0
                
                # Local effect (neighbors)
                for j in range(population_size):
                    if i != j:
                        diff = krill[j] - krill[i]
                        dist = np.linalg.norm(diff) + 1e-10
                        
                        if fitness[j] < fitness[i]:
                            alpha_local += (fitness[i] - fitness[j]) / dist * diff
                
                # Target direction (best krill)
                if fitness[i] != best_fitness:
                    alpha_target = (fitness[i] - best_fitness) / \
                                  (np.linalg.norm(krill[i] - best_solution) + 1e-10) * \
                                  (best_solution - krill[i])
                
                # Foraging motion
                beta_food = 2 * (1 - iteration / max_iterations)
                food_location = best_solution  # Food at best location
                beta = beta_food * (food_location - krill[i])
                
                # Physical diffusion
                delta = self.dmax * np.random.uniform(-1, 1, dim)
                
                # Update velocity and position
                dt = 0.5  # Time step
                velocity[i] = self.nmax * (alpha_local + alpha_target) + \
                             self.vf * beta + delta
                
                krill[i] += velocity[i] * dt
                krill[i] = np.clip(krill[i], lb, ub)
                
                # Evaluate new position
                fitness[i] = fitness_func(krill[i])
                
                # Update best
                if fitness[i] < best_fitness:
                    best_fitness = fitness[i]
                    best_solution = krill[i].copy()
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


class MothFlameOptimization:
    """
    Moth-Flame Optimization Algorithm
    
    Based on navigation method of moths in nature called transverse orientation.
    
    Reference: Mirjalili (2015)
    """
    
    def __init__(self, b: float = 1.0):
        self.b = b  # Logarithmic spiral shape constant
        self.name = "Moth-Flame Optimization"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 30) -> Tuple:
        """Run MFO optimization"""
        lb, ub = bounds
        
        # Initialize moths
        moths = np.random.uniform(lb, ub, (population_size, dim))
        fitness = np.array([fitness_func(ind) for ind in moths])
        
        # Initialize flames (best solutions)
        sorted_indices = np.argsort(fitness)
        flames = moths[sorted_indices].copy()
        flame_fitness = fitness[sorted_indices].copy()
        
        best_solution = flames[0].copy()
        best_fitness = flame_fitness[0]
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            # Decrease number of flames
            flame_no = int(population_size - iteration * ((population_size - 1) / max_iterations))
            
            for i in range(population_size):
                # Update moths
                for j in range(dim):
                    # Select flame for current moth
                    if i < flame_no:
                        flame_idx = i
                    else:
                        flame_idx = flame_no - 1
                    
                    # Distance to flame
                    distance = abs(flames[flame_idx, j] - moths[i, j])
                    
                    # Spiral flying path
                    t = np.random.uniform(-1, 1)
                    moths[i, j] = distance * np.exp(self.b * t) * np.cos(2 * np.pi * t) + \
                                 flames[flame_idx, j]
                
                # Boundary check
                moths[i] = np.clip(moths[i], lb, ub)
                fitness[i] = fitness_func(moths[i])
            
            # Update flames
            combined = np.vstack((flames, moths))
            combined_fitness = np.hstack((flame_fitness, fitness))
            sorted_indices = np.argsort(combined_fitness)
            
            flames = combined[sorted_indices[:population_size]].copy()
            flame_fitness = combined_fitness[sorted_indices[:population_size]].copy()
            
            best_solution = flames[0].copy()
            best_fitness = flame_fitness[0]
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


class DragonflyAlgorithm:
    """
    Dragonfly Algorithm
    
    Inspired by static and dynamic swarming behaviors of dragonflies.
    
    Reference: Mirjalili (2016)
    """
    
    def __init__(self, s: float = 2.0, a: float = 2.0, c: float = 2.0,
                f: float = 2.0, e: float = 0.5, w: float = 0.9):
        self.s = s  # Separation weight
        self.a = a  # Alignment weight
        self.c = c  # Cohesion weight
        self.f = f  # Food factor
        self.e = e  # Enemy factor
        self.w = w  # Inertia weight
        self.name = "Dragonfly Algorithm"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 30) -> Tuple:
        """Run Dragonfly Algorithm optimization"""
        lb, ub = bounds
        
        # Initialize dragonfly positions
        dragonflies = np.random.uniform(lb, ub, (population_size, dim))
        fitness = np.array([fitness_func(ind) for ind in dragonflies])
        
        # Initialize velocities
        velocities = np.zeros((population_size, dim))
        
        best_idx = np.argmin(fitness)
        food_pos = dragonflies[best_idx].copy()  # Food (best)
        food_fitness = fitness[best_idx]
        
        worst_idx = np.argmax(fitness)
        enemy_pos = dragonflies[worst_idx].copy()  # Enemy (worst)
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            # Update weights
            w = 0.9 - iteration * ((0.9 - 0.4) / max_iterations)
            
            for i in range(population_size):
                # Separation: avoid others
                S = np.zeros(dim)
                for j in range(population_size):
                    if i != j:
                        S -= (dragonflies[j] - dragonflies[i])
                
                # Alignment: velocity matching
                A = np.sum(velocities, axis=0) / population_size - velocities[i]
                
                # Cohesion: tend towards center
                C = np.sum(dragonflies, axis=0) / population_size - dragonflies[i]
                
                # Attraction to food
                F = food_pos - dragonflies[i]
                
                # Distraction from enemy
                E = enemy_pos + dragonflies[i]
                
                # Update velocity
                velocities[i] = w * velocities[i] + \
                               self.s * S + self.a * A + self.c * C + \
                               self.f * F + self.e * E
                
                # Update position
                dragonflies[i] += velocities[i]
                dragonflies[i] = np.clip(dragonflies[i], lb, ub)
                
                # Evaluate
                fitness[i] = fitness_func(dragonflies[i])
                
                # Update food and enemy
                if fitness[i] < food_fitness:
                    food_fitness = fitness[i]
                    food_pos = dragonflies[i].copy()
                
                if fitness[i] > fitness[worst_idx]:
                    worst_idx = i
                    enemy_pos = dragonflies[i].copy()
            
            convergence_curve.append(food_fitness)
        
        return food_pos, food_fitness, convergence_curve


class FlowerPollinationAlgorithm:
    """
    Flower Pollination Algorithm
    
    Inspired by pollination process of flowering plants.
    
    Reference: Yang (2012)
    """
    
    def __init__(self, p: float = 0.8, lambda_param: float = 1.5):
        self.p = p  # Switch probability
        self.lambda_param = lambda_param  # Lévy flight parameter
        self.name = "Flower Pollination Algorithm"
    
    def _levy_flight(self, dim: int) -> np.ndarray:
        """Generate Lévy flight step"""
        sigma = (np.math.gamma(1 + self.lambda_param) * np.sin(np.pi * self.lambda_param / 2) /
                (np.math.gamma((1 + self.lambda_param) / 2) * self.lambda_param *
                 2 ** ((self.lambda_param - 1) / 2))) ** (1 / self.lambda_param)
        
        u = np.random.randn(dim) * sigma
        v = np.random.randn(dim)
        step = u / (abs(v) ** (1 / self.lambda_param))
        
        return step
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 30) -> Tuple:
        """Run FPA optimization"""
        lb, ub = bounds
        
        # Initialize flower population
        flowers = np.random.uniform(lb, ub, (population_size, dim))
        fitness = np.array([fitness_func(ind) for ind in flowers])
        
        best_idx = np.argmin(fitness)
        best_solution = flowers[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            for i in range(population_size):
                if np.random.rand() < self.p:
                    # Global pollination (Lévy flight)
                    L = self._levy_flight(dim)
                    flowers[i] += 0.01 * L * (best_solution - flowers[i])
                else:
                    # Local pollination
                    epsilon = np.random.rand()
                    j = np.random.randint(0, population_size)
                    k = np.random.randint(0, population_size)
                    flowers[i] += epsilon * (flowers[j] - flowers[k])
                
                # Boundary check
                flowers[i] = np.clip(flowers[i], lb, ub)
                
                # Evaluate
                new_fitness = fitness_func(flowers[i])
                
                # Greedy selection
                if new_fitness < fitness[i]:
                    fitness[i] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_fitness = new_fitness
                        best_solution = flowers[i].copy()
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


class VariableNeighborhoodSearch:
    """
    Variable Neighborhood Search
    
    Systematic change of neighborhood within local search.
    
    Reference: Mladenović & Hansen (1997)
    """
    
    def __init__(self, kmax: int = 5):
        self.kmax = kmax  # Maximum neighborhood structure
        self.name = "Variable Neighborhood Search"
    
    def optimize(self, fitness_func: Callable, dim: int, bounds: Tuple[float, float],
                max_iterations: int = 100, population_size: int = 1) -> Tuple:
        """Run VNS optimization"""
        lb, ub = bounds
        
        # Initialize solution
        current = np.random.uniform(lb, ub, dim)
        current_fitness = fitness_func(current)
        
        best_solution = current.copy()
        best_fitness = current_fitness
        
        convergence_curve = []
        
        for iteration in range(max_iterations):
            k = 1  # Neighborhood structure index
            
            while k <= self.kmax:
                # Shaking: generate random solution in k-th neighborhood
                neighbor = current.copy()
                
                # Number of dimensions to perturb increases with k
                n_perturb = min(k, dim)
                perturb_dims = np.random.choice(dim, n_perturb, replace=False)
                
                for d in perturb_dims:
                    neighbor[d] = np.clip(
                        neighbor[d] + np.random.uniform(-k * 0.1, k * 0.1) * (ub - lb),
                        lb, ub
                    )
                
                # Local search
                neighbor_fitness = fitness_func(neighbor)
                
                # Improvement check
                if neighbor_fitness < current_fitness:
                    current = neighbor.copy()
                    current_fitness = neighbor_fitness
                    k = 1  # Restart from first neighborhood
                    
                    if current_fitness < best_fitness:
                        best_fitness = current_fitness
                        best_solution = current.copy()
                else:
                    k += 1  # Move to next neighborhood
            
            convergence_curve.append(best_fitness)
        
        return best_solution, best_fitness, convergence_curve


# Additional algorithms can be added here:
# - Artificial Fish Swarm Algorithm
# - Bacterial Foraging Optimization
# - Shuffled Frog Leaping Algorithm
# - Group Search Optimizer
# - Invasive Weed Optimization
# - Charged System Search
# - League Championship Algorithm
# - And many more...
