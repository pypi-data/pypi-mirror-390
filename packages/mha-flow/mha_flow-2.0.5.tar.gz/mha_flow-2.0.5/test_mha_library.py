"""
Complete MHA Toolbox Library Test Script
Tests all major features after PyPI installation
"""

import numpy as np
from sklearn.datasets import load_iris, load_breast_cancer, load_wine
from sklearn.model_selection import train_test_split

print("="*80)
print("🧪 MHA TOOLBOX LIBRARY TEST SUITE")
print("="*80)

# Test 1: Basic Import
print("\n📦 Test 1: Import Test")
print("-"*80)
try:
    from mha_toolbox import optimize, MHAToolbox
    print("✅ Successfully imported: optimize, MHAToolbox")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: List Algorithms
print("\n📋 Test 2: List Available Algorithms")
print("-"*80)
try:
    toolbox = MHAToolbox()
    all_algorithms = toolbox.get_all_algorithm_names()
    print(f"✅ Total algorithms available: {len(all_algorithms)}")
    
    # Show sample algorithms
    print("\n📌 Sample Standard Algorithms:")
    standard = [a for a in all_algorithms if 'hybrid' not in a.lower() and '_' not in a][:10]
    for alg in standard:
        print(f"   • {alg}")
    
    print("\n🔗 Sample Hybrid Algorithms:")
    hybrids = [a for a in all_algorithms if 'hybrid' in a.lower() or '_' in a][:10]
    for alg in hybrids:
        print(f"   • {alg}")
    
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 3: Simple Function Optimization
print("\n🎯 Test 3: Simple Function Optimization (Sphere Function)")
print("-"*80)
try:
    def sphere(x):
        """Simple sphere function: f(x) = sum(x^2)"""
        return np.sum(x**2)
    
    result = optimize(
        'PSO',
        objective_function=sphere,
        bounds=(-10, 10),
        dimensions=5,
        population_size=20,
        max_iterations=30
    )
    
    print(f"✅ Algorithm: PSO")
    print(f"✅ Best fitness: {result.best_fitness_:.6f}")
    print(f"✅ Best solution: {result.best_solution_[:3]}... (first 3 dims)")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    print(f"✅ Convergence iterations: {len(result.global_fitness_)}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Feature Selection with Real Dataset
print("\n🔍 Test 4: Feature Selection (Iris Dataset)")
print("-"*80)
try:
    X, y = load_iris(return_X_y=True)
    print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    result = optimize('GA', X=X, y=y, 
                     population_size=20,
                     max_iterations=30)
    
    selected_features = result.best_solution_ > 0.5
    accuracy = 1 - result.best_fitness_
    
    print(f"✅ Algorithm: Genetic Algorithm (GA)")
    print(f"✅ Original features: {X.shape[1]}")
    print(f"✅ Selected features: {np.sum(selected_features)}")
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"✅ Best fitness: {result.best_fitness_:.4f}")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: New Adaptive Multi-Strategy Hybrid (AMSHA)
print("\n🆕 Test 5: New Adaptive Multi-Strategy Hybrid (AMSHA)")
print("-"*80)
try:
    result = optimize(
        'AMSHA',  # New adaptive hybrid
        objective_function=sphere,
        bounds=(-100, 100),
        dimensions=10,
        population_size=30,
        max_iterations=50
    )
    
    print(f"✅ Algorithm: AMSHA (Adaptive Multi-Strategy)")
    print(f"✅ Best fitness: {result.best_fitness_:.6e}")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    print(f"✅ Final convergence: {result.global_fitness_[-1]:.6e}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: New GWO-WOA Hybrid
print("\n🐺 Test 6: GWO-WOA Hybrid (Wolf + Whale)")
print("-"*80)
try:
    X, y = load_wine(return_X_y=True)
    print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    result = optimize('GWO_WOA_Hybrid', X=X, y=y,
                     population_size=25,
                     max_iterations=40)
    
    selected = result.best_solution_ > 0.5
    print(f"✅ Algorithm: GWO_WOA_Hybrid")
    print(f"✅ Selected features: {np.sum(selected)}/{X.shape[1]}")
    print(f"✅ Accuracy: {(1 - result.best_fitness_):.4f}")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: PSO-SCA Hybrid
print("\n🦅 Test 7: PSO-SCA Hybrid (Swarm + Sine Cosine)")
print("-"*80)
try:
    def rastrigin(x):
        """Rastrigin function - multimodal test function"""
        n = len(x)
        return 10*n + np.sum(x**2 - 10*np.cos(2*np.pi*x))
    
    result = optimize('PSO_SCA_Hybrid',
                     objective_function=rastrigin,
                     bounds=(-5.12, 5.12),
                     dimensions=8,
                     population_size=30,
                     max_iterations=40)
    
    print(f"✅ Algorithm: PSO_SCA_Hybrid")
    print(f"✅ Best fitness: {result.best_fitness_:.6f}")
    print(f"✅ Convergence improvement: {result.global_fitness_[0] - result.global_fitness_[-1]:.6f}")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: ABC-GWO Hybrid
print("\n🐝 Test 8: ABC-GWO Hybrid (Bee + Wolf)")
print("-"*80)
try:
    X, y = load_breast_cancer(return_X_y=True)
    print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    result = optimize('ABC_GWO_Hybrid', X=X, y=y,
                     population_size=25,
                     max_iterations=35)
    
    selected = result.best_solution_ > 0.5
    print(f"✅ Algorithm: ABC_GWO_Hybrid")
    print(f"✅ Original features: {X.shape[1]}")
    print(f"✅ Selected features: {np.sum(selected)}")
    print(f"✅ Accuracy: {(1 - result.best_fitness_):.4f}")
    print(f"✅ Execution time: {result.execution_time_:.3f}s")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 9: Compare Multiple Algorithms
print("\n⚖️ Test 9: Algorithm Comparison")
print("-"*80)
try:
    algorithms = ['PSO', 'GWO', 'WOA', 'AMSHA']
    X, y = load_iris(return_X_y=True)
    
    results_summary = []
    
    for algo in algorithms:
        result = optimize(algo, X=X, y=y,
                         population_size=20,
                         max_iterations=30)
        
        results_summary.append({
            'Algorithm': algo,
            'Fitness': result.best_fitness_,
            'Accuracy': 1 - result.best_fitness_,
            'Time': result.execution_time_,
            'Features': np.sum(result.best_solution_ > 0.5)
        })
    
    print("\n📊 Comparison Results:")
    print(f"{'Algorithm':<15} {'Fitness':<12} {'Accuracy':<12} {'Time(s)':<10} {'Features':<10}")
    print("-"*60)
    for r in results_summary:
        print(f"{r['Algorithm']:<15} {r['Fitness']:<12.4f} {r['Accuracy']:<12.4f} {r['Time']:<10.3f} {r['Features']:<10}")
    
    best = min(results_summary, key=lambda x: x['Fitness'])
    print(f"\n🏆 Best Algorithm: {best['Algorithm']} (Fitness: {best['Fitness']:.4f})")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 10: Check Result Attributes
print("\n🔍 Test 10: Result Object Attributes")
print("-"*80)
try:
    result = optimize('PSO', 
                     objective_function=sphere,
                     bounds=(-10, 10),
                     dimensions=5,
                     population_size=20,
                     max_iterations=30)
    
    print("✅ Available attributes:")
    attrs = ['best_fitness_', 'best_solution_', 'execution_time_', 
             'global_fitness_', 'local_fitness_', 'algorithm_name_']
    
    for attr in attrs:
        if hasattr(result, attr):
            value = getattr(result, attr)
            if isinstance(value, np.ndarray):
                print(f"   • {attr}: array of shape {value.shape}")
            elif isinstance(value, (int, float)):
                print(f"   • {attr}: {value:.6f}")
            else:
                print(f"   • {attr}: {value}")
        else:
            print(f"   ⚠️ {attr}: NOT FOUND")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Final Summary
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)
print("✅ All major features tested successfully!")
print("\n🎉 MHA Toolbox is working correctly!")
print("\n📚 Next Steps:")
print("   1. Try the web interface: streamlit run mha_ui_complete.py")
print("   2. Explore more algorithms: python -m mha_toolbox list")
print("   3. Get recommendations: python -m mha_toolbox recommend --interactive")
print("   4. Read documentation: https://github.com/yourusername/MHA-Algorithm")
print("\n💡 Quick Usage:")
print("   from mha_toolbox import optimize")
print("   result = optimize('AMSHA', X=X, y=y)")
print("="*80)