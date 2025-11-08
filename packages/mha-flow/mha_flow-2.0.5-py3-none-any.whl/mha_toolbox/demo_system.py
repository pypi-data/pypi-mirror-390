"""
Comprehensive MHA Toolbox Demo System

This module provides a complete demonstration system for the MHA Toolbox,
showcasing all capabilities including:
- Single algorithm optimization
- Multi-algorithm comparison
- Hybrid algorithm combinations
- Feature selection
- Function optimization
- Real-world problem solving
- Performance analysis
- Visualization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer, load_wine, load_iris, load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import time
import warnings
warnings.filterwarnings('ignore')

import mha_toolbox as mha
from .advanced_hybrid import AdvancedHybridOptimizer


class MHADemoSystem:
    """Comprehensive demo system for MHA Toolbox."""
    
    def __init__(self):
        self.results_history = []
        self.datasets = {
            'breast_cancer': load_breast_cancer,
            'wine': load_wine,
            'iris': load_iris,
            'digits': load_digits
        }
        
    def demo_feature_selection(self, dataset_name='breast_cancer', algorithms=['pso', 'gwo', 'sca']):
        """
        Demonstrate feature selection capabilities.
        
        Parameters
        ----------
        dataset_name : str
            Name of dataset to use
        algorithms : list
            List of algorithms to test
            
        Returns
        -------
        dict
            Results for each algorithm
        """
        print(f"🧬 FEATURE SELECTION DEMO - Dataset: {dataset_name}")
        print("=" * 60)
        
        # Load dataset
        data_loader = self.datasets[dataset_name]
        X, y = data_loader(return_X_y=True)
        
        print(f"📊 Dataset Info:")
        print(f"   Samples: {X.shape[0]}")
        print(f"   Features: {X.shape[1]}")
        print(f"   Classes: {len(np.unique(y))}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Test baseline (all features)
        baseline_rf = RandomForestClassifier(random_state=42)
        baseline_rf.fit(X_train, y_train)
        baseline_accuracy = accuracy_score(y_test, baseline_rf.predict(X_test))
        
        print(f"📈 Baseline Accuracy (all features): {baseline_accuracy:.4f}")
        print()
        
        # Test each algorithm
        results = {}
        for alg_name in algorithms:
            print(f"🚀 Testing {alg_name.upper()}...")
            
            start_time = time.time()
            result = mha.optimize(alg_name, X_train, y_train, 
                                population_size=30, 
                                max_iterations=50,
                                verbose=False)
            
            # Get selected features
            selected_features = result.best_solution_ > 0.5
            n_selected = np.sum(selected_features)
            
            if n_selected == 0:
                print(f"   ⚠️  No features selected, using top 5 features")
                top_indices = np.argsort(result.best_solution_)[-5:]
                selected_features = np.zeros_like(result.best_solution_, dtype=bool)
                selected_features[top_indices] = True
                n_selected = 5
            
            # Test accuracy with selected features
            if n_selected > 0:
                X_train_selected = X_train[:, selected_features]
                X_test_selected = X_test[:, selected_features]
                
                rf = RandomForestClassifier(random_state=42)
                rf.fit(X_train_selected, y_train)
                accuracy = accuracy_score(y_test, rf.predict(X_test_selected))
                
                reduction = (1 - n_selected / X.shape[1]) * 100
                improvement = (accuracy - baseline_accuracy) * 100
                
                print(f"   ✅ Selected: {n_selected}/{X.shape[1]} features ({reduction:.1f}% reduction)")
                print(f"   ✅ Accuracy: {accuracy:.4f} ({improvement:+.2f}% vs baseline)")
                print(f"   ✅ Fitness: {result.best_fitness_:.4f}")
                print(f"   ⏱️  Time: {time.time() - start_time:.2f}s")
            else:
                accuracy = 0
                reduction = 0
                improvement = -100
                
            results[alg_name] = {
                'result': result,
                'selected_features': selected_features,
                'n_selected': n_selected,
                'accuracy': accuracy,
                'reduction': reduction,
                'improvement': improvement,
                'execution_time': time.time() - start_time
            }
            print()
        
        self._print_feature_selection_summary(results, baseline_accuracy)
        return results
    
    def demo_function_optimization(self, algorithms=['pso', 'gwo', 'sca'], functions=None):
        """
        Demonstrate function optimization capabilities.
        
        Parameters
        ----------
        algorithms : list
            List of algorithms to test
        functions : dict, optional
            Dictionary of test functions
            
        Returns
        -------
        dict
            Results for each algorithm and function
        """
        print(f"🎯 FUNCTION OPTIMIZATION DEMO")
        print("=" * 60)
        
        if functions is None:
            functions = {
                'Sphere': lambda x: np.sum(x**2),
                'Rosenbrock': lambda x: np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2),
                'Rastrigin': lambda x: 10*len(x) + np.sum(x**2 - 10*np.cos(2*np.pi*x)),
                'Ackley': lambda x: -20*np.exp(-0.2*np.sqrt(np.mean(x**2))) - np.exp(np.mean(np.cos(2*np.pi*x))) + 20 + np.e
            }
        
        dimensions = 10
        bounds = (-5, 5)
        
        results = {}
        
        for func_name, func in functions.items():
            print(f"\n📊 Testing Function: {func_name}")
            print("-" * 40)
            
            results[func_name] = {}
            
            for alg_name in algorithms:
                print(f"🚀 {alg_name.upper()}...", end=" ")
                
                start_time = time.time()
                result = mha.optimize(alg_name, 
                                    objective_function=func,
                                    dimensions=dimensions,
                                    lower_bound=bounds[0],
                                    upper_bound=bounds[1],
                                    population_size=30,
                                    max_iterations=100,
                                    verbose=False)
                
                execution_time = time.time() - start_time
                
                print(f"Best: {result.best_fitness_:.6f}, Time: {execution_time:.2f}s")
                
                results[func_name][alg_name] = {
                    'result': result,
                    'best_fitness': result.best_fitness_,
                    'execution_time': execution_time
                }
        
        self._print_function_optimization_summary(results)
        return results
    
    def demo_hybrid_algorithms(self, algorithms=['pso', 'gwo', 'sca'], dataset_name='breast_cancer'):
        """
        Demonstrate hybrid algorithm capabilities.
        
        Parameters
        ----------
        algorithms : list
            List of algorithms to combine
        dataset_name : str
            Dataset to use for testing
            
        Returns
        -------
        dict
            Results for each hybrid strategy
        """
        print(f"🔬 HYBRID ALGORITHMS DEMO - Dataset: {dataset_name}")
        print("=" * 60)
        
        # Load dataset
        data_loader = self.datasets[dataset_name]
        X, y = data_loader(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        from .utils.problem_creator import create_problem
        problem = create_problem(X=X_train, y=y_train, problem_type='feature_selection')
        
        # Create hybrid optimizer
        hybrid = AdvancedHybridOptimizer()
        
        # Test different strategies
        strategies = ['sequential', 'parallel', 'ensemble']
        results = {}
        
        for strategy in strategies:
            print(f"\n🧬 Testing {strategy.upper()} hybrid...")
            
            start_time = time.time()
            result = hybrid.optimize(algorithms, problem, strategy=strategy,
                                   population_size=20, max_iterations=30)
            
            # Evaluate on test set
            selected_features = result.best_solution_ > 0.5
            n_selected = np.sum(selected_features)
            
            if n_selected > 0:
                X_test_selected = X_test[:, selected_features]
                X_train_selected = X_train[:, selected_features]
                
                rf = RandomForestClassifier(random_state=42)
                rf.fit(X_train_selected, y_train)
                accuracy = accuracy_score(y_test, rf.predict(X_test_selected))
            else:
                accuracy = 0
                n_selected = 0
            
            execution_time = time.time() - start_time
            
            print(f"   ✅ Features: {n_selected}/{X.shape[1]}")
            print(f"   ✅ Accuracy: {accuracy:.4f}")
            print(f"   ✅ Fitness: {result.best_fitness_:.4f}")
            print(f"   ⏱️  Time: {execution_time:.2f}s")
            
            results[strategy] = {
                'result': result,
                'accuracy': accuracy,
                'n_selected': n_selected,
                'execution_time': execution_time
            }
        
        self._print_hybrid_summary(results)
        return results
    
    def demo_algorithm_comparison(self, dataset_name='wine', n_algorithms=6):
        """
        Demonstrate algorithm comparison capabilities.
        
        Parameters
        ----------
        dataset_name : str
            Dataset to use
        n_algorithms : int
            Number of algorithms to compare
            
        Returns
        -------
        dict
            Comparison results
        """
        print(f"📊 ALGORITHM COMPARISON DEMO - Dataset: {dataset_name}")
        print("=" * 60)
        
        # Load dataset
        data_loader = self.datasets[dataset_name]
        X, y = data_loader(return_X_y=True)
        
        # Select algorithms to compare
        all_algorithms = ['pso', 'gwo', 'sca', 'woa', 'ga', 'de', 'abc', 'aco', 'alo', 'fa']
        algorithms = all_algorithms[:n_algorithms]
        
        print(f"🎯 Comparing algorithms: {algorithms}")
        print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(y))} classes")
        print()
        
        # Run comparison
        results = mha.compare(algorithms, X, y, 
                            population_size=30, 
                            max_iterations=50, 
                            n_runs=3,
                            verbose=False)
        
        # Analyze results
        performance_data = []
        for alg_name, alg_results in results.items():
            for run_result in alg_results:
                performance_data.append({
                    'Algorithm': alg_name.upper(),
                    'Fitness': run_result.best_fitness_,
                    'Selected_Features': np.sum(run_result.best_solution_ > 0.5),
                    'Execution_Time': getattr(run_result, 'execution_time_', 0)
                })
        
        df = pd.DataFrame(performance_data)
        
        # Print summary statistics
        summary = df.groupby('Algorithm').agg({
            'Fitness': ['mean', 'std', 'min'],
            'Selected_Features': ['mean', 'std'],
            'Execution_Time': ['mean', 'std']
        }).round(4)
        
        print("📈 COMPARISON RESULTS:")
        print(summary)
        
        # Find best algorithm
        best_alg = df.groupby('Algorithm')['Fitness'].mean().idxmin()
        best_fitness = df.groupby('Algorithm')['Fitness'].mean().min()
        
        print(f"\n🏆 Best Algorithm: {best_alg} (avg fitness: {best_fitness:.4f})")
        
        return {'results': results, 'summary': summary, 'best_algorithm': best_alg}
    
    def demo_real_world_problem(self):
        """
        Demonstrate solving a real-world optimization problem.
        """
        print(f"🌍 REAL-WORLD PROBLEM DEMO: Portfolio Optimization")
        print("=" * 60)
        
        # Simulate stock returns data
        np.random.seed(42)
        n_assets = 10
        n_days = 252  # One trading year
        
        # Generate correlated returns
        returns = np.random.multivariate_normal(
            mean=np.random.uniform(0.0005, 0.002, n_assets),
            cov=self._generate_covariance_matrix(n_assets),
            size=n_days
        )
        
        expected_returns = np.mean(returns, axis=0)
        cov_matrix = np.cov(returns.T)
        
        print(f"📈 Portfolio Setup:")
        print(f"   Assets: {n_assets}")
        print(f"   Trading days: {n_days}")
        print(f"   Expected returns: {expected_returns.mean():.4f} ± {expected_returns.std():.4f}")
        print()
        
        # Define portfolio optimization problem
        def portfolio_objective(weights):
            """Minimize negative Sharpe ratio."""
            weights = weights / np.sum(weights)  # Normalize weights
            
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if portfolio_risk == 0:
                return -float('inf')
            
            sharpe_ratio = portfolio_return / portfolio_risk
            return -sharpe_ratio  # Minimize negative Sharpe ratio
        
        # Test different algorithms
        algorithms = ['pso', 'gwo', 'sca', 'ga']
        results = {}
        
        for alg_name in algorithms:
            print(f"🚀 Optimizing portfolio with {alg_name.upper()}...")
            
            result = mha.optimize(alg_name,
                                objective_function=portfolio_objective,
                                dimensions=n_assets,
                                lower_bound=0.0,
                                upper_bound=1.0,
                                population_size=50,
                                max_iterations=100,
                                verbose=False)
            
            # Normalize weights
            weights = result.best_solution_ / np.sum(result.best_solution_)
            
            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = -result.best_fitness_
            
            print(f"   ✅ Return: {portfolio_return*252:.2%} annually")
            print(f"   ✅ Risk: {portfolio_risk*np.sqrt(252):.2%} annually")
            print(f"   ✅ Sharpe Ratio: {sharpe_ratio:.3f}")
            print(f"   ✅ Active Assets: {np.sum(weights > 0.01)}/{n_assets}")
            print()
            
            results[alg_name] = {
                'weights': weights,
                'return': portfolio_return,
                'risk': portfolio_risk,
                'sharpe_ratio': sharpe_ratio,
                'result': result
            }
        
        # Find best portfolio
        best_alg = max(results.keys(), key=lambda k: results[k]['sharpe_ratio'])
        print(f"🏆 Best Portfolio: {best_alg.upper()} (Sharpe: {results[best_alg]['sharpe_ratio']:.3f})")
        
        return results
    
    def run_complete_demo(self):
        """Run a complete demonstration of all capabilities."""
        print("🚀 MHA TOOLBOX - COMPLETE DEMONSTRATION")
        print("=" * 80)
        print("This demo showcases all major capabilities of the MHA Toolbox:")
        print("1. Feature Selection")
        print("2. Function Optimization") 
        print("3. Hybrid Algorithms")
        print("4. Algorithm Comparison")
        print("5. Real-world Problem Solving")
        print("=" * 80)
        print()
        
        # Store all results
        demo_results = {}
        
        try:
            # 1. Feature Selection Demo
            print("🟢 Starting Feature Selection Demo...")
            demo_results['feature_selection'] = self.demo_feature_selection()
            print("\n" + "="*80 + "\n")
            
            # 2. Function Optimization Demo
            print("🟡 Starting Function Optimization Demo...")
            demo_results['function_optimization'] = self.demo_function_optimization()
            print("\n" + "="*80 + "\n")
            
            # 3. Hybrid Algorithms Demo
            print("🔵 Starting Hybrid Algorithms Demo...")
            demo_results['hybrid_algorithms'] = self.demo_hybrid_algorithms()
            print("\n" + "="*80 + "\n")
            
            # 4. Algorithm Comparison Demo
            print("🟣 Starting Algorithm Comparison Demo...")
            demo_results['algorithm_comparison'] = self.demo_algorithm_comparison()
            print("\n" + "="*80 + "\n")
            
            # 5. Real-world Problem Demo
            print("🟠 Starting Real-world Problem Demo...")
            demo_results['real_world_problem'] = self.demo_real_world_problem()
            print("\n" + "="*80 + "\n")
            
            # Final Summary
            self._print_complete_summary()
            
        except Exception as e:
            print(f"❌ Error during demo: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return demo_results
    
    def _print_feature_selection_summary(self, results, baseline_accuracy):
        """Print feature selection summary."""
        print("📊 FEATURE SELECTION SUMMARY:")
        print("-" * 50)
        print(f"{'Algorithm':<12} {'Features':<10} {'Accuracy':<10} {'Improvement':<12} {'Time':<8}")
        print("-" * 50)
        print(f"{'Baseline':<12} {'All':<10} {baseline_accuracy:<10.4f} {'---':<12} {'---':<8}")
        
        for alg_name, result in results.items():
            print(f"{alg_name.upper():<12} "
                  f"{result['n_selected']:<10} "
                  f"{result['accuracy']:<10.4f} "
                  f"{result['improvement']:+7.2f}%<12 "
                  f"{result['execution_time']:<8.2f}s")
        
        # Find best
        best_alg = max(results.keys(), key=lambda k: results[k]['accuracy'])
        print(f"\n🏆 Best: {best_alg.upper()} ({results[best_alg]['accuracy']:.4f} accuracy)")
    
    def _print_function_optimization_summary(self, results):
        """Print function optimization summary."""
        print("\n📊 FUNCTION OPTIMIZATION SUMMARY:")
        print("-" * 60)
        
        for func_name, func_results in results.items():
            print(f"\n{func_name}:")
            best_alg = min(func_results.keys(), key=lambda k: func_results[k]['best_fitness'])
            best_fitness = func_results[best_alg]['best_fitness']
            
            for alg_name, result in func_results.items():
                marker = "🏆" if alg_name == best_alg else "  "
                print(f"  {marker} {alg_name.upper():<8}: {result['best_fitness']:<12.6f} ({result['execution_time']:.2f}s)")
    
    def _print_hybrid_summary(self, results):
        """Print hybrid algorithms summary."""
        print("\n📊 HYBRID ALGORITHMS SUMMARY:")
        print("-" * 50)
        
        best_strategy = max(results.keys(), key=lambda k: results[k]['accuracy'])
        
        for strategy, result in results.items():
            marker = "🏆" if strategy == best_strategy else "  "
            print(f"{marker} {strategy.upper():<12}: "
                  f"Acc={result['accuracy']:.4f}, "
                  f"Features={result['n_selected']}, "
                  f"Time={result['execution_time']:.2f}s")
    
    def _print_complete_summary(self):
        """Print complete demo summary."""
        print("🎉 COMPLETE DEMO FINISHED!")
        print("=" * 60)
        print("✅ Feature Selection - Demonstrated on real datasets")
        print("✅ Function Optimization - Tested on benchmark functions")
        print("✅ Hybrid Algorithms - Sequential, Parallel & Ensemble methods")
        print("✅ Algorithm Comparison - Statistical analysis of performance")
        print("✅ Real-world Problem - Portfolio optimization example")
        print("=" * 60)
        print("🚀 The MHA Toolbox is ready for production use!")
        print("📖 Check the documentation for more advanced features.")
    
    def _generate_covariance_matrix(self, n_assets):
        """Generate a realistic covariance matrix for portfolio optimization."""
        # Create a random correlation matrix
        A = np.random.randn(n_assets, n_assets)
        correlation = np.dot(A, A.T)
        
        # Normalize to get correlation matrix
        d = np.sqrt(np.diag(correlation))
        correlation = correlation / np.outer(d, d)
        
        # Add some structure (sector correlations)
        for i in range(0, n_assets, 3):
            for j in range(i, min(i+3, n_assets)):
                for k in range(i, min(i+3, n_assets)):
                    if j != k:
                        correlation[j, k] = 0.3 + 0.2 * correlation[j, k]
        
        # Ensure positive definite
        correlation = correlation + 0.1 * np.eye(n_assets)
        
        # Convert to covariance with realistic volatilities
        volatilities = np.random.uniform(0.15, 0.35, n_assets)
        covariance = np.outer(volatilities, volatilities) * correlation
        
        return covariance


def run_demo_system(demo_type='complete'):
    """
    Run the MHA Toolbox demo system.
    
    Parameters
    ----------
    demo_type : str
        Type of demo: 'complete', 'feature_selection', 'function_optimization',
        'hybrid', 'comparison', 'real_world'
        
    Returns
    -------
    dict
        Demo results
    """
    demo = MHADemoSystem()
    
    if demo_type == 'complete':
        return demo.run_complete_demo()
    elif demo_type == 'feature_selection':
        return demo.demo_feature_selection()
    elif demo_type == 'function_optimization':
        return demo.demo_function_optimization()
    elif demo_type == 'hybrid':
        return demo.demo_hybrid_algorithms()
    elif demo_type == 'comparison':
        return demo.demo_algorithm_comparison()
    elif demo_type == 'real_world':
        return demo.demo_real_world_problem()
    else:
        raise ValueError(f"Unknown demo type: {demo_type}")


if __name__ == "__main__":
    # Run the complete demo
    results = run_demo_system('complete')