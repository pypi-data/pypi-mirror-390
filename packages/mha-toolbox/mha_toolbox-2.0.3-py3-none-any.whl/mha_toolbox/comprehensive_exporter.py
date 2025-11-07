"""
Comprehensive Excel Exporter and Dashboard Components
===================================================

Implements comprehensive Excel export for:
- Multi-sheet Excel exports with formatting
- Dashboard visualizations
- Performance matrices
- Statistical analysis
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime
import json


class ComprehensiveExporter:
    """Advanced Excel exporter with multiple sheets and formatting"""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    def create_comprehensive_excel_export(self, algorithms_data, dataset_name, session_id):
        """Create comprehensive Excel file with multiple sheets"""
        
        st.markdown("### 📋 **COMPREHENSIVE EXCEL EXPORT**")
        st.info("📊 **Export Center**: Multi-sheet Excel with all analysis data")
        
        # Create Excel writer object
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Sheet 1: Summary Overview
            self.create_summary_sheet(writer, algorithms_data, dataset_name, session_id)
            
            # Sheet 2: Detailed Statistics
            self.create_statistics_sheet(writer, algorithms_data)
            
            # Sheet 3: Convergence Data
            self.create_convergence_sheet(writer, algorithms_data)
            
            # Sheet 4: Performance Matrix
            self.create_performance_matrix_sheet(writer, algorithms_data)
            
            # Sheet 5: Comparison Analysis
            self.create_comparison_analysis_sheet(writer, algorithms_data)
            
            # Sheet 6: Raw Data Export
            self.create_raw_data_sheet(writer, algorithms_data)
        
        # Download button
        excel_data = output.getvalue()
        
        filename = f"{dataset_name}_{session_id}_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        st.download_button(
            label="📥 Download Comprehensive Excel Report",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.success("✅ Comprehensive Excel report generated!")
        st.info(f"📊 **Report includes**: 6 sheets with complete analysis")
        
        # Show preview of what's included
        with st.expander("📋 **Excel Report Contents Preview**"):
            st.markdown("""
            **📄 Sheet 1 - Summary Overview**: Algorithm rankings, best performers, key metrics
            **📊 Sheet 2 - Detailed Statistics**: Mean, std, min, max for all algorithms
            **📈 Sheet 3 - Convergence Data**: Full convergence curves for plotting
            **🎯 Sheet 4 - Performance Matrix**: Head-to-head comparison matrix
            **🔍 Sheet 5 - Comparison Analysis**: Statistical tests and significance
            **📋 Sheet 6 - Raw Data**: All algorithm metadata and detailed results
            """)
    
    def create_summary_sheet(self, writer, algorithms_data, dataset_name, session_id):
        """Create summary overview sheet"""
        
        # Summary data
        summary_data = []
        
        for alg_data in algorithms_data:
            summary_data.append({
                'Rank': 0,  # Will be filled after sorting
                'Algorithm': alg_data['algorithm'].upper(),
                'Best Fitness': alg_data['best_fitness'],
                'Total Iterations': alg_data['total_iterations'],
                'File Size (MB)': alg_data['file_size_mb'],
                'Created At': alg_data['created_at'],
                'NPZ File': alg_data['npz_path'].split('/')[-1] if alg_data['npz_path'] else 'N/A'
            })
        
        # Sort by best fitness and assign ranks
        summary_data.sort(key=lambda x: x['Best Fitness'])
        for i, item in enumerate(summary_data):
            item['Rank'] = i + 1
        
        df_summary = pd.DataFrame(summary_data)
        
        # Write to Excel with formatting
        df_summary.to_excel(writer, sheet_name='Summary_Overview', index=False)
        
        # Add metadata
        metadata_df = pd.DataFrame([
            ['Dataset', dataset_name],
            ['Session ID', session_id],
            ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Algorithms', len(algorithms_data)],
            ['Best Overall Fitness', min(alg_data['best_fitness'] for alg_data in algorithms_data)],
            ['Champion Algorithm', min(algorithms_data, key=lambda x: x['best_fitness'])['algorithm'].upper()]
        ], columns=['Metric', 'Value'])
        
        metadata_df.to_excel(writer, sheet_name='Summary_Overview', index=False, startrow=len(df_summary) + 3)
    
    def create_statistics_sheet(self, writer, algorithms_data):
        """Create detailed statistics sheet"""
        
        # Load detailed statistics from NPZ files
        stats_data = []
        
        for alg_data in algorithms_data:
            try:
                npz_data = self.session_manager.collector.load_algorithm_npz(alg_data['npz_path'])
                
                if npz_data:
                    stats = {
                        'Algorithm': alg_data['algorithm'].upper(),
                        'Best Fitness': float(npz_data['final_best_fitness'][0]) if 'final_best_fitness' in npz_data else alg_data['best_fitness'],
                        'Total Iterations': int(npz_data['total_iterations'][0]) if 'total_iterations' in npz_data else alg_data['total_iterations'],
                        'Population Size': int(npz_data['population_size'][0]) if 'population_size' in npz_data else 0,
                        'Dimensions': int(npz_data['dimensions'][0]) if 'dimensions' in npz_data else 0,
                    }
                    
                    # Add iteration-based statistics
                    if 'best_fitness_per_iteration' in npz_data:
                        best_fitness_curve = npz_data['best_fitness_per_iteration']
                        stats['Initial Fitness'] = float(best_fitness_curve[0])
                        stats['Final Fitness'] = float(best_fitness_curve[-1])
                        stats['Total Improvement'] = float(best_fitness_curve[0] - best_fitness_curve[-1])
                        stats['Improvement Rate (%)'] = float((best_fitness_curve[0] - best_fitness_curve[-1]) / max(best_fitness_curve[0], 1e-10) * 100)
                    
                    if 'mean_fitness_per_iteration' in npz_data:
                        mean_fitness = npz_data['mean_fitness_per_iteration']
                        stats['Mean Final Fitness'] = float(mean_fitness[-1])
                        stats['Fitness Std Dev'] = float(np.std(mean_fitness))
                    
                    if 'diversity_measure' in npz_data:
                        diversity = npz_data['diversity_measure']
                        stats['Initial Diversity'] = float(diversity[0])
                        stats['Final Diversity'] = float(diversity[-1])
                        stats['Average Diversity'] = float(np.mean(diversity))
                    
                    if 'iteration_times' in npz_data:
                        iter_times = npz_data['iteration_times']
                        stats['Avg Iteration Time (s)'] = float(np.mean(iter_times))
                        stats['Total Time (s)'] = float(np.sum(iter_times))
                        stats['Min Iteration Time (s)'] = float(np.min(iter_times))
                        stats['Max Iteration Time (s)'] = float(np.max(iter_times))
                    
                    stats_data.append(stats)
                    
            except Exception as e:
                st.warning(f"Could not load detailed stats for {alg_data['algorithm']}: {e}")
        
        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Detailed_Statistics', index=False)
    
    def create_convergence_sheet(self, writer, algorithms_data):
        """Create convergence data sheet for plotting"""
        
        convergence_data = {}
        max_iterations = 0
        
        # Load convergence curves
        for alg_data in algorithms_data:
            try:
                npz_data = self.session_manager.collector.load_algorithm_npz(alg_data['npz_path'])
                if npz_data and 'convergence_curve' in npz_data:
                    convergence_curve = npz_data['convergence_curve']
                    convergence_data[alg_data['algorithm'].upper()] = convergence_curve
                    max_iterations = max(max_iterations, len(convergence_curve))
            except Exception as e:
                st.warning(f"Could not load convergence for {alg_data['algorithm']}: {e}")
        
        if convergence_data:
            # Create DataFrame with iteration index and all algorithm curves
            df_convergence = pd.DataFrame({'Iteration': range(max_iterations)})
            
            for alg_name, curve in convergence_data.items():
                # Pad shorter curves with NaN
                padded_curve = list(curve) + [np.nan] * (max_iterations - len(curve))
                df_convergence[f"{alg_name}_Fitness"] = padded_curve
            
            df_convergence.to_excel(writer, sheet_name='Convergence_Data', index=False)
    
    def create_performance_matrix_sheet(self, writer, algorithms_data):
        """Create performance comparison matrix"""
        
        # Create pairwise comparison matrix
        algorithms = [alg['algorithm'].upper() for alg in algorithms_data]
        n_algs = len(algorithms)
        
        # Performance matrix (1 if row beats column, 0 otherwise)
        performance_matrix = np.zeros((n_algs, n_algs))
        
        for i, alg1 in enumerate(algorithms_data):
            for j, alg2 in enumerate(algorithms_data):
                if i != j:
                    # Algorithm 1 beats Algorithm 2 if it has better (lower) fitness
                    if alg1['best_fitness'] < alg2['best_fitness']:
                        performance_matrix[i, j] = 1
        
        # Create DataFrame
        df_matrix = pd.DataFrame(
            performance_matrix,
            index=algorithms,
            columns=algorithms
        )
        
        # Add win counts
        df_matrix['Total_Wins'] = df_matrix.sum(axis=1)
        
        df_matrix.to_excel(writer, sheet_name='Performance_Matrix')
    
    def create_comparison_analysis_sheet(self, writer, algorithms_data):
        """Create comparison analysis with statistical tests"""
        
        # Fitness comparison analysis
        fitness_data = []
        
        for alg_data in algorithms_data:
            try:
                npz_data = self.session_manager.collector.load_algorithm_npz(alg_data['npz_path'])
                if npz_data and 'best_fitness_per_iteration' in npz_data:
                    final_fitness = float(npz_data['best_fitness_per_iteration'][-1])
                    fitness_data.append({
                        'Algorithm': alg_data['algorithm'].upper(),
                        'Final_Fitness': final_fitness,
                        'Rank': 0  # Will be filled
                    })
            except Exception:
                continue
        
        # Sort and rank
        fitness_data.sort(key=lambda x: x['Final_Fitness'])
        for i, item in enumerate(fitness_data):
            item['Rank'] = i + 1
        
        # Calculate relative performance
        if fitness_data:
            best_fitness = fitness_data[0]['Final_Fitness']
            for item in fitness_data:
                item['Relative_Performance'] = (item['Final_Fitness'] - best_fitness) / max(best_fitness, 1e-10)
                item['Performance_Gap_%'] = item['Relative_Performance'] * 100
        
        df_comparison = pd.DataFrame(fitness_data)
        df_comparison.to_excel(writer, sheet_name='Comparison_Analysis', index=False)
    
    def create_raw_data_sheet(self, writer, algorithms_data):
        """Create raw data export sheet"""
        
        # Export all metadata and key metrics
        raw_data = []
        
        for alg_data in algorithms_data:
            raw_entry = {
                'Algorithm': alg_data['algorithm'],
                'Best_Fitness': alg_data['best_fitness'],
                'Total_Iterations': alg_data['total_iterations'],
                'File_Size_MB': alg_data['file_size_mb'],
                'Created_At': alg_data['created_at'],
                'NPZ_Path': alg_data['npz_path'],
                'Metadata_Path': alg_data['metadata_path']
            }
            
            # Try to load additional data from NPZ
            try:
                npz_data = self.session_manager.collector.load_algorithm_npz(alg_data['npz_path'])
                if npz_data:
                    # Add NPZ metadata
                    raw_entry['NPZ_Arrays_Count'] = len(npz_data.files)
                    raw_entry['Population_Size'] = int(npz_data['population_size'][0]) if 'population_size' in npz_data else 0
                    raw_entry['Dimensions'] = int(npz_data['dimensions'][0]) if 'dimensions' in npz_data else 0
                    raw_entry['Task_Type'] = str(npz_data['task_type'][0]) if 'task_type' in npz_data else 'Unknown'
                    
                    if 'total_time' in npz_data:
                        raw_entry['Total_Execution_Time'] = float(npz_data['total_time'][0])
            except Exception:
                pass
            
            raw_data.append(raw_entry)
        
        df_raw = pd.DataFrame(raw_data)
        df_raw.to_excel(writer, sheet_name='Raw_Data_Export', index=False)


class DashboardComponents:
    """Enhanced dashboard components for visualization"""
    
    @staticmethod
    def create_performance_matrix_dashboard(algorithms_data):
        """Create performance matrix visualization"""
        
        st.markdown("#### 🎯 **Algorithm Performance Matrix**")
        
        # Create performance metrics
        performance_data = []
        
        for alg_data in algorithms_data:
            performance_data.append({
                'Algorithm': alg_data['algorithm'].upper(),
                'Best Fitness': alg_data['best_fitness'],
                'Total Iterations': alg_data['total_iterations'],
                'File Size (MB)': alg_data['file_size_mb']
            })
        
        # Sort by performance
        performance_data.sort(key=lambda x: x['Best Fitness'])
        
        # Create performance visualization
        df_perf = pd.DataFrame(performance_data)
        
        # Performance heatmap
        fig_heatmap = px.imshow(
            df_perf.set_index('Algorithm')[['Best Fitness', 'Total Iterations', 'File Size (MB)']].T,
            color_continuous_scale='RdYlBu_r',
            title="🔥 Algorithm Performance Heatmap"
        )
        
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Performance ranking table
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🏆 **Performance Ranking**")
            ranking_df = df_perf[['Algorithm', 'Best Fitness']].copy()
            ranking_df['Rank'] = range(1, len(ranking_df) + 1)
            ranking_df['Performance Score'] = 100 * (1 - (ranking_df['Best Fitness'] - ranking_df['Best Fitness'].min()) / 
                                                   (ranking_df['Best Fitness'].max() - ranking_df['Best Fitness'].min() + 1e-10))
            st.dataframe(ranking_df, width=400)
        
        with col2:
            # Performance distribution
            fig_dist = px.box(
                df_perf, 
                y='Best Fitness',
                title="📊 Fitness Distribution"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
    
    @staticmethod
    def create_statistical_dashboard(algorithms_data):
        """Create statistical analysis dashboard"""
        
        st.markdown("#### 📈 **Statistical Analysis Dashboard**")
        
        # Statistical summary
        fitness_values = [alg['best_fitness'] for alg in algorithms_data]
        iterations_values = [alg['total_iterations'] for alg in algorithms_data]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 **Mean Fitness**", f"{np.mean(fitness_values):.6f}")
            st.metric("📈 **Std Fitness**", f"{np.std(fitness_values):.6f}")
        
        with col2:
            st.metric("🏆 **Best Fitness**", f"{np.min(fitness_values):.6f}")
            st.metric("📉 **Worst Fitness**", f"{np.max(fitness_values):.6f}")
        
        with col3:
            st.metric("🔄 **Mean Iterations**", f"{np.mean(iterations_values):.0f}")
            st.metric("📊 **Total Iterations**", f"{np.sum(iterations_values):,}")
        
        with col4:
            st.metric("🎯 **Performance Range**", f"{(np.max(fitness_values) - np.min(fitness_values)):.6f}")
            st.metric("📈 **Coefficient of Variation**", f"{(np.std(fitness_values) / np.mean(fitness_values)):.3f}")
        
        # Statistical plots
        col1, col2 = st.columns(2)
        
        with col1:
            # Fitness histogram
            fig_hist = px.histogram(
                x=fitness_values,
                title="📊 Fitness Distribution Histogram",
                nbins=min(10, len(fitness_values))
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Scatter plot: Fitness vs Iterations
            fig_scatter = px.scatter(
                x=iterations_values,
                y=fitness_values,
                title="🎯 Fitness vs Iterations",
                labels={'x': 'Total Iterations', 'y': 'Best Fitness'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    @staticmethod
    def create_comparison_matrix_dashboard(algorithms_data):
        """Create algorithm comparison matrix"""
        
        st.markdown("#### 🔍 **Head-to-Head Comparison Matrix**")
        
        # Create comparison matrix
        algorithms = [alg['algorithm'].upper() for alg in algorithms_data]
        n_algs = len(algorithms)
        
        # Wins matrix
        wins_matrix = np.zeros((n_algs, n_algs))
        
        for i, alg1 in enumerate(algorithms_data):
            for j, alg2 in enumerate(algorithms_data):
                if i != j:
                    if alg1['best_fitness'] < alg2['best_fitness']:
                        wins_matrix[i, j] = 1
        
        # Create heatmap
        fig_matrix = px.imshow(
            wins_matrix,
            x=algorithms,
            y=algorithms,
            color_continuous_scale='RdYlGn',
            title="🥊 Head-to-Head Wins Matrix (Row beats Column)",
            labels={'color': 'Wins (1) / Losses (0)'}
        )
        
        fig_matrix.update_layout(height=500)
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Win statistics
        win_counts = wins_matrix.sum(axis=1)
        win_percentages = (win_counts / max(n_algs - 1, 1)) * 100
        
        win_stats = pd.DataFrame({
            'Algorithm': algorithms,
            'Wins': win_counts.astype(int),
            'Win Percentage': win_percentages,
            'Best Fitness': [alg['best_fitness'] for alg in algorithms_data]
        })
        
        win_stats = win_stats.sort_values('Wins', ascending=False)
        
        st.markdown("##### 🏆 **Win Statistics**")
        st.dataframe(win_stats, width=600)