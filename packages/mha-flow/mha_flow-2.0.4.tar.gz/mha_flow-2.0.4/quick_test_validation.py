"""Quick test of validation features"""
from mha_toolbox import optimize
from mha_toolbox.benchmarks import sphere

# Test validation with warnings
result = optimize('PSO', 
                 objective_function=sphere, 
                 dimensions=3, 
                 max_iterations=10,
                 population_size=10)

print(f"✅ Optimization completed")
print(f"   Best fitness: {result.best_fitness_:.6f}")
print(f"   Has error_log: {hasattr(result, 'error_log_')}")
print(f"   Has warnings: {hasattr(result, 'warnings_')}")
print(f"   Is successful: {result.is_successful()}")
print(f"   Convergence quality: {result.get_convergence_quality()['quality']}")
