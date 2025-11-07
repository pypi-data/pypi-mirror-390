"""
MHA Results Manager - Persistent Results Storage and Management System
========================================================================

This module handles comprehensive results storage, user session management,
and persistent access to all experiment results and models.

Features:
- Persistent file storage with organized directory structure
- User session tracking and results history
- Comprehensive model and results management
- Download tracking and file organization
- Results backup and recovery system
"""

import os
import json
import pandas as pd
import shutil
from datetime import datetime
from pathlib import Path
import uuid
import streamlit as st


class ResultsManager:
    """Comprehensive results storage and management system"""
    
    def __init__(self, base_dir="results"):
        self.base_dir = Path(base_dir)
        self.setup_directories()
        self.current_session = self.get_or_create_session()
    
    def setup_directories(self):
        """Create organized directory structure"""
        directories = [
            "persistent_storage",
            "persistent_storage/sessions",
            "persistent_storage/models", 
            "persistent_storage/complete_results",
            "persistent_storage/summaries",
            "persistent_storage/plots",
            "user_downloads",
            "backup"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def get_or_create_session(self):
        """Get or create a user session for persistent tracking"""
        if 'user_session_id' not in st.session_state:
            # Create new session
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            st.session_state.user_session_id = session_id
            
            # Create session directory
            session_dir = self.base_dir / "persistent_storage" / "sessions" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Save session metadata
            session_info = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'results_count': 0,
                'last_activity': datetime.now().isoformat(),
                'algorithms_run': [],
                'files_saved': []
            }
            
            with open(session_dir / "session_info.json", 'w') as f:
                json.dump(session_info, f, indent=2)
        
        return st.session_state.user_session_id
    
    def save_comprehensive_results(self, toolbox, session_name=None):
        """Save comprehensive results with enhanced persistence"""
        
        if not toolbox or not toolbox.results:
            return None, None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = session_name or f"experiment_{timestamp}"
        
        # Create session-specific directory
        session_dir = self.base_dir / "persistent_storage" / "sessions" / self.current_session
        experiment_dir = session_dir / session_name
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare comprehensive export data
        export_data = self._prepare_export_data(toolbox, timestamp)
        
        # Save files with enhanced organization
        saved_files = {}
        
        try:
            # 1. Complete results JSON
            results_file = experiment_dir / f"complete_results_{timestamp}.json"
            with open(results_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            saved_files['complete_results'] = str(results_file)
            
            # 2. Best models JSON (high-priority file)
            models_file = experiment_dir / f"BEST_MODELS_{timestamp}.json"
            with open(models_file, 'w') as f:
                json.dump(export_data['models'], f, indent=2, default=str)
            saved_files['models'] = str(models_file)
            
            # 3. Performance summary CSV
            summary_df = self._create_summary_dataframe(toolbox, export_data)
            summary_file = experiment_dir / f"performance_summary_{timestamp}.csv"
            summary_df.to_csv(summary_file, index=False)
            saved_files['summary'] = str(summary_file)
            
            # 4. Algorithm rankings JSON
            rankings_file = experiment_dir / f"algorithm_rankings_{timestamp}.json"
            with open(rankings_file, 'w') as f:
                json.dump(export_data['global_summary']['performance_rankings'], f, indent=2)
            saved_files['rankings'] = str(rankings_file)
            
            # 5. Copy to central storage for easy access
            self._copy_to_central_storage(saved_files, timestamp)
            
            # 6. Update session information
            self._update_session_info(session_name, saved_files, len(toolbox.results))
            
            # 7. Create backup
            self._create_backup(experiment_dir, timestamp)
            
            return export_data, saved_files
            
        except Exception as e:
            st.error(f"❌ Results save failed: {str(e)}")
            return None, None
    
    def _prepare_export_data(self, toolbox, timestamp):
        """Prepare comprehensive export data structure"""
        
        export_data = {
            'metadata': {
                'timestamp': timestamp,
                'session_id': self.current_session,
                'task_type': toolbox.task_type,
                'data_info': toolbox.data_info,
                'total_algorithms': len(toolbox.results),
                'software_version': 'MHA-Comprehensive-v3.0-Persistent',
                'save_location': str(self.base_dir / "persistent_storage"),
                'persistence_enabled': True
            },
            'algorithms': {},
            'models': {},
            'global_summary': {
                'best_overall_fitness': None,
                'best_algorithm': None,
                'performance_rankings': {}
            }
        }
        
        # Process each algorithm's results
        algorithm_performance = {}
        all_fitnesses = []
        
        for alg_name, results in toolbox.results.items():
            stats = results['statistics']
            runs = results['runs']
            
            # Find best run
            best_run = min(runs, key=lambda x: x['best_fitness']) if runs else None
            
            # Algorithm data
            export_data['algorithms'][alg_name] = {
                'statistics': stats,
                'best_run': best_run,
                'performance_score': stats['best_fitness'],
                'execution_time': stats['mean_time'],
                'stability': 1 - (stats['std_fitness'] / max(stats['mean_fitness'], 1e-10))
            }
            
            # Model data
            if best_run:
                export_data['models'][alg_name] = {
                    'best_fitness': best_run['best_fitness'],
                    'execution_time': best_run['execution_time'],
                    'convergence_curve': best_run.get('convergence_curve', []),
                    'model_parameters': {
                        'algorithm': alg_name,
                        'task_type': toolbox.task_type,
                        'optimized_value': best_run['best_fitness'],
                        'ready_for_production': True
                    }
                }
                
                if toolbox.task_type == 'feature_selection' and best_run.get('n_selected_features'):
                    export_data['models'][alg_name]['feature_selection'] = {
                        'selected_features': best_run['n_selected_features'],
                        'accuracy': best_run.get('final_accuracy', 0)
                    }
            
            algorithm_performance[alg_name] = stats['best_fitness']
            all_fitnesses.append(stats['best_fitness'])
        
        # Global summary
        if algorithm_performance:
            best_alg = min(algorithm_performance.items(), key=lambda x: x[1])
            export_data['global_summary'].update({
                'best_overall_fitness': min(all_fitnesses),
                'best_algorithm': best_alg[0],
                'performance_rankings': {
                    'by_fitness': sorted(algorithm_performance.items(), key=lambda x: x[1])
                }
            })
        
        return export_data
    
    def _create_summary_dataframe(self, toolbox, export_data):
        """Create comprehensive summary DataFrame"""
        
        summary_data = []
        for alg_name, alg_data in export_data['algorithms'].items():
            stats = alg_data['statistics']
            
            row = {
                'Algorithm': alg_name.upper(),
                'Best_Fitness': stats['best_fitness'],
                'Mean_Fitness': stats['mean_fitness'], 
                'Std_Fitness': stats['std_fitness'],
                'Mean_Time': stats['mean_time'],
                'Stability_Score': alg_data['stability'],
                'Total_Runs': stats['total_runs'],
                'Model_Available': alg_name in export_data['models'],
                'Session_ID': self.current_session
            }
            
            if toolbox.task_type == 'feature_selection':
                row.update({
                    'Mean_Features': stats.get('mean_features', 0),
                    'Mean_Accuracy': stats.get('mean_accuracy', 0)
                })
            
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def _copy_to_central_storage(self, saved_files, timestamp):
        """Copy important files to central storage for easy access"""
        
        central_dirs = {
            'models': self.base_dir / "persistent_storage" / "models",
            'complete_results': self.base_dir / "persistent_storage" / "complete_results", 
            'summaries': self.base_dir / "persistent_storage" / "summaries"
        }
        
        try:
            # Copy models file
            if 'models' in saved_files:
                shutil.copy2(saved_files['models'], 
                           central_dirs['models'] / f"models_{timestamp}.json")
            
            # Copy complete results
            if 'complete_results' in saved_files:
                shutil.copy2(saved_files['complete_results'],
                           central_dirs['complete_results'] / f"results_{timestamp}.json")
            
            # Copy summary
            if 'summary' in saved_files:
                shutil.copy2(saved_files['summary'],
                           central_dirs['summaries'] / f"summary_{timestamp}.csv")
        
        except Exception as e:
            st.warning(f"Central storage copy warning: {str(e)}")
    
    def _update_session_info(self, experiment_name, saved_files, algorithm_count):
        """Update session tracking information"""
        
        session_dir = self.base_dir / "persistent_storage" / "sessions" / self.current_session
        session_info_file = session_dir / "session_info.json"
        
        try:
            # Load existing session info
            if session_info_file.exists():
                with open(session_info_file, 'r') as f:
                    session_info = json.load(f)
            else:
                session_info = {
                    'session_id': self.current_session,
                    'created_at': datetime.now().isoformat(),
                    'results_count': 0,
                    'algorithms_run': [],
                    'files_saved': []
                }
            
            # Update session info
            session_info.update({
                'last_activity': datetime.now().isoformat(),
                'results_count': session_info.get('results_count', 0) + 1,
                'algorithms_run': session_info.get('algorithms_run', []) + [algorithm_count],
                'files_saved': session_info.get('files_saved', []) + [experiment_name]
            })
            
            # Save updated session info
            with open(session_info_file, 'w') as f:
                json.dump(session_info, f, indent=2)
        
        except Exception as e:
            st.warning(f"Session tracking update warning: {str(e)}")
    
    def _create_backup(self, experiment_dir, timestamp):
        """Create backup of experiment"""
        
        backup_dir = self.base_dir / "backup" / f"backup_{timestamp}"
        try:
            shutil.copytree(experiment_dir, backup_dir)
        except Exception as e:
            st.warning(f"Backup creation warning: {str(e)}")
    
    def get_all_results_history(self):
        """Get complete history of all results"""
        
        history = []
        sessions_dir = self.base_dir / "persistent_storage" / "sessions"
        
        if sessions_dir.exists():
            for session_dir in sessions_dir.iterdir():
                if session_dir.is_dir():
                    session_info_file = session_dir / "session_info.json"
                    if session_info_file.exists():
                        try:
                            with open(session_info_file, 'r') as f:
                                session_info = json.load(f)
                            
                            # Find experiment directories
                            experiments = []
                            for exp_dir in session_dir.iterdir():
                                if exp_dir.is_dir() and exp_dir.name != "session_info.json":
                                    experiments.append({
                                        'name': exp_dir.name,
                                        'path': str(exp_dir),
                                        'files': list(exp_dir.glob("*.json")) + list(exp_dir.glob("*.csv"))
                                    })
                            
                            session_info['experiments'] = experiments
                            history.append(session_info)
                            
                        except Exception as e:
                            continue
        
        return sorted(history, key=lambda x: x.get('last_activity', ''), reverse=True)
    
    def get_available_models(self):
        """Get all available models"""
        
        models_dir = self.base_dir / "persistent_storage" / "models"
        models = []
        
        if models_dir.exists():
            for model_file in models_dir.glob("*.json"):
                try:
                    with open(model_file, 'r') as f:
                        model_data = json.load(f)
                    
                    models.append({
                        'filename': model_file.name,
                        'path': str(model_file),
                        'timestamp': model_file.name.split('_')[-1].replace('.json', ''),
                        'algorithm_count': len(model_data),
                        'data': model_data
                    })
                except Exception:
                    continue
        
        return sorted(models, key=lambda x: x['timestamp'], reverse=True)
    
    def create_download_package(self, session_id=None):
        """Create comprehensive download package"""
        
        if session_id is None:
            session_id = self.current_session
        
        session_dir = self.base_dir / "persistent_storage" / "sessions" / session_id
        download_dir = self.base_dir / "user_downloads" / f"download_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if session_dir.exists():
            try:
                shutil.copytree(session_dir, download_dir)
                
                # Create README
                readme_content = f"""
MHA Algorithm Results Package
============================

Session ID: {session_id}
Generated: {datetime.now().isoformat()}

Contents:
- complete_results_*.json: Comprehensive algorithm results and analysis
- BEST_MODELS_*.json: Optimized models ready for production use
- performance_summary_*.csv: Algorithm performance rankings and statistics
- algorithm_rankings_*.json: Detailed performance rankings

Usage:
- Load JSON files in any programming environment
- CSV files can be opened in Excel or data analysis tools
- Models contain optimized parameters for each algorithm

Support: MHA Comprehensive Toolbox v3.0
"""
                
                with open(download_dir / "README.txt", 'w') as f:
                    f.write(readme_content)
                
                return str(download_dir)
            
            except Exception as e:
                st.error(f"Download package creation failed: {str(e)}")
                return None
        
        return None