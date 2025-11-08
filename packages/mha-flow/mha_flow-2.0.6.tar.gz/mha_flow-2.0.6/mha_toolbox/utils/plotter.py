import matplotlib.pyplot as plt
import numpy as np

def plot_convergence(model, title='Convergence Curve'):
    """
    Plot the convergence curve of an optimization run.
    
    This function handles both the new OptimizationModel objects and 
    the older dictionary-style models for backward compatibility.
    
    Parameters
    ----------
    model : OptimizationModel or dict
        The optimization model containing convergence data
    title : str, optional
        Title for the plot
        
    Returns
    -------
    matplotlib.figure.Figure
        The generated figure
    """
    # Handle both dictionary-style models (backward compatibility) and new OptimizationModel objects
    if hasattr(model, 'convergence_curve'):
        convergence_curve = model.convergence_curve
    elif isinstance(model, dict) and 'convergence_curve' in model:
        convergence_curve = model['convergence_curve']
    else:
        raise ValueError("Input 'model' must contain a 'convergence_curve' attribute or key.")
    
    fig = plt.figure(figsize=(10, 6))
    plt.plot(convergence_curve)
    plt.title(title)
    plt.xlabel("Iteration")
    plt.ylabel("Best Fitness")
    plt.grid(True)
    plt.show()
    
    return fig

def plot_solution_space(model, objective_function, dimension_indices=(0, 1), resolution=100, title=None):
    """
    Plot the solution space and the best solution found for a 2D slice of the problem.
    
    This function creates a visualization of the objective function landscape and
    marks the position of the best solution found by the algorithm.
    
    Parameters
    ----------
    model : OptimizationModel or dict
        The optimization model containing the best solution
    objective_function : callable
        The objective function to visualize
    dimension_indices : tuple, optional
        The two dimensions to visualize (default: the first two dimensions)
    resolution : int, optional
        Grid resolution for visualization (default: 100)
    title : str, optional
        Title for the plot
        
    Returns
    -------
    matplotlib.figure.Figure
        The generated figure
    """
    # Handle both dictionary-style models and new OptimizationModel objects
    if hasattr(model, 'best_solution'):
        best_solution = model.best_solution
        lb = model.parameters.get('lower_bound', None) if hasattr(model, 'parameters') else None
        ub = model.parameters.get('upper_bound', None) if hasattr(model, 'parameters') else None
        algorithm_name = model.algorithm_name if hasattr(model, 'algorithm_name') else "Algorithm"
    elif isinstance(model, dict):
        best_solution = model.get('best_solution_continuous', None)
        lb = model.get('lb', None)
        ub = model.get('ub', None)
        algorithm_name = model.get('algorithm_name', "Algorithm")
    else:
        raise ValueError("Invalid model format")
    
    if best_solution is None:
        raise ValueError("Model does not contain a best solution")
    
    # Use default bounds if not available
    if lb is None or ub is None:
        lb = -10
        ub = 10
    
    # Convert scalar bounds to arrays if needed
    if not isinstance(lb, (list, np.ndarray)):
        lb = np.full(len(best_solution), lb)
    if not isinstance(ub, (list, np.ndarray)):
        ub = np.full(len(best_solution), ub)
    
    # Extract the two dimensions to visualize
    d1, d2 = dimension_indices
    
    # Create grid for visualization
    x = np.linspace(lb[d1], ub[d1], resolution)
    y = np.linspace(lb[d2], ub[d2], resolution)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    # Create a base solution (copy of the best solution)
    base_solution = np.copy(best_solution)
    
    # Calculate function values across the grid
    for i in range(resolution):
        for j in range(resolution):
            # Modify only the dimensions we're visualizing
            solution = base_solution.copy()
            solution[d1] = X[i, j]
            solution[d2] = Y[i, j]
            Z[i, j] = objective_function(solution)
    
    # Create plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, edgecolor='none')
    
    # Mark the best solution found
    ax.scatter(best_solution[d1], best_solution[d2], objective_function(best_solution), 
               color='red', s=100, label='Best Solution')
    
    # Set labels and title
    ax.set_xlabel(f'Dimension {d1}')
    ax.set_ylabel(f'Dimension {d2}')
    ax.set_zlabel('Objective Value')
    
    if title is None:
        title = f"{algorithm_name} - Solution Space"
    ax.set_title(title)
    
    # Add a color bar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.legend()
    plt.show()
    
    return fig
