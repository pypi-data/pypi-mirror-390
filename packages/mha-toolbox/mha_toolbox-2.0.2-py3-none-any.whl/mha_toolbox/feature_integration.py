"""
Extended Features Integration Module
=====================================

Integrates all 14 extended features requested:
1. More algorithms (in progress)
2. Algorithm categorization ✓
3. Frontend connection (this module)
4. Beginner/Advanced modes ✓
5. Dimension-aware hyperparameters ✓
6. Enhanced plots ✓
7. Binary/multiclass support (here)
8. Algorithm recommendation ✓
9. Custom datasets (here)
10. CSV export ✓
11. Box plots ✓
12. MLflow integration (here)
13. Feature threshold slider ✓
14. Workflow implementation ✓
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from mha_toolbox.algorithm_categories import (
    ALGORITHM_CATEGORIES,
    recommend_algorithms,
    get_algorithms_by_difficulty
)
from mha_toolbox.hyperparameter_config import HyperparameterManager, get_preset_config
from mha_toolbox.professional_visualizer import (
    plot_feature_threshold,
    plot_comparison_box_with_stats,
    create_workflow_dashboard,
    export_results_to_csv,
    create_statistical_table
)


class DatasetGenerator:
    """
    Custom dataset generator by sector/field (Feature #9)
    """
    
    SECTOR_TEMPLATES = {
        'healthcare': {
            'n_features': 30,
            'n_samples': 569,
            'n_classes': 2,
            'n_informative': 20,
            'n_redundant': 5,
            'class_sep': 1.0,
            'feature_names': ['mean_radius', 'mean_texture', 'mean_perimeter', 'mean_area', 
                            'mean_smoothness', 'mean_compactness', 'mean_concavity'],
            'description': 'Medical diagnostic data (similar to breast cancer dataset)'
        },
        'finance': {
            'n_features': 20,
            'n_samples': 1000,
            'n_classes': 2,
            'n_informative': 15,
            'n_redundant': 3,
            'class_sep': 0.8,
            'feature_names': ['income', 'age', 'credit_score', 'debt_ratio', 'employment_years',
                            'loan_amount', 'payment_history'],
            'description': 'Credit risk assessment / fraud detection'
        },
        'retail': {
            'n_features': 25,
            'n_samples': 2000,
            'n_classes': 3,
            'n_informative': 18,
            'n_redundant': 4,
            'class_sep': 1.2,
            'feature_names': ['purchase_frequency', 'avg_transaction', 'recency', 'monetary',
                            'product_diversity', 'seasonality', 'loyalty_years'],
            'description': 'Customer segmentation / churn prediction'
        },
        'manufacturing': {
            'n_features': 40,
            'n_samples': 1500,
            'n_classes': 2,
            'n_informative': 30,
            'n_redundant': 6,
            'class_sep': 0.9,
            'feature_names': ['temperature', 'pressure', 'vibration', 'power_consumption',
                            'operating_hours', 'maintenance_interval', 'quality_score'],
            'description': 'Predictive maintenance / quality control'
        },
        'telecom': {
            'n_features': 18,
            'n_samples': 3000,
            'n_classes': 2,
            'n_informative': 12,
            'n_redundant': 3,
            'class_sep': 0.7,
            'feature_names': ['call_duration', 'data_usage', 'monthly_charges', 'contract_length',
                            'customer_service_calls', 'network_quality', 'roaming'],
            'description': 'Customer churn prediction'
        },
        'energy': {
            'n_features': 15,
            'n_samples': 1200,
            'n_classes': 3,
            'n_informative': 10,
            'n_redundant': 2,
            'class_sep': 1.1,
            'feature_names': ['power_demand', 'temperature', 'humidity', 'wind_speed', 
                            'solar_radiation', 'time_of_day', 'day_of_week'],
            'description': 'Energy demand forecasting / consumption classification'
        }
    }
    
    @classmethod
    def generate_dataset(cls, sector: str, n_samples: Optional[int] = None,
                        n_features: Optional[int] = None,
                        random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate synthetic dataset based on sector template
        
        Returns:
            X: Feature matrix
            y: Target vector
            feature_names: List of feature names
        """
        if sector not in cls.SECTOR_TEMPLATES:
            raise ValueError(f"Unknown sector: {sector}. Available: {list(cls.SECTOR_TEMPLATES.keys())}")
        
        template = cls.SECTOR_TEMPLATES[sector]
        
        # Override template values if provided
        n_samples = n_samples or template['n_samples']
        n_features = n_features or template['n_features']
        
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=template['n_informative'],
            n_redundant=template['n_redundant'],
            n_classes=template['n_classes'],
            class_sep=template['class_sep'],
            random_state=random_state
        )
        
        # Generate feature names
        base_names = template['feature_names']
        feature_names = []
        for i in range(n_features):
            if i < len(base_names):
                feature_names.append(base_names[i])
            else:
                feature_names.append(f'feature_{i+1}')
        
        return X, y, feature_names
    
    @classmethod
    def render_generator_ui(cls):
        """Render Streamlit UI for dataset generation"""
        st.subheader("🏭 Custom Dataset Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sector = st.selectbox(
                "Select Sector/Domain",
                options=list(cls.SECTOR_TEMPLATES.keys()),
                format_func=lambda x: x.capitalize()
            )
        
        template = cls.SECTOR_TEMPLATES[sector]
        
        with col2:
            st.info(f"**{sector.capitalize()} Dataset**\n\n{template['description']}")
        
        with st.expander("📊 Dataset Configuration"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                n_samples = st.number_input(
                    "Number of Samples",
                    min_value=100,
                    max_value=10000,
                    value=template['n_samples']
                )
            
            with col2:
                n_features = st.number_input(
                    "Number of Features",
                    min_value=10,
                    max_value=100,
                    value=template['n_features']
                )
            
            with col3:
                random_state = st.number_input(
                    "Random Seed",
                    min_value=0,
                    max_value=9999,
                    value=42
                )
        
        if st.button("🎲 Generate Dataset", type="primary"):
            with st.spinner("Generating dataset..."):
                X, y, feature_names = cls.generate_dataset(
                    sector, n_samples, n_features, random_state
                )
                
                # Store in session state
                st.session_state['X_train'] = X
                st.session_state['y_train'] = y
                st.session_state['feature_names'] = feature_names
                st.session_state['dataset_loaded'] = True
                st.session_state['dataset_name'] = f"{sector}_custom"
                
                st.success(f"✅ Generated {sector} dataset: {X.shape[0]} samples × {X.shape[1]} features")
                
                # Show preview
                df_preview = pd.DataFrame(X[:10], columns=feature_names[:X.shape[1]])
                df_preview['Target'] = y[:10]
                st.dataframe(df_preview, use_container_width=True)
        
        return sector, template


class BinaryMulticlassSupport:
    """
    Binary and multiclass classification support (Feature #7)
    """
    
    @staticmethod
    def detect_problem_type(y: np.ndarray) -> str:
        """Detect if problem is binary or multiclass"""
        n_classes = len(np.unique(y))
        
        if n_classes == 2:
            return 'binary'
        elif n_classes > 2:
            return 'multiclass'
        else:
            return 'unknown'
    
    @staticmethod
    def get_fitness_function(problem_type: str):
        """Get appropriate fitness function based on problem type"""
        if problem_type == 'binary':
            # Fitness for binary classification
            def binary_fitness(solution, X, y):
                from sklearn.neighbors import KNeighborsClassifier
                from sklearn.model_selection import cross_val_score
                
                # Select features
                selected = solution > 0.5
                if not any(selected):
                    return 1.0  # Worst fitness
                
                X_selected = X[:, selected]
                
                # Train classifier
                knn = KNeighborsClassifier(n_neighbors=5)
                scores = cross_val_score(knn, X_selected, y, cv=3, scoring='accuracy')
                
                # Fitness = 1 - accuracy (minimize)
                fitness = 1 - scores.mean()
                
                # Penalize too many features
                feature_ratio = selected.sum() / len(solution)
                fitness += 0.1 * feature_ratio
                
                return fitness
            
            return binary_fitness
        
        elif problem_type == 'multiclass':
            # Fitness for multiclass classification  
            def multiclass_fitness(solution, X, y):
                from sklearn.neighbors import KNeighborsClassifier
                from sklearn.model_selection import cross_val_score
                
                selected = solution > 0.5
                if not any(selected):
                    return 1.0
                
                X_selected = X[:, selected]
                
                # Use macro-averaged F1 for multiclass
                knn = KNeighborsClassifier(n_neighbors=5)
                scores = cross_val_score(knn, X_selected, y, cv=3, scoring='f1_macro')
                
                fitness = 1 - scores.mean()
                feature_ratio = selected.sum() / len(solution)
                fitness += 0.15 * feature_ratio  # Higher penalty for multiclass
                
                return fitness
            
            return multiclass_fitness
    
    @staticmethod
    def render_problem_indicator(y: np.ndarray):
        """Render problem type indicator in Streamlit"""
        problem_type = BinaryMulticlassSupport.detect_problem_type(y)
        n_classes = len(np.unique(y))
        
        if problem_type == 'binary':
            st.success(f"✅ **Binary Classification** ({n_classes} classes)")
        elif problem_type == 'multiclass':
            st.warning(f"⚠️ **Multiclass Classification** ({n_classes} classes)")
        
        class_dist = pd.Series(y).value_counts().sort_index()
        st.write("**Class Distribution:**")
        st.bar_chart(class_dist)


class MLflowIntegration:
    """
    MLflow experiment tracking integration (Feature #12)
    """
    
    def __init__(self, experiment_name: str = "MHA_Optimization"):
        self.experiment_name = experiment_name
        self.enabled = MLFLOW_AVAILABLE
        
        if self.enabled:
            mlflow.set_experiment(experiment_name)
    
    def log_run(self, algorithm_name: str, parameters: Dict, 
                results: Dict, dataset_name: str):
        """Log optimization run to MLflow"""
        if not self.enabled:
            return
        
        with mlflow.start_run(run_name=f"{algorithm_name}_{dataset_name}"):
            # Log parameters
            mlflow.log_param("algorithm", algorithm_name)
            mlflow.log_param("dataset", dataset_name)
            mlflow.log_params(parameters)
            
            # Log metrics
            mlflow.log_metric("best_fitness", results.get('best_fitness', 0))
            mlflow.log_metric("accuracy", results.get('accuracy', 0))
            mlflow.log_metric("execution_time", results.get('execution_time', 0))
            mlflow.log_metric("n_selected_features", results.get('n_selected_features', 0))
            
            if 'mean_fitness' in results:
                mlflow.log_metric("mean_fitness", results['mean_fitness'])
                mlflow.log_metric("std_fitness", results['std_fitness'])
            
            # Log convergence curve as artifact
            if 'convergence_curve' in results:
                conv_df = pd.DataFrame({
                    'iteration': range(1, len(results['convergence_curve']) + 1),
                    'fitness': results['convergence_curve']
                })
                conv_df.to_csv("convergence.csv", index=False)
                mlflow.log_artifact("convergence.csv")
    
    @staticmethod
    def render_mlflow_ui():
        """Render MLflow integration UI"""
        if not MLFLOW_AVAILABLE:
            st.warning("⚠️ MLflow not installed. Install with: `pip install mlflow`")
            return False
        
        with st.expander("📊 MLflow Tracking"):
            col1, col2 = st.columns(2)
            
            with col1:
                enable_mlflow = st.checkbox("Enable MLflow Tracking", value=False)
            
            with col2:
                if enable_mlflow:
                    experiment_name = st.text_input(
                        "Experiment Name",
                        value="MHA_Optimization"
                    )
                    st.session_state['mlflow_experiment'] = experiment_name
            
            if enable_mlflow:
                st.info("💡 View results with: `mlflow ui` in terminal")
        
        return enable_mlflow if MLFLOW_AVAILABLE else False


def render_enhanced_algorithm_selection(X: np.ndarray, y: np.ndarray):
    """
    Render enhanced algorithm selection with categorization and recommendations
    (Features #2, #3, #8)
    """
    st.subheader("🎯 Smart Algorithm Selection")
    
    # Get dataset characteristics
    n_samples, n_features = X.shape
    n_classes = len(np.unique(y))
    
    dataset_features = {
        'n_features': n_features,
        'n_samples': n_samples,
        'n_classes': n_classes,
        'problem_type': 'feature_selection'
    }
    
    # Show recommendations
    with st.expander("🤖 AI-Powered Recommendations", expanded=True):
        recommendations = recommend_algorithms(dataset_features)
        
        st.write(f"**Top Recommendations for your dataset** ({n_samples} samples × {n_features} features, {n_classes} classes)")
        
        rec_df = pd.DataFrame(recommendations).head(10)
        rec_df['score'] = rec_df['score'].apply(lambda x: f"{x:.2f}")
        rec_df.columns = ['Algorithm', 'Score', 'Reason']
        st.dataframe(rec_df, use_container_width=True)
    
    # Selection by difficulty
    st.write("**Select by Experience Level:**")
    difficulty = st.radio(
        "Your Experience",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )
    
    # Get algorithms by difficulty
    available_algos = get_algorithms_by_difficulty(difficulty.lower())
    
    # Group by category
    selected_algorithms = []
    
    for category_name, category_info in ALGORITHM_CATEGORIES.items():
        if category_info['difficulty'] == difficulty.lower() or difficulty == "Advanced":
            category_algos = [a for a in category_info['algorithms'] if a in available_algos]
            
            if category_algos:
                with st.expander(f"{category_name} ({len(category_algos)} algorithms)"):
                    st.write(f"*{category_info['description']}*")
                    
                    for algo in category_algos:
                        if st.checkbox(algo.upper(), key=f"algo_{algo}"):
                            selected_algorithms.append(algo)
    
    return selected_algorithms


def render_dimension_aware_hyperparameters(algorithm: str, n_features: int):
    """
    Render dimension-aware hyperparameter controls (Feature #5)
    """
    st.subheader("⚙️ Hyperparameter Configuration")
    
    hp_manager = HyperparameterManager(dimensions=n_features)
    
    # Preset selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        preset = st.selectbox(
            "Configuration Preset",
            options=['fast', 'standard', 'thorough', 'research'],
            format_func=lambda x: {
                'fast': '⚡ Fast (Quick evaluation)',
                'standard': '⚖️ Standard (Balanced)',
                'thorough': '🔍 Thorough (Comprehensive)',
                'research': '🎓 Research (Publication-quality)'
            }[x]
        )
    
    with col2:
        custom = st.checkbox("Customize Parameters")
    
    if preset:
        config = get_preset_config(preset, n_features)
        st.info(f"**{preset.capitalize()} Configuration:**\n\n"
               f"• Population: {config['population_size']}\n"
               f"• Iterations: {config['max_iterations']}\n"
               f"• Runs: {config['n_runs']}")
    
    parameters = {}
    
    if custom:
        # Get algorithm-specific parameters
        param_bounds = hp_manager.get_parameter_bounds(algorithm)
        
        with st.expander("🎛️ Advanced Parameters"):
            for param_name, param_info in param_bounds.items():
                if param_info['user_adjustable']:
                    if param_info['type'] == 'int':
                        parameters[param_name] = st.slider(
                            param_info['description'],
                            min_value=int(param_info['min']),
                            max_value=int(param_info['max']),
                            value=int(param_info['default']),
                            key=f"param_{algorithm}_{param_name}"
                        )
                    elif param_info['type'] == 'float':
                        parameters[param_name] = st.slider(
                            param_info['description'],
                            min_value=float(param_info['min']),
                            max_value=float(param_info['max']),
                            value=float(param_info['default']),
                            step=0.01,
                            key=f"param_{algorithm}_{param_name}"
                        )
    else:
        # Use preset config
        parameters = config
    
    return parameters
