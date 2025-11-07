"""
Professional Export and Visualization System
============================================

Matplotlib-based export system for publication-quality figures.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json
import csv


class ProfessionalExporter:
    """
    Professional-grade export system for results and visualizations
    """
    
    def __init__(self, export_dir: str = "results/exports"):
        """Initialize exporter with output directory"""
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.export_dir / "plots").mkdir(exist_ok=True)
        (self.export_dir / "data").mkdir(exist_ok=True)
        (self.export_dir / "reports").mkdir(exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.4)
        
    def export_convergence_plot(self, results: Dict[str, Dict], 
                               problem_name: str,
                               format: str = 'png',
                               dpi: int = 300) -> str:
        """
        Export high-quality convergence plot
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary with convergence curves
        problem_name : str
            Name of the problem
        format : str
            Image format ('png', 'pdf', 'svg')
        dpi : int
            Resolution for raster formats
            
        Returns
        -------
        str
            Path to exported file
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo_name, result in results.items():
            if 'convergence_curve' in result:
                curve = result['convergence_curve']
                iterations = np.arange(1, len(curve) + 1)
                ax.plot(iterations, curve, label=algo_name, linewidth=2.5, 
                       marker='o', markersize=4, markevery=max(1, len(curve)//15))
        
        ax.set_xlabel('Iteration', fontsize=14, fontweight='bold')
        ax.set_ylabel('Best Fitness Value', fontsize=14, fontweight='bold')
        ax.set_title(f'Convergence Analysis: {problem_name}', 
                    fontsize=16, fontweight='bold', pad=15)
        ax.legend(loc='best', framealpha=0.95, shadow=True, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
        
        # Use log scale if appropriate
        if self._should_use_log_scale(results):
            ax.set_yscale('log')
            ax.set_ylabel('Best Fitness Value (log scale)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"convergence_{problem_name}_{timestamp}.{format}"
        filepath = self.export_dir / "plots" / filename
        
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white', format=format)
        plt.close()
        
        return str(filepath)
    
    def export_comparison_bar(self, results: Dict[str, Dict],
                             problem_name: str,
                             metric: str = 'best_fitness',
                             format: str = 'png',
                             dpi: int = 300) -> str:
        """Export algorithm comparison bar chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        algorithms = list(results.keys())
        values = [results[algo].get(metric, np.inf) for algo in algorithms]
        
        # Sort by performance
        sorted_indices = np.argsort(values)
        algorithms = [algorithms[i] for i in sorted_indices]
        values = [values[i] for i in sorted_indices]
        
        # Color gradient
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(algorithms)))
        bars = ax.bar(range(len(algorithms)), values, color=colors, 
                     alpha=0.85, edgecolor='black', linewidth=1.2)
        
        ax.set_xticks(range(len(algorithms)))
        ax.set_xticklabels(algorithms, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        ax.set_title(f'Performance Comparison: {problem_name}', 
                    fontsize=16, fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.2e}', ha='center', va='bottom', 
                   fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{problem_name}_{timestamp}.{format}"
        filepath = self.export_dir / "plots" / filename
        
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white', format=format)
        plt.close()
        
        return str(filepath)
    
    def export_results_csv(self, results: Dict[str, Dict],
                          problem_name: str) -> str:
        """
        Export results to CSV format
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary
        problem_name : str
            Problem name
            
        Returns
        -------
        str
            Path to CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{problem_name}_{timestamp}.csv"
        filepath = self.export_dir / "data" / filename
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Algorithm', 'Best Fitness', 'Execution Time (s)', 
                           'Final Iteration', 'Convergence Rate'])
            
            # Data rows
            for algo_name, result in results.items():
                best_fitness = result.get('best_fitness', 'N/A')
                exec_time = result.get('execution_time', 'N/A')
                
                if 'convergence_curve' in result:
                    curve = result['convergence_curve']
                    final_iter = len(curve)
                    # Calculate convergence rate (improvement per iteration)
                    if len(curve) > 1:
                        conv_rate = (curve[0] - curve[-1]) / len(curve)
                    else:
                        conv_rate = 0
                else:
                    final_iter = 'N/A'
                    conv_rate = 'N/A'
                
                writer.writerow([algo_name, best_fitness, exec_time, 
                               final_iter, conv_rate])
        
        return str(filepath)
    
    def export_results_json(self, results: Dict[str, Dict],
                           problem_info: Dict,
                           problem_name: str) -> str:
        """
        Export complete results to JSON format
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary
        problem_info : Dict
            Problem information
        problem_name : str
            Problem name
            
        Returns
        -------
        str
            Path to JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{problem_name}_{timestamp}.json"
        filepath = self.export_dir / "data" / filename
        
        export_data = {
            'metadata': {
                'problem_name': problem_name,
                'export_date': datetime.now().isoformat(),
                'problem_info': problem_info
            },
            'results': {}
        }
        
        for algo_name, result in results.items():
            # Convert numpy arrays to lists for JSON serialization
            algo_data = {}
            for key, value in result.items():
                if isinstance(value, np.ndarray):
                    algo_data[key] = value.tolist()
                elif isinstance(value, (np.integer, np.floating)):
                    algo_data[key] = float(value)
                else:
                    algo_data[key] = value
            
            export_data['results'][algo_name] = algo_data
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(filepath)
    
    def export_convergence_data(self, results: Dict[str, Dict],
                               problem_name: str) -> str:
        """
        Export raw convergence curve data to CSV
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary
        problem_name : str
            Problem name
            
        Returns
        -------
        str
            Path to CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"convergence_data_{problem_name}_{timestamp}.csv"
        filepath = self.export_dir / "data" / filename
        
        # Find maximum iteration count
        max_iters = max(len(result.get('convergence_curve', [])) 
                       for result in results.values())
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            header = ['Iteration'] + list(results.keys())
            writer.writerow(header)
            
            # Data rows
            for i in range(max_iters):
                row = [i + 1]
                for algo_name in results.keys():
                    curve = results[algo_name].get('convergence_curve', [])
                    if i < len(curve):
                        row.append(curve[i])
                    else:
                        row.append('')
                writer.writerow(row)
        
        return str(filepath)
    
    def create_summary_report(self, results: Dict[str, Dict],
                             problem_info: Dict,
                             problem_name: str) -> str:
        """
        Create comprehensive text summary report
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary
        problem_info : Dict
            Problem information
        problem_name : str
            Problem name
            
        Returns
        -------
        str
            Path to report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_report_{problem_name}_{timestamp}.txt"
        filepath = self.export_dir / "reports" / filename
        
        with open(filepath, 'w') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write(f"OPTIMIZATION RESULTS SUMMARY: {problem_name}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            # Problem information
            f.write("PROBLEM INFORMATION\n")
            f.write("-" * 80 + "\n")
            for key, value in problem_info.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Algorithm rankings
            f.write("ALGORITHM RANKINGS\n")
            f.write("-" * 80 + "\n")
            
            # Sort by best fitness
            sorted_results = sorted(results.items(), 
                                  key=lambda x: x[1].get('best_fitness', np.inf))
            
            for rank, (algo_name, result) in enumerate(sorted_results, 1):
                f.write(f"\nRank {rank}: {algo_name}\n")
                f.write(f"  Best Fitness: {result.get('best_fitness', 'N/A')}\n")
                f.write(f"  Execution Time: {result.get('execution_time', 'N/A')} seconds\n")
                
                if 'convergence_curve' in result:
                    curve = result['convergence_curve']
                    f.write(f"  Total Iterations: {len(curve)}\n")
                    f.write(f"  Initial Fitness: {curve[0]:.6e}\n")
                    f.write(f"  Final Fitness: {curve[-1]:.6e}\n")
                    
                    improvement = ((curve[0] - curve[-1]) / curve[0] * 100) if curve[0] != 0 else 0
                    f.write(f"  Improvement: {improvement:.2f}%\n")
            
            f.write("\n")
            
            # Statistical summary
            f.write("STATISTICAL SUMMARY\n")
            f.write("-" * 80 + "\n")
            
            fitness_values = [r.get('best_fitness', np.inf) for r in results.values()]
            fitness_values = [f for f in fitness_values if f != np.inf]
            
            if fitness_values:
                f.write(f"Best Overall: {min(fitness_values):.6e}\n")
                f.write(f"Worst Overall: {max(fitness_values):.6e}\n")
                f.write(f"Mean Fitness: {np.mean(fitness_values):.6e}\n")
                f.write(f"Std Deviation: {np.std(fitness_values):.6e}\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        return str(filepath)
    
    def export_all(self, results: Dict[str, Dict],
                  problem_info: Dict,
                  problem_name: str) -> Dict[str, str]:
        """
        Export all formats at once
        
        Parameters
        ----------
        results : Dict[str, Dict]
            Results dictionary
        problem_info : Dict
            Problem information
        problem_name : str
            Problem name
            
        Returns
        -------
        Dict[str, str]
            Dictionary of export type -> file path
        """
        exports = {}
        
        print("Exporting results...")
        
        # Plots
        print("  - Generating convergence plot...")
        exports['convergence_plot'] = self.export_convergence_plot(results, problem_name)
        
        print("  - Generating comparison chart...")
        exports['comparison_plot'] = self.export_comparison_bar(results, problem_name)
        
        # Data files
        print("  - Exporting CSV data...")
        exports['results_csv'] = self.export_results_csv(results, problem_name)
        
        print("  - Exporting JSON data...")
        exports['results_json'] = self.export_results_json(results, problem_info, problem_name)
        
        print("  - Exporting convergence data...")
        exports['convergence_csv'] = self.export_convergence_data(results, problem_name)
        
        # Report
        print("  - Creating summary report...")
        exports['summary_report'] = self.create_summary_report(results, problem_info, problem_name)
        
        print(f"\nExport complete! Files saved to: {self.export_dir}")
        
        return exports
    
    def _should_use_log_scale(self, results: Dict) -> bool:
        """Determine if log scale is appropriate"""
        all_values = []
        for result in results.values():
            if 'convergence_curve' in result:
                all_values.extend(result['convergence_curve'])
        
        if len(all_values) == 0 or min(all_values) <= 0:
            return False
        
        value_range = max(all_values) / min(all_values)
        return value_range > 1000
