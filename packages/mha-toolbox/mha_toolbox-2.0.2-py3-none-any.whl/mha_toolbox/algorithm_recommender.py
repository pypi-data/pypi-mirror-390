"""
Intelligent Algorithm Recommendation System
===========================================

Suggests optimal algorithms based on dataset characteristics, problem type,
and user preferences. Provides confidence scores and reasoning.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional


class AlgorithmRecommender:
    """
    Intelligent system to recommend optimization algorithms based on dataset characteristics,
    problem type, computational constraints, and historical performance.
    """
    
    def __init__(self):
        self.algorithm_profiles = self._initialize_algorithm_profiles()
        self.hybrid_profiles = self._initialize_hybrid_profiles()
        
    def _initialize_hybrid_profiles(self) -> Dict:
        """Initialize hybrid algorithm profiles"""
        return {
            'PSO_GA_HYBRID': {
                'best_for': ['complex', 'multimodal', 'large_search_space'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium',
                'description': 'Combines PSO exploration with GA exploitation'
            },
            'GWO_PSO_HYBRID': {
                'best_for': ['continuous', 'complex_landscape', 'feature_selection'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_high',
                'complexity': 'medium',
                'description': 'Grey Wolf hunting with particle swarm dynamics'
            },
            'DE_PSO_HYBRID': {
                'best_for': ['high_dimensional', 'continuous', 'numerical'],
                'speed': 'fast',
                'exploration': 'medium',
                'exploitation': 'very_high',
                'dimensions': 'high',
                'complexity': 'low',
                'description': 'Differential Evolution with PSO velocity updates'
            },
            'SA_GA_HYBRID': {
                'best_for': ['combinatorial', 'discrete', 'scheduling'],
                'speed': 'slow',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'high',
                'description': 'Simulated Annealing with genetic operators'
            },
            'ACO_PSO_HYBRID': {
                'best_for': ['graph_problems', 'routing', 'network_optimization'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Ant Colony pheromone with PSO movement'
            },
            'ABC_DE_HYBRID': {
                'best_for': ['numerical_optimization', 'engineering', 'constrained'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium',
                'description': 'Artificial Bee Colony with DE mutation'
            },
            'WOA_GA_HYBRID': {
                'best_for': ['feature_selection', 'classification', 'large_datasets'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_high',
                'complexity': 'low',
                'description': 'Whale Optimization with genetic diversity'
            },
            'BA_PSO_HYBRID': {
                'best_for': ['multimodal', 'complex_landscape', 'real_world'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Bat Algorithm echolocation with PSO'
            },
            'FA_DE_HYBRID': {
                'best_for': ['continuous', 'multimodal', 'clustering'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Firefly attraction with DE mutation'
            }
        }
        
    def _initialize_algorithm_profiles(self) -> Dict:
        """
        Define algorithm profiles with their strengths, weaknesses, and use cases
        """
        return {
            # Swarm Intelligence
            'PSO': {
                'best_for': ['continuous', 'medium_dim', 'smooth', 'fast_convergence'],
                'speed': 'very_fast',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'very_low',
                'description': 'Particle Swarm Optimization - social behavior simulation',
                'typical_use': 'Feature selection, parameter tuning, continuous optimization'
            },
            'GA': {
                'best_for': ['discrete', 'combinatorial', 'multimodal', 'robust'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'description': 'Genetic Algorithm - evolution-inspired',
                'typical_use': 'Scheduling, routing, design optimization'
            },
            'DE': {
                'best_for': ['continuous', 'high_dim', 'complex', 'numerical'],
                'speed': 'fast',
                'exploration': 'medium',
                'exploitation': 'very_high',
                'dimensions': 'medium_to_high',
                'complexity': 'low',
                'description': 'Differential Evolution - mutation-based',
                'typical_use': 'Engineering optimization, function approximation'
            },
            'GWO': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'low'
            },
            'WOA': {
                'best_for': ['continuous', 'multimodal', 'exploration'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low'
            },
            'SMA': {
                'best_for': ['continuous', 'complex', 'noisy'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'medium'
            },
            'SA': {
                'best_for': ['continuous', 'combinatorial', 'simple'],
                'speed': 'slow',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low',
                'complexity': 'very_low'
            },
            'ACO': {
                'best_for': ['discrete', 'graph', 'combinatorial'],
                'speed': 'medium',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium'
            },
            
            # Hybrid algorithms
            'PSO_GA_Hybrid': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'high',
                'dimensions': 'low_to_high',
                'complexity': 'medium'
            },
            'GWO_PSO_Hybrid': {
                'best_for': ['continuous', 'high_dim', 'complex'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'very_high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium'
            },
            'DE_PSO_Hybrid': {
                'best_for': ['continuous', 'very_high_dim', 'complex'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'high',
                'complexity': 'medium'
            },
            'ACO_PSO_Hybrid': {
                'best_for': ['mixed', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'high'
            },
            'SA_PSO_Hybrid': {
                'best_for': ['continuous', 'noisy', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium'
            },
            'GWO_DE_Hybrid': {
                'best_for': ['continuous', 'very_high_dim', 'multimodal'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'very_high',
                'dimensions': 'very_high',
                'complexity': 'medium'
            },
        }
    
    def analyze_dataset(self, X: np.ndarray, y: np.ndarray = None) -> Dict:
        """
        Analyze dataset characteristics
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray, optional
            Target vector
            
        Returns
        -------
        Dict
            Dataset characteristics
        """
        n_samples, n_features = X.shape
        
        characteristics = {
            'n_samples': n_samples,
            'n_features': n_features,
            'sample_size': self._categorize_size(n_samples),
            'dimensionality': self._categorize_dimensions(n_features),
            'complexity': self._estimate_complexity(X),
            'data_type': self._determine_data_type(X),
            'feature_correlation': self._check_correlation(X),
            'has_noise': self._detect_noise(X),
        }
        
        if y is not None:
            characteristics['task_type'] = self._determine_task_type(y)
            characteristics['class_balance'] = self._check_class_balance(y)
        
        return characteristics
    
    def _categorize_size(self, n_samples: int) -> str:
        """Categorize dataset size"""
        if n_samples < 100:
            return 'small'
        elif n_samples < 1000:
            return 'medium'
        elif n_samples < 10000:
            return 'large'
        else:
            return 'very_large'
    
    def _categorize_dimensions(self, n_features: int) -> str:
        """Categorize dimensionality"""
        if n_features <= 10:
            return 'low'
        elif n_features <= 50:
            return 'medium'
        elif n_features <= 200:
            return 'high'
        else:
            return 'very_high'
    
    def _estimate_complexity(self, X: np.ndarray) -> str:
        """Estimate problem complexity"""
        # Use feature variance and correlation as complexity indicators
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        variance = np.var(X_scaled, axis=0).mean()
        
        if variance < 0.5:
            return 'simple'
        elif variance < 1.5:
            return 'medium'
        else:
            return 'complex'
    
    def _determine_data_type(self, X: np.ndarray) -> str:
        """Determine if data is continuous or discrete"""
        # Check if data is mostly integer-like
        is_integer = np.allclose(X, X.astype(int), rtol=1e-5)
        unique_ratio = len(np.unique(X)) / X.size
        
        if is_integer and unique_ratio < 0.1:
            return 'discrete'
        else:
            return 'continuous'
    
    def _check_correlation(self, X: np.ndarray) -> str:
        """Check feature correlation"""
        if X.shape[1] < 2:
            return 'none'
        
        corr_matrix = np.corrcoef(X.T)
        avg_corr = np.mean(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        
        if avg_corr < 0.3:
            return 'low'
        elif avg_corr < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _detect_noise(self, X: np.ndarray) -> bool:
        """Simple noise detection"""
        # Check for outliers using IQR method
        Q1 = np.percentile(X, 25, axis=0)
        Q3 = np.percentile(X, 75, axis=0)
        IQR = Q3 - Q1
        outliers = ((X < (Q1 - 1.5 * IQR)) | (X > (Q3 + 1.5 * IQR))).sum()
        outlier_ratio = outliers / X.size
        
        return outlier_ratio > 0.05
    
    def _determine_task_type(self, y: np.ndarray) -> str:
        """Determine if classification or regression"""
        unique_values = len(np.unique(y))
        if unique_values <= 20:
            return 'classification'
        else:
            return 'regression'
    
    def _check_class_balance(self, y: np.ndarray) -> str:
        """Check class balance for classification"""
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) <= 1:
            return 'single_class'
        
        balance_ratio = counts.min() / counts.max()
        if balance_ratio > 0.8:
            return 'balanced'
        elif balance_ratio > 0.5:
            return 'slightly_imbalanced'
        else:
            return 'imbalanced'
    
    def recommend_algorithms(self, X: np.ndarray, y: np.ndarray = None, 
                           top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Recommend top-k algorithms for the given dataset
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray, optional
            Target vector
        top_k : int
            Number of recommendations to return
            
        Returns
        -------
        List[Tuple[str, float, str]]
            List of (algorithm_name, confidence_score, reason) tuples
        """
        characteristics = self.analyze_dataset(X, y)
        scores = {}
        
        for algo_name, profile in self.algorithm_profiles.items():
            score = self._calculate_match_score(characteristics, profile)
            scores[algo_name] = score
        
        # Sort by score
        sorted_algos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate recommendations with reasons
        recommendations = []
        for algo_name, score in sorted_algos[:top_k]:
            reason = self._generate_recommendation_reason(
                algo_name, characteristics, self.algorithm_profiles[algo_name]
            )
            recommendations.append((algo_name, score, reason))
        
        return recommendations
    
    def _calculate_match_score(self, characteristics: Dict, profile: Dict) -> float:
        """Calculate how well an algorithm matches dataset characteristics"""
        score = 0.0
        max_possible_score = 15.0  # Increased max score for better scaling
        
        # Dimensionality match (0-4 points)
        dim_map = {
            'low': ['low', 'low_to_medium'],
            'medium': ['low_to_medium', 'medium', 'medium_to_high'],
            'high': ['medium_to_high', 'high', 'low_to_high'],
            'very_high': ['high', 'very_high', 'medium_to_high', 'low_to_high']
        }
        if profile['dimensions'] in dim_map.get(characteristics['dimensionality'], []):
            score += 4.0
        elif any(d in dim_map.get(characteristics['dimensionality'], []) for d in [profile['dimensions']]):
            score += 2.0
        
        # Data type match (0-3 points)
        if characteristics['data_type'] in profile['best_for']:
            score += 3.0
        
        # Complexity match (0-3 points)
        if characteristics['complexity'] in profile['best_for']:
            score += 3.0
        elif characteristics['complexity'] == 'complex' and 'multimodal' in profile['best_for']:
            score += 2.0
        
        # Noise handling (0-2 points)
        if characteristics['has_noise']:
            if profile['exploitation'] in ['high', 'very_high']:
                score += 2.0
            elif profile['exploitation'] == 'medium':
                score += 1.0
        else:
            score += 1.0  # Give some points for clean data
        
        # Speed bonus for large datasets (0-2 points)
        if characteristics['sample_size'] in ['large', 'very_large']:
            if profile['speed'] in ['fast', 'very_fast']:
                score += 2.0
            elif profile['speed'] == 'medium':
                score += 1.0
        else:
            if profile['speed'] in ['fast', 'very_fast', 'medium']:
                score += 1.0
        
        # Exploration bonus for complex problems (0-2 points)
        if characteristics['complexity'] in ['complex', 'medium']:
            if profile['exploration'] in ['high', 'very_high']:
                score += 2.0
            elif profile['exploration'] == 'medium':
                score += 1.0
        
        # Feature selection bonus
        if 'feature_selection' in profile['best_for'] or 'classification' in profile['best_for']:
            score += 1.0
        
        # Normalize score to 0-10 range
        normalized_score = (score / max_possible_score) * 10.0
        
        return min(10.0, max(5.0, normalized_score))  # Ensure scores are between 5-10
    
    def _generate_recommendation_reason(self, algo_name: str, 
                                       characteristics: Dict, 
                                       profile: Dict) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if characteristics['dimensionality'] in ['high', 'very_high']:
            reasons.append(f"Handles {characteristics['dimensionality']}-dimensional data well")
        
        if characteristics['data_type'] in profile['best_for']:
            reasons.append(f"Optimized for {characteristics['data_type']} data")
        
        if characteristics['complexity'] == 'complex':
            if profile['exploration'] in ['high', 'very_high']:
                reasons.append("Strong exploration for complex problems")
        
        if characteristics['has_noise']:
            if profile['exploitation'] in ['high', 'very_high']:
                reasons.append("Robust to noisy data")
        
        if profile['speed'] == 'fast':
            reasons.append("Fast convergence")
        
        if not reasons:
            reasons.append("Good general-purpose algorithm")
        
        return "; ".join(reasons)
    
    def get_recommended_parameters(self, algo_name: str, 
                                  characteristics: Dict) -> Dict:
        """
        Get recommended hyperparameters for an algorithm based on dataset
        
        Parameters
        ----------
        algo_name : str
            Algorithm name
        characteristics : Dict
            Dataset characteristics
            
        Returns
        -------
        Dict
            Recommended hyperparameters
        """
        # Base parameters
        params = {
            'pop_size': 50,
            'max_iter': 100
        }
        
        # Adjust based on dataset size
        if characteristics['n_samples'] > 1000:
            params['pop_size'] = 30
            params['max_iter'] = 150
        elif characteristics['n_samples'] < 100:
            params['pop_size'] = 20
            params['max_iter'] = 200
        
        # Adjust based on dimensionality
        if characteristics['dimensionality'] in ['high', 'very_high']:
            params['pop_size'] = min(100, characteristics['n_features'] * 10)
            params['max_iter'] = 200
        
        return params
