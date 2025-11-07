"""
Real-time Visualization Manager
==============================

Professional visualization system with:
- Real-time convergence plotting
- Individual algorithm analysis
- Comparative bar charts and statistics
- Interactive dashboard components
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional


class RealTimeVisualizer:
    """Advanced real-time visualization manager"""
    
    def __init__(self):
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
        ]
    
    def display_main_dashboard(self, session_controller):
        """Display the main visualization dashboard"""
        
        st.markdown("# 📊 **Real-time Algorithm Analysis**")
        
        # Get session data
        algorithm_results = session_controller.get_algorithm_results()
        current_progress = st.session_state.current_progress
        
        if not algorithm_results and current_progress['status'] != 'running':
            self._display_empty_state()
            return
        
        # Layout with tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 **Live Convergence**", 
            "📊 **Performance Comparison**", 
            "🔍 **Individual Analysis**", 
            "📋 **Summary Statistics**"
        ])
        
        with tab1:
            self._display_live_convergence(algorithm_results, current_progress)
        
        with tab2:
            self._display_performance_comparison(algorithm_results)
        
        with tab3:
            self._display_individual_analysis(algorithm_results)
        
        with tab4:
            self._display_summary_statistics(algorithm_results, session_controller)
    
    def _display_empty_state(self):
        """Display empty state when no data is available"""
        
        st.markdown("""
        <div style="
            text-align: center; 
            padding: 4rem 2rem; 
            background: #f8f9fa; 
            border-radius: 15px;
            margin: 2rem 0;
        ">
            <h2>📊 No Results Yet</h2>
            <p style="font-size: 1.2rem; color: #666; margin: 1rem 0;">
                Start running algorithms to see real-time visualizations here
            </p>
            <p style="color: #888;">
                Your convergence curves, performance comparisons, and detailed analytics will appear as algorithms complete
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show example visualization
        st.markdown("### 🎯 **What You'll See Here:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Example convergence plot
            fig = self._create_example_convergence_plot()
            st.plotly_chart(fig, use_container_width=True)
            st.caption("**Real-time Convergence Curves** - Watch algorithms improve in real-time")
        
        with col2:
            # Example comparison plot
            fig = self._create_example_comparison_plot()
            st.plotly_chart(fig, use_container_width=True)
            st.caption("**Performance Comparison** - Compare algorithm effectiveness")
    
    def _display_live_convergence(self, algorithm_results: Dict, current_progress: Dict):
        """Display live convergence curves"""
        
        st.markdown("### 📈 **Live Convergence Tracking**")
        
        if current_progress['status'] == 'running':
            # Show currently running algorithm
            st.markdown(f"**🔄 Currently Running: {current_progress['algorithm_name']}**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Iteration", f"{current_progress['current_iteration']}/{current_progress['max_iterations']}")
            with col2:
                st.metric("Progress", f"{current_progress['progress_percentage']:.1f}%")
            with col3:
                if current_progress.get('current_fitness'):
                    st.metric("Current Fitness", f"{current_progress['current_fitness']:.6f}")
            
            # Progress bar
            st.progress(current_progress['progress_percentage'] / 100)
        
        # Create convergence plot
        if algorithm_results:
            fig = self._create_convergence_plot(algorithm_results)
            st.plotly_chart(fig, use_container_width=True)
        
        # Auto-refresh toggle
        col1, col2 = st.columns([3, 1])
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=st.session_state.get('auto_refresh', True))
            st.session_state.auto_refresh = auto_refresh
            
            if auto_refresh and current_progress['status'] == 'running':
                st.rerun()
    
    def _display_performance_comparison(self, algorithm_results: Dict):
        """Display performance comparison charts"""
        
        st.markdown("### 📊 **Performance Comparison**")
        
        if not algorithm_results:
            st.info("Run multiple algorithms to see performance comparisons")
            return
        
        # Performance metrics
        metrics_df = self._prepare_performance_metrics(algorithm_results)
        
        # Side-by-side layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Best fitness comparison
            fig_fitness = self._create_fitness_comparison(metrics_df)
            st.plotly_chart(fig_fitness, use_container_width=True)
        
        with col2:
            # Execution time comparison
            fig_time = self._create_time_comparison(metrics_df)
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Combined performance chart
        st.markdown("#### 🎯 **Combined Performance Analysis**")
        fig_combined = self._create_combined_performance_chart(metrics_df)
        st.plotly_chart(fig_combined, use_container_width=True)
        
        # Performance ranking table
        st.markdown("#### 🏆 **Algorithm Rankings**")
        ranking_df = self._create_ranking_table(metrics_df)
        st.dataframe(ranking_df, use_container_width=True)
    
    def _display_individual_analysis(self, algorithm_results: Dict):
        """Display individual algorithm analysis"""
        
        st.markdown("### 🔍 **Individual Algorithm Analysis**")
        
        if not algorithm_results:
            st.info("No algorithms to analyze yet")
            return
        
        # Algorithm selector
        selected_algorithm = st.selectbox(
            "Select Algorithm for Detailed Analysis:",
            list(algorithm_results.keys()),
            key="individual_analysis_selector"
        )
        
        if selected_algorithm:
            self._show_algorithm_details(selected_algorithm, algorithm_results[selected_algorithm])
    
    def _display_summary_statistics(self, algorithm_results: Dict, session_controller):
        """Display comprehensive summary statistics"""
        
        st.markdown("### 📋 **Session Summary & Statistics**")
        
        if not algorithm_results:
            st.info("No statistics available yet")
            return
        
        # Session overview
        session_summary = session_controller.get_session_summary()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🧬 **Total Algorithms**", session_summary['total_algorithms'])
        with col2:
            st.metric("🏆 **Best Algorithm**", session_summary['best_algorithm'])
        with col3:
            st.metric("📈 **Best Fitness**", f"{session_summary['best_fitness']:.6f}")
        with col4:
            st.metric("⏱️ **Total Time**", f"{session_summary['total_execution_time']:.1f}s")
        
        # Statistical analysis
        stats_df = self._calculate_comprehensive_stats(algorithm_results)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 **Statistical Summary**")
            st.dataframe(stats_df, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 **Performance Distribution**")
            fig_dist = self._create_performance_distribution(algorithm_results)
            st.plotly_chart(fig_dist, use_container_width=True)
    
    def _create_convergence_plot(self, algorithm_results: Dict):
        """Create interactive convergence plot"""
        
        fig = go.Figure()
        
        for i, (alg_name, results) in enumerate(algorithm_results.items()):
            convergence_curve = results.get('convergence_curve', [])
            
            if convergence_curve:
                iterations = list(range(len(convergence_curve)))
                
                fig.add_trace(go.Scatter(
                    x=iterations,
                    y=convergence_curve,
                    mode='lines+markers',
                    name=alg_name.upper(),
                    line=dict(color=self.colors[i % len(self.colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=f"<b>{alg_name.upper()}</b><br>Iteration: %{{x}}<br>Fitness: %{{y:.6f}}<extra></extra>"
                ))
        
        fig.update_layout(
            title="📈 Convergence Curves Comparison",
            xaxis_title="Iteration",
            yaxis_title="Fitness Value",
            hovermode='x unified',
            showlegend=True,
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def _create_fitness_comparison(self, metrics_df: pd.DataFrame):
        """Create fitness comparison bar chart"""
        
        fig = px.bar(
            metrics_df,
            x='Algorithm',
            y='Best Fitness',
            color='Best Fitness',
            color_continuous_scale='RdYlBu_r',
            title="🎯 Best Fitness Comparison"
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def _create_time_comparison(self, metrics_df: pd.DataFrame):
        """Create execution time comparison"""
        
        fig = px.bar(
            metrics_df,
            x='Algorithm',
            y='Execution Time',
            color='Execution Time',
            color_continuous_scale='viridis',
            title="⏱️ Execution Time Comparison"
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def _create_combined_performance_chart(self, metrics_df: pd.DataFrame):
        """Create combined performance scatter plot"""
        
        fig = px.scatter(
            metrics_df,
            x='Execution Time',
            y='Best Fitness',
            size='Convergence Rate',
            color='Algorithm',
            title="🎯 Performance vs Speed Analysis",
            hover_data=['Algorithm', 'Best Fitness', 'Execution Time'],
            size_max=20
        )
        
        fig.update_layout(
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def _create_performance_distribution(self, algorithm_results: Dict):
        """Create performance distribution plot"""
        
        fitness_values = [results.get('best_fitness', 0) for results in algorithm_results.values()]
        
        fig = px.histogram(
            x=fitness_values,
            title="📊 Fitness Distribution",
            nbins=min(10, len(fitness_values)),
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            xaxis_title="Fitness Value",
            yaxis_title="Count",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def _show_algorithm_details(self, algorithm_name: str, results: Dict):
        """Show detailed analysis for individual algorithm"""
        
        st.markdown(f"#### 🔍 **{algorithm_name.upper()} Detailed Analysis**")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 **Best Fitness**", f"{results.get('best_fitness', 0):.6f}")
        with col2:
            st.metric("🔄 **Iterations**", results.get('total_iterations', 0))
        with col3:
            st.metric("⏱️ **Time**", f"{results.get('execution_time', 0):.2f}s")
        with col4:
            convergence_rate = results.get('convergence_rate', 0)
            st.metric("📈 **Convergence Rate**", f"{convergence_rate:.4f}")
        
        # Individual convergence plot
        if results.get('convergence_curve'):
            fig = go.Figure()
            
            convergence_curve = results['convergence_curve']
            iterations = list(range(len(convergence_curve)))
            
            fig.add_trace(go.Scatter(
                x=iterations,
                y=convergence_curve,
                mode='lines+markers',
                name=algorithm_name.upper(),
                line=dict(width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=f"📈 {algorithm_name.upper()} Convergence Curve",
                xaxis_title="Iteration",
                yaxis_title="Fitness Value",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional statistics
        if results.get('statistics'):
            st.markdown("#### 📊 **Additional Statistics**")
            
            stats = results['statistics']
            stats_data = []
            
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    stats_data.append({
                        'Metric': key.replace('_', ' ').title(),
                        'Value': f"{value:.6f}" if isinstance(value, float) else str(value)
                    })
            
            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True)
    
    def _prepare_performance_metrics(self, algorithm_results: Dict) -> pd.DataFrame:
        """Prepare performance metrics dataframe"""
        
        metrics_data = []
        
        for alg_name, results in algorithm_results.items():
            metrics_data.append({
                'Algorithm': alg_name.upper(),
                'Best Fitness': results.get('best_fitness', float('inf')),
                'Execution Time': results.get('execution_time', 0),
                'Total Iterations': results.get('total_iterations', 0),
                'Convergence Rate': results.get('convergence_rate', 0)
            })
        
        return pd.DataFrame(metrics_data)
    
    def _create_ranking_table(self, metrics_df: pd.DataFrame) -> pd.DataFrame:
        """Create algorithm ranking table"""
        
        # Sort by best fitness (ascending for minimization)
        ranking_df = metrics_df.sort_values('Best Fitness').reset_index(drop=True)
        ranking_df.insert(0, 'Rank', range(1, len(ranking_df) + 1))
        
        # Add ranking emojis
        emoji_map = {1: '🥇', 2: '🥈', 3: '🥉'}
        ranking_df['Medal'] = ranking_df['Rank'].map(lambda x: emoji_map.get(x, ''))
        
        return ranking_df
    
    def _calculate_comprehensive_stats(self, algorithm_results: Dict) -> pd.DataFrame:
        """Calculate comprehensive statistics"""
        
        fitness_values = [results.get('best_fitness', 0) for results in algorithm_results.values()]
        time_values = [results.get('execution_time', 0) for results in algorithm_results.values()]
        
        stats_data = {
            'Metric': [
                'Mean Fitness', 'Median Fitness', 'Std Fitness',
                'Min Fitness', 'Max Fitness', 'Range',
                'Mean Time', 'Total Time', 'Best Algorithm'
            ],
            'Value': [
                f"{np.mean(fitness_values):.6f}",
                f"{np.median(fitness_values):.6f}",
                f"{np.std(fitness_values):.6f}",
                f"{np.min(fitness_values):.6f}",
                f"{np.max(fitness_values):.6f}",
                f"{np.max(fitness_values) - np.min(fitness_values):.6f}",
                f"{np.mean(time_values):.2f}s",
                f"{np.sum(time_values):.2f}s",
                min(algorithm_results.keys(), key=lambda x: algorithm_results[x].get('best_fitness', float('inf'))).upper()
            ]
        }
        
        return pd.DataFrame(stats_data)
    
    def _create_example_convergence_plot(self):
        """Create example convergence plot for empty state"""
        
        # Generate sample data
        iterations = list(range(50))
        pso_curve = [1.0 * np.exp(-i/15) + np.random.normal(0, 0.02) for i in iterations]
        ga_curve = [1.0 * np.exp(-i/12) + np.random.normal(0, 0.03) for i in iterations]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=iterations, y=pso_curve, mode='lines', name='PSO',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=iterations, y=ga_curve, mode='lines', name='GA',
            line=dict(color='#ff7f0e', width=3)
        ))
        
        fig.update_layout(
            title="Example: Convergence Curves",
            xaxis_title="Iteration",
            yaxis_title="Fitness Value",
            height=300,
            template="plotly_white"
        )
        
        return fig
    
    def _create_example_comparison_plot(self):
        """Create example comparison plot for empty state"""
        
        algorithms = ['PSO', 'GA', 'SMA', 'WOA']
        fitness_values = [0.045, 0.052, 0.038, 0.041]
        
        fig = px.bar(
            x=algorithms,
            y=fitness_values,
            color=fitness_values,
            color_continuous_scale='RdYlBu_r',
            title="Example: Performance Comparison"
        )
        
        fig.update_layout(
            xaxis_title="Algorithm",
            yaxis_title="Best Fitness",
            height=300,
            showlegend=False,
            template="plotly_white"
        )
        
        return fig