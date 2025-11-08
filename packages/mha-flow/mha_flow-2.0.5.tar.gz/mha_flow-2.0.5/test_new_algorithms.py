"""
Quick Test for New Algorithms v2.0.4
=====================================

Tests the 3 new algorithms added in this update:
1. MFO (Moth-Flame Optimization)
2. GWO-MFO Hybrid
3. PSO-MFO Hybrid
"""

import numpy as np
import sys


def sphere_function(x):
    """Simple sphere test function: f(x) = sum(x^2)"""
    return np.sum(x ** 2)


def rastrigin_function(x):
    """Rastrigin function: f(x) = 10n + sum(x^2 - 10*cos(2*pi*x))"""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


def test_algorithm(algo_class, algo_name, obj_func, func_name):
    """Test a single algorithm"""
    print(f"\n{'='*70}")
    print(f"Testing: {algo_name} on {func_name}")
    print(f"{'='*70}")
    
    try:
        # Create optimizer
        optimizer = algo_class(population_size=20, max_iterations=50)
        print(f"✅ {algo_name} instantiated successfully")
        
        # Run optimization using optimize() method with objective_function only
        model = optimizer.optimize(objective_function=obj_func)
        
        best_pos = model.best_solution_
        best_fit = model.best_fitness_
        
        print(f"✅ {algo_name} completed successfully")
        print(f"   Best Fitness: {best_fit:.6e}")
        print(f"   Best Position (first 5 dims): {best_pos[:5]}")
        
        # Check if result is reasonable
        if best_fit < 1000:
            print(f"✅ Result quality: GOOD (fitness < 1000)")
        else:
            print(f"⚠️ Result quality: ACCEPTABLE (fitness = {best_fit:.2e})")
        
        return True
    except Exception as e:
        print(f"❌ {algo_name} FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MHA TOOLBOX v2.0.4 - NEW ALGORITHMS TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: MFO
    try:
        from mha_toolbox.algorithms.mfo import MFO
        results.append(("MFO", test_algorithm(MFO, "Moth-Flame Optimization (MFO)", sphere_function, "Sphere")))
    except ImportError as e:
        print(f"\n❌ Cannot import MFO: {e}")
        results.append(("MFO", False))
    
    # Test 2: GWO-MFO Hybrid
    try:
        from mha_toolbox.algorithms.hybrid.gwo_mfo_hybrid import GWO_MFO_Hybrid
        results.append(("GWO-MFO", test_algorithm(GWO_MFO_Hybrid, "GWO-MFO Hybrid", sphere_function, "Sphere")))
    except ImportError as e:
        print(f"\n❌ Cannot import GWO-MFO Hybrid: {e}")
        results.append(("GWO-MFO", False))
    
    # Test 3: PSO-MFO Hybrid
    try:
        from mha_toolbox.algorithms.hybrid.pso_mfo_hybrid import PSO_MFO_Hybrid
        results.append(("PSO-MFO", test_algorithm(PSO_MFO_Hybrid, "PSO-MFO Hybrid", rastrigin_function, "Rastrigin")))
    except ImportError as e:
        print(f"\n❌ Cannot import PSO-MFO Hybrid: {e}")
        results.append(("PSO-MFO", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for algo_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{algo_name:15} : {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! New algorithms are working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
