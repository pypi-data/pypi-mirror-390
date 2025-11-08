"""
Advanced Hyperparameter Tuning and Performance Analysis System
==============================================================

Comprehensive system for:
- Hyperparameter tuning with custom bounds
- Statistical analysis (mean, std, median, IQR)
- Performance metrics (accuracy, fitness, time)
- Detailed visualization (convergence, box plots, statistical plots)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Callable, Dict, List, Tuple, Optional, Any
from scipy import stats
import time
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class HyperparameterBounds:
    """Define hyperparameter bounds for tuning"""
    name: str
    lower: float
    upper: float
    type: str = 'continuous'  # 'continuous', 'integer', 'discrete'
    values: Optional[List] = None  # For discrete parameters
    
    def sample(self) -> float:
        """Sample a value from the bounds"""
        if self.type == 'continuous':
            return np.random.uniform(self.lower, self.upper)
        elif self.type == 'integer':
            return np.random.randint(self.lower, self.upper + 1)
        elif self.type == 'discrete' and self.values:
            return np.random.choice(self.values)
        return (self.lower + self.upper) / 2


@dataclass
class PerformanceMetrics:
    """Store comprehensive performance metrics"""
    algorithm_name: str
    run_times: List[float]
    fitness_values: List[float]
    convergence_curves: List[List[float]]
    best_solution: np.ndarray
    best_fitness: float
    hyperparameters: Dict[str, Any]
    
    # Statistical metrics
    mean_fitness: float = None
    std_fitness: float = None
    median_fitness: float = None
    iqr_fitness: float = None
    min_fitness: float = None
    max_fitness: float = None
    
    mean_time: float = None
    std_time: float = None
    
    # Success rate
    success_rate: float = None
    convergence_speed: float = None
    
    def __post_init__(self):
        """Calculate statistical metrics"""
        self.mean_fitness = np.mean(self.fitness_values)
        self.std_fitness = np.std(self.fitness_values)
        self.median_fitness = np.median(self.fitness_values)
        self.iqr_fitness = np.percentile(self.fitness_values, 75) - np.percentile(self.fitness_values, 25)
        self.min_fitness = np.min(self.fitness_values)
        self.max_fitness = np.max(self.fitness_values)
        
        self.mean_time = np.mean(self.run_times)
        self.std_time = np.std(self.run_times)
        
        # Calculate convergence speed (iterations to reach 90% of best)
        if self.convergence_curves:
            avg_curve = np.mean(self.convergence_curves, axis=0)
            target = self.best_fitness * 1.1  # 90% of best
            converged = np.where(avg_curve <= target)[0]
            self.convergence_speed = converged[0] if len(converged) > 0 else len(avg_curve)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'algorithm': self.algorithm_name,
            'mean_fitness': float(self.mean_fitness),
            'std_fitness': float(self.std_fitness),
            'median_fitness': float(self.median_fitness),
            'iqr_fitness': float(self.iqr_fitness),
            'min_fitness': float(self.min_fitness),
            'max_fitness': float(self.max_fitness),
            'best_fitness': float(self.best_fitness),
            'mean_time': float(self.mean_time),
            'std_time': float(self.std_time),
            'success_rate': float(self.success_rate) if self.success_rate else 0.0,
            'convergence_speed': float(self.convergence_speed),
            'hyperparameters': self.hyperparameters,
            'num_runs': len(self.fitness_values)
        }


class HyperparameterTuner:
    """
    Advanced hyperparameter tuning with custom bounds
    """
    
    def __init__(self, algorithm_class, objective_function: Callable,
                 dimensions: int, bounds: np.ndarray,
                 hyperparameter_bounds: Dict[str, HyperparameterBounds]):
        """
        Initialize tuner
        
        Parameters:
        -----------
        algorithm_class : class
            Algorithm class to tune
        objective_function : callable
            Objective function to optimize
        dimensions : int
            Problem dimensions
        bounds : np.ndarray
            Problem bounds
        hyperparameter_bounds : dict
            Dictionary of hyperparameter bounds
        """
        self.algorithm_class = algorithm_class
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.hyperparameter_bounds = hyperparameter_bounds
        
        self.results = []
    
    def tune(self, n_trials: int = 20, n_runs_per_trial: int = 10,
             max_iterations: int = 100, population_size: int = 50) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning
        
        Parameters:
        -----------
        n_trials : int
            Number of hyperparameter combinations to try
        n_runs_per_trial : int
            Number of independent runs per trial
        max_iterations : int
            Max iterations for each run
        population_size : int
            Population size
            
        Returns:
        --------
        dict : Best hyperparameters and performance
        """
        print(f"🔧 Starting hyperparameter tuning...")
        print(f"   Trials: {n_trials}, Runs per trial: {n_runs_per_trial}")
        
        for trial in range(n_trials):
            # Sample hyperparameters
            hyperparams = {
                name: bound.sample()
                for name, bound in self.hyperparameter_bounds.items()
            }
            
            # Add fixed parameters
            hyperparams['population_size'] = population_size
            hyperparams['max_iterations'] = max_iterations
            
            # Run multiple times with these hyperparameters
            trial_fitness = []
            trial_times = []
            
            for run in range(n_runs_per_trial):
                try:
                    start_time = time.time()
                    
                    # Create algorithm instance
                    algo = self.algorithm_class(
                        objective_function=self.objective_function,
                        dimensions=self.dimensions,
                        bounds=self.bounds,
                        **hyperparams
                    )
                    
                    # Run optimization
                    best_pos, best_fit, _ = algo.optimize()
                    
                    elapsed_time = time.time() - start_time
                    
                    trial_fitness.append(best_fit)
                    trial_times.append(elapsed_time)
                    
                except Exception as e:
                    print(f"   Trial {trial+1}, Run {run+1} failed: {e}")
                    continue
            
            if trial_fitness:
                self.results.append({
                    'hyperparameters': hyperparams,
                    'mean_fitness': np.mean(trial_fitness),
                    'std_fitness': np.std(trial_fitness),
                    'mean_time': np.mean(trial_times),
                    'fitness_values': trial_fitness
                })
                
                print(f"   Trial {trial+1}/{n_trials}: "
                      f"Mean Fitness = {np.mean(trial_fitness):.6f} ± {np.std(trial_fitness):.6f}")
        
        # Find best hyperparameters
        best_trial = min(self.results, key=lambda x: x['mean_fitness'])
        
        print(f"\n✅ Best hyperparameters found:")
        for param, value in best_trial['hyperparameters'].items():
            print(f"   {param}: {value}")
        print(f"   Mean Fitness: {best_trial['mean_fitness']:.6f} ± {best_trial['std_fitness']:.6f}")
        
        return best_trial


