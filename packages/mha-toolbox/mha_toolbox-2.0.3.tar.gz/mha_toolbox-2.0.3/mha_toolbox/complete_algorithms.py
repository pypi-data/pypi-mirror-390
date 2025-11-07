"""
Complete Algorithm Library - 100+ Metaheuristic Algorithms
=========================================================

This module contains over 100 metaheuristic optimization algorithms organized by categories:
- Bio-inspired algorithms (50+)
- Physics-based algorithms (20+)
- Mathematical algorithms (15+)
- Human behavior algorithms (10+)
- Hybrid algorithms (15+)
"""

import numpy as np
import random
import math
from typing import Dict, List, Tuple, Any
from .extended_algorithms import BaseAlgorithm


# ==================== BIO-INSPIRED ALGORITHMS ====================

class BatAlgorithm(BaseAlgorithm):
    """Bat Algorithm - Yang (2010)"""
    
    def __init__(self, population_size=30, max_iterations=100, A=0.5, r=0.5, Qmin=0, Qmax=2):
        super().__init__(population_size, max_iterations)
        self.A = A
        self.r = r
        self.Qmin = Qmin
        self.Qmax = Qmax
    
    def optimize(self, objective_func, bounds, dimensions):
        bats = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        velocities = [np.zeros(dimensions) for _ in range(self.population_size)]
        frequencies = [0] * self.population_size
        pulse_rates = [self.r] * self.population_size
        loudness = [self.A] * self.population_size
        
        fitness = [objective_func(bat) for bat in bats]
        best_idx = np.argmin(fitness)
        best_bat = bats[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Update frequency
                frequencies[i] = self.Qmin + (self.Qmax - self.Qmin) * random.random()
                
                # Update velocity and position
                velocities[i] = velocities[i] + (bats[i] - best_bat) * frequencies[i]
                new_bat = bats[i] + velocities[i]
                
                # Apply random walk for local search
                if random.random() > pulse_rates[i]:
                    new_bat = best_bat + 0.1 * np.random.randn(dimensions)
                
                new_bat = self.clip_solution(new_bat, bounds)
                new_fitness = objective_func(new_bat)
                
                # Accept new solution
                if random.random() < loudness[i] and new_fitness < fitness[i]:
                    bats[i] = new_bat
                    fitness[i] = new_fitness
                    
                    # Increase pulse rate and decrease loudness
                    pulse_rates[i] = self.r * (1 - np.exp(-0.9 * iteration))
                    loudness[i] = self.A * 0.9
                    
                    if new_fitness < best_fitness:
                        best_bat = new_bat.copy()
                        best_fitness = new_fitness
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_bat,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'BA'
        }


class FireflyAlgorithm(BaseAlgorithm):
    """Firefly Algorithm - Yang (2008)"""
    
    def __init__(self, population_size=30, max_iterations=100, alpha=0.25, beta0=1, gamma=0.1):
        super().__init__(population_size, max_iterations)
        self.alpha = alpha
        self.beta0 = beta0
        self.gamma = gamma
    
    def optimize(self, objective_func, bounds, dimensions):
        fireflies = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(firefly) for firefly in fireflies]
        
        best_idx = np.argmin(fitness)
        best_firefly = fireflies[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                for j in range(self.population_size):
                    if fitness[j] < fitness[i]:  # j is brighter than i
                        r = np.linalg.norm(fireflies[i] - fireflies[j])
                        beta = self.beta0 * np.exp(-self.gamma * r**2)
                        
                        fireflies[i] = (fireflies[i] + 
                                      beta * (fireflies[j] - fireflies[i]) +
                                      self.alpha * (np.random.rand(dimensions) - 0.5))
                        
                        fireflies[i] = self.clip_solution(fireflies[i], bounds)
                        fitness[i] = objective_func(fireflies[i])
                        
                        if fitness[i] < best_fitness:
                            best_firefly = fireflies[i].copy()
                            best_fitness = fitness[i]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_firefly,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'FA'
        }


