"""
Comprehensive Test Script for ALL 130+ MHA Algorithms
======================================================

This script tests all algorithms in the MHA Toolbox to ensure:
1. All 130+ algorithms are discovered and loaded
2. Each algorithm can be initialized
3. Each algorithm can run on a simple optimization problem
4. Results are valid (no NaN, inf, or errors)

"""

import numpy as np
from mha_toolbox import MHAToolbox
import time
from datetime import datetime

def simple_sphere_function(solution):
    """Simple sphere function for testing: f(x) = sum(x^2)"""
    return np.sum(np.array(solution) ** 2)

def test_all_algorithms():
    """Test all algorithms in the toolbox"""
    
    print("=" * 80)
    print("MHA TOOLBOX - COMPREHENSIVE ALGORITHM TEST")
    print("=" * 80)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize toolbox
    print("Initializing MHA Toolbox...")
    toolbox = MHAToolbox(verbose=True)
    
    # Get all algorithms
    all_algorithms = toolbox.list_algorithms()
    total_count = len(all_algorithms)
    
    print(f"\n{'=' * 80}")
    print(f"✅ Total algorithms discovered: {total_count}")
    print(f"{'=' * 80}\n")
    
    # Test parameters
    dim = 10  # Problem dimension
    lb = -5.0  # Lower bound
    ub = 5.0   # Upper bound
    max_iter = 50  # Iterations
    pop_size = 20  # Population size
    
    # Track results
    successful = []
    failed = []
    errors = {}
    
    print(f"Test Configuration:")
    print(f"  - Problem: Sphere function (minimization)")
    print(f"  - Dimensions: {dim}")
    print(f"  - Bounds: [{lb}, {ub}]")
    print(f"  - Iterations: {max_iter}")
    print(f"  - Population: {pop_size}")
    print(f"\n{'=' * 80}\n")
    
    # Test each algorithm
    for idx, algo_name in enumerate(sorted(all_algorithms), 1):
        try:
            print(f"[{idx}/{total_count}] Testing {algo_name.upper()}... ", end='', flush=True)
            
            # Get algorithm
            start_time = time.time()
            optimizer = toolbox.get_optimizer(algo_name)
            
            # Run optimization
            best_solution, best_fitness, convergence = optimizer.optimize(
                objective_function=simple_sphere_function,
                n_dim=dim,
                lower_bounds=lb,
                upper_bounds=ub,
                max_iterations=max_iter,
                population_size=pop_size
            )
            
            elapsed = time.time() - start_time
            
            # Validate results
            if best_solution is None or best_fitness is None:
                raise ValueError("Returned None values")
            
            if np.isnan(best_fitness) or np.isinf(best_fitness):
                raise ValueError(f"Invalid fitness: {best_fitness}")
            
            if len(best_solution) != dim:
                raise ValueError(f"Wrong dimension: expected {dim}, got {len(best_solution)}")
            
            # Success!
            successful.append(algo_name)
            print(f"✅ OK (fitness: {best_fitness:.6e}, time: {elapsed:.2f}s)")
            
        except Exception as e:
            failed.append(algo_name)
            errors[algo_name] = str(e)
            print(f"❌ FAILED: {str(e)[:60]}")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"✅ Successful: {len(successful)}/{total_count} ({len(successful)/total_count*100:.1f}%)")
    print(f"❌ Failed: {len(failed)}/{total_count} ({len(failed)/total_count*100:.1f}%)")
    print(f"{'=' * 80}\n")
    
    if successful:
        print(f"✅ WORKING ALGORITHMS ({len(successful)}):")
        print("-" * 80)
        for i, algo in enumerate(sorted(successful), 1):
            print(f"  {i:3d}. {algo.upper()}")
        print()
    
    if failed:
        print(f"\n❌ FAILED ALGORITHMS ({len(failed)}):")
        print("-" * 80)
        for i, algo in enumerate(sorted(failed), 1):
            error_msg = errors.get(algo, "Unknown error")[:60]
            print(f"  {i:3d}. {algo.upper():<20} - {error_msg}")
        print()
    
    # Algorithm categories breakdown
    print(f"\n{'=' * 80}")
    print("ALGORITHM CATEGORIES")
    print(f"{'=' * 80}")
    categories = toolbox.list_algorithms_by_category()
    for category, algos in categories.items():
        working = [a for a in algos if a in successful]
        failing = [a for a in algos if a in failed]
        print(f"\n{category}:")
        print(f"  Total: {len(algos)}, Working: {len(working)}, Failed: {len(failing)}")
        if failing:
            print(f"  Failed: {', '.join([a.upper() for a in failing])}")
    
    print(f"\n{'=' * 80}")
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")
    
    return {
        'total': total_count,
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful)/total_count*100,
        'successful_algorithms': successful,
        'failed_algorithms': failed,
        'errors': errors
    }

if __name__ == "__main__":
    results = test_all_algorithms()
    
    # Exit with appropriate code
    if results['failed'] == 0:
        print("🎉 ALL ALGORITHMS WORKING PERFECTLY! 🎉")
        exit(0)
    elif results['success_rate'] >= 90:
        print(f"⚠️  Most algorithms working ({results['success_rate']:.1f}%)")
        exit(0)
    else:
        print(f"❌ Too many failures ({results['failed']}/{results['total']})")
        exit(1)
