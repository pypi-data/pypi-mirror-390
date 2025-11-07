"""
Enhanced Algorithm Runner with Detailed Data Collection
======================================================

Integrates with DetailedResultsCollector to capture comprehensive
iteration-by-iteration data for comprehensive analysis.
"""

import numpy as np
import time
from datetime import datetime
import streamlit as st
from .detailed_results_collector import DetailedResultsCollector


def run_algorithm_with_detailed_tracking(algorithm_name, X, y, task_type, 
                                        max_iterations, population_size, n_runs,
                                        timeout_seconds, collector, 
                                        show_progress=True):
    """
    Run algorithm with comprehensive detailed tracking
    Captures all iteration data for comprehensive analysis
    """
    
    if show_progress:
        st.info(f"🔬 Starting detailed tracking for {algorithm_name.upper()}")
    
    # Initialize algorithm tracking
    success = collector.start_algorithm_tracking(
        algorithm_name=algorithm_name,
        population_size=population_size,
        dimensions=X.shape[1],
        max_iterations=max_iterations,
        task_type=task_type
    )
    
    if not success:
        st.error(f"Failed to initialize tracking for {algorithm_name}")
        return None
    
    # Import MHA toolbox
    from mha_comparison_toolbox import MHAComparisonToolbox
    
    runs_data = []
    total_start_time = time.time()
    
    for run in range(n_runs):
        if show_progress:
            st.write(f"🚀 **Run {run + 1}/{n_runs}** for {algorithm_name.upper()}")
        
        run_start_time = time.time()
        
        try:
            # Initialize MHA toolbox for this run
            mha = MHAComparisonToolbox()
            
            # Create objective function based on task type
            if task_type == 'feature_selection':
                objective_function = create_feature_selection_objective(X, y)
                bounds = [(0, 1)] * X.shape[1]  # Binary/continuous weights for features
                
            elif task_type == 'feature_optimization':
                objective_function = create_feature_optimization_objective(X, y)
                bounds = [(0, 1)] * X.shape[1]  # Feature weights
                
            elif task_type == 'hyperparameter_tuning':
                objective_function = create_hyperparameter_objective(X, y)
                bounds = [(0, 1)] * 3  # Simplified hyperparameter space
                
            else:
                st.error(f"Unknown task type: {task_type}")
                continue
            
            # Enhanced optimization with detailed tracking
            result = run_optimization_with_tracking(
                mha=mha,
                algorithm_name=algorithm_name,
                objective_function=objective_function,
                dimensions=len(bounds),
                bounds=bounds,
                max_iterations=max_iterations,
                population_size=population_size,
                collector=collector,
                run_id=run,
                show_progress=show_progress
            )
            
            if result:
                run_result = {
                    'run': run + 1,
                    'best_fitness': float(result['best_fitness']),
                    'convergence_curve': result['convergence_curve'],
                    'execution_time': time.time() - run_start_time,
                    'best_solution': result['best_solution'],
                    'total_iterations': result['total_iterations'],
                    'success': True
                }
                
                runs_data.append(run_result)
                
                if show_progress:
                    st.success(f"✅ Run {run + 1} completed - Best fitness: {result['best_fitness']:.6f}")
            
        except Exception as e:
            st.error(f"❌ Run {run + 1} failed: {str(e)}")
            continue
    
    # Finalize algorithm tracking
    if runs_data:
        best_run = min(runs_data, key=lambda x: x['best_fitness'])
        collector.finalize_algorithm(
            algorithm_name=algorithm_name,
            final_solution=best_run['best_solution'],
            final_fitness=best_run['best_fitness'],
            total_iterations=sum(r['total_iterations'] for r in runs_data),
            convergence_reached=True  # Could be enhanced with convergence detection
        )
        
        # Calculate comprehensive statistics
        statistics = calculate_detailed_statistics(runs_data, task_type)
        
        return {
            'algorithm': algorithm_name,
            'runs': runs_data,
            'statistics': statistics,
            'task_type': task_type,
            'total_execution_time': time.time() - total_start_time
        }
    
    return None


