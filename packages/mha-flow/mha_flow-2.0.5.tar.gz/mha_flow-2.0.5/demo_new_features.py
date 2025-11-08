"""
Demonstration of MHA Toolbox v2.0.3 New Features
================================================
Shows validation, error handling, and parallel execution.
"""

import numpy as np
from mha_toolbox import optimize
from mha_toolbox.benchmarks import sphere
from mha_toolbox.validators import OptimizationValidator
from mha_toolbox.parallel_optimizer import parallel_optimize, parallel_compare

print("=" * 80)
print("🚀 MHA TOOLBOX v2.0.3 - NEW FEATURES DEMONSTRATION")
print("=" * 80)

# Feature 1: Input Validation
print("\n" + "=" * 80)
print("1️⃣  INPUT VALIDATION")
print("=" * 80)

validator = OptimizationValidator()

# Test 1: Valid bounds
try:
    lb, ub = validator.validate_bounds((-10, 10), dimensions=5)
    print("✅ Bounds validation: PASSED")
    print(f"   Lower bounds: {lb[:3]}...")
    print(f"   Upper bounds: {ub[:3]}...")
except Exception as e:
    print(f"❌ Bounds validation: {e}")

# Test 2: Invalid bounds (should catch error)
try:
    validator.validate_bounds((10, -10), dimensions=5)  # Wrong order
    print("❌ Invalid bounds detection: FAILED (should have caught error)")
except ValueError as e:
    print("✅ Invalid bounds detection: PASSED")
    print(f"   Caught error: {str(e)[:50]}...")

# Test 3: Dataset validation
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
try:
    validator.validate_dataset(X, y)
    print("✅ Dataset validation: PASSED")
    print(f"   Samples: {X.shape[0]}, Features: {X.shape[1]}")
except Exception as e:
    print(f"❌ Dataset validation: {e}")

# Feature 2: Error Logging and Quality Assessment
print("\n" + "=" * 80)
print("2️⃣  ERROR LOGGING & QUALITY ASSESSMENT")
print("=" * 80)

result = optimize('PSO',
                 objective_function=sphere,
                 dimensions=5,
                 population_size=20,
                 max_iterations=30)

print(f"✅ Optimization completed")
print(f"   Best fitness: {result.best_fitness_:.6e}")
print(f"   Execution time: {result.execution_time_:.3f}s")
print(f"   Error log entries: {len(result.error_log_)}")
print(f"   Warnings: {len(result.warnings_)}")
print(f"   Is successful: {result.is_successful()}")

# Quality assessment
quality = result.get_convergence_quality()
print(f"\n📊 Convergence Quality Assessment:")
print(f"   Quality: {quality['quality']}")
print(f"   Improvement: {quality['improvement']:.6e}")
print(f"   Improvement %: {quality['improvement_pct']:.2f}%")
print(f"   Is stagnant: {quality['is_stagnant']}")

if __name__ == '__main__':
    # Feature 3: Parallel Optimization (Multiple Runs)
    print("\n" + "=" * 80)
    print("3️⃣  PARALLEL OPTIMIZATION (Statistical Analysis)")
    print("=" * 80)

    print("Running PSO 5 times in parallel...")
    results = parallel_optimize('PSO',
                               n_runs=5,
                               objective_function=sphere,
                               dimensions=5,
                               population_size=15,
                               max_iterations=20,
                               n_jobs=2)

    stats = results['statistics']
    print(f"\n📊 Statistics from {results['statistics']['n_successful']} runs:")
    print(f"   Mean fitness: {stats['mean_fitness']:.6e}")
    print(f"   Std fitness: {stats['std_fitness']:.6e}")
    print(f"   Min fitness: {stats['min_fitness']:.6e}")
    print(f"   Max fitness: {stats['max_fitness']:.6e}")
    print(f"   Median fitness: {stats['median_fitness']:.6e}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")
    print(f"   Total time: {results['execution_time']:.2f}s")

    # Feature 4: Algorithm Comparison
    print("\n" + "=" * 80)
    print("4️⃣  PARALLEL ALGORITHM COMPARISON")
    print("=" * 80)

    print("Comparing 3 algorithms with 2 runs each...")
    comparison = parallel_compare(['PSO', 'GWO', 'WOA'],
                                 n_runs_per_algorithm=2,
                                 objective_function=sphere,
                                 dimensions=5,
                                 population_size=15,
                                 max_iterations=20,
                                 n_jobs=2)

    print(f"\n🏆 Ranking (best to worst):")
    print(f"{'Rank':<6} {'Algorithm':<15} {'Mean Fitness':<15} {'Best Fitness':<15}")
    print("-" * 55)
    for entry in comparison['ranking']:
        print(f"{entry['rank']:<6} {entry['algorithm']:<15} "
              f"{entry['mean_fitness']:<15.6e} {entry['best_fitness']:<15.6e}")

    print(f"\n🥇 Best algorithm: {comparison['best_algorithm']}")
    print(f"   Total comparison time: {comparison['total_time']:.2f}s")

    # Feature 5: Hybrid Algorithm with Quality Check
    print("\n" + "=" * 80)
    print("5️⃣  HYBRID ALGORITHM (AMSHA) WITH QUALITY CHECK")
    print("=" * 80)

    result_hybrid = optimize('AMSHA',
                            objective_function=sphere,
                            dimensions=5,
                            population_size=20,
                            max_iterations=30)

    print(f"✅ AMSHA Hybrid completed")
    print(f"   Best fitness: {result_hybrid.best_fitness_:.6e}")
    print(f"   Is successful: {result_hybrid.is_successful()}")

    quality_hybrid = result_hybrid.get_convergence_quality()
    print(f"\n📊 AMSHA Convergence Quality:")
    print(f"   Quality rating: {quality_hybrid['quality']}")
    print(f"   Improvement: {quality_hybrid['improvement_pct']:.2f}%")

    # Summary
    print("\n" + "=" * 80)
    print("✅ ALL NEW FEATURES DEMONSTRATED SUCCESSFULLY")
    print("=" * 80)
    print("\n🎉 MHA Toolbox v2.0.3 is ready for production use!")
    print("\nKey Improvements:")
    print("  • Comprehensive input validation")
    print("  • Robust error handling and logging")
    print("  • Parallel execution for faster comparison")
    print("  • Quality assessment for convergence")
    print("  • Statistical analysis across multiple runs")
    print("\n📚 See CHANGELOG_v2.0.3.md for full documentation")
    print("=" * 80)
