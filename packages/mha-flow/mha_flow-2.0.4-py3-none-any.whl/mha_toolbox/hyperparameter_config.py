"""
Dynamic Hyperparameter Configuration
=====================================

Provides dimension-aware hyperparameter bounds and intelligent defaults.
"""

import numpy as np
from typing import Dict, Tuple, Any


class HyperparameterManager:
    """Manages hyperparameters with dimension-aware bounds."""
    
    def __init__(self, dimensions: int, problem_type: str = "continuous"):
        self.dimensions = dimensions
        self.problem_type = problem_type
        
    def get_parameter_bounds(self, algorithm: str) -> Dict[str, Dict[str, Any]]:
        """
        Get hyperparameter bounds for an algorithm based on problem dimensions.
        
        Returns dict with structure:
        {
            'param_name': {
                'default': value,
                'min': min_value,
                'max': max_value,
                'type': 'int'/'float'/'bool',
                'description': 'Parameter description',
                'user_adjustable': True/False
            }
        }
        """
        # Base parameters common to most algorithms
        base_params = {
            'population_size': {
                'default': max(30, min(100, self.dimensions * 5)),
                'min': max(10, self.dimensions * 2),
                'max': min(200, self.dimensions * 20),
                'type': 'int',
                'description': 'Number of search agents',
                'user_adjustable': True,
                'scales_with_dimensions': True
            },
            'max_iterations': {
                'default': max(100, self.dimensions * 10),
                'min': 50,
                'max': 1000,
                'type': 'int',
                'description': 'Maximum number of iterations',
                'user_adjustable': True,
                'scales_with_dimensions': True
            }
        }
        
        # Algorithm-specific parameters
        algo_specific = self._get_algorithm_specific_params(algorithm.lower())
        
        return {**base_params, **algo_specific}
    
    def _get_algorithm_specific_params(self, algorithm: str) -> Dict:
        """Get algorithm-specific hyperparameters."""
        
        params_map = {
            'pso': {
                'w': {
                    'default': 0.7,
                    'min': 0.4,
                    'max': 0.9,
                    'type': 'float',
                    'description': 'Inertia weight (controls exploration/exploitation)',
                    'user_adjustable': True
                },
                'c1': {
                    'default': 1.5,
                    'min': 0.5,
                    'max': 3.0,
                    'type': 'float',
                    'description': 'Cognitive coefficient (personal best influence)',
                    'user_adjustable': True
                },
                'c2': {
                    'default': 1.5,
                    'min': 0.5,
                    'max': 3.0,
                    'type': 'float',
                    'description': 'Social coefficient (global best influence)',
                    'user_adjustable': True
                }
            },
            
            'ga': {
                'crossover_rate': {
                    'default': 0.8,
                    'min': 0.5,
                    'max': 0.95,
                    'type': 'float',
                    'description': 'Probability of crossover operation',
                    'user_adjustable': True
                },
                'mutation_rate': {
                    'default': 0.1,
                    'min': 0.01,
                    'max': 0.3,
                    'type': 'float',
                    'description': 'Probability of mutation operation',
                    'user_adjustable': True
                },
                'elite_ratio': {
                    'default': 0.1,
                    'min': 0.0,
                    'max': 0.3,
                    'type': 'float',
                    'description': 'Ratio of elite individuals to preserve',
                    'user_adjustable': True
                }
            },
            
            'de': {
                'F': {
                    'default': 0.8,
                    'min': 0.4,
                    'max': 1.0,
                    'type': 'float',
                    'description': 'Differential weight (scaling factor)',
                    'user_adjustable': True
                },
                'CR': {
                    'default': 0.9,
                    'min': 0.5,
                    'max': 1.0,
                    'type': 'float',
                    'description': 'Crossover probability',
                    'user_adjustable': True
                }
            },
            
            'gwo': {
                'a_min': {
                    'default': 0.0,
                    'min': 0.0,
                    'max': 1.0,
                    'type': 'float',
                    'description': 'Minimum value of control parameter',
                    'user_adjustable': False
                },
                'a_max': {
                    'default': 2.0,
                    'min': 1.0,
                    'max': 3.0,
                    'type': 'float',
                    'description': 'Maximum value of control parameter',
                    'user_adjustable': True
                }
            },
            
            'sca': {
                'a': {
                    'default': 2.0,
                    'min': 1.0,
                    'max': 3.0,
                    'type': 'float',
                    'description': 'Control parameter for exploration',
                    'user_adjustable': True
                }
            },
            
            'woa': {
                'a_min': {
                    'default': 0.0,
                    'min': 0.0,
                    'max': 1.0,
                    'type': 'float',
                    'description': 'Minimum value of control parameter',
                    'user_adjustable': False
                },
                'a_max': {
                    'default': 2.0,
                    'min': 1.0,
                    'max': 3.0,
                    'type': 'float',
                    'description': 'Maximum value of control parameter',
                    'user_adjustable': True
                },
                'b': {
                    'default': 1.0,
                    'min': 0.5,
                    'max': 2.0,
                    'type': 'float',
                    'description': 'Spiral shape constant',
                    'user_adjustable': True
                }
            },
            
            'sa': {
                'initial_temp': {
                    'default': 100.0,
                    'min': 50.0,
                    'max': 500.0,
                    'type': 'float',
                    'description': 'Initial temperature',
                    'user_adjustable': True
                },
                'cooling_rate': {
                    'default': 0.95,
                    'min': 0.8,
                    'max': 0.99,
                    'type': 'float',
                    'description': 'Temperature reduction rate per iteration',
                    'user_adjustable': True
                }
            },
            
            'aco': {
                'alpha': {
                    'default': 1.0,
                    'min': 0.5,
                    'max': 2.0,
                    'type': 'float',
                    'description': 'Pheromone importance',
                    'user_adjustable': True
                },
                'beta': {
                    'default': 2.0,
                    'min': 1.0,
                    'max': 5.0,
                    'type': 'float',
                    'description': 'Heuristic importance',
                    'user_adjustable': True
                },
                'evaporation': {
                    'default': 0.5,
                    'min': 0.1,
                    'max': 0.9,
                    'type': 'float',
                    'description': 'Pheromone evaporation rate',
                    'user_adjustable': True
                }
            },
            
            # Hybrid algorithms
            'pso_ga_hybrid': {
                'w': {'default': 0.7, 'min': 0.4, 'max': 0.9, 'type': 'float', 
                      'description': 'PSO inertia weight', 'user_adjustable': True},
                'c1': {'default': 1.5, 'min': 0.5, 'max': 3.0, 'type': 'float',
                       'description': 'PSO cognitive coefficient', 'user_adjustable': True},
                'c2': {'default': 1.5, 'min': 0.5, 'max': 3.0, 'type': 'float',
                       'description': 'PSO social coefficient', 'user_adjustable': True},
                'crossover_rate': {'default': 0.8, 'min': 0.5, 'max': 0.95, 'type': 'float',
                                  'description': 'GA crossover rate', 'user_adjustable': True},
                'mutation_rate': {'default': 0.1, 'min': 0.01, 'max': 0.3, 'type': 'float',
                                 'description': 'GA mutation rate', 'user_adjustable': True}
            }
        }
        
        return params_map.get(algorithm, {})
    
    def adjust_for_dimensions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust parameter ranges based on problem dimensions."""
        adjusted = params.copy()
        
        for param_name, param_info in adjusted.items():
            if param_info.get('scales_with_dimensions', False):
                # Adjust population size based on dimensions
                if param_name == 'population_size':
                    param_info['default'] = max(30, min(100, self.dimensions * 5))
                    param_info['min'] = max(10, self.dimensions * 2)
                    param_info['max'] = min(200, self.dimensions * 20)
                
                # Adjust iterations based on dimensions
                elif param_name == 'max_iterations':
                    param_info['default'] = max(100, self.dimensions * 10)
                    param_info['min'] = 50
                    param_info['max'] = min(1000, self.dimensions * 50)
        
        return adjusted
    
    def validate_parameters(self, algorithm: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate user-provided parameters."""
        bounds = self.get_parameter_bounds(algorithm)
        
        for param_name, value in params.items():
            if param_name not in bounds:
                return False, f"Unknown parameter: {param_name}"
            
            param_info = bounds[param_name]
            
            # Type check
            if param_info['type'] == 'int' and not isinstance(value, int):
                return False, f"{param_name} must be an integer"
            elif param_info['type'] == 'float' and not isinstance(value, (int, float)):
                return False, f"{param_name} must be a number"
            
            # Range check
            if 'min' in param_info and value < param_info['min']:
                return False, f"{param_name} must be >= {param_info['min']}"
            if 'max' in param_info and value > param_info['max']:
                return False, f"{param_name} must be <= {param_info['max']}"
        
        return True, "Valid"
    
    def get_default_parameters(self, algorithm: str) -> Dict[str, Any]:
        """Get default parameters for an algorithm."""
        bounds = self.get_parameter_bounds(algorithm)
        return {name: info['default'] for name, info in bounds.items()}
    
    def get_user_adjustable_parameters(self, algorithm: str) -> Dict[str, Dict]:
        """Get only user-adjustable parameters."""
        bounds = self.get_parameter_bounds(algorithm)
        return {
            name: info for name, info in bounds.items()
            if info.get('user_adjustable', True)
        }


