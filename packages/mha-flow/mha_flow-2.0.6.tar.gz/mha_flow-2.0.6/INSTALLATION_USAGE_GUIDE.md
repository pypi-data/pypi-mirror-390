# 🚀 MHA Flow - Installation & Usage Guide

## Quick Start Commands

```bash
# Install the package
pip install mha-flow

# Open online web interface (no local setup needed)
mha-flow-web

# Launch local web interface
mha-flow

# Command-line interface
mha-flow-cli --help

# Run demo
mha-demo
```

---

## 📦 Installation Options

### Option 1: Basic Installation (Library Only)
```bash
pip install mha-flow
```
Includes: Core algorithms, Python API

### Option 2: With Web Interface
```bash
pip install mha-flow[ui]
```
Includes: Core + Streamlit interface + visualizations

### Option 3: Complete Installation (Recommended)
```bash
pip install mha-flow[complete]
```
Includes: Everything (core + UI + advanced features + exports)

### Option 4: Development Installation
```bash
pip install mha-flow[dev]
```
Includes: All features + testing tools + documentation builders

### Option 5: From Source
```bash
git clone https://github.com/Achyut103040/MHA-Algorithm.git
cd MHA-Algorithm
pip install -e .[complete]
```

---

## 🌐 Web Interface Usage

### Online Interface (Recommended - No Installation!)
```bash
mha-flow-web
```
- Opens https://mha-flow.streamlit.app/ in your browser
- No installation required
- Full features available
- Multi-user support with authentication
- Access from anywhere

### Local Interface
```bash
mha-flow
```
- Runs Streamlit server locally
- Full offline functionality
- Data stays on your machine
- Customizable settings

---

## 💻 Python Library Usage

### Basic Optimization
```python
from mha_toolbox import MHAToolbox
from sklearn.datasets import load_iris

# Load data
X, y = load_iris(return_X_y=True)

# Initialize toolbox
toolbox = MHAToolbox()

# Run optimization
result = toolbox.optimize(
    algorithm='pso',
    X=X,
    y=y,
    population_size=30,
    max_iterations=100
)

# Access results
print(f"Best Fitness: {result.best_fitness_}")
print(f"Best Solution: {result.best_solution_}")
print(f"Execution Time: {result.execution_time_}s")
print(f"Convergence: {result.convergence_curve_}")
```

### AI-Powered Algorithm Recommendations
```python
from mha_toolbox import AlgorithmRecommender
from sklearn.datasets import load_wine

# Load data
X, y = load_wine(return_X_y=True)

# Initialize recommender
recommender = AlgorithmRecommender()

# Analyze dataset
characteristics = recommender.analyze_dataset(X, y)
print("Dataset Characteristics:")
for key, value in characteristics.items():
    print(f"  {key}: {value}")

# Get top recommendations
recommendations = recommender.recommend_algorithms(X, y, top_k=5)

print("\nTop 5 Recommended Algorithms:")
for i, (algo, confidence, reason) in enumerate(recommendations, 1):
    print(f"{i}. {algo.upper()}")
    print(f"   Confidence: {confidence:.1f}/10")
    print(f"   Reason: {reason}\n")

# Use top recommendation
best_algo = recommendations[0][0]
result = toolbox.optimize(best_algo, X=X, y=y)
print(f"Best Result: {result.best_fitness_}")
```

### Compare Multiple Algorithms
```python
from mha_toolbox import MHAToolbox
import pandas as pd

toolbox = MHAToolbox()

# Algorithms to compare
algorithms = ['pso', 'gwo', 'woa', 'ga', 'de']

# Run comparisons
results = {}
for algo in algorithms:
    result = toolbox.optimize(
        algo, 
        X=X, 
        y=y,
        population_size=30,
        max_iterations=50
    )
    results[algo] = {
        'fitness': result.best_fitness_,
        'time': result.execution_time_
    }

# Display comparison
df = pd.DataFrame(results).T
print(df.sort_values('fitness'))
```

### Feature Selection
```python
from mha_toolbox import MHAToolbox
from sklearn.datasets import load_breast_cancer

# Load data
X, y = load_breast_cancer(return_X_y=True)

toolbox = MHAToolbox()

# Feature selection task
result = toolbox.optimize(
    algorithm='pso',
    X=X,
    y=y,
    task_type='feature_selection',
    n_features_to_select=10,
    population_size=30,
    max_iterations=100
)

# Get selected features
selected_features = result.best_solution_ > 0.5
print(f"Selected {selected_features.sum()} features out of {len(selected_features)}")
print(f"Feature indices: {np.where(selected_features)[0]}")

# Use selected features
X_selected = X[:, selected_features]
print(f"Original shape: {X.shape}")
print(f"Selected shape: {X_selected.shape}")
```

---

## 🖥️ Command-Line Interface

### Basic Usage
```bash
# Show help
mha-flow-cli --help

# List all algorithms
mha-flow-cli list-algorithms

# List by category
mha-flow-cli list-algorithms --category swarm

# Run optimization
mha-flow-cli optimize --algorithm pso --dataset iris --iterations 100

# Compare algorithms
mha-flow-cli compare --algorithms pso,gwo,woa --dataset wine

# Get recommendations
mha-flow-cli recommend --dataset breast_cancer
```