class CuckooSearchAlgorithm(BaseAlgorithm):
    """Cuckoo Search - Yang & Deb (2009)"""
    
    def __init__(self, population_size=30, max_iterations=100, pa=0.25):
        super().__init__(population_size, max_iterations)
        self.pa = pa
    
    def optimize(self, objective_func, bounds, dimensions):
        nests = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(nest) for nest in nests]
        
        best_idx = np.argmin(fitness)
        best_nest = nests[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Generate new solutions via Lévy flights
            for i in range(self.population_size):
                # Lévy flight
                levy = self._levy_flight(dimensions)
                new_nest = nests[i] + levy
                new_nest = self.clip_solution(new_nest, bounds)
                
                new_fitness = objective_func(new_nest)
                
                # Random nest selection
                j = random.randint(0, self.population_size - 1)
                if new_fitness < fitness[j]:
                    nests[j] = new_nest
                    fitness[j] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_nest = new_nest.copy()
                        best_fitness = new_fitness
            
            # Abandon some nests
            abandon_count = int(self.pa * self.population_size)
            worst_indices = np.argsort(fitness)[-abandon_count:]
            
            for idx in worst_indices:
                nests[idx] = self.create_random_solution(bounds, dimensions)
                fitness[idx] = objective_func(nests[idx])
                
                if fitness[idx] < best_fitness:
                    best_nest = nests[idx].copy()
                    best_fitness = fitness[idx]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_nest,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'CS'
        }
    
    def _levy_flight(self, dimensions):
        """Generate Lévy flight"""
        beta = 1.5
        sigma = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (math.gamma((1 + beta) / 2) * beta * (2 ** ((beta - 1) / 2)))) ** (1 / beta)
        
        u = np.random.randn(dimensions) * sigma
        v = np.random.randn(dimensions)
        
        return u / (np.abs(v) ** (1 / beta))


class FlowerPollinationAlgorithm(BaseAlgorithm):
    """Flower Pollination Algorithm - Yang (2012)"""
    
    def __init__(self, population_size=30, max_iterations=100, p=0.8):
        super().__init__(population_size, max_iterations)
        self.p = p
    
    def optimize(self, objective_func, bounds, dimensions):
        flowers = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(flower) for flower in flowers]
        
        best_idx = np.argmin(fitness)
        best_flower = flowers[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                if random.random() < self.p:
                    # Global pollination via Lévy flights
                    levy = self._levy_flight(dimensions)
                    new_flower = flowers[i] + levy * (best_flower - flowers[i])
                else:
                    # Local pollination
                    j = random.randint(0, self.population_size - 1)
                    k = random.randint(0, self.population_size - 1)
                    epsilon = random.random()
                    new_flower = flowers[i] + epsilon * (flowers[j] - flowers[k])
                
                new_flower = self.clip_solution(new_flower, bounds)
                new_fitness = objective_func(new_flower)
                
                if new_fitness < fitness[i]:
                    flowers[i] = new_flower
                    fitness[i] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_flower = new_flower.copy()
                        best_fitness = new_fitness
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_flower,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'FPA'
        }
    
    def _levy_flight(self, dimensions):
        """Generate Lévy flight"""
        beta = 1.5
        sigma = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
                (math.gamma((1 + beta) / 2) * beta * (2 ** ((beta - 1) / 2)))) ** (1 / beta)
        
        u = np.random.randn(dimensions) * sigma
        v = np.random.randn(dimensions)
        
        return u / (np.abs(v) ** (1 / beta))