# Preset configurations
PRESET_CONFIGS = {
    "fast": {
        "description": "Quick evaluation (low accuracy)",
        "population_multiplier": 0.5,
        "iteration_multiplier": 0.3,
        "n_runs": 1
    },
    "standard": {
        "description": "Balanced performance (recommended)",
        "population_multiplier": 1.0,
        "iteration_multiplier": 1.0,
        "n_runs": 3
    },
    "thorough": {
        "description": "Comprehensive search (high accuracy)",
        "population_multiplier": 1.5,
        "iteration_multiplier": 2.0,
        "n_runs": 5
    },
    "research": {
        "description": "Publication-quality results",
        "population_multiplier": 2.0,
        "iteration_multiplier": 3.0,
        "n_runs": 10
    }
}


def get_preset_config(preset_name: str, dimensions: int) -> Dict[str, Any]:
    """Get preset configuration adjusted for dimensions."""
    if preset_name not in PRESET_CONFIGS:
        preset_name = "standard"
    
    config = PRESET_CONFIGS[preset_name]
    
    base_pop = max(30, min(100, dimensions * 5))
    base_iter = max(100, dimensions * 10)
    
    return {
        "population_size": int(base_pop * config["population_multiplier"]),
        "max_iterations": int(base_iter * config["iteration_multiplier"]),
        "n_runs": config["n_runs"],
        "description": config["description"]
    }
