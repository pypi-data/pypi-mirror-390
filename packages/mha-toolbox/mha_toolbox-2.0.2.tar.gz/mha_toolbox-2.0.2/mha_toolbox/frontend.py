"""
Web-based Frontend for MHA Toolbox

This module provides a comprehensive web interface for the MHA Toolbox using Streamlit.
Users can interact with all features through an intuitive graphical interface.
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from sklearn.datasets import load_breast_cancer, load_wine, load_iris, load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import time
import json

# Import MHA Toolbox
try:
    import mha_toolbox as mha
    from mha_toolbox.demo_system import MHADemoSystem
    from mha_toolbox.advanced_hybrid import AdvancedHybridOptimizer
except ImportError:
    st.error("MHA Toolbox not found. Please install the package.")
    st.stop()


def configure_page():
    """Configure Streamlit page."""
    st.set_page_config(
        page_title="MHA Toolbox - Interactive Interface",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_navigation():
    """Create sidebar navigation."""
    st.sidebar.title("🧬 MHA Toolbox")
    st.sidebar.markdown("**Professional Metaheuristic Algorithms**")
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "🏠 Home",
            "🎯 Function Optimization", 
            "🧬 Feature Selection",
            "🔬 Hybrid Algorithms",
            "📊 Algorithm Comparison",
            "🌍 Real-world Problems",
            "📈 Visualization Center",
            "⚙️ Algorithm Explorer",
            "📚 Documentation"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Quick Actions")
    
    if st.sidebar.button("🏃‍♂️ Run Quick Demo"):
        st.session_state.run_quick_demo = True
    
    if st.sidebar.button("📊 Show All Algorithms"):
        st.session_state.show_algorithms = True
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About")
    st.sidebar.info("""
    **MHA Toolbox** provides 36+ metaheuristic optimization algorithms
    with hybrid combinations, real-time visualization, and comprehensive
    analysis tools.
    
    🔥 **Features:**
    - Single & Multi-objective Optimization
    - Feature Selection & Engineering
    - Hybrid Algorithm Combinations
    - Real-time Visualization
    - Statistical Analysis
    - Export Results
    """)
    
    return page


def home_page():
    """Display home page."""
    st.markdown('<div class="main-header">🧬 MHA Toolbox - Interactive Interface</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Available Algorithms", "36+", "+16 New")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Hybrid Strategies", "4", "Sequential, Parallel, Ensemble, Adaptive")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Problem Types", "Multiple", "Feature Selection, Function Optimization")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick start section
    st.markdown('<div class="sub-header">🚀 Quick Start</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Function Optimization**
        - Optimize mathematical functions
        - Benchmark algorithm performance
        - Compare multiple algorithms
        - Visualize convergence
        """)
        
        if st.button("Start Function Optimization"):
            st.session_state.page = "🎯 Function Optimization"
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        **🧬 Feature Selection**
        - Select optimal feature subsets
        - Improve model performance
        - Reduce dimensionality
        - Analyze feature importance
        """)
        
        if st.button("Start Feature Selection"):
            st.session_state.page = "🧬 Feature Selection"
            st.experimental_rerun()
    
    # Algorithm showcase
    st.markdown('<div class="sub-header">🔧 Available Algorithms</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🐝 Swarm Intelligence**")
        st.markdown("- PSO, GWO, WOA\n- ACO, ABC, SCA\n- SSA, ALO, MFO")
    
    with col2:
        st.markdown("**🧬 Bio-inspired**")
        st.markdown("- GA, DE, ES\n- BA, FA, CSA\n- COA, MRFO")
    
    with col3:
        st.markdown("**⚡ Physics-based**")
        st.markdown("- SA, EO, WDO\n- CGO, GBO, HGSO\n- AO, AOA")
    
    with col4:
        st.markdown("**🎯 Hybrid Methods**")
        st.markdown("- Sequential\n- Parallel\n- Ensemble\n- Adaptive")
    
    # Recent results
    if 'results_history' in st.session_state and st.session_state.results_history:
        st.markdown('<div class="sub-header">📊 Recent Results</div>', unsafe_allow_html=True)
        
        recent_results = st.session_state.results_history[-5:]  # Last 5 results
        for i, result in enumerate(recent_results):
            with st.expander(f"Result {len(st.session_state.results_history)-len(recent_results)+i+1}: {result.get('algorithm', 'Unknown')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Best Fitness", f"{result.get('fitness', 0):.6f}")
                with col2:
                    st.metric("Execution Time", f"{result.get('time', 0):.2f}s")
                with col3:
                    st.metric("Problem Type", result.get('problem_type', 'Unknown'))


def function_optimization_page():
    """Display function optimization page."""
    st.markdown('<div class="main-header">🎯 Function Optimization</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Configuration")
        
        # Algorithm selection
        algorithm = st.selectbox(
            "Select Algorithm:",
            ["pso", "gwo", "sca", "woa", "ga", "de", "abc", "aco", "alo", "fa", "ba", "csa"]
        )
        
        # Function selection
        function_name = st.selectbox(
            "Select Test Function:",
            ["Sphere", "Rosenbrock", "Rastrigin", "Ackley", "Griewank", "Custom"]
        )
        
        # Parameters
        dimensions = st.slider("Dimensions:", 2, 50, 10)
        population_size = st.slider("Population Size:", 10, 200, 30)
        max_iterations = st.slider("Max Iterations:", 10, 500, 100)
        
        # Bounds
        st.markdown("**Bounds:**")
        col_a, col_b = st.columns(2)
        with col_a:
            lower_bound = st.number_input("Lower:", value=-5.0)
        with col_b:
            upper_bound = st.number_input("Upper:", value=5.0)
        
        # Custom function
        if function_name == "Custom":
            custom_function = st.text_area(
                "Custom Function (Python):",
                "lambda x: sum(x**2)",
                help="Enter a lambda function. Variable 'x' is a numpy array."
            )
    
    with col2:
        st.markdown("### 🚀 Optimization")
        
        if st.button("Start Optimization", type="primary"):
            # Define test functions
            functions = {
                'Sphere': lambda x: np.sum(x**2),
                'Rosenbrock': lambda x: np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2),
                'Rastrigin': lambda x: 10*len(x) + np.sum(x**2 - 10*np.cos(2*np.pi*x)),
                'Ackley': lambda x: -20*np.exp(-0.2*np.sqrt(np.mean(x**2))) - np.exp(np.mean(np.cos(2*np.pi*x))) + 20 + np.e,
                'Griewank': lambda x: 1 + np.sum(x**2)/4000 - np.prod(np.cos(x/np.sqrt(np.arange(1, len(x)+1))))
            }
            
            if function_name == "Custom":
                try:
                    objective_function = eval(custom_function)
                except:
                    st.error("Invalid custom function. Please check syntax.")
                    st.stop()
            else:
                objective_function = functions[function_name]
            
            # Run optimization
            with st.spinner(f"Running {algorithm.upper()} optimization..."):
                start_time = time.time()
                
                try:
                    result = mha.optimize(
                        algorithm,
                        objective_function=objective_function,
                        dimensions=dimensions,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        population_size=population_size,
                        max_iterations=max_iterations,
                        verbose=False
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Store result
                    if 'results_history' not in st.session_state:
                        st.session_state.results_history = []
                    
                    st.session_state.results_history.append({
                        'algorithm': algorithm,
                        'fitness': result.best_fitness_,
                        'time': execution_time,
                        'problem_type': 'Function Optimization',
                        'function': function_name,
                        'dimensions': dimensions
                    })
                    
                    # Display results
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Optimization Complete!")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Best Fitness", f"{result.best_fitness_:.6f}")
                    with col_b:
                        st.metric("Execution Time", f"{execution_time:.2f}s")
                    with col_c:
                        st.metric("Iterations", max_iterations)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Convergence plot
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=result.global_fitness_,
                        mode='lines',
                        name='Best Fitness',
                        line=dict(color='blue', width=2)
                    ))
                    fig.update_layout(
                        title=f'{algorithm.upper()} Convergence - {function_name} Function',
                        xaxis_title='Iteration',
                        yaxis_title='Fitness Value',
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Solution details
                    with st.expander("📊 Solution Details"):
                        st.markdown("**Best Solution:**")
                        solution_df = pd.DataFrame({
                            'Dimension': range(1, len(result.best_solution_) + 1),
                            'Value': result.best_solution_
                        })
                        st.dataframe(solution_df)
                        
                        # Download results
                        results_json = {
                            'algorithm': algorithm,
                            'function': function_name,
                            'best_fitness': float(result.best_fitness_),
                            'best_solution': result.best_solution_.tolist(),
                            'convergence': result.global_fitness_,
                            'parameters': {
                                'dimensions': dimensions,
                                'population_size': population_size,
                                'max_iterations': max_iterations,
                                'bounds': [lower_bound, upper_bound]
                            }
                        }
                        
                        st.download_button(
                            "📥 Download Results (JSON)",
                            json.dumps(results_json, indent=2),
                            file_name=f"{algorithm}_{function_name}_results.json",
                            mime="application/json"
                        )
                
                except Exception as e:
                    st.error(f"Optimization failed: {str(e)}")


def feature_selection_page():
    """Display feature selection page."""
    st.markdown('<div class="main-header">🧬 Feature Selection</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📊 Dataset Configuration")
        
        # Dataset selection
        dataset_option = st.selectbox(
            "Select Dataset:",
            ["breast_cancer", "wine", "iris", "digits", "Upload Custom"]
        )
        
        if dataset_option == "Upload Custom":
            uploaded_file = st.file_uploader("Upload CSV file:", type="csv")
            if uploaded_file:
                data = pd.read_csv(uploaded_file)
                st.write("Preview:", data.head())
                
                target_column = st.selectbox("Select target column:", data.columns)
                feature_columns = st.multiselect("Select feature columns:", 
                                                [col for col in data.columns if col != target_column])
                
                if feature_columns:
                    X = data[feature_columns].values
                    y = data[target_column].values
                else:
                    st.warning("Please select feature columns.")
                    return
            else:
                st.warning("Please upload a dataset.")
                return
        else:
            # Load built-in dataset
            datasets = {
                'breast_cancer': load_breast_cancer,
                'wine': load_wine,
                'iris': load_iris,
                'digits': load_digits
            }
            
            data_loader = datasets[dataset_option]
            X, y = data_loader(return_X_y=True)
        
        # Algorithm selection
        algorithm = st.selectbox(
            "Select Algorithm:",
            ["pso", "gwo", "sca", "woa", "ga", "de", "abc", "aco", "alo"]
        )
        
        # Parameters
        st.markdown("**Algorithm Parameters:**")
        population_size = st.slider("Population Size:", 10, 100, 30)
        max_iterations = st.slider("Max Iterations:", 10, 200, 50)
        
        # Test size
        test_size = st.slider("Test Size:", 0.1, 0.5, 0.3)
    
    with col2:
        st.markdown("### 📈 Dataset Overview")
        
        # Dataset info
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Samples", X.shape[0])
        with col_b:
            st.metric("Features", X.shape[1])
        with col_c:
            st.metric("Classes", len(np.unique(y)))
        
        # Feature distribution plot
        if X.shape[1] <= 20:  # Only show for reasonable number of features
            feature_importance = np.std(X, axis=0)
            fig = px.bar(x=range(1, len(feature_importance)+1), y=feature_importance,
                        title="Feature Variability")
            fig.update_layout(xaxis_title="Feature", yaxis_title="Standard Deviation")
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🚀 Start Feature Selection", type="primary"):
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # Baseline performance
            baseline_rf = RandomForestClassifier(random_state=42)
            baseline_rf.fit(X_train, y_train)
            baseline_accuracy = accuracy_score(y_test, baseline_rf.predict(X_test))
            
            with st.spinner(f"Running {algorithm.upper()} feature selection..."):
                start_time = time.time()
                
                try:
                    result = mha.optimize(
                        algorithm,
                        X_train, y_train,
                        population_size=population_size,
                        max_iterations=max_iterations,
                        verbose=False
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Process results
                    selected_features = result.best_solution_ > 0.5
                    n_selected = np.sum(selected_features)
                    
                    if n_selected == 0:
                        # Select top features if none selected
                        top_indices = np.argsort(result.best_solution_)[-5:]
                        selected_features = np.zeros_like(result.best_solution_, dtype=bool)
                        selected_features[top_indices] = True
                        n_selected = 5
                    
                    # Test with selected features
                    if n_selected > 0:
                        X_train_selected = X_train[:, selected_features]
                        X_test_selected = X_test[:, selected_features]
                        
                        rf = RandomForestClassifier(random_state=42)
                        rf.fit(X_train_selected, y_train)
                        accuracy = accuracy_score(y_test, rf.predict(X_test_selected))
                        
                        reduction = (1 - n_selected / X.shape[1]) * 100
                        improvement = (accuracy - baseline_accuracy) * 100
                    else:
                        accuracy = 0
                        reduction = 0
                        improvement = -100
                    
                    # Display results
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Feature Selection Complete!")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("Selected Features", f"{n_selected}/{X.shape[1]}")
                    with col_b:
                        st.metric("Reduction", f"{reduction:.1f}%")
                    with col_c:
                        st.metric("Accuracy", f"{accuracy:.4f}")
                    with col_d:
                        st.metric("Improvement", f"{improvement:+.2f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Comparison chart
                    comparison_data = pd.DataFrame({
                        'Method': ['Baseline (All Features)', f'{algorithm.upper()} (Selected)'],
                        'Accuracy': [baseline_accuracy, accuracy],
                        'Features': [X.shape[1], n_selected]
                    })
                    
                    fig = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=('Accuracy Comparison', 'Feature Count'),
                        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
                    )
                    
                    fig.add_trace(
                        go.Bar(x=comparison_data['Method'], y=comparison_data['Accuracy'], 
                              name='Accuracy', marker_color=['lightblue', 'darkblue']),
                        row=1, col=1
                    )
                    
                    fig.add_trace(
                        go.Bar(x=comparison_data['Method'], y=comparison_data['Features'], 
                              name='Features', marker_color=['lightcoral', 'darkred']),
                        row=1, col=2
                    )
                    
                    fig.update_layout(title="Feature Selection Results", template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Feature selection visualization
                    if X.shape[1] <= 50:  # Only show for reasonable number of features
                        fig = go.Figure(data=go.Heatmap(
                            z=[selected_features.astype(int)],
                            colorscale=[[0, 'white'], [1, 'darkblue']],
                            showscale=False
                        ))
                        fig.update_layout(
                            title="Selected Features (Blue = Selected, White = Not Selected)",
                            xaxis_title="Feature Index",
                            yaxis_title="Selection",
                            height=200
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Store result
                    if 'results_history' not in st.session_state:
                        st.session_state.results_history = []
                    
                    st.session_state.results_history.append({
                        'algorithm': algorithm,
                        'fitness': result.best_fitness_,
                        'time': execution_time,
                        'problem_type': 'Feature Selection',
                        'dataset': dataset_option,
                        'accuracy': accuracy,
                        'features_selected': n_selected
                    })
                
                except Exception as e:
                    st.error(f"Feature selection failed: {str(e)}")


def hybrid_algorithms_page():
    """Display hybrid algorithms page."""
    st.markdown('<div class="main-header">🔬 Hybrid Algorithms</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Hybrid algorithms combine multiple optimization strategies to achieve better performance.
    Choose from different combination strategies:
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Configuration")
        
        # Algorithm selection
        st.markdown("**Select Algorithms to Combine:**")
        algorithms = st.multiselect(
            "Algorithms:",
            ["pso", "gwo", "sca", "woa", "ga", "de", "abc", "aco", "alo", "fa"],
            default=["pso", "gwo", "sca"]
        )
        
        if len(algorithms) < 2:
            st.warning("Please select at least 2 algorithms to combine.")
            return
        
        # Strategy selection
        strategy = st.selectbox(
            "Hybrid Strategy:",
            ["parallel", "sequential", "ensemble", "adaptive"]
        )
        
        # Strategy description
        strategy_descriptions = {
            "parallel": "Run algorithms in parallel and select the best result",
            "sequential": "Run algorithms in sequence, using output of one as input to next",
            "ensemble": "Combine solutions from multiple algorithms using ensemble methods",
            "adaptive": "Adaptively switch between algorithms based on performance"
        }
        
        st.info(strategy_descriptions[strategy])
        
        # Problem type
        problem_type = st.selectbox(
            "Problem Type:",
            ["Feature Selection", "Function Optimization"]
        )
        
        if problem_type == "Feature Selection":
            dataset = st.selectbox(
                "Dataset:",
                ["breast_cancer", "wine", "iris"]
            )
        else:
            function = st.selectbox(
                "Test Function:",
                ["Sphere", "Rosenbrock", "Rastrigin", "Ackley"]
            )
            dimensions = st.slider("Dimensions:", 2, 20, 10)
        
        # Parameters
        st.markdown("**Parameters:**")
        population_size = st.slider("Population Size:", 10, 100, 30)
        max_iterations = st.slider("Max Iterations:", 10, 200, 50)
    
    with col2:
        st.markdown("### 🚀 Hybrid Optimization")
        
        if st.button("Start Hybrid Optimization", type="primary"):
            with st.spinner(f"Running {strategy} hybrid with {len(algorithms)} algorithms..."):
                try:
                    from mha_toolbox.advanced_hybrid import AdvancedHybridOptimizer
                    from mha_toolbox.utils.problem_creator import create_problem
                    
                    # Create problem
                    if problem_type == "Feature Selection":
                        datasets = {
                            'breast_cancer': load_breast_cancer,
                            'wine': load_wine,
                            'iris': load_iris
                        }
                        X, y = datasets[dataset](return_X_y=True)
                        problem = create_problem(X=X, y=y, problem_type='feature_selection')
                    else:
                        functions = {
                            'Sphere': lambda x: np.sum(x**2),
                            'Rosenbrock': lambda x: np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2),
                            'Rastrigin': lambda x: 10*len(x) + np.sum(x**2 - 10*np.cos(2*np.pi*x)),
                            'Ackley': lambda x: -20*np.exp(-0.2*np.sqrt(np.mean(x**2))) - np.exp(np.mean(np.cos(2*np.pi*x))) + 20 + np.e
                        }
                        problem = create_problem(objective_function=functions[function], 
                                               dimensions=dimensions, problem_type='function')
                    
                    # Run hybrid optimization
                    start_time = time.time()
                    hybrid = AdvancedHybridOptimizer()
                    result = hybrid.optimize(algorithms, problem, strategy=strategy,
                                           population_size=population_size, 
                                           max_iterations=max_iterations)
                    
                    execution_time = time.time() - start_time
                    
                    # Display results
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Hybrid Optimization Complete!")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Best Fitness", f"{result.best_fitness_:.6f}")
                    with col_b:
                        st.metric("Execution Time", f"{execution_time:.2f}s")
                    with col_c:
                        st.metric("Strategy", strategy.title())
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Strategy-specific results
                    if hasattr(result, 'hybrid_results_') and result.hybrid_results_:
                        st.markdown("### 📊 Individual Algorithm Results")
                        
                        individual_results = []
                        for i, alg_result in enumerate(result.hybrid_results_):
                            individual_results.append({
                                'Algorithm': algorithms[i].upper(),
                                'Fitness': alg_result.best_fitness_,
                                'Status': '🏆 Best' if alg_result.best_fitness_ == result.best_fitness_ else '✅ Complete'
                            })
                        
                        results_df = pd.DataFrame(individual_results)
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Comparison chart
                        fig = px.bar(results_df, x='Algorithm', y='Fitness', 
                                   title=f'{strategy.title()} Hybrid - Individual Results')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Convergence plot
                    if hasattr(result, 'global_fitness_'):
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            y=result.global_fitness_,
                            mode='lines',
                            name='Hybrid Best Fitness',
                            line=dict(color='red', width=3)
                        ))
                        
                        # Add individual algorithm convergences if available
                        if hasattr(result, 'hybrid_results_'):
                            colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink']
                            for i, alg_result in enumerate(result.hybrid_results_):
                                if hasattr(alg_result, 'global_fitness_'):
                                    fig.add_trace(go.Scatter(
                                        y=alg_result.global_fitness_,
                                        mode='lines',
                                        name=f'{algorithms[i].upper()}',
                                        line=dict(color=colors[i % len(colors)], width=1, dash='dash')
                                    ))
                        
                        fig.update_layout(
                            title=f'{strategy.title()} Hybrid Convergence',
                            xaxis_title='Iteration',
                            yaxis_title='Fitness Value',
                            template='plotly_white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Hybrid optimization failed: {str(e)}")
                    import traceback
                    st.text(traceback.format_exc())


def algorithm_comparison_page():
    """Display algorithm comparison page."""
    st.markdown('<div class="main-header">📊 Algorithm Comparison</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Comparison Setup")
        
        # Algorithm selection
        st.markdown("**Select Algorithms to Compare:**")
        all_algorithms = ["pso", "gwo", "sca", "woa", "ga", "de", "abc", "aco", "alo", "fa", "ba", "csa"]
        selected_algorithms = st.multiselect(
            "Algorithms:",
            all_algorithms,
            default=["pso", "gwo", "sca", "woa"]
        )
        
        if len(selected_algorithms) < 2:
            st.warning("Please select at least 2 algorithms to compare.")
            return
        
        # Problem setup
        problem_type = st.selectbox(
            "Problem Type:",
            ["Feature Selection", "Function Optimization"]
        )
        
        if problem_type == "Feature Selection":
            dataset = st.selectbox("Dataset:", ["breast_cancer", "wine", "iris"])
        else:
            function = st.selectbox("Function:", ["Sphere", "Rosenbrock", "Rastrigin", "Ackley"])
            dimensions = st.slider("Dimensions:", 2, 30, 10)
        
        # Comparison parameters
        st.markdown("**Comparison Parameters:**")
        n_runs = st.slider("Number of Runs:", 1, 10, 3)
        population_size = st.slider("Population Size:", 10, 100, 30)
        max_iterations = st.slider("Max Iterations:", 10, 200, 50)
        
        # Statistical analysis
        show_statistics = st.checkbox("Show Statistical Analysis", True)
        confidence_level = st.slider("Confidence Level:", 0.90, 0.99, 0.95)
    
    with col2:
        st.markdown("### 📈 Comparison Results")
        
        if st.button("🚀 Start Comparison", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_runs = len(selected_algorithms) * n_runs
            current_run = 0
            
            results = {}
            
            # Run comparison
            for alg_name in selected_algorithms:
                results[alg_name] = []
                
                for run in range(n_runs):
                    status_text.text(f"Running {alg_name.upper()} - Run {run+1}/{n_runs}")
                    
                    try:
                        if problem_type == "Feature Selection":
                            datasets = {
                                'breast_cancer': load_breast_cancer,
                                'wine': load_wine,
                                'iris': load_iris
                            }
                            X, y = datasets[dataset](return_X_y=True)
                            
                            result = mha.optimize(
                                alg_name, X, y,
                                population_size=population_size,
                                max_iterations=max_iterations,
                                verbose=False
                            )
                        else:
                            functions = {
                                'Sphere': lambda x: np.sum(x**2),
                                'Rosenbrock': lambda x: np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2),
                                'Rastrigin': lambda x: 10*len(x) + np.sum(x**2 - 10*np.cos(2*np.pi*x)),
                                'Ackley': lambda x: -20*np.exp(-0.2*np.sqrt(np.mean(x**2))) - np.exp(np.mean(np.cos(2*np.pi*x))) + 20 + np.e
                            }
                            
                            result = mha.optimize(
                                alg_name,
                                objective_function=functions[function],
                                dimensions=dimensions,
                                lower_bound=-5, upper_bound=5,
                                population_size=population_size,
                                max_iterations=max_iterations,
                                verbose=False
                            )
                        
                        results[alg_name].append(result)
                        
                    except Exception as e:
                        st.error(f"Error running {alg_name}: {str(e)}")
                        continue
                    
                    current_run += 1
                    progress_bar.progress(current_run / total_runs)
            
            status_text.text("Analysis complete!")
            progress_bar.empty()
            
            # Analyze results
            if results:
                st.markdown("### 📊 Statistical Summary")
                
                summary_data = []
                for alg_name, alg_results in results.items():
                    if alg_results:
                        fitnesses = [r.best_fitness_ for r in alg_results]
                        summary_data.append({
                            'Algorithm': alg_name.upper(),
                            'Mean': np.mean(fitnesses),
                            'Std': np.std(fitnesses),
                            'Min': np.min(fitnesses),
                            'Max': np.max(fitnesses),
                            'Runs': len(fitnesses)
                        })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df = summary_df.round(6)
                st.dataframe(summary_df, use_container_width=True)
                
                # Visualization
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Box plot
                    plot_data = []
                    for alg_name, alg_results in results.items():
                        if alg_results:
                            for result in alg_results:
                                plot_data.append({
                                    'Algorithm': alg_name.upper(),
                                    'Fitness': result.best_fitness_
                                })
                    
                    if plot_data:
                        plot_df = pd.DataFrame(plot_data)
                        fig = px.box(plot_df, x='Algorithm', y='Fitness', 
                                   title='Fitness Distribution')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col_b:
                    # Mean comparison
                    fig = px.bar(summary_df, x='Algorithm', y='Mean', 
                               error_y='Std', title='Mean Fitness with Error Bars')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Convergence comparison
                st.markdown("### 📈 Convergence Comparison")
                
                fig = go.Figure()
                colors = px.colors.qualitative.Set1
                
                for i, (alg_name, alg_results) in enumerate(results.items()):
                    if alg_results:
                        # Average convergence across runs
                        all_convergences = []
                        for result in alg_results:
                            if hasattr(result, 'global_fitness_'):
                                all_convergences.append(result.global_fitness_)
                        
                        if all_convergences:
                            # Ensure all convergences have same length
                            min_length = min(len(conv) for conv in all_convergences)
                            trimmed_convergences = [conv[:min_length] for conv in all_convergences]
                            avg_convergence = np.mean(trimmed_convergences, axis=0)
                            
                            fig.add_trace(go.Scatter(
                                y=avg_convergence,
                                mode='lines',
                                name=alg_name.upper(),
                                line=dict(color=colors[i % len(colors)], width=2)
                            ))
                
                fig.update_layout(
                    title='Average Convergence Comparison',
                    xaxis_title='Iteration',
                    yaxis_title='Fitness Value',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Best algorithm
                best_alg = summary_df.loc[summary_df['Mean'].idxmin(), 'Algorithm']
                best_mean = summary_df['Mean'].min()
                
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### 🏆 Best Algorithm: {best_alg}")
                st.markdown(f"**Mean Fitness:** {best_mean:.6f}")
                st.markdown('</div>', unsafe_allow_html=True)


def visualization_center_page():
    """Display visualization center."""
    st.markdown('<div class="main-header">📈 Visualization Center</div>', unsafe_allow_html=True)
    
    if 'results_history' not in st.session_state or not st.session_state.results_history:
        st.warning("No results available for visualization. Please run some optimizations first.")
        return
    
    # Results overview
    st.markdown("### 📊 Results Overview")
    
    results_df = pd.DataFrame(st.session_state.results_history)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Runs", len(results_df))
    with col2:
        st.metric("Algorithms Tested", results_df['algorithm'].nunique())
    with col3:
        st.metric("Problem Types", results_df['problem_type'].nunique())
    with col4:
        st.metric("Avg Execution Time", f"{results_df['time'].mean():.2f}s")
    
    # Performance over time
    st.markdown("### 📈 Performance Over Time")
    fig = px.line(results_df.reset_index(), x='index', y='fitness', 
                  color='algorithm', title='Fitness Over Time')
    fig.update_layout(xaxis_title='Run Number', yaxis_title='Fitness Value')
    st.plotly_chart(fig, use_container_width=True)
    
    # Algorithm performance comparison
    st.markdown("### 🔥 Algorithm Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        # Best fitness by algorithm
        alg_performance = results_df.groupby('algorithm')['fitness'].agg(['mean', 'min', 'count']).reset_index()
        fig = px.bar(alg_performance, x='algorithm', y='mean', 
                    title='Average Fitness by Algorithm')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Execution time by algorithm
        fig = px.box(results_df, x='algorithm', y='time', 
                    title='Execution Time Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Problem type analysis
    if results_df['problem_type'].nunique() > 1:
        st.markdown("### 🎯 Problem Type Analysis")
        
        problem_stats = results_df.groupby(['problem_type', 'algorithm'])['fitness'].mean().reset_index()
        fig = px.bar(problem_stats, x='algorithm', y='fitness', 
                    color='problem_type', barmode='group',
                    title='Performance by Problem Type')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    st.markdown("### 📋 Detailed Results")
    display_df = results_df.copy()
    display_df['fitness'] = display_df['fitness'].round(6)
    display_df['time'] = display_df['time'].round(2)
    st.dataframe(display_df, use_container_width=True)
    
    # Export options
    st.markdown("### 📥 Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = results_df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV",
            csv,
            file_name="mha_results.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = results_df.to_json(orient='records', indent=2)
        st.download_button(
            "📋 Download JSON",
            json_data,
            file_name="mha_results.json",
            mime="application/json"
        )


def algorithm_explorer_page():
    """Display algorithm explorer."""
    st.markdown('<div class="main-header">⚙️ Algorithm Explorer</div>', unsafe_allow_html=True)
    
    # Get available algorithms
    try:
        toolbox = mha.get_toolbox()
        algorithms = toolbox.list_algorithms()
    except:
        st.error("Could not load algorithms. Please check MHA Toolbox installation.")
        return
    
    st.markdown("### 🔍 Explore Available Algorithms")
    
    # Algorithm categories
    for category, alg_list in algorithms.items():
        if alg_list:  # Only show non-empty categories
            with st.expander(f"📁 {category} ({len(alg_list)} algorithms)"):
                for alg_name in alg_list:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{alg_name}**")
                    
                    with col2:
                        if st.button(f"Info", key=f"info_{alg_name}"):
                            st.session_state.selected_algorithm = alg_name
                    
                    with col3:
                        if st.button(f"Test", key=f"test_{alg_name}"):
                            st.session_state.test_algorithm = alg_name
    
    # Algorithm details
    if 'selected_algorithm' in st.session_state:
        st.markdown(f"### 📖 Algorithm Details: {st.session_state.selected_algorithm}")
        
        try:
            info = toolbox.get_algorithm_info(st.session_state.selected_algorithm)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Information:**")
                st.write(f"**Name:** {info.get('name', 'N/A')}")
                st.write(f"**Class:** {info.get('class', 'N/A')}")
                st.write(f"**Module:** {info.get('module', 'N/A')}")
            
            with col2:
                st.markdown("**Parameters:**")
                params = info.get('parameters', {})
                if params:
                    for param, default in params.items():
                        st.write(f"**{param}:** {default}")
                else:
                    st.write("No parameter information available")
            
            # Algorithm aliases
            if 'aliases' in info:
                st.markdown("**Aliases:**")
                st.write(", ".join(info['aliases']))
            
        except Exception as e:
            st.error(f"Could not load algorithm information: {str(e)}")
    
    # Quick test
    if 'test_algorithm' in st.session_state:
        st.markdown(f"### 🧪 Quick Test: {st.session_state.test_algorithm}")
        
        with st.spinner("Running quick test..."):
            try:
                result = mha.optimize(
                    st.session_state.test_algorithm,
                    objective_function=lambda x: np.sum(x**2),
                    dimensions=5,
                    population_size=20,
                    max_iterations=30,
                    verbose=False
                )
                
                st.success(f"✅ Test completed! Best fitness: {result.best_fitness_:.6f}")
                
                # Quick convergence plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=result.global_fitness_,
                    mode='lines',
                    name='Fitness'
                ))
                fig.update_layout(
                    title=f'{st.session_state.test_algorithm.upper()} - Quick Test',
                    xaxis_title='Iteration',
                    yaxis_title='Fitness',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Test failed: {str(e)}")
        
        # Clear test state
        del st.session_state.test_algorithm


def documentation_page():
    """Display documentation page."""
    st.markdown('<div class="main-header">📚 Documentation</div>', unsafe_allow_html=True)
    
    # Table of contents
    st.markdown("### 📋 Table of Contents")
    st.markdown("""
    1. [Getting Started](#getting-started)
    2. [Function Optimization](#function-optimization)
    3. [Feature Selection](#feature-selection)
    4. [Hybrid Algorithms](#hybrid-algorithms)
    5. [API Reference](#api-reference)
    6. [Examples](#examples)
    """)
    
    # Getting started
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    The MHA Toolbox provides a simple, unified interface for metaheuristic optimization algorithms.
    
    **Basic Usage:**
    ```python
    import mha_toolbox as mha
    
    # Function optimization
    result = mha.optimize('pso', objective_function=lambda x: sum(x**2), dimensions=10)
    
    # Feature selection
    result = mha.optimize('gwo', X, y)
    
    # Algorithm comparison
    results = mha.compare(['pso', 'gwo', 'sca'], X, y)
    ```
    """)
    
    # Function optimization
    st.markdown("### 🎯 Function Optimization")
    st.markdown("""
    Optimize mathematical functions using metaheuristic algorithms.
    
    **Parameters:**
    - `algorithm`: Algorithm name (e.g., 'pso', 'gwo', 'sca')
    - `objective_function`: Function to optimize
    - `dimensions`: Problem dimensionality
    - `lower_bound`, `upper_bound`: Search space bounds
    - `population_size`: Population size (default: 30)
    - `max_iterations`: Maximum iterations (default: 100)
    
    **Example:**
    ```python
    # Optimize Sphere function
    result = mha.optimize('pso', 
                         objective_function=lambda x: sum(x**2),
                         dimensions=10,
                         lower_bound=-5,
                         upper_bound=5)
    
    print(f"Best fitness: {result.best_fitness_}")
    result.plot_convergence()
    ```
    """)
    
    # Feature selection
    st.markdown("### 🧬 Feature Selection")
    st.markdown("""
    Select optimal feature subsets for machine learning.
    
    **Parameters:**
    - `algorithm`: Algorithm name
    - `X`: Feature matrix
    - `y`: Target vector
    - `population_size`: Population size (default: 30)
    - `max_iterations`: Maximum iterations (default: 100)
    
    **Example:**
    ```python
    from sklearn.datasets import load_breast_cancer
    
    X, y = load_breast_cancer(return_X_y=True)
    result = mha.optimize('gwo', X, y)
    
    selected_features = result.best_solution_ > 0.5
    print(f"Selected {sum(selected_features)} features")
    ```
    """)
    
    # Hybrid algorithms
    st.markdown("### 🔬 Hybrid Algorithms")
    st.markdown("""
    Combine multiple algorithms for improved performance.
    
    **Strategies:**
    - **Parallel**: Run algorithms in parallel, select best result
    - **Sequential**: Run algorithms in sequence
    - **Ensemble**: Combine solutions using ensemble methods
    - **Adaptive**: Adaptively switch between algorithms
    
    **Example:**
    ```python
    from mha_toolbox.advanced_hybrid import AdvancedHybridOptimizer
    
    hybrid = AdvancedHybridOptimizer()
    result = hybrid.optimize(['pso', 'gwo', 'sca'], problem, strategy='parallel')
    ```
    """)
    
    # API reference
    st.markdown("### 📖 API Reference")
    st.markdown("""
    **Main Functions:**
    
    - `mha.optimize(algorithm, ...)`: Main optimization function
    - `mha.compare(algorithms, ...)`: Compare multiple algorithms
    - `mha.list_algorithms()`: List available algorithms
    - `mha.load_data(dataset)`: Load built-in datasets
    
    **Result Object:**
    
    - `result.best_fitness_`: Best fitness value
    - `result.best_solution_`: Best solution
    - `result.global_fitness_`: Convergence history
    - `result.plot_convergence()`: Plot convergence
    - `result.summary()`: Print summary
    """)
    
    # Examples
    st.markdown("### 💡 Examples")
    
    with st.expander("🎯 Function Optimization Examples"):
        st.code("""
# Sphere function
result = mha.optimize('pso', objective_function=lambda x: sum(x**2), dimensions=10)

# Rosenbrock function
def rosenbrock(x):
    return sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

result = mha.optimize('gwo', objective_function=rosenbrock, dimensions=10, 
                     lower_bound=-2, upper_bound=2)

# Rastrigin function
def rastrigin(x):
    return 10*len(x) + sum(x**2 - 10*np.cos(2*np.pi*x))

result = mha.optimize('sca', objective_function=rastrigin, dimensions=10)
        """)
    
    with st.expander("🧬 Feature Selection Examples"):
        st.code("""
from sklearn.datasets import load_breast_cancer, load_wine, load_iris

# Breast cancer dataset
X, y = load_breast_cancer(return_X_y=True)
result = mha.optimize('pso', X, y)

# Wine dataset with custom parameters
X, y = load_wine(return_X_y=True)
result = mha.optimize('gwo', X, y, population_size=50, max_iterations=100)

# Iris dataset
X, y = load_iris(return_X_y=True)
result = mha.optimize('sca', X, y, verbose=True)
        """)
    
    with st.expander("📊 Comparison Examples"):
        st.code("""
# Compare algorithms on feature selection
X, y = load_breast_cancer(return_X_y=True)
results = mha.compare(['pso', 'gwo', 'sca', 'woa'], X, y, n_runs=5)

# Compare on function optimization
results = mha.compare(['pso', 'gwo', 'sca'], 
                     objective_function=lambda x: sum(x**2),
                     dimensions=10, n_runs=3)

# Statistical analysis
for alg, alg_results in results.items():
    fitnesses = [r.best_fitness_ for r in alg_results]
    print(f"{alg}: mean={np.mean(fitnesses):.6f}, std={np.std(fitnesses):.6f}")
        """)


def main():
    """Main application function."""
    configure_page()
    
    # Initialize session state
    if 'results_history' not in st.session_state:
        st.session_state.results_history = []
    
    # Navigation
    page = sidebar_navigation()
    
    # Handle quick demo
    if st.session_state.get('run_quick_demo', False):
        st.session_state.run_quick_demo = False
        
        with st.spinner("Running quick demo..."):
            try:
                # Quick function optimization demo
                result = mha.optimize('pso', 
                                    objective_function=lambda x: np.sum(x**2),
                                    dimensions=5,
                                    population_size=20,
                                    max_iterations=30,
                                    verbose=False)
                
                st.success(f"✅ Quick demo completed! PSO found fitness: {result.best_fitness_:.6f}")
                
                # Store result
                st.session_state.results_history.append({
                    'algorithm': 'pso',
                    'fitness': result.best_fitness_,
                    'time': 1.0,  # Approximate
                    'problem_type': 'Quick Demo',
                    'function': 'Sphere'
                })
                
            except Exception as e:
                st.error(f"Quick demo failed: {str(e)}")
    
    # Handle show algorithms
    if st.session_state.get('show_algorithms', False):
        st.session_state.show_algorithms = False
        
        try:
            toolbox = mha.get_toolbox()
            algorithms = toolbox.list_algorithms()
            
            st.info("**Available Algorithms:**")
            for category, alg_list in algorithms.items():
                if alg_list:
                    st.write(f"**{category}:** {', '.join(alg_list)}")
        except Exception as e:
            st.error(f"Could not load algorithms: {str(e)}")
    
    # Route to pages
    if page == "🏠 Home":
        home_page()
    elif page == "🎯 Function Optimization":
        function_optimization_page()
    elif page == "🧬 Feature Selection":
        feature_selection_page()
    elif page == "🔬 Hybrid Algorithms":
        hybrid_algorithms_page()
    elif page == "📊 Algorithm Comparison":
        algorithm_comparison_page()
    elif page == "🌍 Real-world Problems":
        st.markdown("### 🌍 Real-world Problems")
        st.info("Real-world problem demos coming soon! Check the demo system module for portfolio optimization and other examples.")
    elif page == "📈 Visualization Center":
        visualization_center_page()
    elif page == "⚙️ Algorithm Explorer":
        algorithm_explorer_page()
    elif page == "📚 Documentation":
        documentation_page()


if __name__ == "__main__":
    main()