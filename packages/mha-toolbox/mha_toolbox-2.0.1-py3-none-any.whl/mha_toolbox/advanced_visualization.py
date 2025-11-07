"""
Advanced Visualization and Professional Export System
====================================================

This module provides comprehensive visualization capabilities and professional data export
with multiple sheets for systematic parameter storage.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import io
import base64
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


class AdvancedVisualizer:
    """Advanced visualization system for optimization results"""
    
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
        self.default_layout = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': dict(l=80, r=80, t=80, b=80),
            'showlegend': True,
            'legend': dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        }
    
    def create_convergence_comparison(self, results_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive convergence comparison plot"""
        
        fig = go.Figure()
        
        for i, (alg_name, result) in enumerate(results_data.items()):
            if 'convergence_curve' in result:
                color = self.colors[i % len(self.colors)]
                
                # Main convergence curve
                fig.add_trace(go.Scatter(
                    x=list(range(len(result['convergence_curve']))),
                    y=result['convergence_curve'],
                    mode='lines',
                    name=f'{alg_name}',
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{alg_name}</b><br>' +
                                'Iteration: %{x}<br>' +
                                'Best Fitness: %{y:.6f}<br>' +
                                '<extra></extra>'
                ))
                
                # Add final point marker
                fig.add_trace(go.Scatter(
                    x=[len(result['convergence_curve'])-1],
                    y=[result['convergence_curve'][-1]],
                    mode='markers',
                    name=f'{alg_name} Final',
                    marker=dict(color=color, size=10, symbol='star'),
                    showlegend=False,
                    hovertemplate=f'<b>{alg_name} Final</b><br>' +
                                f'Best Fitness: {result["convergence_curve"][-1]:.6f}<br>' +
                                '<extra></extra>'
                ))
        
        fig.update_layout(
            title={
                'text': '<b>Algorithm Convergence Comparison</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='<b>Iteration</b>',
            yaxis_title='<b>Best Fitness Value</b>',
            yaxis_type='log',
            **self.default_layout
        )
        
        return fig
    
    def create_performance_comparison(self, results_data: Dict[str, Any]) -> go.Figure:
        """Create performance comparison bar chart"""
        
        algorithms = list(results_data.keys())
        best_fitness = [results_data[alg].get('best_fitness', float('inf')) for alg in algorithms]
        iterations_to_converge = []
        
        # Calculate iterations to convergence (95% of final value)
        for alg in algorithms:
            if 'convergence_curve' in results_data[alg]:
                curve = results_data[alg]['convergence_curve']
                final_val = curve[-1]
                threshold = final_val * 1.05  # 95% convergence
                
                converged_at = len(curve)
                for i, val in enumerate(curve):
                    if val <= threshold:
                        converged_at = i
                        break
                iterations_to_converge.append(converged_at)
            else:
                iterations_to_converge.append(0)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Best Fitness Achieved', 'Convergence Speed', 
                          'Fitness Distribution', 'Algorithm Ranking'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "box"}, {"type": "bar"}]]
        )
        
        # Best fitness comparison
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=best_fitness,
                name='Best Fitness',
                marker_color=self.colors[:len(algorithms)],
                text=[f'{val:.4f}' for val in best_fitness],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Best Fitness: %{y:.6f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Convergence speed
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=iterations_to_converge,
                name='Iterations to Converge',
                marker_color=self.colors[:len(algorithms)],
                text=iterations_to_converge,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Iterations: %{y}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Fitness distribution (box plot)
        for i, alg in enumerate(algorithms):
            if 'convergence_curve' in results_data[alg]:
                curve = results_data[alg]['convergence_curve']
                fig.add_trace(
                    go.Box(
                        y=curve,
                        name=alg,
                        marker_color=self.colors[i % len(self.colors)],
                        boxpoints='outliers'
                    ),
                    row=2, col=1
                )
        
        # Algorithm ranking
        ranking_scores = []
        for i, alg in enumerate(algorithms):
            # Composite score: normalized fitness + normalized convergence speed
            norm_fitness = 1 - (best_fitness[i] - min(best_fitness)) / (max(best_fitness) - min(best_fitness) + 1e-10)
            norm_speed = 1 - (iterations_to_converge[i] - min(iterations_to_converge)) / (max(iterations_to_converge) - min(iterations_to_converge) + 1e-10)
            score = (norm_fitness + norm_speed) / 2
            ranking_scores.append(score)
        
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=ranking_scores,
                name='Performance Score',
                marker_color=self.colors[:len(algorithms)],
                text=[f'{score:.3f}' for score in ranking_scores],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title={
                'text': '<b>Comprehensive Performance Analysis</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=False,
            **self.default_layout
        )
        
        return fig
    
    def create_population_evolution(self, results_data: Dict[str, Any], selected_algorithm: str) -> go.Figure:
        """Create population evolution visualization"""
        
        if selected_algorithm not in results_data:
            return go.Figure()
        
        result = results_data[selected_algorithm]
        
        if 'population_history' not in result or not result['population_history']:
            return go.Figure()
        
        # Sample some iterations for visualization
        population_history = result['population_history']
        sample_iterations = np.linspace(0, len(population_history)-1, min(10, len(population_history)), dtype=int)
        
        fig = go.Figure()
        
        for i, iteration in enumerate(sample_iterations):
            population = population_history[iteration]
            
            if len(population[0]) >= 2:  # At least 2D for visualization
                x_coords = [ind[0] for ind in population]
                y_coords = [ind[1] for ind in population]
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    name=f'Iteration {iteration}',
                    marker=dict(
                        size=8,
                        opacity=0.7,
                        color=i,
                        colorscale='Viridis'
                    ),
                    hovertemplate=f'<b>Iteration {iteration}</b><br>' +
                                'X: %{x:.4f}<br>' +
                                'Y: %{y:.4f}<br>' +
                                '<extra></extra>'
                ))
        
        fig.update_layout(
            title={
                'text': f'<b>Population Evolution - {selected_algorithm}</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title='<b>Dimension 1</b>',
            yaxis_title='<b>Dimension 2</b>',
            **self.default_layout
        )
        
        return fig
    
    def create_parameter_sensitivity_analysis(self, results_data: Dict[str, Any]) -> go.Figure:
        """Create parameter sensitivity analysis"""
        
        algorithms = list(results_data.keys())
        
        # Create radar chart for different performance metrics
        metrics = ['Best Fitness', 'Convergence Speed', 'Stability', 'Exploration', 'Exploitation']
        
        fig = go.Figure()
        
        for i, alg in enumerate(algorithms):
            if 'convergence_curve' in results_data[alg]:
                curve = results_data[alg]['convergence_curve']
                
                # Calculate metrics
                best_fitness_score = 1 / (1 + results_data[alg]['best_fitness'])
                convergence_speed = 1 / (1 + len(curve))
                stability = 1 / (1 + np.std(curve[-10:]))  # Stability in last 10 iterations
                exploration = np.std(curve[:len(curve)//4])  # Diversity in first quarter
                exploitation = abs(curve[-1] - curve[-10]) / (curve[0] + 1e-10)  # Improvement in last iterations
                
                values = [best_fitness_score, convergence_speed, stability, exploration, exploitation]
                values += values[:1]  # Close the radar chart
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metrics + [metrics[0]],
                    fill='toself',
                    name=alg,
                    line_color=self.colors[i % len(self.colors)]
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title={
                'text': '<b>Algorithm Performance Radar Chart</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            **self.default_layout
        )
        
        return fig


class ProfessionalExporter:
    """Professional data export system with multiple sheets"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_comprehensive_results(self, results_data: Dict[str, Any], 
                                   experiment_config: Dict[str, Any]) -> bytes:
        """Export comprehensive results to Excel with multiple sheets"""
        
        # Create Excel writer object
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            data_format = workbook.add_format({
                'border': 1,
                'num_format': '0.000000'
            })
            
            # Sheet 1: Summary Results
            self._create_summary_sheet(writer, results_data, experiment_config, header_format, data_format)
            
            # Sheet 2: Detailed Convergence Data
            self._create_convergence_sheet(writer, results_data, header_format, data_format)
            
            # Sheet 3: Algorithm Parameters
            self._create_parameters_sheet(writer, results_data, experiment_config, header_format, data_format)
            
            # Sheet 4: Statistical Analysis
            self._create_statistics_sheet(writer, results_data, header_format, data_format)
            
            # Sheet 5: Performance Metrics
            self._create_performance_sheet(writer, results_data, header_format, data_format)
            
            # Sheet 6: Experiment Configuration
            self._create_config_sheet(writer, experiment_config, header_format, data_format)
        
        output.seek(0)
        return output.getvalue()
    
    def _create_summary_sheet(self, writer, results_data, experiment_config, header_format, data_format):
        """Create summary results sheet"""
        
        summary_data = []
        for alg_name, result in results_data.items():
            summary_data.append({
                'Algorithm': alg_name,
                'Best Fitness': result.get('best_fitness', 'N/A'),
                'Final Solution': str(result.get('best_solution', 'N/A')[:5]) + '...' if isinstance(result.get('best_solution'), np.ndarray) else 'N/A',
                'Iterations': len(result.get('convergence_curve', [])),
                'Success Rate': '100%' if result.get('best_fitness', float('inf')) < float('inf') else '0%',
                'Execution Time': result.get('execution_time', 'N/A')
            })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False, startrow=1)
        
        worksheet = writer.sheets['Summary']
        
        # Add title
        worksheet.write(0, 0, f'MHA Optimization Results Summary - {self.timestamp}', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_summary.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    
    def _create_convergence_sheet(self, writer, results_data, header_format, data_format):
        """Create detailed convergence data sheet"""
        
        max_iterations = max(len(result.get('convergence_curve', [])) for result in results_data.values())
        
        convergence_data = {'Iteration': list(range(max_iterations))}
        
        for alg_name, result in results_data.items():
            curve = result.get('convergence_curve', [])
            # Pad with last value if shorter
            padded_curve = curve + [curve[-1]] * (max_iterations - len(curve)) if curve else [float('inf')] * max_iterations
            convergence_data[f'{alg_name}_Fitness'] = padded_curve
        
        df_convergence = pd.DataFrame(convergence_data)
        df_convergence.to_excel(writer, sheet_name='Convergence_Data', index=False, startrow=1)
        
        worksheet = writer.sheets['Convergence_Data']
        worksheet.write(0, 0, 'Detailed Convergence Curves', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_convergence.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 12)
    
    def _create_parameters_sheet(self, writer, results_data, experiment_config, header_format, data_format):
        """Create algorithm parameters sheet"""
        
        parameters_data = []
        
        for alg_name, result in results_data.items():
            # Extract best solution parameters
            best_solution = result.get('best_solution', [])
            if isinstance(best_solution, np.ndarray):
                for i, param in enumerate(best_solution):
                    parameters_data.append({
                        'Algorithm': alg_name,
                        'Parameter_Index': i,
                        'Parameter_Value': param,
                        'Parameter_Name': f'x{i+1}'
                    })
        
        df_params = pd.DataFrame(parameters_data)
        df_params.to_excel(writer, sheet_name='Parameters', index=False, startrow=1)
        
        worksheet = writer.sheets['Parameters']
        worksheet.write(0, 0, 'Optimized Parameters', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_params.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    
    def _create_statistics_sheet(self, writer, results_data, header_format, data_format):
        """Create statistical analysis sheet"""
        
        stats_data = []
        
        for alg_name, result in results_data.items():
            curve = result.get('convergence_curve', [])
            if curve:
                stats_data.append({
                    'Algorithm': alg_name,
                    'Mean_Fitness': np.mean(curve),
                    'Std_Fitness': np.std(curve),
                    'Min_Fitness': np.min(curve),
                    'Max_Fitness': np.max(curve),
                    'Median_Fitness': np.median(curve),
                    'Initial_Fitness': curve[0],
                    'Final_Fitness': curve[-1],
                    'Improvement_Rate': (curve[0] - curve[-1]) / curve[0] if curve[0] != 0 else 0,
                    'Convergence_Rate': np.mean(np.diff(curve)),
                    'Stability_Index': 1 / (1 + np.std(curve[-10:])) if len(curve) >= 10 else 0
                })
        
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Statistics', index=False, startrow=1)
        
        worksheet = writer.sheets['Statistics']
        worksheet.write(0, 0, 'Statistical Analysis', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_stats.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    
    def _create_performance_sheet(self, writer, results_data, header_format, data_format):
        """Create performance metrics sheet"""
        
        performance_data = []
        
        # Calculate performance metrics
        all_fitness = [result.get('best_fitness', float('inf')) for result in results_data.values()]
        best_overall = min(all_fitness)
        
        for alg_name, result in results_data.items():
            curve = result.get('convergence_curve', [])
            best_fitness = result.get('best_fitness', float('inf'))
            
            # Performance metrics
            relative_error = (best_fitness - best_overall) / (best_overall + 1e-10) if best_overall != 0 else 0
            success_rate = 1.0 if best_fitness < float('inf') else 0.0
            
            # Convergence metrics
            if curve and len(curve) > 1:
                convergence_speed = 0
                threshold = curve[-1] * 1.05
                for i, val in enumerate(curve):
                    if val <= threshold:
                        convergence_speed = i / len(curve)
                        break
                
                diversity_loss = (np.std(curve[:len(curve)//4]) - np.std(curve[-len(curve)//4:])) / (np.std(curve[:len(curve)//4]) + 1e-10)
            else:
                convergence_speed = 0
                diversity_loss = 0
            
            performance_data.append({
                'Algorithm': alg_name,
                'Relative_Error': relative_error,
                'Success_Rate': success_rate,
                'Convergence_Speed': convergence_speed,
                'Diversity_Loss': diversity_loss,
                'Efficiency_Score': (success_rate * (1 - relative_error) * convergence_speed),
                'Robustness_Score': 1 / (1 + np.std(curve[-10:])) if curve and len(curve) >= 10 else 0,
                'Overall_Rank': 0  # Will be calculated after sorting
            })
        
        # Calculate ranks
        df_temp = pd.DataFrame(performance_data)
        df_temp['Overall_Rank'] = df_temp['Efficiency_Score'].rank(ascending=False, method='min')
        
        df_performance = df_temp
        df_performance.to_excel(writer, sheet_name='Performance_Metrics', index=False, startrow=1)
        
        worksheet = writer.sheets['Performance_Metrics']
        worksheet.write(0, 0, 'Performance Metrics and Rankings', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_performance.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 18)
    
    def _create_config_sheet(self, writer, experiment_config, header_format, data_format):
        """Create experiment configuration sheet"""
        
        config_data = []
        
        for key, value in experiment_config.items():
            config_data.append({
                'Parameter': key,
                'Value': str(value),
                'Type': type(value).__name__
            })
        
        df_config = pd.DataFrame(config_data)
        df_config.to_excel(writer, sheet_name='Configuration', index=False, startrow=1)
        
        worksheet = writer.sheets['Configuration']
        worksheet.write(0, 0, 'Experiment Configuration', header_format)
        
        # Format headers
        for col_num, value in enumerate(df_config.columns.values):
            worksheet.write(1, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
    
    def create_download_link(self, data: bytes, filename: str) -> str:
        """Create download link for the exported file"""
        
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download {filename}</a>'
        return href
    
    def save_plots_as_html(self, figures: Dict[str, go.Figure], results_data: Dict[str, Any]) -> str:
        """Save all plots as interactive HTML file"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MHA Optimization Results - {self.timestamp}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .plot-container {{ margin-bottom: 30px; }}
                .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>MHA Optimization Results Report</h1>
            <div class="summary">
                <h2>Experiment Summary</h2>
                <p><strong>Timestamp:</strong> {self.timestamp}</p>
                <p><strong>Algorithms Tested:</strong> {', '.join(results_data.keys())}</p>
                <p><strong>Best Algorithm:</strong> {min(results_data.keys(), key=lambda x: results_data[x].get('best_fitness', float('inf')))}</p>
            </div>
        """
        
        for plot_name, fig in figures.items():
            plot_html = fig.to_html(include_plotlyjs=False, div_id=f"plot_{plot_name}")
            html_content += f"""
            <div class="plot-container">
                <h2>{plot_name.replace('_', ' ').title()}</h2>
                {plot_html}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content