### Advanced CLI Usage
```bash
# Custom dataset
mha-flow-cli optimize \
    --algorithm pso \
    --file data.csv \
    --target target_column \
    --iterations 100 \
    --population 30 \
    --runs 5

# Export results
mha-flow-cli optimize \
    --algorithm gwo \
    --dataset iris \
    --export results.json \
    --format json

# Batch processing
mha-flow-cli batch \
    --config batch_config.yaml \
    --output results/
```

---

## 📊 Available Features

### Optimization Tasks
- **Feature Selection**: Select optimal subset of features
- **Feature Optimization**: Optimize feature weights
- **Hyperparameter Tuning**: Tune ML model parameters

### Algorithm Categories (130+ Total)
- 🐝 Swarm Intelligence (PSO, GWO, WOA, ACO, ABC, etc.)
- 🧬 Evolutionary (GA, DE, ES, EP, etc.)
- 🌡️ Physics-Based (SA, GSA, MVO, HGSO, etc.)
- 🦠 Bio-Inspired (BA, FA, CSA, COA, etc.)
- 🔥 Hybrid Algorithms (PSO_GA, GWO_PSO, etc.)
- 🧠 Human-Based (TLBO, ICA, QSA, etc.)

### Visualizations
- Convergence curves
- Algorithm comparisons
- Feature importance heatmaps
- Box plots with statistics
- Real-time progress tracking

### Export Formats
- CSV
- JSON
- Excel (.xlsx)
- PNG (plots)
- PDF (reports)

---

## 🎯 Usage Examples

### Example 1: Quick Optimization
```python
from mha_toolbox import quick_optimize

result = quick_optimize('pso', 'iris')
print(result)
```

### Example 2: Algorithm Comparison
```python
from mha_toolbox import compare_algorithms

results = compare_algorithms(
    algorithms=['pso', 'gwo', 'woa'],
    dataset='wine',
    n_runs=5
)
print(results.summary())
```

### Example 3: Custom Objective Function
```python
from mha_toolbox import MHAToolbox
import numpy as np

def rosenbrock(x):
    return sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)

toolbox = MHAToolbox()

result = toolbox.optimize(
    algorithm='pso',
    objective_function=rosenbrock,
    dimensions=10,
    lower_bound=-5.0,
    upper_bound=5.0,
    population_size=50,
    max_iterations=200
)

print(f"Best fitness: {result.best_fitness_}")
print(f"Best solution: {result.best_solution_}")
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Set default algorithm
export MHA_DEFAULT_ALGORITHM=pso

# Set default iterations
export MHA_DEFAULT_ITERATIONS=100

# Enable debug mode
export MHA_DEBUG=1
```

### Configuration File (~/.mha-flow/config.yaml)
```yaml
default:
  algorithm: pso
  population_size: 30
  max_iterations: 100
  n_runs: 3

ui:
  theme: dark
  auto_run: false

export:
  default_format: csv
  save_plots: true
```

---

## 🐛 Troubleshooting

### Issue: Command not found
```bash
# Reinstall package
pip install --upgrade --force-reinstall mha-flow

# Check installation
pip show mha-flow

# Verify commands
python -m mha_toolbox.launcher --help
```

### Issue: Import errors
```bash
# Complete reinstall
pip uninstall mha-flow -y
pip install mha-flow[complete]

# Verify imports
python -c "from mha_toolbox import MHAToolbox; print('OK')"
```

### Issue: Streamlit not found
```bash
# Install UI dependencies
pip install mha-flow[ui]

# Or use online interface
mha-flow-web
```

### Issue: Module not found
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or complete installation
pip install mha-flow[complete]
```

---

## 📚 Resources

- **GitHub**: https://github.com/Achyut103040/MHA-Algorithm
- **Online Interface**: https://mha-flow.streamlit.app/
- **PyPI Package**: https://pypi.org/project/mha-flow/
- **Documentation**: Check About page in web interface
- **Migration Guide**: See MIGRATION_GUIDE.md

---

## 💡 Tips & Best Practices

1. **Start with Online Interface**: Try `mha-flow-web` first to explore features
2. **Use AI Recommendations**: Let the recommender analyze your dataset
3. **Multiple Runs**: Run algorithms 3-5 times for statistical significance
4. **Parameter Presets**: Use "Demo", "Standard", or "Thorough" presets
5. **Export Results**: Save results in multiple formats for analysis
6. **Compare Algorithms**: Always compare at least 3-5 algorithms
7. **Feature Selection**: Start with 50% of features, adjust based on results

---

## 🎓 Learning Path

### Beginner
1. Use `mha-flow-web` to explore the interface
2. Try sample datasets (Iris, Wine)
3. Use AI recommendations
4. Run with "Demo (Fast)" preset

### Intermediate
1. Install locally: `pip install mha-flow[ui]`
2. Upload custom datasets
3. Compare multiple algorithms
4. Adjust parameters manually
5. Export and analyze results

### Advanced
1. Use Python library directly
2. Implement custom objective functions
3. Create hybrid algorithms
4. Use CLI for batch processing
5. Integrate into ML pipelines

---

**Happy Optimizing! 🚀**

MHA Flow makes metaheuristic optimization accessible to everyone, from beginners to experts.
