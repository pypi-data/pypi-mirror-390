"""
Intelligent Session Management System
====================================

Features:
- User profile management (multi-user support)
- Automatic session resumption for same dataset
- Result comparison and auto-update if improved
- Hash-based dataset identification
- Session history tracking
- Profile-based isolation
- Portable user profiles via environment variables
"""

import os
import json
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Import portable user profile
try:
    from .user_profile import load_profile, get_active_profile, UserProfile as PortableUserProfile
    PORTABLE_PROFILE_AVAILABLE = True
except ImportError:
    PORTABLE_PROFILE_AVAILABLE = False
    import getpass
    import platform


@dataclass
class UserProfile:
    """User profile information"""
    username: str
    user_id: str
    created_at: str
    last_active: str
    total_sessions: int = 0
    total_experiments: int = 0
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                'auto_resume': True,
                'auto_update_best': True,
                'default_algorithms': [],
                'notification_enabled': True
            }


@dataclass
class DatasetInfo:
    """Dataset identification and metadata"""
    dataset_hash: str
    dataset_name: str
    n_samples: int
    n_features: int
    feature_names: List[str]
    target_name: Optional[str]
    created_at: str
    file_path: Optional[str] = None


@dataclass
class SessionResult:
    """Optimization session results"""
    session_id: str
    user_id: str
    dataset_hash: str
    algorithm: str
    timestamp: str
    best_fitness: float
    mean_fitness: float
    std_fitness: float
    execution_time: float
    hyperparameters: Dict[str, Any]
    convergence_curve: List[float]
    best_solution: List[float]
    n_runs: int
    improved_previous: bool = False