def run_optimization_with_tracking(mha, algorithm_name, objective_function, 
                                  dimensions, bounds, max_iterations, 
                                  population_size, collector, run_id, 
                                  show_progress=True):
    """
    Enhanced optimization with detailed iteration tracking
    """
    
    try:
        # Set up MHA parameters
        params = {
            'max_iterations': max_iterations,
            'population_size': population_size,
            'verbose': False
        }
        
        # Custom optimization loop with detailed tracking
        class DetailedOptimizationResult:
            def __init__(self):
                self.best_fitness_ = float('inf')
                self.best_solution_ = None
                self.global_fitness_ = []
                self.iteration_data = []
                self.population_history = []
        
        # Initialize population
        np.random.seed(42 + run_id)  # Consistent but different seeds per run
        
        # Create initial population
        population = []
        population_fitness = []
        
        for i in range(population_size):
            # Generate random solution within bounds
            solution = np.array([
                np.random.uniform(bound[0], bound[1]) 
                for bound in bounds
            ])
            
            fitness = objective_function(solution)
            
            population.append({
                'position': solution.copy(),
                'fitness': fitness,
                'local_best_position': solution.copy(),
                'local_best_fitness': fitness,
                'velocity': np.zeros_like(solution),  # For PSO-type algorithms
                'agent_id': i
            })
            
            population_fitness.append(fitness)
        
        # Find initial global best
        best_idx = np.argmin(population_fitness)
        global_best_position = population[best_idx]['position'].copy()
        global_best_fitness = population_fitness[best_idx]
        
        result = DetailedOptimizationResult()
        result.best_fitness_ = global_best_fitness
        result.best_solution_ = global_best_position.copy()
        
        # Progress tracking for UI
        if show_progress:
            progress_container = st.empty()
            iteration_container = st.empty()
        
        # Main optimization loop with detailed tracking
        for iteration in range(max_iterations):
            iteration_start_time = time.time()
            
            # Update progress display
            if show_progress and iteration % 10 == 0:
                progress = (iteration + 1) / max_iterations
                with progress_container.container():
                    st.progress(progress)
                    with iteration_container.container():
                        st.text(f"Iteration {iteration + 1}/{max_iterations} - Best: {global_best_fitness:.6f}")
            
            # Simulate algorithm-specific updates (simplified for demo)
            new_population = []
            new_fitness = []
            
            for agent in population:
                # Algorithm-specific position update (simplified)
                if algorithm_name.lower() in ['pso']:
                    # PSO update
                    w = 0.7  # Inertia weight
                    c1, c2 = 1.5, 1.5  # Acceleration coefficients
                    
                    # Update velocity
                    r1, r2 = np.random.random(dimensions), np.random.random(dimensions)
                    agent['velocity'] = (w * agent['velocity'] +
                                       c1 * r1 * (agent['local_best_position'] - agent['position']) +
                                       c2 * r2 * (global_best_position - agent['position']))
                    
                    # Update position
                    new_position = agent['position'] + agent['velocity']
                    
                elif algorithm_name.lower() in ['gwo', 'grey_wolf']:
                    # Grey Wolf Optimizer update (simplified)
                    a = 2 - iteration * (2 / max_iterations)  # Decreasing from 2 to 0
                    
                    # Random updates towards global best
                    r1, r2 = np.random.random(), np.random.random()
                    A = 2 * a * r1 - a
                    C = 2 * r2
                    
                    D = abs(C * global_best_position - agent['position'])
                    new_position = global_best_position - A * D
                    
                else:
                    # Generic random walk with bias towards global best
                    noise = np.random.normal(0, 0.1, dimensions)
                    bias_towards_best = 0.1 * (global_best_position - agent['position'])
                    new_position = agent['position'] + noise + bias_towards_best
                
                # Ensure bounds
                new_position = np.clip(new_position, 
                                     [b[0] for b in bounds], 
                                     [b[1] for b in bounds])
                
                # Evaluate new position
                new_fitness_val = objective_function(new_position)
                
                # Update agent
                updated_agent = agent.copy()
                updated_agent['position'] = new_position
                updated_agent['fitness'] = new_fitness_val
                
                # Update local best
                if new_fitness_val < agent['local_best_fitness']:
                    updated_agent['local_best_position'] = new_position.copy()
                    updated_agent['local_best_fitness'] = new_fitness_val
                
                new_population.append(updated_agent)
                new_fitness.append(new_fitness_val)
            
            # Update global best
            current_best_idx = np.argmin(new_fitness)
            current_best_fitness = new_fitness[current_best_idx]
            
            if current_best_fitness < global_best_fitness:
                global_best_fitness = current_best_fitness
                global_best_position = new_population[current_best_idx]['position'].copy()
                result.best_fitness_ = global_best_fitness
                result.best_solution_ = global_best_position.copy()
            
            # Track detailed iteration data
            iteration_time = time.time() - iteration_start_time
            
            collector.track_iteration(
                algorithm_name=algorithm_name,
                iteration=iteration,
                population_data=new_population,
                global_best_fitness=global_best_fitness,
                global_best_position=global_best_position,
                iteration_time=iteration_time,
                additional_data={
                    'algorithm_specific_params': {
                        'a_parameter': 2 - iteration * (2 / max_iterations) if 'gwo' in algorithm_name.lower() else None
                    }
                }
            )
            
            # Store convergence data
            result.global_fitness_.append(global_best_fitness)
            
            # Update population for next iteration
            population = new_population
        
        # Clean up progress display
        if show_progress:
            progress_container.empty()
            iteration_container.empty()
        
        return {
            'best_fitness': result.best_fitness_,
            'best_solution': result.best_solution_.tolist(),
            'convergence_curve': result.global_fitness_,
            'total_iterations': len(result.global_fitness_)
        }
        
    except Exception as e:
        st.error(f"Optimization tracking failed: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


def create_feature_selection_objective(X, y):
    """Create feature selection objective function"""
    def objective(weights):
        try:
            # Convert weights to binary feature selection
            selected_features = weights > 0.5
            
            if not np.any(selected_features):
                return 1.0  # Penalty for selecting no features
            
            X_selected = X[:, selected_features]
            
            # Use cross-validation for evaluation
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            
            rf = RandomForestClassifier(n_estimators=10, random_state=42)
            scores = cross_val_score(rf, X_selected, y, cv=3, scoring='accuracy')
            
            # Objective: minimize (1 - accuracy) + penalty for too many features
            accuracy = np.mean(scores)
            feature_penalty = np.sum(selected_features) / len(weights) * 0.1
            
            return (1 - accuracy) + feature_penalty
            
        except Exception as e:
            return 1.0  # High penalty for errors
    
    return objective


def create_feature_optimization_objective(X, y):
    """Create feature optimization objective function"""
    def objective(weights):
        try:
            # Apply weights to features
            X_weighted = X * weights.reshape(1, -1)
            
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            
            rf = RandomForestClassifier(n_estimators=10, random_state=42)
            scores = cross_val_score(rf, X_weighted, y, cv=3, scoring='accuracy')
            
            return 1.0 - np.mean(scores)  # Minimize (1 - accuracy)
            
        except Exception as e:
            return 1.0
    
    return objective


def create_hyperparameter_objective(X, y):
    """Create hyperparameter tuning objective function"""
    def objective(params_vector):
        try:
            # Map normalized parameters to actual hyperparameters
            n_estimators = max(10, int(params_vector[0] * 190 + 10))  # 10-200
            max_depth = max(3, int(params_vector[1] * 17 + 3)) if params_vector[1] > 0.1 else None
            min_samples_split = max(2, int(params_vector[2] * 18 + 2))  # 2-20
            
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            
            rf = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                random_state=42
            )
            
            scores = cross_val_score(rf, X, y, cv=3, scoring='accuracy')
            return 1.0 - np.mean(scores)
            
        except Exception as e:
            return 1.0
    
    return objective


