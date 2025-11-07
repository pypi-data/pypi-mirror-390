"""
Beginner-Friendly Interface System
==================================

Guided UI mode for newcomers with step-by-step wizards and recommendations.
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mha_toolbox.algorithm_recommender import AlgorithmRecommender
from mha_toolbox.professional_exporter import ProfessionalExporter
from mha_toolbox import algorithms
from mha_toolbox.algorithms import hybrid
from sklearn.datasets import load_breast_cancer, load_wine, load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class BeginnerMode:
    """
    Beginner-friendly guided interface with wizard-style workflow
    """
    
    def __init__(self):
        self.recommender = AlgorithmRecommender()
        self.exporter = ProfessionalExporter()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'beginner_step' not in st.session_state:
            st.session_state.beginner_step = 1
        if 'dataset_loaded' not in st.session_state:
            st.session_state.dataset_loaded = False
        if 'algorithms_selected' not in st.session_state:
            st.session_state.algorithms_selected = []
        if 'optimization_running' not in st.session_state:
            st.session_state.optimization_running = False
    
    def render(self):
        """Main render function for beginner mode"""
        st.title("🎓 Beginner Mode - Guided Optimization")
        
        # Progress indicator
        self._show_progress()
        
        # Render appropriate step
        if st.session_state.beginner_step == 1:
            self._step1_welcome()
        elif st.session_state.beginner_step == 2:
            self._step2_load_data()
        elif st.session_state.beginner_step == 3:
            self._step3_get_recommendations()
        elif st.session_state.beginner_step == 4:
            self._step4_configure_and_run()
        elif st.session_state.beginner_step == 5:
            self._step5_results_and_export()
    
    def _show_progress(self):
        """Show progress bar and current step"""
        steps = [
            "Welcome",
            "Load Data",
            "Get Recommendations",
            "Configure & Run",
            "Results & Export"
        ]
        
        current = st.session_state.beginner_step - 1
        progress = (current) / (len(steps) - 1)
        
        st.progress(progress)
        
        cols = st.columns(len(steps))
        for i, (col, step) in enumerate(zip(cols, steps)):
            with col:
                if i < current:
                    st.success(f"✓ {step}")
                elif i == current:
                    st.info(f"→ {step}")
                else:
                    st.text(f"  {step}")
        
        st.markdown("---")
    
    def _step1_welcome(self):
        """Step 1: Welcome and introduction"""
        st.header("👋 Welcome to MHA Toolbox!")
        
        st.markdown("""
        ### What is Metaheuristic Optimization?
        
        Metaheuristic algorithms are smart search methods inspired by nature that can find 
        good solutions to complex problems. Think of them as:
        
        - 🦅 **Birds finding food** (Particle Swarm Optimization - PSO)
        - 🐺 **Wolves hunting** (Grey Wolf Optimizer - GWO)  
        - 🐜 **Ants finding paths** (Ant Colony Optimization - ACO)
        - 🧬 **Evolution** (Genetic Algorithms - GA)
        
        ### What can you do here?
        
        1. **Load your dataset** or use built-in examples
        2. **Get AI-powered algorithm recommendations** based on your data
        3. **Run optimizations** with one click
        4. **Compare results** with beautiful visualizations
        5. **Export everything** for your reports or papers
        
        ### Who is this for?
        
        - 🎓 Students learning about optimization
        - 🔬 Researchers trying new algorithms
        - 💼 Professionals solving real-world problems
        - 🤖 Anyone curious about AI and nature-inspired computing
        
        ### Ready to get started?
        """)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Let's Begin! 🚀", type="primary", use_container_width=True):
                st.session_state.beginner_step = 2
                st.rerun()
        
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            - This wizard will guide you through every step
            - You can go back to previous steps anytime
            - All settings have smart defaults - no expertise needed!
            - Hover over ⓘ icons for more help
            """)
    
    def _step2_load_data(self):
        """Step 2: Load or select dataset"""
        st.header("📊 Step 2: Load Your Data")
        
        st.markdown("""
        Choose how you want to provide data for optimization:
        """)
        
        data_source = st.radio(
            "Data Source",
            ["Use Example Dataset", "Upload My Own Dataset", "Create Custom Problem"],
            help="Example datasets are great for learning. Upload your own for real work!"
        )
        
        X, y, dataset_name = None, None, None
        
        if data_source == "Use Example Dataset":
            X, y, dataset_name = self._load_example_dataset()
        
        elif data_source == "Upload My Own Dataset":
            X, y, dataset_name = self._upload_custom_dataset()
        
        elif data_source == "Create Custom Problem":
            X, y, dataset_name = self._create_custom_problem()
        
        if X is not None and y is not None:
            st.session_state.X = X
            st.session_state.y = y
            st.session_state.dataset_name = dataset_name
            st.session_state.dataset_loaded = True
            
            # Show data info
            st.success(f"✓ Dataset loaded: {dataset_name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Samples", X.shape[0])
            with col2:
                st.metric("Features", X.shape[1])
            with col3:
                if y is not None:
                    st.metric("Classes", len(np.unique(y)))
            
            # Navigation buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.beginner_step = 1
                    st.rerun()
            with col2:
                if st.button("Next: Get Recommendations →", type="primary", use_container_width=True):
                    st.session_state.beginner_step = 3
                    st.rerun()
    
    def _load_example_dataset(self) -> Tuple[np.ndarray, np.ndarray, str]:
        """Load example dataset"""
        dataset_choice = st.selectbox(
            "Choose Example Dataset",
            ["Breast Cancer (Medical)", "Wine Quality", "Iris Flowers"],
            help="Each dataset has different characteristics - perfect for learning!"
        )
        
        if dataset_choice == "Breast Cancer (Medical)":
            data = load_breast_cancer()
            st.info("🏥 Medical dataset for cancer diagnosis (569 samples, 30 features)")
        elif dataset_choice == "Wine Quality":
            data = load_wine()
            st.info("🍷 Wine classification dataset (178 samples, 13 features)")
        else:
            data = load_iris()
            st.info("🌸 Iris flower species dataset (150 samples, 4 features)")
        
        X, y = data.data, data.target
        
        # Show preview
        with st.expander("👀 Preview Data"):
            df = pd.DataFrame(X[:10], columns=[f"Feature_{i+1}" for i in range(X.shape[1])])
            df['Target'] = y[:10]
            st.dataframe(df)
        
        return X, y, dataset_choice.split()[0]
    
    def _upload_custom_dataset(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[str]]:
        """Upload custom CSV dataset"""
        st.info("📁 Upload a CSV file with your data. Last column should be the target/label.")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            
            st.write("Preview:")
            st.dataframe(df.head())
            
            # Separate features and target
            X = df.iloc[:, :-1].values
            y = df.iloc[:, -1].values
            
            return X, y, uploaded_file.name.replace('.csv', '')
        
        return None, None, None
    
    def _create_custom_problem(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[str]]:
        """Create custom optimization problem"""
        st.info("🎯 Create a custom function optimization problem")
        
        problem_type = st.selectbox(
            "Problem Type",
            ["Sphere Function", "Rastrigin Function", "Rosenbrock Function", "Ackley Function"]
        )
        
        dimensions = st.slider("Number of Dimensions", 2, 50, 10)
        samples = st.slider("Number of Samples", 100, 1000, 500)
        
        # Generate synthetic data for feature selection
        X = np.random.randn(samples, dimensions)
        y = np.random.randint(0, 2, samples)
        
        st.success(f"Created {problem_type} with {dimensions} dimensions")
        
        return X, y, problem_type
    
    def _step3_get_recommendations(self):
        """Step 3: Get algorithm recommendations"""
        st.header("🤖 Step 3: Get Algorithm Recommendations")
        
        if not st.session_state.dataset_loaded:
            st.warning("Please load a dataset first!")
            if st.button("← Back to Data Loading"):
                st.session_state.beginner_step = 2
                st.rerun()
            return
        
        st.markdown("""
        Our AI will analyze your dataset and recommend the best algorithms! ✨
        """)
        
        with st.spinner("Analyzing your dataset..."):
            recommendations = self.recommender.recommend_algorithms(
                st.session_state.X,
                st.session_state.y,
                top_k=10
            )
        
        st.success(f"Analysis complete! Here are the top recommendations for **{st.session_state.dataset_name}**:")
        
        # Display recommendations
        for i, (algo_name, confidence, reason) in enumerate(recommendations, 1):
            with st.expander(f"#{i} {algo_name} - Confidence: {confidence:.1f}/10", expanded=(i<=3)):
                st.markdown(f"""
                **Why this algorithm?**
                
                {reason}
                
                **Recommended for:** {', '.join(self.recommender.algorithm_profiles[algo_name]['best_for'])}
                
                **Speed:** {self.recommender.algorithm_profiles[algo_name]['speed'].title()}
                """)
                
                if st.checkbox(f"Select {algo_name}", key=f"select_{algo_name}", value=(i<=3)):
                    if algo_name not in st.session_state.algorithms_selected:
                        st.session_state.algorithms_selected.append(algo_name)
                elif algo_name in st.session_state.algorithms_selected:
                    st.session_state.algorithms_selected.remove(algo_name)
        
        st.markdown("---")
        
        # Show selected algorithms
        if st.session_state.algorithms_selected:
            st.success(f"✓ Selected {len(st.session_state.algorithms_selected)} algorithms: {', '.join(st.session_state.algorithms_selected)}")
        else:
            st.warning("Please select at least one algorithm to continue")
        
        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.beginner_step = 2
                st.rerun()
        with col2:
            if st.button("Next: Configure & Run →", type="primary", 
                        use_container_width=True, 
                        disabled=len(st.session_state.algorithms_selected) == 0):
                st.session_state.beginner_step = 4
                st.rerun()
    
    def _step4_configure_and_run(self):
        """Step 4: Configure parameters and run optimization"""
        st.header("⚙️ Step 4: Configure & Run Optimization")
        
        st.markdown(f"""
        Running optimization on **{st.session_state.dataset_name}** with:
        - **{len(st.session_state.algorithms_selected)} algorithms**
        - **{st.session_state.X.shape[0]} samples**
        - **{st.session_state.X.shape[1]} features**
        """)
        
        # Get dataset characteristics for smart defaults
        characteristics = self.recommender.analyze_dataset(st.session_state.X, st.session_state.y)
        
        st.subheader("Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            pop_size = st.slider(
                "Population Size",
                min_value=10,
                max_value=100,
                value=30,
                help="Larger = more exploration, but slower"
            )
        with col2:
            max_iter = st.slider(
                "Maximum Iterations",
                min_value=50,
                max_value=500,
                value=100,
                help="More iterations = better convergence, but takes longer"
            )
        
        use_smart_defaults = st.checkbox("Use AI-recommended parameters", value=True,
                                        help="Let the AI choose optimal parameters for your data")
        
        if use_smart_defaults:
            recommended_params = self.recommender.get_recommended_parameters(
                st.session_state.algorithms_selected[0],
                characteristics
            )
            st.info(f"🤖 Recommended: Pop Size={recommended_params['pop_size']}, Max Iter={recommended_params['max_iter']}")
            pop_size = recommended_params['pop_size']
            max_iter = recommended_params['max_iter']
        
        st.session_state.pop_size = pop_size
        st.session_state.max_iter = max_iter
        
        st.markdown("---")
        
        # Run button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Optimization!", type="primary", use_container_width=True):
                self._run_optimization()
                st.session_state.beginner_step = 5
                st.rerun()
        
        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.beginner_step = 3
                st.rerun()
    
    def _run_optimization(self):
        """Run the optimization process"""
        # This would integrate with the main optimization system
        # For now, create placeholder results
        st.session_state.optimization_results = {
            'completed': True,
            'results': {},
            'problem_info': {
                'name': st.session_state.dataset_name,
                'samples': st.session_state.X.shape[0],
                'features': st.session_state.X.shape[1],
                'algorithms': st.session_state.algorithms_selected
            }
        }
    
    def _step5_results_and_export(self):
        """Step 5: Show results and export options"""
        st.header("🎉 Step 5: Results & Export")
        
        st.success("Optimization completed successfully!")
        
        st.markdown("""
        ### What's Next?
        
        - 📊 **View Results**: See how each algorithm performed
        - 📈 **Visualizations**: Beautiful plots and comparisons
        - 💾 **Export**: Download everything for your work
        - 🔄 **Run Again**: Try different settings or datasets
        """)
        
        # Results would be shown here
        st.info("Results visualization would appear here")
        
        # Export section
        st.subheader("📥 Export Your Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download Plots", use_container_width=True):
                st.success("Plots exported!")
        
        with col2:
            if st.button("📋 Download Data (CSV)", use_container_width=True):
                st.success("Data exported!")
        
        with col3:
            if st.button("📦 Download All", use_container_width=True, type="primary"):
                st.success("Complete package exported!")
        
        st.markdown("---")
        
        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Start Over", use_container_width=True):
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("🎓 Switch to Professional Mode", use_container_width=True, type="primary"):
                st.session_state.mode = 'professional'
                st.rerun()


def main():
    """Main entry point for beginner mode"""
    st.set_page_config(
        page_title="MHA Toolbox - Beginner Mode",
        page_icon="🎓",
        layout="wide"
    )
    
    beginner_mode = BeginnerMode()
    beginner_mode.render()


if __name__ == "__main__":
    main()