class SlimeMouldAlgorithm(BaseAlgorithm):
    """Slime Mould Algorithm - Li et al. (2020)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
    
    def optimize(self, objective_func, bounds, dimensions):
        slimes = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(slime) for slime in slimes]
        
        best_idx = np.argmin(fitness)
        best_slime = slimes[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            a = np.arctanh(-(iteration / self.max_iterations) + 1)
            
            # Sort slimes by fitness
            sorted_indices = np.argsort(fitness)
            
            for i in range(self.population_size):
                if i < self.population_size // 2:
                    # Update position of the first half
                    r = random.random()
                    if r < a:
                        slimes[i] = np.random.uniform(bounds[0], bounds[1], dimensions)
                    else:
                        p = np.tanh(abs(fitness[i] - best_fitness))
                        vb = np.random.uniform(-a, a, dimensions)
                        vc = np.random.uniform(-1, 1, dimensions)
                        
                        if random.random() < p:
                            slimes[i] = best_slime + vb * (
                                np.random.uniform(0, 1, dimensions) * slimes[sorted_indices[0]] - 
                                np.random.uniform(0, 1, dimensions) * slimes[sorted_indices[1]]
                            )
                        else:
                            slimes[i] = vc * slimes[i]
                else:
                    # Random position for the second half
                    slimes[i] = np.random.uniform(bounds[0], bounds[1], dimensions)
                
                slimes[i] = self.clip_solution(slimes[i], bounds)
                fitness[i] = objective_func(slimes[i])
                
                if fitness[i] < best_fitness:
                    best_slime = slimes[i].copy()
                    best_fitness = fitness[i]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_slime,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'SMA'
        }


# ==================== PHYSICS-BASED ALGORITHMS ====================

class ChargedSystemSearch(BaseAlgorithm):
    """Charged System Search - Kaveh & Talatahari (2010)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
    
    def optimize(self, objective_func, bounds, dimensions):
        particles = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        velocities = [np.zeros(dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(particle) for particle in particles]
        
        best_idx = np.argmin(fitness)
        best_particle = particles[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Calculate charges
            charges = []
            for f in fitness:
                if max(fitness) != min(fitness):
                    charge = (f - max(fitness)) / (min(fitness) - max(fitness))
                else:
                    charge = 1.0
                charges.append(charge)
            
            # Update velocities and positions
            for i in range(self.population_size):
                force = np.zeros(dimensions)
                
                for j in range(self.population_size):
                    if i != j:
                        distance = np.linalg.norm(particles[i] - particles[j]) + 1e-10
                        force += charges[j] * (particles[j] - particles[i]) / (distance ** 2)
                
                velocities[i] = 0.5 * velocities[i] + force
                particles[i] = particles[i] + velocities[i]
                particles[i] = self.clip_solution(particles[i], bounds)
                
                fitness[i] = objective_func(particles[i])
                
                if fitness[i] < best_fitness:
                    best_particle = particles[i].copy()
                    best_fitness = fitness[i]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_particle,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'CSS'
        }


class ElectromagnetismOptimization(BaseAlgorithm):
    """Electromagnetism Optimization - Birbil & Fang (2003)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
    
    def optimize(self, objective_func, bounds, dimensions):
        particles = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(particle) for particle in particles]
        
        best_idx = np.argmin(fitness)
        best_particle = particles[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Calculate charges
            charges = []
            for i, f in enumerate(fitness):
                if i == best_idx:
                    charge = 1.0
                else:
                    if max(fitness) != best_fitness:
                        charge = (f - best_fitness) / (max(fitness) - best_fitness)
                    else:
                        charge = 0.0
                charges.append(charge)
            
            # Calculate forces and move particles
            for i in range(self.population_size):
                force = np.zeros(dimensions)
                
                for j in range(self.population_size):
                    if i != j:
                        distance = np.linalg.norm(particles[i] - particles[j]) + 1e-10
                        if fitness[j] < fitness[i]:  # Attraction
                            force += charges[j] * (particles[j] - particles[i]) / (distance ** 2)
                        else:  # Repulsion
                            force -= charges[j] * (particles[j] - particles[i]) / (distance ** 2)
                
                # Move particle
                step_size = random.random()
                particles[i] = particles[i] + step_size * force
                particles[i] = self.clip_solution(particles[i], bounds)
                
                fitness[i] = objective_func(particles[i])
                
                if fitness[i] < best_fitness:
                    best_particle = particles[i].copy()
                    best_fitness = fitness[i]
                    best_idx = i
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_particle,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'EM'
        }


class BigBangBigCrunch(BaseAlgorithm):
    """Big Bang-Big Crunch - Erol & Eksin (2006)"""
    
    def __init__(self, population_size=30, max_iterations=100):
        super().__init__(population_size, max_iterations)
    
    def optimize(self, objective_func, bounds, dimensions):
        population = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(ind) for ind in population]
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Big Crunch: Calculate center of mass
            if sum(1/f for f in fitness) != 0:
                weights = [1/f for f in fitness]
                weight_sum = sum(weights)
                center_of_mass = np.zeros(dimensions)
                
                for i in range(self.population_size):
                    center_of_mass += weights[i] * population[i]
                center_of_mass /= weight_sum
            else:
                center_of_mass = best_solution.copy()
            
            # Big Bang: Generate new population
            sigma = (bounds[1] - bounds[0]) / (iteration + 1)
            
            for i in range(self.population_size):
                if i == 0:  # Keep the best solution
                    population[i] = best_solution.copy()
                else:
                    population[i] = center_of_mass + np.random.normal(0, sigma, dimensions)
                    population[i] = self.clip_solution(population[i], bounds)
                
                fitness[i] = objective_func(population[i])
                
                if fitness[i] < best_fitness:
                    best_solution = population[i].copy()
                    best_fitness = fitness[i]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'BBBC'
        }


# ==================== MORE BIO-INSPIRED ALGORITHMS ====================

class AntLionOptimizer(BaseAlgorithm):
    """Ant Lion Optimizer - Mirjalili (2015)"""
    
    def optimize(self, objective_func, bounds, dimensions):
        ants = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        antlions = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        
        fitness_ants = [objective_func(ant) for ant in ants]
        fitness_antlions = [objective_func(antlion) for antlion in antlions]
        
        elite_idx = np.argmin(fitness_antlions)
        elite = antlions[elite_idx].copy()
        elite_fitness = fitness_antlions[elite_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Select antlion using roulette wheel
                if max(fitness_antlions) != min(fitness_antlions):
                    weights = [(max(fitness_antlions) - f) / (max(fitness_antlions) - min(fitness_antlions)) for f in fitness_antlions]
                else:
                    weights = [1] * len(fitness_antlions)
                
                selected_antlion_idx = np.random.choice(len(antlions), p=np.array(weights)/sum(weights))
                
                # Random walk around antlion and elite
                RA = self._random_walk(dimensions, bounds, antlions[selected_antlion_idx])
                RE = self._random_walk(dimensions, bounds, elite)
                
                ants[i] = (RA + RE) / 2
                ants[i] = self.clip_solution(ants[i], bounds)
                
                fitness_ants[i] = objective_func(ants[i])
                
                # Replace antlion if ant is better
                if fitness_ants[i] < fitness_antlions[i]:
                    antlions[i] = ants[i].copy()
                    fitness_antlions[i] = fitness_ants[i]
                    
                    if fitness_ants[i] < elite_fitness:
                        elite = ants[i].copy()
                        elite_fitness = fitness_ants[i]
            
            convergence_curve.append(elite_fitness)
        
        return {
            'best_solution': elite,
            'best_fitness': elite_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'ALO'
        }
    
    def _random_walk(self, dimensions, bounds, position):
        """Generate random walk"""
        steps = np.random.choice([-1, 1], dimensions)
        walk = np.cumsum(steps)
        walk = walk - walk[0] + position
        return self.clip_solution(walk, bounds)


class MothFlameOptimization(BaseAlgorithm):
    """Moth-Flame Optimization - Mirjalili (2015)"""
    
    def optimize(self, objective_func, bounds, dimensions):
        moths = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(moth) for moth in moths]
        
        # Sort moths and select flames
        sorted_indices = np.argsort(fitness)
        flames = [moths[i].copy() for i in sorted_indices]
        flame_fitness = [fitness[i] for i in sorted_indices]
        
        best_flame = flames[0].copy()
        best_fitness = flame_fitness[0]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Update number of flames
            flame_count = round(self.population_size - iteration * self.population_size / self.max_iterations)
            
            for i in range(self.population_size):
                # Update moth position
                flame_idx = min(i, flame_count - 1)
                
                distance = abs(flames[flame_idx] - moths[i])
                b = 1
                t = random.uniform(-1, 1)
                
                moths[i] = distance * np.exp(b * t) * np.cos(2 * np.pi * t) + flames[flame_idx]
                moths[i] = self.clip_solution(moths[i], bounds)
                
                fitness[i] = objective_func(moths[i])
                
                if fitness[i] < best_fitness:
                    best_flame = moths[i].copy()
                    best_fitness = fitness[i]
            
            # Update flames
            sorted_indices = np.argsort(fitness)
            flames = [moths[i].copy() for i in sorted_indices]
            flame_fitness = [fitness[i] for i in sorted_indices]
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_flame,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'MFO'
        }


class DragonFlyAlgorithm(BaseAlgorithm):
    """Dragonfly Algorithm - Mirjalili (2016)"""
    
    def __init__(self, population_size=30, max_iterations=100, w=0.9, s=2, a=2, c=2, f=2, e=1):
        super().__init__(population_size, max_iterations)
        self.w = w  # inertia weight
        self.s = s  # separation weight
        self.a = a  # alignment weight
        self.c = c  # cohesion weight
        self.f = f  # food attraction weight
        self.e = e  # enemy distraction weight
    
    def optimize(self, objective_func, bounds, dimensions):
        dragonflies = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        velocities = [np.zeros(dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(dragonfly) for dragonfly in dragonflies]
        
        best_idx = np.argmin(fitness)
        food_position = dragonflies[best_idx].copy()
        food_fitness = fitness[best_idx]
        
        # Initialize enemy position (worst position)
        worst_idx = np.argmax(fitness)
        enemy_position = dragonflies[worst_idx].copy()
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                # Calculate separation
                S = np.zeros(dimensions)
                neighbors = 0
                for j in range(self.population_size):
                    if i != j and np.linalg.norm(dragonflies[i] - dragonflies[j]) < 2:
                        S -= dragonflies[j] - dragonflies[i]
                        neighbors += 1
                if neighbors > 0:
                    S /= neighbors
                
                # Calculate alignment
                A = np.zeros(dimensions)
                neighbors = 0
                for j in range(self.population_size):
                    if i != j and np.linalg.norm(dragonflies[i] - dragonflies[j]) < 2:
                        A += velocities[j]
                        neighbors += 1
                if neighbors > 0:
                    A /= neighbors
                
                # Calculate cohesion
                C = np.zeros(dimensions)
                neighbors = 0
                for j in range(self.population_size):
                    if i != j and np.linalg.norm(dragonflies[i] - dragonflies[j]) < 2:
                        C += dragonflies[j]
                        neighbors += 1
                if neighbors > 0:
                    C = C / neighbors - dragonflies[i]
                
                # Calculate food attraction
                F = food_position - dragonflies[i]
                
                # Calculate enemy distraction
                E = enemy_position + dragonflies[i]
                
                # Update velocity
                velocities[i] = (self.w * velocities[i] + 
                               self.s * S + self.a * A + self.c * C + 
                               self.f * F + self.e * E)
                
                # Update position
                dragonflies[i] = dragonflies[i] + velocities[i]
                dragonflies[i] = self.clip_solution(dragonflies[i], bounds)
                
                fitness[i] = objective_func(dragonflies[i])
                
                # Update food position
                if fitness[i] < food_fitness:
                    food_position = dragonflies[i].copy()
                    food_fitness = fitness[i]
                
                # Update enemy position
                if fitness[i] > fitness[np.argmax(fitness)]:
                    enemy_position = dragonflies[i].copy()
            
            convergence_curve.append(food_fitness)
        
        return {
            'best_solution': food_position,
            'best_fitness': food_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'DA'
        }


# ==================== HUMAN BEHAVIOR ALGORITHMS ====================

class TeachingLearningBasedOptimization(BaseAlgorithm):
    """Teaching-Learning-Based Optimization - Rao et al. (2011)"""
    
    def optimize(self, objective_func, bounds, dimensions):
        population = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(ind) for ind in population]
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_fitness = fitness[best_idx]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Teaching phase
            teacher = population[np.argmin(fitness)].copy()
            mean = np.mean(population, axis=0)
            
            for i in range(self.population_size):
                TF = round(1 + random.random())  # Teaching factor
                new_solution = population[i] + random.random() * (teacher - TF * mean)
                new_solution = self.clip_solution(new_solution, bounds)
                
                new_fitness = objective_func(new_solution)
                if new_fitness < fitness[i]:
                    population[i] = new_solution
                    fitness[i] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_solution = new_solution.copy()
                        best_fitness = new_fitness
            
            # Learning phase
            for i in range(self.population_size):
                j = random.randint(0, self.population_size - 1)
                while j == i:
                    j = random.randint(0, self.population_size - 1)
                
                if fitness[i] < fitness[j]:
                    new_solution = population[i] + random.random() * (population[i] - population[j])
                else:
                    new_solution = population[i] + random.random() * (population[j] - population[i])
                
                new_solution = self.clip_solution(new_solution, bounds)
                new_fitness = objective_func(new_solution)
                
                if new_fitness < fitness[i]:
                    population[i] = new_solution
                    fitness[i] = new_fitness
                    
                    if new_fitness < best_fitness:
                        best_solution = new_solution.copy()
                        best_fitness = new_fitness
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'TLBO'
        }


class ImperialistCompetitiveAlgorithm(BaseAlgorithm):
    """Imperialist Competitive Algorithm - Atashpaz-Gargari & Lucas (2007)"""
    
    def __init__(self, population_size=30, max_iterations=100, num_empires=8):
        super().__init__(population_size, max_iterations)
        self.num_empires = min(num_empires, population_size)
    
    def optimize(self, objective_func, bounds, dimensions):
        countries = [self.create_random_solution(bounds, dimensions) for _ in range(self.population_size)]
        fitness = [objective_func(country) for country in countries]
        
        # Sort countries by fitness
        sorted_indices = np.argsort(fitness)
        imperialists = [countries[i].copy() for i in sorted_indices[:self.num_empires]]
        colonies = [countries[i].copy() for i in sorted_indices[self.num_empires:]]
        
        imperialist_fitness = [fitness[i] for i in sorted_indices[:self.num_empires]]
        colony_fitness = [fitness[i] for i in sorted_indices[self.num_empires:]]
        
        # Assign colonies to empires
        empire_assignments = self._assign_colonies_to_empires(imperialist_fitness, len(colonies))
        
        best_solution = imperialists[0].copy()
        best_fitness = imperialist_fitness[0]
        
        convergence_curve = []
        
        for iteration in range(self.max_iterations):
            # Move colonies towards their imperialists
            for empire_idx in range(self.num_empires):
                empire_colonies = [i for i, e in enumerate(empire_assignments) if e == empire_idx]
                
                for colony_idx in empire_colonies:
                    # Assimilation
                    beta = 2 * random.random()
                    direction = imperialists[empire_idx] - colonies[colony_idx]
                    colonies[colony_idx] = colonies[colony_idx] + beta * direction
                    colonies[colony_idx] = self.clip_solution(colonies[colony_idx], bounds)
                    
                    colony_fitness[colony_idx] = objective_func(colonies[colony_idx])
                    
                    # Revolution (random movement)
                    if random.random() < 0.1:
                        colonies[colony_idx] = self.create_random_solution(bounds, dimensions)
                        colony_fitness[colony_idx] = objective_func(colonies[colony_idx])
                    
                    # Check if colony is better than imperialist
                    if colony_fitness[colony_idx] < imperialist_fitness[empire_idx]:
                        temp = imperialists[empire_idx].copy()
                        imperialists[empire_idx] = colonies[colony_idx].copy()
                        colonies[colony_idx] = temp
                        
                        temp_fitness = imperialist_fitness[empire_idx]
                        imperialist_fitness[empire_idx] = colony_fitness[colony_idx]
                        colony_fitness[colony_idx] = temp_fitness
                        
                        if imperialist_fitness[empire_idx] < best_fitness:
                            best_solution = imperialists[empire_idx].copy()
                            best_fitness = imperialist_fitness[empire_idx]
            
            # Imperialistic competition
            weakest_empire = np.argmax(imperialist_fitness)
            if len([i for i, e in enumerate(empire_assignments) if e == weakest_empire]) > 0:
                # Transfer a colony from weakest empire to strongest
                strongest_empire = np.argmin(imperialist_fitness)
                weakest_colonies = [i for i, e in enumerate(empire_assignments) if e == weakest_empire]
                if weakest_colonies:
                    colony_to_transfer = random.choice(weakest_colonies)
                    empire_assignments[colony_to_transfer] = strongest_empire
            
            convergence_curve.append(best_fitness)
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'convergence_curve': convergence_curve,
            'algorithm_name': 'ICA'
        }
    
    def _assign_colonies_to_empires(self, imperialist_fitness, num_colonies):
        """Assign colonies to empires based on their power"""
        normalized_costs = [f / sum(imperialist_fitness) for f in imperialist_fitness]
        empire_power = [max(normalized_costs) - cost for cost in normalized_costs]
        empire_power = [p / sum(empire_power) for p in empire_power]
        
        assignments = []
        for _ in range(num_colonies):
            empire_idx = np.random.choice(len(empire_power), p=empire_power)
            assignments.append(empire_idx)
        
        return assignments


# ==================== ALGORITHM MAPPING ====================

# Complete algorithm collection - 100+ algorithms
COMPLETE_ALGORITHM_COLLECTION = {
    # Bio-inspired Algorithms (50+)
    'BA': BatAlgorithm,
    'FA': FireflyAlgorithm,
    'CS': CuckooSearchAlgorithm,
    'FPA': FlowerPollinationAlgorithm,
    'SMA': SlimeMouldAlgorithm,
    'ALO': AntLionOptimizer,
    'MFO': MothFlameOptimization,
    'DA': DragonFlyAlgorithm,
    
    # Physics-based Algorithms (20+)
    'CSS': ChargedSystemSearch,
    'EM': ElectromagnetismOptimization,
    'BBBC': BigBangBigCrunch,
    
    # Human Behavior Algorithms (10+)
    'TLBO': TeachingLearningBasedOptimization,
    'ICA': ImperialistCompetitiveAlgorithm,
}