def calculate_detailed_statistics(runs_data, task_type):
    """Calculate comprehensive statistics from runs"""
    
    if not runs_data:
        return {}
    
    # Extract basic metrics
    fitnesses = [run['best_fitness'] for run in runs_data]
    times = [run['execution_time'] for run in runs_data]
    
    statistics = {
        'mean_fitness': float(np.mean(fitnesses)),
        'std_fitness': float(np.std(fitnesses)),
        'best_fitness': float(np.min(fitnesses)),
        'worst_fitness': float(np.max(fitnesses)),
        'median_fitness': float(np.median(fitnesses)),
        'mean_time': float(np.mean(times)),
        'std_time': float(np.std(times)),
        'total_runs': len(runs_data),
        'success_rate': len([r for r in runs_data if r['success']]) / len(runs_data)
    }
    
    # Task-specific statistics
    if task_type == 'feature_selection':
        # Calculate feature statistics
        solutions = [run['best_solution'] for run in runs_data]
        feature_counts = [np.sum(np.array(sol) > 0.5) for sol in solutions]
        
        statistics.update({
            'mean_features': float(np.mean(feature_counts)),
            'std_features': float(np.std(feature_counts)),
            'min_features': int(np.min(feature_counts)),
            'max_features': int(np.max(feature_counts))
        })
    
    return statistics