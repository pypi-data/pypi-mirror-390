"""
Detailed Results Collector for MHA Algorithms
============================================

Implements comprehensive data collection and NPZ-based storage with the following features:
- Convergence curve points for each iteration
- Best fitness per iteration
- Mean fitness per iteration  
- Local fitness for each agent per iteration
- Local solution for each agent per iteration
- Tree-like storage structure: Dataset/Session/Algorithm.npz
- Efficient NumPy NPZ format for large array storage
- Easy comparison and plotting capabilities
"""

import numpy as np
import os
import json
from pathlib import Path
from datetime import datetime
import pickle
import streamlit as st


class DetailedResultsCollector:
    """Enhanced results collector with comprehensive iteration tracking"""
    
    def __init__(self, base_dir="results/detailed_storage"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session tracking
        self.current_session = None
        self.current_dataset = None
        self.algorithm_data = {}
        
    def initialize_session(self, dataset_name, session_id=None):
        """Initialize a new session for data collection"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = session_id
        self.current_dataset = dataset_name
        
        # Create session directory structure
        self.session_dir = self.base_dir / dataset_name / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session metadata
        self.session_metadata = {
            'session_id': session_id,
            'dataset_name': dataset_name,
            'created_at': datetime.now().isoformat(),
            'algorithms_run': [],
            'total_algorithms': 0,
            'session_status': 'active'
        }
        
        return session_id
    
    def start_algorithm_tracking(self, algorithm_name, population_size, dimensions, 
                                max_iterations, task_type):
        """Start detailed tracking for an algorithm"""
        
        self.algorithm_data[algorithm_name] = {
            'algorithm_name': algorithm_name,
            'population_size': population_size,
            'dimensions': dimensions,
            'max_iterations': max_iterations,
            'task_type': task_type,
            'started_at': datetime.now().isoformat(),
            
            # Detailed iteration tracking arrays
            'iteration_data': {
                'best_fitness_per_iteration': [],
                'mean_fitness_per_iteration': [],
                'worst_fitness_per_iteration': [],
                'std_fitness_per_iteration': [],
                'convergence_curve': [],
                
                # Population tracking per iteration
                'population_fitness_history': [],     # [iteration][agent] fitness values
                'population_positions_history': [],   # [iteration][agent][dimension] positions
                'local_best_fitness_history': [],     # [iteration][agent] local best fitness
                'local_best_positions_history': [],   # [iteration][agent][dimension] local best pos
                
                # Algorithm-specific tracking
                'velocity_history': [],               # For PSO-type algorithms
                'exploration_exploitation_ratio': [], # Exploration vs exploitation per iteration
                'diversity_measure': [],              # Population diversity per iteration
                'search_bounds_history': [],          # Dynamic bounds if applicable
                
                # Performance metrics
                'iteration_times': [],               # Time per iteration
                'cumulative_time': [],              # Cumulative time
                'improvement_rate': [],             # Fitness improvement rate
                'stagnation_counter': []            # Iterations without improvement
            },
            
            # Final results
            'final_results': {
                'best_solution': None,
                'best_fitness': None,
                'total_iterations': 0,
                'total_time': 0,
                'convergence_reached': False,
                'final_population': None
            }
        }
        
        st.info(f"🔬 Started detailed tracking for {algorithm_name.upper()}")
        return True
    
    def track_iteration(self, algorithm_name, iteration, population_data, 
                       global_best_fitness, global_best_position, 
                       iteration_time=None, additional_data=None):
        """Track detailed data for a single iteration"""
        
        if algorithm_name not in self.algorithm_data:
            st.error(f"Algorithm {algorithm_name} not initialized for tracking!")
            return False
        
        data = self.algorithm_data[algorithm_name]['iteration_data']
        
        try:
            # Extract population data
            population_fitness = []
            population_positions = []
            local_best_fitness = []
            local_best_positions = []
            
            for agent in population_data:
                population_fitness.append(float(agent.get('fitness', float('inf'))))
                population_positions.append(list(agent.get('position', [])))
                local_best_fitness.append(float(agent.get('local_best_fitness', float('inf'))))
                local_best_positions.append(list(agent.get('local_best_position', [])))
            
            # Calculate iteration statistics
            fitness_array = np.array(population_fitness)
            mean_fitness = float(np.mean(fitness_array))
            worst_fitness = float(np.max(fitness_array))
            std_fitness = float(np.std(fitness_array))
            
            # Store iteration data
            data['best_fitness_per_iteration'].append(float(global_best_fitness))
            data['mean_fitness_per_iteration'].append(mean_fitness)
            data['worst_fitness_per_iteration'].append(worst_fitness)
            data['std_fitness_per_iteration'].append(std_fitness)
            data['convergence_curve'].append(float(global_best_fitness))
            
            # Store population data
            data['population_fitness_history'].append(population_fitness)
            data['population_positions_history'].append(population_positions)
            data['local_best_fitness_history'].append(local_best_fitness)
            data['local_best_positions_history'].append(local_best_positions)
            
            # Calculate diversity measure (average distance between agents)
            if len(population_positions) > 1:
                positions_array = np.array(population_positions)
                diversity = float(np.mean(np.std(positions_array, axis=0)))
                data['diversity_measure'].append(diversity)
            else:
                data['diversity_measure'].append(0.0)
            
            # Track timing
            if iteration_time:
                data['iteration_times'].append(float(iteration_time))
                total_time = sum(data['iteration_times'])
                data['cumulative_time'].append(total_time)
            
            # Calculate improvement rate
            if len(data['best_fitness_per_iteration']) > 1:
                current_best = data['best_fitness_per_iteration'][-1]
                previous_best = data['best_fitness_per_iteration'][-2]
                improvement = abs(previous_best - current_best) / max(abs(previous_best), 1e-10)
                data['improvement_rate'].append(float(improvement))
            else:
                data['improvement_rate'].append(0.0)
            
            # Track stagnation
            if len(data['best_fitness_per_iteration']) > 1:
                if abs(data['best_fitness_per_iteration'][-1] - data['best_fitness_per_iteration'][-2]) < 1e-8:
                    last_stagnation = data['stagnation_counter'][-1] if data['stagnation_counter'] else 0
                    data['stagnation_counter'].append(last_stagnation + 1)
                else:
                    data['stagnation_counter'].append(0)
            else:
                data['stagnation_counter'].append(0)
            
            # Store additional algorithm-specific data
            if additional_data:
                for key, value in additional_data.items():
                    if key not in data:
                        data[key] = []
                    data[key].append(value)
            
            return True
            
        except Exception as e:
            st.error(f"Error tracking iteration {iteration} for {algorithm_name}: {e}")
            return False
    
    def finalize_algorithm(self, algorithm_name, final_solution, final_fitness, 
                          total_iterations, convergence_reached=False):
        """Finalize algorithm tracking and prepare for NPZ storage"""
        
        if algorithm_name not in self.algorithm_data:
            return False
        
        # Store final results
        final_data = self.algorithm_data[algorithm_name]['final_results']
        final_data['best_solution'] = list(final_solution) if hasattr(final_solution, '__iter__') else [final_solution]
        final_data['best_fitness'] = float(final_fitness)
        final_data['total_iterations'] = int(total_iterations)
        final_data['convergence_reached'] = bool(convergence_reached)
        final_data['completed_at'] = datetime.now().isoformat()
        
        # Calculate total time
        iteration_times = self.algorithm_data[algorithm_name]['iteration_data']['iteration_times']
        final_data['total_time'] = sum(iteration_times) if iteration_times else 0
        
        # Add to session metadata
        self.session_metadata['algorithms_run'].append(algorithm_name)
        self.session_metadata['total_algorithms'] = len(self.session_metadata['algorithms_run'])
        
        st.success(f"✅ Finalized detailed tracking for {algorithm_name.upper()}")
        return True
    
    def save_algorithm_npz(self, algorithm_name):
        """Save algorithm data to NPZ format with structured organization"""
        
        if algorithm_name not in self.algorithm_data:
            st.error(f"No data found for algorithm {algorithm_name}")
            return None
        
        try:
            # Prepare data for NPZ storage
            alg_data = self.algorithm_data[algorithm_name]
            iteration_data = alg_data['iteration_data']
            
            # Convert lists to numpy arrays for efficient storage
            npz_data = {
                # Basic iteration metrics (1D arrays)
                'best_fitness_per_iteration': np.array(iteration_data['best_fitness_per_iteration']),
                'mean_fitness_per_iteration': np.array(iteration_data['mean_fitness_per_iteration']),
                'worst_fitness_per_iteration': np.array(iteration_data['worst_fitness_per_iteration']),
                'std_fitness_per_iteration': np.array(iteration_data['std_fitness_per_iteration']),
                'convergence_curve': np.array(iteration_data['convergence_curve']),
                'diversity_measure': np.array(iteration_data['diversity_measure']),
                'iteration_times': np.array(iteration_data['iteration_times']),
                'cumulative_time': np.array(iteration_data['cumulative_time']),
                'improvement_rate': np.array(iteration_data['improvement_rate']),
                'stagnation_counter': np.array(iteration_data['stagnation_counter']),
                
                # Population data (2D and 3D arrays)
                'population_fitness_history': np.array(iteration_data['population_fitness_history']),
                'local_best_fitness_history': np.array(iteration_data['local_best_fitness_history']),
                
                # Final results
                'final_best_solution': np.array(alg_data['final_results']['best_solution']),
                'final_best_fitness': np.array([alg_data['final_results']['best_fitness']]),
                'total_iterations': np.array([alg_data['final_results']['total_iterations']]),
                'total_time': np.array([alg_data['final_results']['total_time']]),
                
                # Metadata
                'algorithm_name': np.array([algorithm_name], dtype='U50'),
                'population_size': np.array([alg_data['population_size']]),
                'dimensions': np.array([alg_data['dimensions']]),
                'max_iterations': np.array([alg_data['max_iterations']]),
                'task_type': np.array([alg_data['task_type']], dtype='U50'),
            }
            
            # Handle 3D position arrays (more complex)
            if iteration_data['population_positions_history']:
                try:
                    # Convert to 3D array: [iteration, agent, dimension]
                    positions_3d = np.array(iteration_data['population_positions_history'])
                    npz_data['population_positions_history'] = positions_3d
                except:
                    # Fallback: save as object array if dimensions don't match
                    npz_data['population_positions_history'] = np.array(iteration_data['population_positions_history'], dtype=object)
            
            if iteration_data['local_best_positions_history']:
                try:
                    local_best_3d = np.array(iteration_data['local_best_positions_history'])
                    npz_data['local_best_positions_history'] = local_best_3d
                except:
                    npz_data['local_best_positions_history'] = np.array(iteration_data['local_best_positions_history'], dtype=object)
            
            # Create filename with structured organization
            npz_filename = f"{algorithm_name}_detailed.npz"
            npz_path = self.session_dir / npz_filename
            
            # Save compressed NPZ file
            np.savez_compressed(npz_path, **npz_data)
            
            # Create metadata JSON file
            metadata = {
                'algorithm_name': algorithm_name,
                'npz_file': npz_filename,
                'session_id': self.current_session,
                'dataset_name': self.current_dataset,
                'created_at': datetime.now().isoformat(),
                'data_arrays': list(npz_data.keys()),
                'total_iterations': int(alg_data['final_results']['total_iterations']),
                'best_fitness': float(alg_data['final_results']['best_fitness']),
                'file_size_mb': os.path.getsize(npz_path) / (1024 * 1024)
            }
            
            metadata_path = self.session_dir / f"{algorithm_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            st.success(f"💾 Saved detailed NPZ data: {npz_path}")
            st.info(f"📊 Arrays stored: {', '.join(npz_data.keys())}")
            st.info(f"💽 File size: {metadata['file_size_mb']:.2f} MB")
            
            return {
                'npz_path': str(npz_path),
                'metadata_path': str(metadata_path),
                'metadata': metadata
            }
            
        except Exception as e:
            st.error(f"Failed to save NPZ for {algorithm_name}: {e}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
    def list_available_results(self, dataset_name=None):
        """List all available NPZ result files for comparison"""
        
        available_results = []
        
        if dataset_name:
            search_dirs = [self.base_dir / dataset_name]
        else:
            search_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]
        
        for dataset_dir in search_dirs:
            if not dataset_dir.is_dir():
                continue
                
            for session_dir in dataset_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                
                for npz_file in session_dir.glob("*_detailed.npz"):
                    metadata_file = session_dir / f"{npz_file.stem.replace('_detailed', '')}_metadata.json"
                    
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            available_results.append({
                                'dataset': dataset_dir.name,
                                'session': session_dir.name,
                                'algorithm': metadata['algorithm_name'],
                                'npz_path': str(npz_file),
                                'metadata_path': str(metadata_file),
                                'metadata': metadata
                            })
                        except:
                            continue
        
        return sorted(available_results, key=lambda x: x['metadata']['created_at'], reverse=True)
    
    def load_algorithm_npz(self, npz_path):
        """Load algorithm data from NPZ file"""
        
        try:
            # Load NPZ data
            npz_data = np.load(npz_path, allow_pickle=True)
            
            # Convert back to dictionary format
            loaded_data = {}
            for key in npz_data.files:
                loaded_data[key] = npz_data[key]
            
            return loaded_data
            
        except Exception as e:
            st.error(f"Failed to load NPZ file {npz_path}: {e}")
            return None
    
    def finalize_session(self):
        """Finalize the current session and save session metadata"""
        
        if not self.current_session:
            return False
        
        try:
            # Update session metadata
            self.session_metadata['completed_at'] = datetime.now().isoformat()
            self.session_metadata['session_status'] = 'completed'
            
            # Save session metadata
            session_metadata_path = self.session_dir / "session_metadata.json"
            with open(session_metadata_path, 'w') as f:
                json.dump(self.session_metadata, f, indent=2)
            
            # Save all algorithm NPZ files
            saved_files = []
            for algorithm_name in self.algorithm_data.keys():
                npz_result = self.save_algorithm_npz(algorithm_name)
                if npz_result:
                    saved_files.append(npz_result)
            
            st.success(f"🎯 Session {self.current_session} completed with {len(saved_files)} algorithms")
            
            return {
                'session_metadata_path': str(session_metadata_path),
                'saved_algorithms': saved_files,
                'session_summary': self.session_metadata
            }
            
        except Exception as e:
            st.error(f"Failed to finalize session: {e}")
            return False