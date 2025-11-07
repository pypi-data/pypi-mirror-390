"""
Comprehensive CSV Manager with Multi-Sheet Support
=================================================

Implements professional CSV export system with:
- Multi-sheet CSV exports for different datasets/algorithms
- Professional file naming conventions
- Session-based result organization
- Convergence curve data export
- User-friendly dashboard integration
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import json
from pathlib import Path
from datetime import datetime
import io
import zipfile


class ComprehensiveCSVManager:
    """Advanced CSV manager with multi-dataset and session support"""
    
    def __init__(self, base_dir="results/csv_exports"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        self.session_data = {}
        
    def initialize_session(self, session_name=None, dataset_name=None):
        """Initialize a new session for CSV exports"""
        
        if session_name is None:
            session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = session_name
        
        # Create session directory with professional structure
        self.session_dir = self.base_dir / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organized storage
        (self.session_dir / "convergence_data").mkdir(exist_ok=True)
        (self.session_dir / "summary_reports").mkdir(exist_ok=True)
        (self.session_dir / "algorithm_details").mkdir(exist_ok=True)
        (self.session_dir / "comparison_matrices").mkdir(exist_ok=True)
        
        # Initialize session metadata
        self.session_data = {
            'session_name': session_name,
            'created_at': datetime.now().isoformat(),
            'dataset_name': dataset_name,
            'algorithms': [],
            'total_runs': 0,
            'last_updated': datetime.now().isoformat(),
            'export_files': []
        }
        
        return session_name
    
    def add_algorithm_to_session(self, algorithm_name, algorithm_data, convergence_data=None):
        """Add algorithm results to current session"""
        
        if not self.current_session:
            st.error("No active session. Please initialize a session first.")
            return False
        
        # Add algorithm to session data
        algorithm_entry = {
            'algorithm_name': algorithm_name,
            'added_at': datetime.now().isoformat(),
            'best_fitness': algorithm_data.get('best_fitness', 0),
            'total_iterations': algorithm_data.get('total_iterations', 0),
            'execution_time': algorithm_data.get('execution_time', 0),
            'convergence_points': len(convergence_data) if convergence_data else 0
        }
        
        self.session_data['algorithms'].append(algorithm_entry)
        self.session_data['total_runs'] += 1
        self.session_data['last_updated'] = datetime.now().isoformat()
        
        # Export algorithm-specific CSV
        self.export_algorithm_csv(algorithm_name, algorithm_data, convergence_data)
        
        # Update session summary
        self.update_session_summary()
        
        return True
    
    def export_algorithm_csv(self, algorithm_name, algorithm_data, convergence_data=None):
        """Export individual algorithm data to CSV with professional naming"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.session_data.get('dataset_name', 'unknown_dataset')
        
        # Professional file naming: DATASET_ALGORITHM_YYYYMMDD_HHMMSS.csv
        filename = f"{dataset_name}_{algorithm_name.upper()}_{timestamp}.csv"
        filepath = self.session_dir / "algorithm_details" / filename
        
        # Prepare algorithm summary data
        summary_data = {
            'Metric': [
                'Algorithm Name',
                'Dataset',
                'Session ID',
                'Best Fitness',
                'Total Iterations',
                'Execution Time (s)',
                'Export Timestamp',
                'Convergence Points Available'
            ],
            'Value': [
                algorithm_name.upper(),
                dataset_name,
                self.current_session,
                algorithm_data.get('best_fitness', 'N/A'),
                algorithm_data.get('total_iterations', 'N/A'),
                algorithm_data.get('execution_time', 'N/A'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if convergence_data else 'No'
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        
        # Create comprehensive CSV with multiple sections
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            # Write header
            f.write(f"# Algorithm Results Export - {algorithm_name.upper()}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Session: {self.current_session}\n")
            f.write("#\n\n")
            
            # Write summary section
            f.write("## ALGORITHM SUMMARY\n")
            df_summary.to_csv(f, index=False)
            f.write("\n\n")
            
            # Write convergence data if available
            if convergence_data:
                f.write("## CONVERGENCE DATA\n")
                convergence_df = pd.DataFrame({
                    'Iteration': range(len(convergence_data)),
                    'Best_Fitness': convergence_data,
                    'Improvement': [0] + [convergence_data[i-1] - convergence_data[i] for i in range(1, len(convergence_data))]
                })
                convergence_df.to_csv(f, index=False)
                f.write("\n\n")
            
            # Write detailed statistics if available
            if 'statistics' in algorithm_data:
                f.write("## DETAILED STATISTICS\n")
                stats = algorithm_data['statistics']
                stats_df = pd.DataFrame([{
                    'Mean_Fitness': stats.get('mean_fitness', 'N/A'),
                    'Std_Fitness': stats.get('std_fitness', 'N/A'),
                    'Best_Fitness': stats.get('best_fitness', 'N/A'),
                    'Worst_Fitness': stats.get('worst_fitness', 'N/A'),
                    'Mean_Time': stats.get('mean_time', 'N/A'),
                    'Total_Runs': stats.get('total_runs', 'N/A')
                }])
                stats_df.to_csv(f, index=False)
        
        # Track exported file
        self.session_data['export_files'].append({
            'filename': filename,
            'filepath': str(filepath),
            'algorithm': algorithm_name,
            'type': 'algorithm_detail',
            'created_at': datetime.now().isoformat()
        })
        
        st.success(f"✅ Algorithm CSV exported: {filename}")
        return filepath
    
    def export_convergence_comparison_csv(self, algorithms_data):
        """Export convergence comparison data for multiple algorithms"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.session_data.get('dataset_name', 'unknown_dataset')
        
        # Professional filename for comparison
        filename = f"{dataset_name}_CONVERGENCE_COMPARISON_{timestamp}.csv"
        filepath = self.session_dir / "convergence_data" / filename
        
        # Prepare convergence data for all algorithms
        max_iterations = 0
        convergence_dict = {'Iteration': []}
        
        # Collect convergence data
        for alg_name, alg_data in algorithms_data.items():
            if 'convergence_curve' in alg_data:
                convergence = alg_data['convergence_curve']
                max_iterations = max(max_iterations, len(convergence))
                convergence_dict[f"{alg_name.upper()}_Fitness"] = convergence
        
        # Pad all curves to same length
        convergence_dict['Iteration'] = list(range(max_iterations))
        
        for alg_name in convergence_dict:
            if alg_name != 'Iteration':
                curve = convergence_dict[alg_name]
                # Pad with NaN for shorter curves
                padded_curve = list(curve) + [np.nan] * (max_iterations - len(curve))
                convergence_dict[alg_name] = padded_curve
        
        # Create DataFrame and export
        df_convergence = pd.DataFrame(convergence_dict)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(f"# Convergence Comparison Export\n")
            f.write(f"# Dataset: {dataset_name}\n")
            f.write(f"# Session: {self.current_session}\n")
            f.write(f"# Algorithms: {', '.join([k.replace('_Fitness', '') for k in convergence_dict.keys() if k != 'Iteration'])}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#\n\n")
            
            df_convergence.to_csv(f, index=False)
        
        # Track exported file
        self.session_data['export_files'].append({
            'filename': filename,
            'filepath': str(filepath),
            'type': 'convergence_comparison',
            'algorithms': list(algorithms_data.keys()),
            'created_at': datetime.now().isoformat()
        })
        
        st.success(f"✅ Convergence comparison CSV exported: {filename}")
        return filepath
    
    def export_session_summary_csv(self):
        """Export comprehensive session summary"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.session_data.get('dataset_name', 'unknown_dataset')
        
        filename = f"{dataset_name}_SESSION_SUMMARY_{self.current_session}_{timestamp}.csv"
        filepath = self.session_dir / "summary_reports" / filename
        
        # Create comprehensive summary
        algorithms_summary = []
        
        for alg in self.session_data['algorithms']:
            algorithms_summary.append({
                'Rank': 0,  # Will be calculated
                'Algorithm': alg['algorithm_name'].upper(),
                'Best_Fitness': alg['best_fitness'],
                'Total_Iterations': alg['total_iterations'],
                'Execution_Time_s': alg['execution_time'],
                'Added_At': alg['added_at'],
                'Convergence_Points': alg['convergence_points']
            })
        
        # Sort by best fitness and assign ranks
        algorithms_summary.sort(key=lambda x: x['Best_Fitness'])
        for i, alg in enumerate(algorithms_summary):
            alg['Rank'] = i + 1
        
        df_summary = pd.DataFrame(algorithms_summary)
        
        # Session metadata
        metadata = pd.DataFrame([
            ['Session_ID', self.current_session],
            ['Dataset', dataset_name],
            ['Created_At', self.session_data['created_at']],
            ['Last_Updated', self.session_data['last_updated']],
            ['Total_Algorithms', len(self.session_data['algorithms'])],
            ['Best_Overall_Fitness', min(alg['best_fitness'] for alg in self.session_data['algorithms']) if self.session_data['algorithms'] else 'N/A'],
            ['Champion_Algorithm', algorithms_summary[0]['Algorithm'] if algorithms_summary else 'N/A'],
            ['Export_Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ], columns=['Metric', 'Value'])
        
        # Export with multiple sections
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(f"# Session Summary Report\n")
            f.write(f"# Session: {self.current_session}\n")
            f.write(f"# Dataset: {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#\n\n")
            
            f.write("## SESSION METADATA\n")
            metadata.to_csv(f, index=False)
            f.write("\n\n")
            
            f.write("## ALGORITHM RANKINGS\n")
            df_summary.to_csv(f, index=False)
        
        # Track exported file
        self.session_data['export_files'].append({
            'filename': filename,
            'filepath': str(filepath),
            'type': 'session_summary',
            'created_at': datetime.now().isoformat()
        })
        
        st.success(f"✅ Session summary CSV exported: {filename}")
        return filepath
    
    def update_session_summary(self):
        """Update session metadata file"""
        
        metadata_file = self.session_dir / "session_metadata.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(self.session_data, f, indent=2, default=str)
    
    def create_comprehensive_export_package(self, algorithms_data):
        """Create a comprehensive ZIP package with all CSV exports"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.session_data.get('dataset_name', 'unknown_dataset')
        
        zip_filename = f"{dataset_name}_COMPREHENSIVE_EXPORT_{self.current_session}_{timestamp}.zip"
        zip_filepath = self.session_dir / zip_filename
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # Add all exported CSV files
            for export_file in self.session_data['export_files']:
                file_path = Path(export_file['filepath'])
                if file_path.exists():
                    zipf.write(file_path, file_path.name)
            
            # Add session metadata
            metadata_file = self.session_dir / "session_metadata.json"
            if metadata_file.exists():
                zipf.write(metadata_file, "session_metadata.json")
            
            # Create and add README
            readme_content = f"""
# MHA Algorithm Comparison Results Export Package

## Session Information
- Session ID: {self.current_session}
- Dataset: {dataset_name}
- Created: {self.session_data['created_at']}
- Total Algorithms: {len(self.session_data['algorithms'])}

## Package Contents
- Algorithm Details: Individual CSV files for each algorithm
- Convergence Data: Comparison CSV with convergence curves
- Summary Reports: Session summary and rankings
- Session Metadata: JSON file with complete session information

## File Naming Convention
- Algorithm Details: DATASET_ALGORITHM_YYYYMMDD_HHMMSS.csv
- Convergence Data: DATASET_CONVERGENCE_COMPARISON_YYYYMMDD_HHMMSS.csv
- Session Summary: DATASET_SESSION_SUMMARY_SESSIONID_YYYYMMDD_HHMMSS.csv

## Usage
Import CSV files into Excel, Python, R, or other analysis tools for further processing.
All convergence data is ready for plotting and statistical analysis.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            zipf.writestr("README.txt", readme_content)
        
        st.success(f"✅ Comprehensive export package created: {zip_filename}")
        
        # Provide download button
        with open(zip_filepath, 'rb') as f:
            st.download_button(
                label="📦 Download Comprehensive Export Package",
                data=f.read(),
                file_name=zip_filename,
                mime="application/zip"
            )
        
        return zip_filepath
    
    def get_session_algorithms(self):
        """Get list of algorithms in current session"""
        if not self.session_data:
            return []
        return [alg['algorithm_name'] for alg in self.session_data['algorithms']]
    
    def load_existing_session(self, session_dir_path):
        """Load an existing session for continuation"""
        
        session_path = Path(session_dir_path)
        metadata_file = session_path / "session_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.session_data = json.load(f)
            
            self.current_session = self.session_data['session_name']
            self.session_dir = session_path
            
            st.success(f"✅ Loaded existing session: {self.current_session}")
            return True
        else:
            st.error("❌ No session metadata found in specified directory")
            return False


class ConvergencePlotManager:
    """Advanced convergence curve plotting with user selection"""
    
    def __init__(self, csv_manager):
        self.csv_manager = csv_manager
    
    def display_convergence_interface(self, algorithms_data):
        """Display interactive convergence plotting interface"""
        
        st.markdown("### 📈 **CONVERGENCE CURVE ANALYSIS**")
        st.info("🎯 Select specific algorithms to plot convergence curves")
        
        if not algorithms_data:
            st.warning("No algorithm data available for plotting")
            return
        
        # Algorithm selection interface
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("#### 🎛️ **Plot Controls**")
            
            # Algorithm selection
            available_algorithms = list(algorithms_data.keys())
            selected_algorithms = st.multiselect(
                "Select algorithms to plot:",
                available_algorithms,
                default=available_algorithms[:3] if len(available_algorithms) >= 3 else available_algorithms,
                help="Choose which algorithms to include in the convergence plot"
            )
            
            # Plot customization
            plot_style = st.selectbox(
                "Plot Style:",
                ["Lines Only", "Lines + Markers", "Markers Only", "Filled Area"],
                index=0
            )
            
            color_scheme = st.selectbox(
                "Color Scheme:",
                ["Qualitative", "Sequential", "Diverging", "Custom"],
                index=0
            )
            
            y_scale = st.selectbox(
                "Y-axis Scale:",
                ["Linear", "Logarithmic"],
                index=0
            )
            
            show_statistics = st.checkbox("Show Statistics Overlay", value=False)
            show_improvement = st.checkbox("Show Improvement Rate", value=False)
            
            # Export options
            st.markdown("#### 💾 **Export Options**")
            
            if st.button("📥 Export Selected Convergence CSV"):
                self.export_selected_convergence(selected_algorithms, algorithms_data)
            
            if st.button("📊 Export Plot as HTML"):
                self.export_plot_html(selected_algorithms, algorithms_data)
        
        with col1:
            if selected_algorithms:
                self.create_convergence_plot(
                    selected_algorithms, 
                    algorithms_data, 
                    plot_style, 
                    color_scheme, 
                    y_scale,
                    show_statistics,
                    show_improvement
                )
            else:
                st.info("👆 Select algorithms from the controls panel to display convergence curves")
    
    def create_convergence_plot(self, selected_algorithms, algorithms_data, 
                               plot_style, color_scheme, y_scale, show_statistics, show_improvement):
        """Create customized convergence plot"""
        
        fig = go.Figure()
        
        # Color schemes
        if color_scheme == "Qualitative":
            colors = px.colors.qualitative.Set1
        elif color_scheme == "Sequential":
            colors = px.colors.sequential.Viridis
        elif color_scheme == "Diverging":
            colors = px.colors.diverging.RdYlBu
        else:
            colors = px.colors.qualitative.Plotly
        
        # Plot each selected algorithm
        for i, alg_name in enumerate(selected_algorithms):
            if alg_name in algorithms_data and 'convergence_curve' in algorithms_data[alg_name]:
                convergence = algorithms_data[alg_name]['convergence_curve']
                iterations = np.arange(len(convergence))
                
                # Determine plot mode
                mode = 'lines'
                if plot_style == "Lines + Markers":
                    mode = 'lines+markers'
                elif plot_style == "Markers Only":
                    mode = 'markers'
                
                color = colors[i % len(colors)]
                
                if plot_style == "Filled Area":
                    fig.add_trace(go.Scatter(
                        x=iterations,
                        y=convergence,
                        mode='lines',
                        name=f"{alg_name.upper()}",
                        fill='tonexty' if i > 0 else 'tozeroy',
                        fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.3])}",
                        line=dict(color=color, width=2),
                        hovertemplate=f"<b>{alg_name.upper()}</b><br>" +
                                    "Iteration: %{x}<br>" +
                                    "Fitness: %{y:.6f}<br>" +
                                    "<extra></extra>"
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=iterations,
                        y=convergence,
                        mode=mode,
                        name=f"{alg_name.upper()}",
                        line=dict(color=color, width=3),
                        marker=dict(size=8) if 'markers' in mode else None,
                        hovertemplate=f"<b>{alg_name.upper()}</b><br>" +
                                    "Iteration: %{x}<br>" +
                                    "Fitness: %{y:.6f}<br>" +
                                    "<extra></extra>"
                    ))
                
                # Add improvement rate if requested
                if show_improvement and len(convergence) > 1:
                    improvement_rate = [0] + [
                        abs(convergence[j-1] - convergence[j]) / max(abs(convergence[j-1]), 1e-10)
                        for j in range(1, len(convergence))
                    ]
                    
                    fig.add_trace(go.Scatter(
                        x=iterations,
                        y=improvement_rate,
                        mode='lines',
                        name=f"{alg_name.upper()} - Improvement Rate",
                        line=dict(color=color, width=1, dash='dash'),
                        yaxis='y2',
                        showlegend=False,
                        hovertemplate=f"<b>{alg_name.upper()} - Improvement</b><br>" +
                                    "Iteration: %{x}<br>" +
                                    "Improvement Rate: %{y:.4f}<br>" +
                                    "<extra></extra>"
                    ))
        
        # Customize layout
        layout_updates = {
            'title': dict(
                text="🚀 Algorithm Convergence Comparison",
                font=dict(size=20, color='darkblue'),
                x=0.5
            ),
            'xaxis_title': "Iteration",
            'yaxis_title': "Best Fitness",
            'yaxis_type': "log" if y_scale == "Logarithmic" else "linear",
            'legend': dict(
                x=0.02, y=0.98, 
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1
            ),
            'hovermode': 'x unified',
            'template': "plotly_white",
            'height': 600
        }
        
        # Add secondary y-axis for improvement rate
        if show_improvement:
            layout_updates['yaxis2'] = dict(
                title="Improvement Rate",
                overlaying='y',
                side='right',
                showgrid=False
            )
        
        fig.update_layout(**layout_updates)
        
        # Add statistics overlay if requested
        if show_statistics:
            self.add_statistics_overlay(fig, selected_algorithms, algorithms_data)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display convergence statistics
        self.display_convergence_statistics(selected_algorithms, algorithms_data)
    
    def add_statistics_overlay(self, fig, selected_algorithms, algorithms_data):
        """Add statistical information overlay to the plot"""
        
        for alg_name in selected_algorithms:
            if alg_name in algorithms_data and 'convergence_curve' in algorithms_data[alg_name]:
                convergence = algorithms_data[alg_name]['convergence_curve']
                
                # Add mean line
                mean_fitness = np.mean(convergence)
                fig.add_hline(
                    y=mean_fitness,
                    line_dash="dot",
                    line_color="gray",
                    annotation_text=f"Mean: {mean_fitness:.4f}",
                    annotation_position="top right"
                )
    
    def display_convergence_statistics(self, selected_algorithms, algorithms_data):
        """Display detailed convergence statistics"""
        
        st.markdown("#### 📊 **Convergence Statistics**")
        
        stats_data = []
        
        for alg_name in selected_algorithms:
            if alg_name in algorithms_data and 'convergence_curve' in algorithms_data[alg_name]:
                convergence = algorithms_data[alg_name]['convergence_curve']
                
                # Calculate statistics
                initial_fitness = convergence[0]
                final_fitness = convergence[-1]
                total_improvement = initial_fitness - final_fitness
                improvement_rate = total_improvement / max(initial_fitness, 1e-10) * 100
                
                # Find convergence point (when improvement becomes minimal)
                convergence_point = len(convergence)
                for i in range(10, len(convergence)):
                    recent_improvement = abs(convergence[i-10] - convergence[i])
                    if recent_improvement < 1e-6:
                        convergence_point = i
                        break
                
                stats_data.append({
                    'Algorithm': alg_name.upper(),
                    'Initial Fitness': f"{initial_fitness:.6f}",
                    'Final Fitness': f"{final_fitness:.6f}",
                    'Total Improvement': f"{total_improvement:.6f}",
                    'Improvement Rate (%)': f"{improvement_rate:.2f}%",
                    'Convergence Point': convergence_point,
                    'Total Iterations': len(convergence)
                })
        
        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, width=800)
    
    def export_selected_convergence(self, selected_algorithms, algorithms_data):
        """Export convergence data for selected algorithms"""
        
        selected_data = {alg: algorithms_data[alg] for alg in selected_algorithms if alg in algorithms_data}
        
        if selected_data:
            filepath = self.csv_manager.export_convergence_comparison_csv(selected_data)
            st.success(f"✅ Exported convergence data for {len(selected_algorithms)} algorithms")
        else:
            st.error("No valid algorithm data found for export")
    
    def export_plot_html(self, selected_algorithms, algorithms_data):
        """Export plot as interactive HTML"""
        
        # Create the plot
        fig = go.Figure()
        colors = px.colors.qualitative.Set1
        
        for i, alg_name in enumerate(selected_algorithms):
            if alg_name in algorithms_data and 'convergence_curve' in algorithms_data[alg_name]:
                convergence = algorithms_data[alg_name]['convergence_curve']
                iterations = np.arange(len(convergence))
                
                fig.add_trace(go.Scatter(
                    x=iterations,
                    y=convergence,
                    mode='lines+markers',
                    name=f"{alg_name.upper()}",
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title="Algorithm Convergence Comparison",
            xaxis_title="Iteration",
            yaxis_title="Best Fitness",
            template="plotly_white"
        )
        
        # Export as HTML
        html_str = fig.to_html(include_plotlyjs='cdn')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"convergence_plot_{timestamp}.html"
        
        st.download_button(
            label="📥 Download Interactive Plot (HTML)",
            data=html_str,
            file_name=filename,
            mime="text/html"
        )
        
        st.success("✅ Interactive plot HTML ready for download")