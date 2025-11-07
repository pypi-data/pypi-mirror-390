"""
MHA Toolbox - Web Interface
============================

Professional web interface for meta-heuristic algorithms with:
- Beginner Mode: Guided workflow with recommendations
- Professional Mode: Full control and advanced features
- Real-time optimization tracking
- Interactive visualizations
- Result export and management

Usage:
    python -m mha_toolbox ui
    
    Or directly:
    python mha_web_interface.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import time
import contextlib
import sys

# Your wakepy import remains the same
try:
    from wakepy import keep
    WAKEPY_AVAILABLE = True
except ImportError:
    WAKEPY_AVAILABLE = False
    print("⚠️ wakepy not installed. Sleep prevention disabled.")
    
# Import helper modules
# Note: Some modules may not be available if they depend on removed dependencies
try:
    from mha_toolbox.enhanced_runner import run_comparison_with_live_progress
except ImportError:
    run_comparison_with_live_progress = None
    print("⚠️ enhanced_runner not available")

from mha_toolbox.persistent_state import PersistentStateManager
from mha_toolbox.enhanced_session_manager import EnhancedSessionManager
from mha_toolbox.results_manager import ResultsManager
from mha_toolbox.algorithm_recommender import AlgorithmRecommender
try:
    from mha_toolbox.intelligent_session_manager import get_session_manager
except ImportError:
    get_session_manager = None
    print("⚠️ intelligent_session_manager not available")

# Import new feature modules
from mha_toolbox.professional_visualizer import (
    plot_feature_threshold,
    plot_comparison_box_with_stats,
    create_workflow_dashboard,
    export_results_to_csv,
    create_statistical_table
)
from mha_toolbox.feature_integration import (
    DatasetGenerator,
    BinaryMulticlassSupport,
    MLflowIntegration,
    render_enhanced_algorithm_selection,
    render_dimension_aware_hyperparameters
)
from mha_toolbox.algorithm_categories import (
    ALGORITHM_CATEGORIES,
    recommend_algorithms
)
from mha_toolbox.hyperparameter_config import (
    HyperparameterManager,
    get_preset_config
)
from mha_toolbox.beginner_mode import BeginnerMode
# Use optimized multi-user profile system
from mha_toolbox.user_profile_optimized import (
    get_current_user_info,
    create_session_profile,
    load_profile,
    save_profile,
    UserProfile
)

def toggle_algorithm_selection(algorithm_name):
    """Callback to toggle algorithm selection."""
    if algorithm_name in st.session_state.selected_algorithms:
        st.session_state.selected_algorithms.remove(algorithm_name)
    else:
        st.session_state.selected_algorithms.append(algorithm_name)

# Page configuration
st.set_page_config(
    page_title="MHA Toolbox - Optimization Suite",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional design
st.markdown("""
<style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinner-emoji {
        display: inline-block;
        animation: spin 2s linear infinite;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .mode-selector {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #e0e0e0;
        color: #1e1e1e;
    }
    .mode-selector h3, .mode-selector h4, .mode-selector p, .mode-selector label {
        color: #1e1e1e !important;
    }
    .algorithm-card {
        background: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        color: #FAFAFA;
        transition: all 0.3s ease;
    }
    .algorithm-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.2);
    }
    .algorithm-card h4, .algorithm-card p {
        color: #FAFAFA;
    }
    .algorithm-card-running { border-left-color: #ffa500; }
    .algorithm-card-completed { border-left-color: #28a745; }
    .algorithm-card-failed { border-left-color: #dc3545; }
    .recommendation-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
        color: #1e1e1e;
    }
    .recommendation-card h4, .recommendation-card p, .recommendation-card span {
        color: #1e1e1e !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        color: white !important;
        text-align: center !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    .metric-card h1, .metric-card h2, .metric-card h3, 
    .metric-card h4, .metric-card h5, .metric-card h6 {
        color: white !important;
    }
    
    .metric-card p, .metric-card span, .metric-card div {
        color: white !important;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #155724;
    }
    .success-box h4, .success-box p, .success-box span {
        color: #155724 !important;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #856404;
    }
    .warning-box h4, .warning-box p, .warning-box span {
        color: #856404 !important;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #0c5460;
    }
    .info-box h4, .info-box p, .info-box span {
        color: #0c5460 !important;
    }
    .step-indicator {
        display: inline-block;
        width: 30px;
        height: 30px;
        background: #667eea;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
    }
    div[data-testid="stMetric"] {
        background-color: transparent;
        border: 1px solid #444;
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Fix white section visibility - ensure dark text in all containers */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        color: #1e1e1e !important;
    }
    
    /* Streamlit expanders - better contrast */
    div[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        color: #1e1e1e;
    }
    
    div[data-testid="stExpander"] summary {
        color: #1e1e1e !important;
        font-weight: 600;
    }
    
    div[data-testid="stExpander"] div[role="button"] {
        color: #1e1e1e !important;
    }
    
    /* Container styling for white sections */
    section[data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Main content area - ensure readability */
    .main .block-container {
        color: #1e1e1e;
    }
    
    /* Fix text in white cards/containers */
    div[data-baseweb="card"],
    div[data-testid="column"] > div {
        color: #1e1e1e;
    }
    
    /* Markdown text in main area */
    .main p, .main li, .main span, .main div {
        color: #1e1e1e !important;
    }
    
    /* Headers in main area */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #1e1e1e !important;
    }
    
    /* AGGRESSIVE: Force all elements in main to have dark text */
    /* BUT exclude special cards that have their own color schemes */
    .main *:not(.metric-card):not(.metric-card *):not(.algorithm-card):not(.algorithm-card *):not(.main-header):not(.main-header *) {
        color: #1e1e1e !important;
    }
    
    /* CRITICAL: Override Streamlit's default markdown styling */
    .main .stMarkdown:not(.metric-card):not(.metric-card *), 
    .main .stMarkdown *:not(.metric-card):not(.metric-card *) {
        color: #1e1e1e !important;
    }
    
    /* Column content - but not if it's inside special cards */
    div[data-testid="column"]:not(:has(.metric-card)), 
    div[data-testid="column"]:not(:has(.metric-card)) * {
        color: #1e1e1e !important;
    }
    
    /* Block container content */
    .block-container:not(:has(.metric-card)), 
    .block-container:not(:has(.metric-card)) * {
        color: #1e1e1e !important;
    }
    
    /* Element container */
    .element-container:not(:has(.metric-card)), 
    .element-container:not(:has(.metric-card)) * {
        color: #1e1e1e !important;
    }
    
    /* Tables */
    .main table {
        color: #1e1e1e !important;
    }
    
    /* Input fields - better visibility */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1e1e1e !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Buttons - maintain visibility */
    button[kind="primary"] {
        background-color: #667eea !important;
        color: #ffffff !important;
    }
    
    button[kind="secondary"] {
        background-color: #6c757d !important;
        color: #ffffff !important;
    }
    
    /* Radio buttons and checkboxes labels */
    label {
        color: #1e1e1e !important;
    }
    
    /* Selectbox and multiselect */
    div[data-baseweb="select"] {
        background-color: #ffffff;
        color: #1e1e1e;
    }
    
    /* Info messages */
    div[data-testid="stMarkdownContainer"] {
        color: #1e1e1e;
    }
    
    /* Code blocks - keep readable */
    code {
        background-color: #f8f9fa;
        color: #d63384;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    pre {
        background-color: #f8f9fa;
        color: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
@st.cache_resource
def get_safe_managers():
    """Initialize manager instances that don't use widgets and are safe to cache."""
    return {
        'session': EnhancedSessionManager(),
        'results': ResultsManager()
    }

# Initialize the persistent state manager (with cookies) separately.
# This ensures it's created only once per session but NOT inside a cached function.
if 'persistent_manager' not in st.session_state:
    st.session_state.persistent_manager = PersistentStateManager()

# Get the cached managers
safe_managers = get_safe_managers()

# Combine all managers into a single dictionary for easy access throughout the app
managers = {
    'persistent': st.session_state.persistent_manager,
    'session': safe_managers['session'],
    'results': safe_managers['results']
}

# Initialize user profile with session-based isolation for multi-user support
if 'user_profile' not in st.session_state:
    username, system_id, session_id = get_current_user_info()
    # Create session-based profile for concurrent user access
    st.session_state.user_profile = create_session_profile(username, session_id=session_id, system_id=system_id)
    st.session_state.username = username
    st.session_state.system_id = system_id
    st.session_state.session_id = session_id

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard_home'
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'selected_algorithms' not in st.session_state:
    st.session_state.selected_algorithms = []
if 'experiment_results' not in st.session_state:
    st.session_state.experiment_results = {}
if 'interface_mode' not in st.session_state:
    # Load preferred mode from user profile
    st.session_state.interface_mode = st.session_state.user_profile.preferences.get('mode', 'Professional')


def main():
    """Main application entry point"""
    
    # Sidebar Navigation
    with st.sidebar:
        # User Profile Section
        st.markdown("### 👤 User Profile")
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**System:** {st.session_state.system_id[:8]}...")
        
        # Mode Toggle
        st.markdown("---")
        st.markdown("### 🎯 Interface Mode")
        new_mode = st.radio(
            "Select Mode",
            ["Beginner", "Professional"],
            index=0 if st.session_state.interface_mode == "Beginner" else 1,
            help="Beginner: Guided workflow with recommendations\nProfessional: Full control and advanced features"
        )
        
        if new_mode != st.session_state.interface_mode:
            st.session_state.interface_mode = new_mode
            # Save preference to user profile
            st.session_state.user_profile.preferences['mode'] = new_mode
            save_profile(st.session_state.user_profile)
            st.rerun()
        
        st.markdown("---")
        st.markdown("## 📍 Navigation")
        
        # Navigation buttons
        if st.button("🏠 Dashboard Home", use_container_width=True, 
                    type="primary" if st.session_state.current_page == 'dashboard_home' else "secondary"):
            st.session_state.current_page = 'dashboard_home'
            st.rerun()
        
        if st.button("🔬 New Experiment", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'new_experiment' else "secondary"):
            st.session_state.current_page = 'new_experiment'
            st.rerun()
        
        if st.button("📚 Results History", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'results_history' else "secondary"):
            st.session_state.current_page = 'results_history'
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        **MHA Toolbox v2.0**
        
        Analyze and compare 37+ metaheuristic algorithms with intuitive workflows and real-time progress tracking.
        """)
    
    # Route to appropriate page
    if st.session_state.current_page == 'dashboard_home':
        show_dashboard_home()
    elif st.session_state.current_page == 'new_experiment':
        show_new_experiment()
    elif st.session_state.current_page == 'results_history':
        show_results_history()


def show_dashboard_home():
    """Dashboard Home Page - Hides summary section if no history exists."""
    
    # The header is correctly placed here
    st.markdown("""
    <div class="main-header">
        <h1>🧬 MHA Analysis Dashboard</h1>
        <p>Professional Platform for Metaheuristic Algorithm Comparison and Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🏠 Dashboard Home")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    # Simplified - no session recovery for now
    if False:  # Disabled session recovery
        session_context = {}
        if session_context:
            st.success(f"👋 **Welcome back!** You have a previous session on the **{session_context['dataset_name']}** dataset.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Continue My Session", type="primary", use_container_width=True):
                    st.session_state.continue_session_id = session_id_from_browser
                    st.session_state.continue_session_context = session_context
                    st.session_state.current_page = 'new_experiment'
                    st.rerun()
            with col2:
                if st.button("🆕 No, Start New", use_container_width=True):
                    managers['persistent'].set_session_id_in_browser('')
                    st.rerun()
    else:
        # (existing quick actions logic)
        st.markdown("### 🚀 Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🔬 Start New Experiment</h3>
                <p>Run and compare algorithms on your dataset with guided workflow</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Run New Experiment", type="primary", use_container_width=True):
                st.session_state.current_page = 'new_experiment'
                st.rerun()
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 View Results</h3>
                <p>Access and analyze your previous experiment results</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📚 View Results History", use_container_width=True):
                st.session_state.current_page = 'results_history'
                st.rerun()

    # --- THIS IS THE UPDATED SECTION ---
    
    # First, check if a summary exists BEFORE rendering the title
    latest_summary = managers['results'].get_latest_run_summary()
    
    # Only render the entire "Last Run Summary" section if there are results
    if latest_summary:
        st.markdown("---")
        st.markdown("### 📊 Last Run Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Dataset", latest_summary['dataset_name'])
        with col2:
            st.metric("🏆 Best Performer", 
                     latest_summary['best_performer_name'].upper(),
                     f"{latest_summary['best_performer_fitness']:.6f}")
        with col3:
            st.metric("⚡ Fastest Algorithm", 
                     latest_summary['fastest_algorithm_name'].upper(),
                     f"{latest_summary['fastest_algorithm_time']:.2f}s")
        with col4:
            st.metric("🧬 Total Algorithms", latest_summary['total_algorithms'])
        st.info(f"📅 Last run: {latest_summary['last_run_date_human']}")


def show_new_experiment():
    """New Experiment Page - Guided 3-step workflow"""
    
    st.markdown("## 🔬 New Experiment")
    
    # Check interface mode and render accordingly
    if st.session_state.interface_mode == "Beginner":
        # Render beginner mode with guided workflow
        beginner = BeginnerMode()
        beginner.render()
        return
    
    # Professional Mode continues with existing workflow
    # Check if continuing a session
    if 'continue_session_context' in st.session_state:
        context = st.session_state.continue_session_context
        st.info(f"📂 **Continuing session**: {context['session_id']} | Dataset: {context['dataset_name']} | {context['total_algorithms']} algorithms already completed")
        
        # Option to start fresh instead
        if st.button("🔄 Start Fresh Instead"):
            del st.session_state.continue_session_context
            del st.session_state.continue_session_id
            st.rerun()
    
    # Three-tab guided workflow
    tab1, tab2, tab3 = st.tabs([
        "📊 Step 1: Select Dataset",
        "🧬 Step 2: Choose Algorithms",
        "⚙️ Step 3: Configure & Run"
    ])
    
    # TAB 1: Dataset Selection
    with tab1:
        show_dataset_selection_tab()
    
    # TAB 2: Algorithm Selection
    with tab2:
        show_algorithm_selection_tab()
    
    # TAB 3: Configuration and Run
    with tab3:
        show_configuration_and_run_tab()


def show_dataset_selection_tab():
    """Tab 1: Dataset Selection"""
    
    st.markdown("### <span class='step-indicator'>1</span> Select Your Dataset", unsafe_allow_html=True)
    
    # Dataset source selection
    data_source = st.radio(
        "Choose data source:",
        ["📦 Sample Datasets", "📤 Upload CSV", "🎲 Generate Dataset"],
        horizontal=True
    )
    
    if data_source == "📦 Sample Datasets":
        # Sample dataset grid
        st.markdown("#### Available Sample Datasets")
        
        datasets = [
            {"name": "Breast Cancer", "samples": 569, "features": 30, "type": "Classification"},
            {"name": "Wine", "samples": 178, "features": 13, "type": "Classification"},
            {"name": "Iris", "samples": 150, "features": 4, "type": "Classification"},
            {"name": "Digits", "samples": 1797, "features": 64, "type": "Classification"},
            {"name": "California Housing", "samples": 20640, "features": 8, "type": "Regression"},
            {"name": "Diabetes", "samples": 442, "features": 10, "type": "Regression"}
        ]
        
        # Display in grid
        cols = st.columns(3)
        
        for i, dataset in enumerate(datasets):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="algorithm-card">
                        <h4>{dataset['name']}</h4>
                        <p><strong>Samples:</strong> {dataset['samples']}</p>
                        <p><strong>Features:</strong> {dataset['features']}</p>
                        <p><strong>Type:</strong> {dataset['type']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select {dataset['name']}", key=f"select_{dataset['name']}", use_container_width=True):
                        st.session_state.selected_dataset = dataset['name']
                        st.session_state.dataset_type = 'sample'
                        st.success(f"✅ Selected: {dataset['name']}")
                        st.info("👉 Now proceed to **Step 2: Choose Algorithms**")
    
    elif data_source == "📤 Upload CSV":
        # CSV Upload
        st.markdown("#### Upload Your Dataset")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Preview
                with st.expander("📋 Dataset Preview"):
                    st.dataframe(df.head(10))
                    st.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                
                # Target selection
                target_col = st.selectbox("Select target column:", df.columns)
                
                if st.button("Confirm Dataset", type="primary"):
                    st.session_state.selected_dataset = uploaded_file.name
                    st.session_state.dataset_type = 'uploaded'
                    st.session_state.uploaded_data = df
                    st.session_state.target_column = target_col
                    st.success(f"✅ Dataset configured!")
                    st.info("👉 Now proceed to **Step 2: Choose Algorithms**")
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    elif data_source == "🎲 Generate Dataset":
        # Dataset Generator
        st.markdown("#### 🎲 Generate Synthetic Dataset")
        st.info("Generate domain-specific datasets for testing optimization algorithms")
        
        # Render dataset generator UI
        generator = DatasetGenerator()
        result = generator.render_generator_ui()
        
        if result:
            st.session_state.selected_dataset = f"Generated_{result['sector']}_{result['n_samples']}x{result['n_features']}"
            st.session_state.dataset_type = 'generated'
            st.session_state.generated_data = result
            st.success(f"✅ Dataset generated: {result['n_samples']} samples, {result['n_features']} features")
            st.info("👉 Now proceed to **Step 2: Choose Algorithms**")
    
    # Show current selection
    if st.session_state.selected_dataset:
        st.markdown("---")
        st.success(f"✅ **Currently Selected**: {st.session_state.selected_dataset}")


def show_algorithm_selection_tab():
    """Tab 2: Algorithm Selection with Custom Interface"""
    
    st.markdown("### <span class='step-indicator'>2</span> Choose Algorithms to Compare", unsafe_allow_html=True)
    
    if not st.session_state.selected_dataset:
        st.warning("⚠️ Please select a dataset first in **Step 1**")
        return
    
    # AI Recommendations based on dataset characteristics
    st.markdown("#### 🤖 AI Recommendations")
    
    # Get dataset info for recommendations
    if st.session_state.dataset_type == 'generated' and 'generated_data' in st.session_state:
        data_info = st.session_state.generated_data
        n_features = data_info['n_features']
        n_samples = data_info['n_samples']
        n_classes = data_info.get('n_classes', 2)
    elif st.session_state.dataset_type == 'uploaded' and 'uploaded_data' in st.session_state:
        df = st.session_state.uploaded_data
        n_features = df.shape[1] - 1
        n_samples = df.shape[0]
        n_classes = len(df[st.session_state.target_column].unique()) if st.session_state.target_column in df.columns else 2
    else:
        # Default for sample datasets
        dataset_info_map = {
            "Breast Cancer": (30, 569, 2),
            "Wine": (13, 178, 3),
            "Iris": (4, 150, 3),
            "Digits": (64, 1797, 10),
        }
        n_features, n_samples, n_classes = dataset_info_map.get(st.session_state.selected_dataset, (10, 100, 2))
    
    # Get AI recommendations
    recommendations = recommend_algorithms(n_features, n_samples, n_classes)
    
    with st.expander("📊 View AI Recommendations", expanded=True):
        st.write(f"**Dataset:** {n_features} features, {n_samples} samples, {n_classes} classes")
        
        rec_cols = st.columns(5)
        for i, (algo, score) in enumerate(recommendations[:10]):
            with rec_cols[i % 5]:
                st.metric(algo.upper(), f"{score:.2f}")
        
        if st.button("✨ Use Recommended Algorithms", key="use_recommended"):
            st.session_state.selected_algorithms = [algo for algo, _ in recommendations[:10]]
            st.success("✅ Top 10 recommended algorithms selected!")
            st.rerun()
    
    # Available algorithms (grouped by category)
    algorithm_groups = {
        "🐝 Swarm Intelligence": ["pso", "alo", "woa", "gwo", "ssa", "mrfo", "spider"],
        "🧬 Evolutionary": ["ga", "de", "eo", "innov"],
        "🌊 Physics-Based": ["sca", "sa", "hgso", "wca", "wdo"],
        "🔬 Bio-Inspired": ["ba", "fa", "csa", "coa", "msa"],
        "🌟 Novel": ["ao", "aoa", "cgo", "fbi", "gbo", "ica", "pfa", "qsa", "sma", "spbo", "tso", "vcs", "vns"],
        "🔥 Hybrid Algorithms": [
            "pso_ga_hybrid", "gwo_pso_hybrid", "de_pso_hybrid",
            "sa_ga_hybrid", "woa_ga_hybrid", "ba_pso_hybrid",
            "sca_pso_hybrid", "aco_pso_hybrid", "abc_de_hybrid",
            "fa_de_hybrid", "cs_ga_hybrid", "alo_pso_hybrid",
            "ssa_de_hybrid", "mvo_ga_hybrid", "hho_de_hybrid",
            "gto_pso_hybrid", "aoa_ga_hybrid", "rsa_pso_hybrid"
        ]
    }
    
    # Search bar
    search = st.text_input("🔍 Search algorithms", placeholder="Type to filter...")
    
    # Master controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Select All", use_container_width=True, key="select_all_btn"):
            all_algs = [alg for group in algorithm_groups.values() for alg in group]
            st.session_state.selected_algorithms = all_algs.copy()
            st.rerun()
    
    with col2:
        if st.button("⭐ Select Recommended (Top 10)", use_container_width=True, key="select_recommended_btn"):
            st.session_state.selected_algorithms = ["pso", "gwo", "sca", "woa", "alo", "ga", "de", "ssa", "fa", "ba"]
            st.rerun()
    
    with col3:
        if st.button("❌ Clear Selection", use_container_width=True, key="clear_selection_btn"):
            st.session_state.selected_algorithms = []
            st.rerun()
    
    st.markdown("---")
    
    # Display algorithm groups with checkboxes
    for group_name, algorithms in algorithm_groups.items():
        # Filter algorithms based on search
        filtered_algorithms = [alg for alg in algorithms 
                              if not search or search.lower() in alg.lower()]
        
        if not filtered_algorithms:
            continue
            
        with st.expander(f"{group_name} ({len(algorithms)} algorithms)", expanded=False):
            cols = st.columns(4)
            
            for i, alg in enumerate(filtered_algorithms):
                with cols[i % 4]:
                    # Check if algorithm is currently selected
                    is_selected = alg in st.session_state.selected_algorithms
                    
                    # Create checkbox with unique key
                    checkbox_key = f"alg_checkbox_{alg}_{is_selected}"
                    
                    # Use the checkbox and handle state changes
                    checked = st.checkbox(
                        alg.upper(), 
                        value=is_selected, 
                        key=checkbox_key
                    )
                    
                    # Update selection based on checkbox state
                    if checked and alg not in st.session_state.selected_algorithms:
                        st.session_state.selected_algorithms.append(alg)
                        st.rerun()
                    elif not checked and alg in st.session_state.selected_algorithms:
                        st.session_state.selected_algorithms.remove(alg)
                        st.rerun()
    
    # Selection summary
    st.markdown("---")
    if st.session_state.selected_algorithms:
        st.success(f"✅ **{len(st.session_state.selected_algorithms)} algorithms selected**")
        
        # Show first 10 selected
        display_algs = [alg.upper() for alg in st.session_state.selected_algorithms[:10]]
        alg_text = ", ".join(display_algs)
        
        if len(st.session_state.selected_algorithms) > 10:
            alg_text += f" ... and {len(st.session_state.selected_algorithms) - 10} more"
        
        st.info(f"📋 Selected: {alg_text}")
        st.info("👉 Proceed to **Step 3: Configure & Run**")
    else:
        st.warning("⚠️ No algorithms selected. Please select at least one algorithm.")


def show_configuration_and_run_tab():
    """Tab 3: Configuration and Run - ENHANCED WITH PERSISTENT RESULTS"""
    
    # FIXED: Check for persisted results first to prevent reversion on interactions
    if 'experiment_results' in st.session_state and st.session_state.experiment_results:
        st.success("✅ Experiment completed! View results below.")
        
        # Buttons to manage state
        col_back, col_clear = st.columns([3, 1])
        with col_back:
            if st.button("🔄 New Run", use_container_width=True):
                if 'experiment_results' in st.session_state:
                    del st.session_state.experiment_results
                st.rerun()
        with col_clear:
            if st.button("🗑️ Clear Results", use_container_width=True):
                if 'experiment_results' in st.session_state:
                    del st.session_state.experiment_results
                st.rerun()
        
        # Show persisted results dashboard
        show_results_dashboard(st.session_state.experiment_results)
        return  # Exit early, don't show config form
    
    # ORIGINAL: Show config form if no persisted results
    st.markdown("### <span class='step-indicator'>3</span> Configure & Run Experiment", unsafe_allow_html=True)
    
    # Validation
    if not st.session_state.selected_dataset:
        st.warning("⚠️ Please select a dataset in **Step 1**")
        return
    
    if not st.session_state.selected_algorithms:
        st.warning("⚠️ Please select algorithms in **Step 2**")
        return
    
    # Show configuration summary
    st.markdown("#### 📋 Experiment Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Dataset**: {st.session_state.selected_dataset}
        **Type**: {st.session_state.get('dataset_type', 'sample')}
        """)
    
    with col2:
        st.info(f"""
        **Algorithms**: {len(st.session_state.selected_algorithms)}
        **Names**: {', '.join([alg.upper() for alg in st.session_state.selected_algorithms[:5]])}{'...' if len(st.session_state.selected_algorithms) > 5 else ''}
        """)
    
    st.markdown("---")
    st.markdown("#### ⚙️ Parameters")
    
    # Hyperparameter Preset Configuration
    st.markdown("##### 🎛️ Preset Configuration")
    preset_type = st.selectbox(
        "Choose preset:",
        ["fast", "standard", "thorough", "research"],
        format_func=lambda x: {
            "fast": "⚡ Fast (Demo)",
            "standard": "⚖️ Standard (Balanced)",
            "thorough": "🎯 Thorough (Comprehensive)",
            "research": "🔬 Research (Maximum)"
        }[x],
        help="Pre-configured parameter sets optimized for different scenarios"
    )
    
    # Get preset configuration
    preset_config = get_preset_config(preset_type)
    
    # Display preset info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Population", f"{preset_config['population_multiplier']}x")
    with col2:
        st.metric("Iterations", f"{preset_config['iteration_multiplier']}x")
    with col3:
        st.metric("Runs", preset_config['n_runs'])
    with col4:
        st.metric("Timeout", f"{preset_config.get('timeout_minutes', 10)} min")
    
    # Dimension-aware adjustment
    if st.session_state.dataset_type == 'generated' and 'generated_data' in st.session_state:
        n_features = st.session_state.generated_data['n_features']
    else:
        n_features = 30  # Default
    
    hp_manager = HyperparameterManager(n_features)
    adjusted_params = hp_manager.get_algorithm_parameters("pso")  # Get base params
    
    st.info(f"📊 Dimension-aware: Adjusted for {n_features} features → Pop: {adjusted_params['population_size']}, Iter: {adjusted_params['max_iterations']}")
    
    # MLflow Integration
    st.markdown("##### 📊 MLflow Tracking")
    enable_mlflow = MLflowIntegration.render_mlflow_ui()
    
    # Parameter presets (keeping backward compatibility)
    preset = st.selectbox(
        "Legacy preset (override):",
        ["Use Preset Above", "Demo (Fast)", "Standard", "Thorough", "Custom"],
        help="Legacy parameter configuration (optional override)"
    )
    
    if preset != "Use Preset Above":
        if preset == "Demo (Fast)":
            max_iter, pop_size, n_runs, timeout = 20, 15, 2, 5
            st.info("⚡ Fast demo settings for quick results")
        elif preset == "Standard":
            max_iter, pop_size, n_runs, timeout = 50, 25, 3, 10
            st.info("⚖️ Balanced settings for good results")
        elif preset == "Thorough":
            max_iter, pop_size, n_runs, timeout = 100, 40, 5, 20
            st.info("🎯 Comprehensive settings for best results")
        else:
            col1, col2 = st.columns(2)
            with col1:
                max_iter = st.slider("Max Iterations", 10, 200, 50)
                pop_size = st.slider("Population Size", 10, 100, 25)
            with col2:
                n_runs = st.slider("Number of Runs", 1, 10, 3)
                timeout = st.slider("Timeout (minutes)", 1, 60, 10)
    else:
        # Use preset config values
        max_iter = int(adjusted_params['max_iterations'] * preset_config['iteration_multiplier'])
        pop_size = int(adjusted_params['population_size'] * preset_config['population_multiplier'])
        n_runs = preset_config['n_runs']
        timeout = preset_config.get('timeout_minutes', 10)
    
    # Advanced options (collapsed)
    with st.expander("⚙️ Advanced Options"):
        task_type = st.selectbox(
            "Task Type:",
            ["feature_selection", "feature_optimization", "hyperparameter_tuning"],
            format_func=lambda x: {
                "feature_selection": "🔍 Feature Selection",
                "feature_optimization": "🎯 Feature Optimization",
                "hyperparameter_tuning": "⚙️ Hyperparameter Tuning"
            }[x]
        )
        
        enable_detailed_tracking = st.checkbox("Enable detailed iteration tracking", value=True)
        save_results = st.checkbox("Auto-save results", value=True)
    
    st.markdown("---")
    
    # Final run button
    if st.button("🚀 Start Comparison", type="primary", use_container_width=True):
        # FIXED: Capture return value (assuming run_experiment_with_live_progress returns all_results)
        all_results = run_experiment_with_live_progress(
            max_iterations=max_iter,
            population_size=pop_size,
            n_runs=n_runs,
            timeout_minutes=timeout,
            task_type=task_type if 'task_type' in locals() else 'feature_selection'
        )
        
        # Persist results to session_state for persistence across reruns
        if all_results:
            st.session_state.experiment_results = all_results
            st.success("✅ Experiment completed successfully!")
            st.rerun()  # Rerun to show persisted results


def run_experiment_with_live_progress(max_iterations, population_size, n_runs, 
                                     timeout_minutes, task_type='feature_selection'):
    """Run experiment with live progress and save results to history."""
    
    st.markdown("---")
    st.markdown("## 🚀 Running Experiment")
    
    # (The code to load the dataset and set up the keep-awake context remains the same)
    # ...
    X, y, dataset_name = load_dataset(
        st.session_state.selected_dataset,
        st.session_state.get('dataset_type', 'sample')
    )
    if X is None:
        st.error("Failed to load dataset")
        return

    if WAKEPY_AVAILABLE:
        st.info("☕ **Keep-awake mode enabled** - Your system will stay active during the experiment.")
        keep_awake_context = keep.running()
    else:
        st.warning("⚠️ Sleep prevention not available. Install 'wakepy' to keep your system active: `pip install wakepy`")
        keep_awake_context = contextlib.nullcontext()

    with keep_awake_context:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        cards_placeholder = st.empty()
        algorithm_states = {alg: {'status': 'pending'} for alg in st.session_state.selected_algorithms}
        all_results = {}
        
        with cards_placeholder.container():
            for alg_name, state in algorithm_states.items():
                show_algorithm_card(alg_name, state['status'])

        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        managers['persistent'].set_session_id_in_browser(session_id)
        
        # The main loop remains the same
        for update in run_comparison_with_live_progress(
            X, y, dataset_name, task_type,
            st.session_state.selected_algorithms,
            max_iterations, population_size, n_runs, timeout_minutes
        ):
            # ... (all the existing loop logic is unchanged) ...
            algorithm = update['algorithm']
            status = update['status']
            progress = update.get('progress', 0)
            
            progress_bar.progress(progress)
            
            if algorithm in algorithm_states:
                if status == 'running':
                    status_text.text(f"🔄 Running {algorithm.upper()} [{update.get('iteration', '')}]...")
                    algorithm_states[algorithm]['status'] = 'running'
                elif status == 'completed' and 'result_data' in update:
                    status_text.text(f"✅ {algorithm.upper()} completed!")
                    all_results[algorithm] = update['result_data']
                    algorithm_states[algorithm]['status'] = 'completed'
                    algorithm_states[algorithm]['data'] = update['result_data']
                elif status == 'failed':
                    status_text.text(f"❌ {algorithm.upper()} failed: {update.get('error', 'Unknown error')}")
                    algorithm_states[algorithm]['status'] = 'failed'
                    algorithm_states[algorithm]['error'] = update.get('error')

            with cards_placeholder.container():
                for alg_name, state in algorithm_states.items():
                    show_algorithm_card(
                        alg_name, 
                        state['status'], 
                        result_data=state.get('data'), 
                        error=state.get('error')
                    )
            time.sleep(0.1)

    # Finalize
    progress_bar.progress(1.0)
    status_text.success("✅ All algorithms completed!")
    
    # --- THIS IS THE FIX ---
    # Persist the final results to a file for the history page
    if all_results:
        with st.spinner("💾 Saving experiment results to history..."):
            save_path = managers['results'].save_experiment_results(
                results=all_results,
                dataset_name=dataset_name,
                session_id=session_id
            )
            if save_path:
                st.success(f"Results for session `{session_id}` saved to history.")
            else:
                st.error("Failed to save results to history.")
    # --- END OF FIX ---

    # Store results in session state for the current view
    st.session_state.experiment_results = all_results
    
    # Show results dashboard for the current run
    if all_results:
        st.markdown("---")
        show_results_dashboard(all_results)


def show_algorithm_card(algorithm, status, result_data=None, error=None):
    """Display an algorithm card with status, including an animated emoji for 'running'."""
    
    card_class = f"algorithm-card algorithm-card-{status}"
    alg_display = algorithm.upper()
    
    with st.container():
        if status == 'pending':
            st.markdown(f"""
            <div class="{card_class}" style="border-left-color: #888;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>⏳</div>
                    <div>
                        <h4>{alg_display}</h4>
                        <p style="color: #888; margin: 0;"><strong>Queued...</strong></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif status == 'running':
            # --- THIS IS THE CHANGE ---
            # Using the emoji with the spinner class instead of the GIF
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>
                        <span class="spinner-emoji">⏳</span>
                    </div>
                    <div>
                        <h4>{alg_display}</h4>
                        <p style="color: #ffa500; margin: 0;"><strong>Running...</strong></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif status == 'completed' and result_data:
            stats = result_data.get('statistics', {})
            cols = st.columns([1, 2, 2, 2])
            with cols[0]:
                st.markdown(f"<div style='text-align: center; font-size: 2em; padding-top: 10px;'>✅</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{alg_display}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.metric("Best Fitness", f"{stats.get('best_fitness', 0):.6f}")
            with cols[2]:
                st.metric("Mean Fitness", f"{stats.get('mean_fitness', 0):.6f}")
            with cols[3]:
                st.metric("Execution Time", f"{stats.get('mean_time', 0):.2f}s")
        
        elif status == 'failed':
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>❌</div>
                    <div>
                        <h4>{alg_display} - Failed</h4>
                        <p style="color: #dc3545; margin: 0;"><strong>Error:</strong> {error or 'Unknown error'}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def show_results_dashboard(results):
    """Display comprehensive results dashboard with icons and better styling."""
    
    st.markdown("## 🎯 Results Dashboard")
    
    # Summary metrics with icons
    col1, col2, col3, col4 = st.columns(4)
    
    best_alg = min(results.items(), key=lambda x: x[1]['statistics']['best_fitness'])
    fastest_alg = min(results.items(), key=lambda x: x[1]['statistics']['mean_time'])
    
    with col1:
        st.metric("🧬 Algorithms Tested", len(results))
    
    with col2:
        st.metric("🏆 Best Performer",  # <-- ADDED EMOJI
                 best_alg[0].upper(),
                 f"{best_alg[1]['statistics']['best_fitness']:.6f}")
    
    with col3:
        st.metric("⚡ Fastest",  # <-- ADDED EMOJI
                 fastest_alg[0].upper(),
                 f"{fastest_alg[1]['statistics']['mean_time']:.2f}s")
    
    with col4:
        avg_time = np.mean([r['statistics']['mean_time'] for r in results.values()])
        st.metric("⏱️ Avg Time", f"{avg_time:.2f}s") # <-- ADDED EMOJI
    
    # Tabbed results (This part is now handled by the new tab structure)
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Summary", "⚖️ Comparative Analysis", "🔄 Convergence Analysis", "💾 Export"])

    with tab1:
        show_results_summary(results)
    with tab2:
        show_comparative_analysis(results)
    with tab3:
        show_convergence_analysis(results)
    with tab4:
        show_export_options(results)


def show_results_summary(results):
    """Show summary table and the main performance chart with dynamic colors."""
    
    st.markdown("### 📊 Performance Summary")
    
    # Create summary DataFrame
    summary_data = []
    for alg_name, result in results.items():
        stats = result['statistics']
        summary_data.append({
            'Algorithm': alg_name.upper(),
            'Best Fitness': stats['best_fitness'],
            'Mean Fitness': stats['mean_fitness'],
            'Std Dev': stats['std_fitness'],
            'Mean Time (s)': stats['mean_time'],
            'Runs': stats['total_runs']
        })
    df = pd.DataFrame(summary_data)
    
    # Display the table
    st.dataframe(df.style.format({
        'Best Fitness': '{:.6f}',
        'Mean Fitness': '{:.6f}',
        'Std Dev': '{:.6f}',
        'Mean Time (s)': '{:.2f}'
    }), use_container_width=True)
    
    # --- THIS IS THE KEY CHANGE ---
    # Main Performance Bar Chart (with dynamic coloring)
    st.markdown("### 📈 Performance Comparison: Mean Fitness")
    
    fig_bar = px.bar(
        df,
        x='Algorithm',
        y='Mean Fitness',
        color='Mean Fitness',  # <-- DYNAMIC COLORING ADDED
        color_continuous_scale='RdYlGn_r', # Green for low (good), Red for high (bad)
        title="Algorithm Performance: Mean Fitness (Lower is Better)",
        text_auto='.4f'
    )
    # This tells Plotly to inherit Streamlit's theme (light or dark)
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

def show_comparative_analysis(results):
    """Show comparative charts for deeper analysis."""
    
    st.markdown("### ⚖️ Comparative Analysis")

    # Create a DataFrame from the results for easy plotting
    summary_data = []
    for alg_name, result in results.items():
        stats = result['statistics']
        summary_data.append({
            'Algorithm': alg_name.upper(),
            'Mean Fitness': stats['mean_fitness'],
            'Mean Time (s)': stats['mean_time'],
            'Std Dev': stats['std_fitness'],
            'Runs': stats['total_runs']
        })
    df = pd.DataFrame(summary_data)
    
    # --- NEW FEATURE: Interactive Performance Chart ---
    st.markdown("#### 📈 Interactive Performance Comparison")
    
    metric_to_plot = st.selectbox(
        "Choose a metric to compare:",
        ['Mean Fitness', 'Mean Time (s)', 'Std Dev']
    )
    
    is_lower_better = "Time" in metric_to_plot or "Fitness" in metric_to_plot
    chart_title = f"Algorithm Performance: {metric_to_plot} ({'Lower is Better' if is_lower_better else 'Higher is Better'})"

    fig_interactive_bar = px.bar(
        df,
        x=metric_to_plot,
        y='Algorithm',
        orientation='h',
        color=metric_to_plot,
        color_continuous_scale='RdYlGn_r' if is_lower_better else 'RdYlGn',
        title=chart_title,
        text_auto='.4f'
    )
    fig_interactive_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_interactive_bar, use_container_width=True, theme=None)

    # --- Fitness vs. Time Trade-off Scatter Plot (Moved here) ---
    st.markdown("#### ⚖️ Fitness vs. Time Trade-off")
    st.write("Scatter: Lower X & Y = Ideal (Bubble size = Runs)")

    fig_scatter = px.scatter(
        df,
        x='Mean Time (s)',
        y='Mean Fitness',
        size='Runs',
        color='Algorithm',
        hover_name='Algorithm',
        title="Fitness vs. Time Trade-off"
    )
    fig_scatter.update_layout(
        xaxis_title="Time (s, lower is better)",
        yaxis_title="Mean Fitness (lower is better)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True, theme=None)

def show_convergence_analysis(results):
    """Show detailed analysis with convergence curves"""
    
    st.markdown("### 🔄 Convergence Analysis")
    
    # Convergence curves
    fig = go.Figure()
    
    for alg_name, result in results.items():
        # Get best run's convergence
        best_run = min(result['runs'], key=lambda x: x['best_fitness'])
        convergence = best_run['convergence_curve']
        
        fig.add_trace(go.Scatter(
            x=list(range(len(convergence))),
            y=convergence,
            mode='lines+markers',
            name=alg_name.upper(),
            line=dict(width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Convergence Curves (Best Runs)",
        xaxis_title="Iteration",
        yaxis_title="Fitness Value",
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_export_options(results):
    """Show export and download options"""
    
    st.markdown("### 💾 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        summary_data = []
        for alg_name, result in results.items():
            stats = result['statistics']
            summary_data.append({
                'Algorithm': alg_name.upper(),
                'Best_Fitness': stats['best_fitness'],
                'Mean_Fitness': stats['mean_fitness'],
                'Std_Fitness': stats['std_fitness'],
                'Mean_Time': stats['mean_time'],
                'Total_Runs': stats['total_runs']
            })
        
        df_export = pd.DataFrame(summary_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=csv,
            file_name=f"mha_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        import json
        
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_algorithms': len(results)
            },
            'results': {alg: result for alg, result in results.items()}
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Complete Results (JSON)",
            data=json_str,
            file_name=f"mha_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )


def show_results_history():
    """Results History Page"""
    
    st.markdown("## 📚 Results History")
    
    # Get all experiments
    experiments = managers['results'].list_all_experiments()
    
    if not experiments:
        st.info("📝 No previous results found. Run your first experiment to start building history!")
        return
    
    st.success(f"📂 Found {len(experiments)} previous experiments")
    
    # Display experiments
    for exp in experiments:
        with st.expander(f"📊 {exp['dataset_name']} - {exp['session_id']} ({exp['modified_at'][:10]})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text(f"Dataset: {exp['dataset_name']}")
            with col2:
                st.text(f"Session: {exp['session_id']}")
            with col3:
                st.text(f"Date: {exp['modified_at'][:10]}")
            
            # Load and display button
            if st.button(f"📊 View Results", key=f"view_{exp['session_id']}"):
                results = managers['results'].load_experiment_results(
                    exp['dataset_name'], 
                    exp['session_id']
                )
                
                if results:
                    st.session_state.experiment_results = results
                    show_results_dashboard(results)


def load_dataset(dataset_name, dataset_type):
    """Load dataset based on name and type"""
    
    try:
        if dataset_type == 'sample':
            from sklearn.datasets import (load_breast_cancer, load_wine, load_iris,
                                         load_digits, fetch_california_housing, load_diabetes)
            
            if dataset_name == "Breast Cancer":
                data = load_breast_cancer()
                return data.data, data.target, "Breast Cancer"
            
            elif dataset_name == "Wine":
                data = load_wine()
                return data.data, data.target, "Wine"
            
            elif dataset_name == "Iris":
                data = load_iris()
                return data.data, data.target, "Iris"
            
            elif dataset_name == "Digits":
                data = load_digits()
                return data.data, data.target, "Digits"
            
            elif dataset_name == "California Housing":
                data = fetch_california_housing()
                return data.data, data.target, "California Housing"
            
            elif dataset_name == "Diabetes":
                data = load_diabetes()
                return data.data, data.target, "Diabetes"
        
        elif dataset_type == 'uploaded':
            # Load from session state
            df = st.session_state.get('uploaded_data')
            target_col = st.session_state.get('target_column')
            
            if df is not None and target_col:
                feature_cols = [col for col in df.columns if col != target_col]
                X = df[feature_cols].values
                y = df[target_col].values
                return X, y, dataset_name
        
        return None, None, None
        
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None, None, None


if __name__ == "__main__":
    main()