class PerformanceAnalyzer:
    """
    Comprehensive performance analysis and visualization
    """
    
    def __init__(self, output_dir: str = "results/analysis"):
        """Initialize analyzer"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_list: List[PerformanceMetrics] = []
        
        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """Add performance metrics"""
        self.metrics_list.append(metrics)
    
    def compare_algorithms(self, algorithms: List[str], 
                          objective_function: Callable,
                          dimensions: int,
                          bounds: np.ndarray,
                          n_runs: int = 30,
                          population_size: int = 50,
                          max_iterations: int = 100) -> pd.DataFrame:
        """
        Compare multiple algorithms with statistical analysis
        
        Parameters:
        -----------
        algorithms : list
            List of algorithm names or classes
        n_runs : int
            Number of independent runs for statistical significance
            
        Returns:
        --------
        DataFrame : Comparison results with statistics
        """
        print(f"\n📊 Comparing {len(algorithms)} algorithms with {n_runs} runs each...")
        
        comparison_data = []
        
        for algo_name in algorithms:
            print(f"\n🔄 Testing {algo_name}...")
            
            fitness_values = []
            run_times = []
            convergence_curves = []
            best_overall_solution = None
            best_overall_fitness = float('inf')
            
            for run in range(n_runs):
                try:
                    start_time = time.time()
                    
                    # Import and run algorithm
                    # (This is a placeholder - actual implementation would import from algorithms)
                    from mha_toolbox.algorithms import hybrid_advanced
                    
                    # Get algorithm class
                    algo_class = getattr(hybrid_advanced, algo_name, None)
                    if algo_class is None:
                        print(f"   Algorithm {algo_name} not found, skipping...")
                        break
                    
                    # Run algorithm
                    algo = algo_class(
                        objective_function=objective_function,
                        dimensions=dimensions,
                        bounds=bounds,
                        population_size=population_size,
                        max_iterations=max_iterations
                    )
                    
                    best_pos, best_fit, conv_curve = algo.optimize()
                    
                    elapsed_time = time.time() - start_time
                    
                    fitness_values.append(best_fit)
                    run_times.append(elapsed_time)
                    convergence_curves.append(conv_curve)
                    
                    if best_fit < best_overall_fitness:
                        best_overall_fitness = best_fit
                        best_overall_solution = best_pos
                    
                    print(f"   Run {run+1}/{n_runs}: Fitness = {best_fit:.6f}, Time = {elapsed_time:.3f}s")
                    
                except Exception as e:
                    print(f"   Run {run+1} failed: {e}")
                    continue
            
            if fitness_values:
                # Create performance metrics
                metrics = PerformanceMetrics(
                    algorithm_name=algo_name,
                    run_times=run_times,
                    fitness_values=fitness_values,
                    convergence_curves=convergence_curves,
                    best_solution=best_overall_solution,
                    best_fitness=best_overall_fitness,
                    hyperparameters={
                        'population_size': population_size,
                        'max_iterations': max_iterations
                    }
                )
                
                self.add_metrics(metrics)
                comparison_data.append(metrics.to_dict())
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Save results
        df.to_csv(self.output_dir / "comparison_results.csv", index=False)
        
        # Print summary
        print("\n" + "="*80)
        print("COMPARISON SUMMARY")
        print("="*80)
        print(df[['algorithm', 'mean_fitness', 'std_fitness', 'mean_time', 'convergence_speed']].to_string(index=False))
        print("="*80)
        
        return df
    
    def plot_convergence_curves(self, show_std: bool = True, save_fig: bool = True):
        """
        Plot convergence curves for all algorithms
        
        Parameters:
        -----------
        show_std : bool
            Show standard deviation bands
        save_fig : bool
            Save figure to file
        """
        if not self.metrics_list:
            print("No metrics to plot!")
            return
        
        plt.figure(figsize=(14, 8))
        
        for metrics in self.metrics_list:
            curves = np.array(metrics.convergence_curves)
            mean_curve = np.mean(curves, axis=0)
            std_curve = np.std(curves, axis=0)
            iterations = np.arange(len(mean_curve))
            
            # Plot mean curve
            plt.plot(iterations, mean_curve, label=metrics.algorithm_name, linewidth=2)
            
            # Plot std band
            if show_std:
                plt.fill_between(iterations,
                                mean_curve - std_curve,
                                mean_curve + std_curve,
                                alpha=0.2)
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Fitness Value', fontsize=12)
        plt.title('Convergence Curves Comparison (Mean ± Std)', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.yscale('log')  # Log scale for better visualization
        plt.tight_layout()
        
        if save_fig:
            plt.savefig(self.output_dir / "convergence_curves.png", dpi=300, bbox_inches='tight')
            print(f"✅ Convergence plot saved to {self.output_dir}/convergence_curves.png")
        
        plt.show()
    
    def plot_box_plots(self, save_fig: bool = True):
        """Plot box plots for fitness distribution"""
        if not self.metrics_list:
            print("No metrics to plot!")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Fitness box plots
        data_fitness = [metrics.fitness_values for metrics in self.metrics_list]
        labels = [metrics.algorithm_name for metrics in self.metrics_list]
        
        bp1 = axes[0].boxplot(data_fitness, labels=labels, patch_artist=True,
                             notch=True, showmeans=True)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(data_fitness)))
        for patch, color in zip(bp1['boxes'], colors):
            patch.set_facecolor(color)
        
        axes[0].set_xlabel('Algorithm', fontsize=12)
        axes[0].set_ylabel('Fitness Value', fontsize=12)
        axes[0].set_title('Fitness Distribution (Box Plot)', fontsize=14, fontweight='bold')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # Time box plots
        data_time = [metrics.run_times for metrics in self.metrics_list]
        
        bp2 = axes[1].boxplot(data_time, labels=labels, patch_artist=True,
                             notch=True, showmeans=True)
        
        for patch, color in zip(bp2['boxes'], colors):
            patch.set_facecolor(color)
        
        axes[1].set_xlabel('Algorithm', fontsize=12)
        axes[1].set_ylabel('Execution Time (s)', fontsize=12)
        axes[1].set_title('Execution Time Distribution', fontsize=14, fontweight='bold')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_fig:
            plt.savefig(self.output_dir / "box_plots.png", dpi=300, bbox_inches='tight')
            print(f"✅ Box plots saved to {self.output_dir}/box_plots.png")
        
        plt.show()
    
    def plot_statistical_summary(self, save_fig: bool = True):
        """Plot comprehensive statistical summary"""
        if not self.metrics_list:
            print("No metrics to plot!")
            return
        
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        algorithms = [m.algorithm_name for m in self.metrics_list]
        means = [m.mean_fitness for m in self.metrics_list]
        stds = [m.std_fitness for m in self.metrics_list]
        medians = [m.median_fitness for m in self.metrics_list]
        iqrs = [m.iqr_fitness for m in self.metrics_list]
        times = [m.mean_time for m in self.metrics_list]
        conv_speeds = [m.convergence_speed for m in self.metrics_list]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))
        
        # Plot 1: Mean Fitness with Error Bars
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(range(len(algorithms)), means, yerr=stds, capsize=5, color=colors, alpha=0.7)
        ax1.set_xticks(range(len(algorithms)))
        ax1.set_xticklabels(algorithms, rotation=45, ha='right')
        ax1.set_ylabel('Mean Fitness ± Std')
        ax1.set_title('Mean Fitness Comparison', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Median Fitness
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(range(len(algorithms)), medians, color=colors, alpha=0.7)
        ax2.set_xticks(range(len(algorithms)))
        ax2.set_xticklabels(algorithms, rotation=45, ha='right')
        ax2.set_ylabel('Median Fitness')
        ax2.set_title('Median Fitness Comparison', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: IQR (Interquartile Range)
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.bar(range(len(algorithms)), iqrs, color=colors, alpha=0.7)
        ax3.set_xticks(range(len(algorithms)))
        ax3.set_xticklabels(algorithms, rotation=45, ha='right')
        ax3.set_ylabel('IQR')
        ax3.set_title('Robustness (IQR)', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Standard Deviation
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.bar(range(len(algorithms)), stds, color=colors, alpha=0.7)
        ax4.set_xticks(range(len(algorithms)))
        ax4.set_xticklabels(algorithms, rotation=45, ha='right')
        ax4.set_ylabel('Standard Deviation')
        ax4.set_title('Consistency (Lower is Better)', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Execution Time
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.bar(range(len(algorithms)), times, color=colors, alpha=0.7)
        ax5.set_xticks(range(len(algorithms)))
        ax5.set_xticklabels(algorithms, rotation=45, ha='right')
        ax5.set_ylabel('Mean Time (s)')
        ax5.set_title('Computational Efficiency', fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Plot 6: Convergence Speed
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.bar(range(len(algorithms)), conv_speeds, color=colors, alpha=0.7)
        ax6.set_xticks(range(len(algorithms)))
        ax6.set_xticklabels(algorithms, rotation=45, ha='right')
        ax6.set_ylabel('Iterations to Convergence')
        ax6.set_title('Convergence Speed (Lower is Better)', fontweight='bold')
        ax6.grid(True, alpha=0.3)
        
        # Plot 7: Fitness vs Time Scatter
        ax7 = fig.add_subplot(gs[2, :2])
        for i, (m, algo, color) in enumerate(zip(self.metrics_list, algorithms, colors)):
            ax7.scatter([m.mean_time], [m.mean_fitness], s=200, alpha=0.6, 
                       color=color, label=algo, edgecolors='black', linewidth=1.5)
        ax7.set_xlabel('Mean Execution Time (s)', fontsize=12)
        ax7.set_ylabel('Mean Fitness', fontsize=12)
        ax7.set_title('Efficiency-Quality Trade-off', fontsize=14, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # Plot 8: Ranking Table
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        
        # Create ranking
        ranking_data = []
        for m in self.metrics_list:
            score = (m.mean_fitness / max(means) * 0.4 +  # Fitness (40%)
                    m.std_fitness / max(stds) * 0.2 +     # Consistency (20%)
                    m.mean_time / max(times) * 0.2 +      # Speed (20%)
                    m.convergence_speed / max(conv_speeds) * 0.2)  # Convergence (20%)
            ranking_data.append((m.algorithm_name, score))
        
        ranking_data.sort(key=lambda x: x[1])
        
        table_text = "Rank  Algorithm\n" + "-" * 20 + "\n"
        for rank, (algo, _) in enumerate(ranking_data, 1):
            table_text += f"{rank:2d}.   {algo}\n"
        
        ax8.text(0.1, 0.5, table_text, fontsize=11, family='monospace',
                verticalalignment='center')
        ax8.set_title('Overall Ranking', fontweight='bold')
        
        plt.suptitle('Comprehensive Performance Analysis', fontsize=16, fontweight='bold', y=0.995)
        
        if save_fig:
            plt.savefig(self.output_dir / "statistical_summary.png", dpi=300, bbox_inches='tight')
            print(f"✅ Statistical summary saved to {self.output_dir}/statistical_summary.png")
        
        plt.show()
    
    def generate_report(self, filename: str = "performance_report.json"):
        """Generate comprehensive JSON report"""
        report = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'num_algorithms': len(self.metrics_list),
            'algorithms': [m.to_dict() for m in self.metrics_list]
        }
        
        report_path = self.output_dir / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to {report_path}")
        
        return report