class IntelligentSessionManager:
    """
    Intelligent session manager with user profiles and automatic session handling
    """
    
    def __init__(self, base_dir: str = "persistent_state"):
        """
        Initialize session manager
        
        Parameters:
        -----------
        base_dir : str
            Base directory for storing all session data
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Directory structure
        self.users_dir = self.base_dir / "users"
        self.datasets_dir = self.base_dir / "datasets"
        self.sessions_dir = self.base_dir / "sessions"
        self.results_dir = self.base_dir / "results"
        
        for directory in [self.users_dir, self.datasets_dir, self.sessions_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Current session state
        self.current_user: Optional[UserProfile] = None
        self.current_dataset: Optional[DatasetInfo] = None
        self.current_session_id: Optional[str] = None
        
        # Load or create default user
        self._initialize_user()
    
    def _initialize_user(self):
        """Initialize user based on system username"""
        system_username = getpass.getuser()
        hostname = platform.node()
        
        user_id = hashlib.md5(f"{system_username}@{hostname}".encode()).hexdigest()[:16]
        
        user_file = self.users_dir / f"{user_id}.json"
        
        if user_file.exists():
            # Load existing user
            with open(user_file, 'r') as f:
                user_data = json.load(f)
            self.current_user = UserProfile(**user_data)
            self.current_user.last_active = datetime.now().isoformat()
            self._save_user()
        else:
            # Create new user
            self.current_user = UserProfile(
                username=system_username,
                user_id=user_id,
                created_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat()
            )
            self._save_user()
        
        print(f"👤 User: {self.current_user.username} (ID: {self.current_user.user_id})")
        print(f"📊 Total sessions: {self.current_user.total_sessions}")
    
    def _save_user(self):
        """Save current user profile"""
        if self.current_user:
            user_file = self.users_dir / f"{self.current_user.user_id}.json"
            with open(user_file, 'w') as f:
                json.dump(asdict(self.current_user), f, indent=2)
    
    def switch_user(self, username: str, hostname: Optional[str] = None) -> UserProfile:
        """
        Switch to a different user profile
        
        Parameters:
        -----------
        username : str
            Username to switch to
        hostname : str, optional
            Hostname (defaults to current machine)
            
        Returns:
        --------
        UserProfile : The switched user profile
        """
        if hostname is None:
            hostname = platform.node()
        
        user_id = hashlib.md5(f"{username}@{hostname}".encode()).hexdigest()[:16]
        user_file = self.users_dir / f"{user_id}.json"
        
        if user_file.exists():
            with open(user_file, 'r') as f:
                user_data = json.load(f)
            self.current_user = UserProfile(**user_data)
        else:
            self.current_user = UserProfile(
                username=username,
                user_id=user_id,
                created_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat()
            )
        
        self.current_user.last_active = datetime.now().isoformat()
        self._save_user()
        
        print(f"✅ Switched to user: {self.current_user.username}")
        return self.current_user
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all user profiles on this system"""
        users = []
        for user_file in self.users_dir.glob("*.json"):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
            users.append(user_data)
        
        return sorted(users, key=lambda x: x['last_active'], reverse=True)
    
    def compute_dataset_hash(self, data: pd.DataFrame, target_column: Optional[str] = None) -> str:
        """
        Compute unique hash for dataset based on shape and content sample
        
        Parameters:
        -----------
        data : pd.DataFrame
            Dataset to hash
        target_column : str, optional
            Target column name
            
        Returns:
        --------
        str : Dataset hash
        """
        # Create hash based on shape, columns, and sample of data
        hash_components = [
            str(data.shape),
            str(sorted(data.columns.tolist())),
            str(data.head(5).values.tobytes()),
            str(data.tail(5).values.tobytes()),
            str(target_column) if target_column else ""
        ]
        
        hash_string = "|".join(hash_components)
        dataset_hash = hashlib.sha256(hash_string.encode()).hexdigest()[:32]
        
        return dataset_hash
    
    def register_dataset(self, data: pd.DataFrame, dataset_name: str,
                        target_column: Optional[str] = None,
                        file_path: Optional[str] = None) -> DatasetInfo:
        """
        Register a dataset and return its info
        
        Parameters:
        -----------
        data : pd.DataFrame
            Dataset to register
        dataset_name : str
            Name for the dataset
        target_column : str, optional
            Target column name
        file_path : str, optional
            Original file path
            
        Returns:
        --------
        DatasetInfo : Dataset information
        """
        dataset_hash = self.compute_dataset_hash(data, target_column)
        
        # Check if dataset already exists
        dataset_file = self.datasets_dir / f"{dataset_hash}.json"
        
        if dataset_file.exists():
            with open(dataset_file, 'r') as f:
                dataset_data = json.load(f)
            dataset_info = DatasetInfo(**dataset_data)
            print(f"📂 Dataset already registered: {dataset_info.dataset_name}")
            print(f"   Hash: {dataset_hash}")
        else:
            dataset_info = DatasetInfo(
                dataset_hash=dataset_hash,
                dataset_name=dataset_name,
                n_samples=len(data),
                n_features=len(data.columns) - (1 if target_column else 0),
                feature_names=data.columns.tolist(),
                target_name=target_column,
                created_at=datetime.now().isoformat(),
                file_path=file_path
            )
            
            # Save dataset info
            with open(dataset_file, 'w') as f:
                json.dump(asdict(dataset_info), f, indent=2)
            
            print(f"✅ Dataset registered: {dataset_name}")
            print(f"   Hash: {dataset_hash}")
            print(f"   Samples: {dataset_info.n_samples}, Features: {dataset_info.n_features}")
        
        self.current_dataset = dataset_info
        return dataset_info
    
    def find_previous_session(self, dataset_hash: str, algorithm: str) -> Optional[SessionResult]:
        """
        Find previous session for same dataset and algorithm
        
        Parameters:
        -----------
        dataset_hash : str
            Dataset hash
        algorithm : str
            Algorithm name
            
        Returns:
        --------
        SessionResult or None : Previous session if exists
        """
        # Search for previous sessions
        user_results_dir = self.results_dir / self.current_user.user_id / dataset_hash
        
        if not user_results_dir.exists():
            return None
        
        best_session = None
        best_fitness = float('inf')
        
        for result_file in user_results_dir.glob(f"{algorithm}_*.json"):
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            
            if result_data['best_fitness'] < best_fitness:
                best_fitness = result_data['best_fitness']
                # Convert lists back for convergence_curve and best_solution
                best_session = SessionResult(**result_data)
        
        return best_session
    
    def should_resume_session(self, dataset_hash: str) -> Tuple[bool, Optional[str]]:
        """
        Check if session should be resumed for this dataset
        
        Parameters:
        -----------
        dataset_hash : str
            Dataset hash
            
        Returns:
        --------
        tuple : (should_resume, message)
        """
        if not self.current_user.preferences.get('auto_resume', True):
            return False, "Auto-resume disabled in preferences"
        
        # Check if any previous results exist for this dataset
        user_results_dir = self.results_dir / self.current_user.user_id / dataset_hash
        
        if not user_results_dir.exists() or not list(user_results_dir.glob("*.json")):
            return False, "No previous results found for this dataset"
        
        # Count previous experiments
        n_previous = len(list(user_results_dir.glob("*.json")))
        
        return True, f"Found {n_previous} previous result(s) for this dataset"
    
    def save_result(self, algorithm: str, best_fitness: float, mean_fitness: float,
                   std_fitness: float, execution_time: float, hyperparameters: Dict[str, Any],
                   convergence_curve: List[float], best_solution: np.ndarray,
                   n_runs: int, force_new_session: bool = False) -> SessionResult:
        """
        Save optimization result with intelligent update logic
        
        Parameters:
        -----------
        algorithm : str
            Algorithm name
        best_fitness : float
            Best fitness achieved
        mean_fitness : float
            Mean fitness across runs
        std_fitness : float
            Standard deviation of fitness
        execution_time : float
            Total execution time
        hyperparameters : dict
            Hyperparameters used
        convergence_curve : list
            Convergence curve
        best_solution : np.ndarray
            Best solution found
        n_runs : int
            Number of runs
        force_new_session : bool
            Force creation of new session
            
        Returns:
        --------
        SessionResult : Saved session result
        """
        if self.current_dataset is None:
            raise ValueError("No dataset registered. Call register_dataset() first.")
        
        dataset_hash = self.current_dataset.dataset_hash
        
        # Check for previous session
        previous_session = self.find_previous_session(dataset_hash, algorithm)
        
        improved = False
        action = "NEW"
        
        if previous_session and not force_new_session:
            if self.current_user.preferences.get('auto_update_best', True):
                if best_fitness < previous_session.best_fitness:
                    improved = True
                    action = "IMPROVED"
                    print(f"🎯 Improvement detected!")
                    print(f"   Previous best: {previous_session.best_fitness:.6f}")
                    print(f"   New best: {best_fitness:.6f}")
                    print(f"   Improvement: {((previous_session.best_fitness - best_fitness) / previous_session.best_fitness * 100):.2f}%")
                else:
                    action = "NO_IMPROVEMENT"
                    print(f"ℹ️  No improvement over previous best: {previous_session.best_fitness:.6f}")
                    print(f"   Current best: {best_fitness:.6f}")
                    
                    if not self.current_user.preferences.get('save_worse_results', False):
                        print(f"⏭️  Skipping save (no improvement)")
                        return previous_session
        
        # Create session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{algorithm}_{timestamp}"
        
        # Create result
        result = SessionResult(
            session_id=session_id,
            user_id=self.current_user.user_id,
            dataset_hash=dataset_hash,
            algorithm=algorithm,
            timestamp=datetime.now().isoformat(),
            best_fitness=best_fitness,
            mean_fitness=mean_fitness,
            std_fitness=std_fitness,
            execution_time=execution_time,
            hyperparameters=hyperparameters,
            convergence_curve=convergence_curve,
            best_solution=best_solution.tolist() if isinstance(best_solution, np.ndarray) else best_solution,
            n_runs=n_runs,
            improved_previous=improved
        )
        
        # Save result
        user_results_dir = self.results_dir / self.current_user.user_id / dataset_hash
        user_results_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = user_results_dir / f"{session_id}.json"
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        # Update user stats
        self.current_user.total_experiments += 1
        self._save_user()
        
        print(f"✅ Result saved: {action}")
        print(f"   Session ID: {session_id}")
        print(f"   File: {result_file}")
        
        return result
    
    def get_session_history(self, dataset_hash: Optional[str] = None,
                           algorithm: Optional[str] = None,
                           limit: int = 10) -> List[SessionResult]:
        """
        Get session history for current user
        
        Parameters:
        -----------
        dataset_hash : str, optional
            Filter by dataset hash
        algorithm : str, optional
            Filter by algorithm
        limit : int
            Maximum number of results
            
        Returns:
        --------
        list : List of SessionResult objects
        """
        user_results_dir = self.results_dir / self.current_user.user_id
        
        if not user_results_dir.exists():
            return []
        
        results = []
        
        if dataset_hash:
            search_dir = user_results_dir / dataset_hash
            if search_dir.exists():
                result_files = list(search_dir.glob("*.json"))
            else:
                result_files = []
        else:
            result_files = list(user_results_dir.rglob("*.json"))
        
        for result_file in result_files:
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            
            if algorithm and result_data['algorithm'] != algorithm:
                continue
            
            results.append(SessionResult(**result_data))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results[:limit]
    
    def get_best_result(self, dataset_hash: str, algorithm: Optional[str] = None) -> Optional[SessionResult]:
        """
        Get best result for a dataset
        
        Parameters:
        -----------
        dataset_hash : str
            Dataset hash
        algorithm : str, optional
            Filter by algorithm
            
        Returns:
        --------
        SessionResult or None : Best result
        """
        results = self.get_session_history(dataset_hash, algorithm, limit=1000)
        
        if not results:
            return None
        
        return min(results, key=lambda x: x.best_fitness)
    
    def compare_with_history(self, dataset_hash: str, algorithm: str) -> Dict[str, Any]:
        """
        Compare current algorithm with historical performance
        
        Parameters:
        -----------
        dataset_hash : str
            Dataset hash
        algorithm : str
            Algorithm name
            
        Returns:
        --------
        dict : Comparison statistics
        """
        results = self.get_session_history(dataset_hash, algorithm, limit=1000)
        
        if not results:
            return {
                'n_experiments': 0,
                'message': 'No previous experiments found'
            }
        
        fitness_values = [r.best_fitness for r in results]
        
        return {
            'n_experiments': len(results),
            'best_ever': min(fitness_values),
            'worst_ever': max(fitness_values),
            'mean': np.mean(fitness_values),
            'std': np.std(fitness_values),
            'median': np.median(fitness_values),
            'recent_best': results[0].best_fitness if results else None,
            'improvement_rate': self._calculate_improvement_rate(results)
        }
    
    def _calculate_improvement_rate(self, results: List[SessionResult]) -> float:
        """Calculate improvement rate over time"""
        if len(results) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_results = sorted(results, key=lambda x: x.timestamp)
        
        first_fitness = sorted_results[0].best_fitness
        last_fitness = sorted_results[-1].best_fitness
        
        if first_fitness == 0:
            return 0.0
        
        improvement = (first_fitness - last_fitness) / first_fitness * 100
        return improvement
    
    def export_session_report(self, output_file: str = "session_report.json"):
        """
        Export comprehensive session report for current user
        
        Parameters:
        -----------
        output_file : str
            Output file path
        """
        report = {
            'user': asdict(self.current_user),
            'generated_at': datetime.now().isoformat(),
            'datasets': [],
            'total_results': 0
        }
        
        user_results_dir = self.results_dir / self.current_user.user_id
        
        if user_results_dir.exists():
            for dataset_dir in user_results_dir.iterdir():
                if dataset_dir.is_dir():
                    dataset_hash = dataset_dir.name
                    
                    # Load dataset info
                    dataset_file = self.datasets_dir / f"{dataset_hash}.json"
                    if dataset_file.exists():
                        with open(dataset_file, 'r') as f:
                            dataset_info = json.load(f)
                    else:
                        dataset_info = {'dataset_hash': dataset_hash}
                    
                    # Get all results for this dataset
                    results = self.get_session_history(dataset_hash, limit=1000)
                    
                    dataset_summary = {
                        'dataset_info': dataset_info,
                        'n_experiments': len(results),
                        'algorithms_tested': list(set(r.algorithm for r in results)),
                        'best_fitness': min(r.best_fitness for r in results) if results else None,
                        'results': [asdict(r) for r in results]
                    }
                    
                    report['datasets'].append(dataset_summary)
                    report['total_results'] += len(results)
        
        # Save report
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Session report exported to: {output_path}")
        print(f"   Total datasets: {len(report['datasets'])}")
        print(f"   Total experiments: {report['total_results']}")
        
        return report


# Convenience functions
def get_session_manager() -> IntelligentSessionManager:
    """Get global session manager instance"""
    global _session_manager
    if '_session_manager' not in globals():
        _session_manager = IntelligentSessionManager()
    return _session_manager


def quick_save(algorithm: str, best_fitness: float, **kwargs):
    """Quick save result using global session manager"""
    manager = get_session_manager()
    return manager.save_result(algorithm, best_fitness, **kwargs)
