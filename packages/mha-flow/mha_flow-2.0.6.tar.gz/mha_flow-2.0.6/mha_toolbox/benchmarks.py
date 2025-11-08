import numpy as np

def sphere(solution):
    """Sphere function: f(x) = sum(x_i^2)"""
    return np.sum(np.square(solution))

def rastrigin(solution):
    """Rastrigin function: f(x) = A*n + sum(x_i^2 - A*cos(2*pi*x_i))"""
    A = 10
    n = len(solution)
    return A * n + np.sum(solution**2 - A * np.cos(2 * np.pi * solution))

def rosenbrock(solution):
    """Rosenbrock function: f(x) = sum(100*(x_{i+1} - x_i^2)^2 + (1 - x_i)^2)"""
    return np.sum(100.0 * (solution[1:] - solution[:-1]**2)**2 + (1 - solution[:-1])**2)

def ackley(solution):
    """Ackley function"""
    a = 20
    b = 0.2
    c = 2 * np.pi
    n = len(solution)
    
    sum1 = np.sum(solution**2)
    sum2 = np.sum(np.cos(c * solution))
    
    term1 = -a * np.exp(-b * np.sqrt(sum1 / n))
    term2 = -np.exp(sum2 / n)
    
    return term1 + term2 + a + np.exp(1)

def griewank(solution):
    """Griewank function"""
    sum_term = np.sum(solution**2) / 4000
    prod_term = np.prod(np.cos(solution / np.sqrt(np.arange(1, len(solution) + 1))))
    return sum_term - prod_term + 1
