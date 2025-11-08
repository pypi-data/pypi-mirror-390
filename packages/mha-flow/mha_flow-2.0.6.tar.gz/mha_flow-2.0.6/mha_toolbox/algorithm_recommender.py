"""
Intelligent Algorithm Recommendation System
===========================================

Suggests optimal algorithms based on dataset characteristics, problem type,
and user preferences. Provides confidence scores and reasoning.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional


class AlgorithmRecommender:
    """
    Intelligent system to recommend optimization algorithms based on dataset characteristics,
    problem type, computational constraints, and historical performance.
    """
    
    def __init__(self):
        self.algorithm_profiles = self._initialize_algorithm_profiles()
        self.hybrid_profiles = self._initialize_hybrid_profiles()
        
    def _initialize_hybrid_profiles(self) -> Dict:
        """Initialize hybrid algorithm profiles"""
        return {
            'PSO_GA_HYBRID': {
                'best_for': ['complex', 'multimodal', 'large_search_space'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium',
                'description': 'Combines PSO exploration with GA exploitation'
            },
            'GWO_PSO_HYBRID': {
                'best_for': ['continuous', 'complex_landscape', 'feature_selection'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_high',
                'complexity': 'medium',
                'description': 'Grey Wolf hunting with particle swarm dynamics'
            },
            'DE_PSO_HYBRID': {
                'best_for': ['high_dimensional', 'continuous', 'numerical'],
                'speed': 'fast',
                'exploration': 'medium',
                'exploitation': 'very_high',
                'dimensions': 'high',
                'complexity': 'low',
                'description': 'Differential Evolution with PSO velocity updates'
            },
            'SA_GA_HYBRID': {
                'best_for': ['combinatorial', 'discrete', 'scheduling'],
                'speed': 'slow',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'high',
                'description': 'Simulated Annealing with genetic operators'
            },
            'ACO_PSO_HYBRID': {
                'best_for': ['graph_problems', 'routing', 'network_optimization'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Ant Colony pheromone with PSO movement'
            },
            'ABC_DE_HYBRID': {
                'best_for': ['numerical_optimization', 'engineering', 'constrained'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium',
                'description': 'Artificial Bee Colony with DE mutation'
            },
            'WOA_GA_HYBRID': {
                'best_for': ['feature_selection', 'classification', 'large_datasets'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_high',
                'complexity': 'low',
                'description': 'Whale Optimization with genetic diversity'
            },
            'BA_PSO_HYBRID': {
                'best_for': ['multimodal', 'complex_landscape', 'real_world'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Bat Algorithm echolocation with PSO'
            },
            'FA_DE_HYBRID': {
                'best_for': ['continuous', 'multimodal', 'clustering'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'medium',
                'description': 'Firefly attraction with DE mutation'
            }
        }
        
    def _initialize_algorithm_profiles(self) -> Dict:
        """
        Define algorithm profiles with their strengths, weaknesses, and use cases.
        Expanded to include ALL available algorithms in the MHA Toolbox.
        """
        return {
            # ===== SWARM INTELLIGENCE ALGORITHMS =====
            'pso': {
                'best_for': ['continuous', 'medium_dim', 'smooth', 'fast_convergence'],
                'speed': 'very_fast',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'very_low',
                'category': 'swarm',
                'description': 'Particle Swarm Optimization - social behavior simulation'
            },
            'gwo': {
                'best_for': ['continuous', 'multimodal', 'complex', 'feature_selection'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'swarm',
                'description': 'Grey Wolf Optimizer - hunting hierarchy'
            },
            'woa': {
                'best_for': ['continuous', 'multimodal', 'exploration', 'large_search_space'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'swarm',
                'description': 'Whale Optimization Algorithm - bubble-net feeding'
            },
            'ssa': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'swarm',
                'description': 'Salp Swarm Algorithm - chain movement'
            },
            'alo': {
                'best_for': ['continuous', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'swarm',
                'description': 'Ant Lion Optimizer - antlion hunting'
            },
            'goa': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'swarm',
                'description': 'Grasshopper Optimization Algorithm'
            },
            'hho': {
                'best_for': ['continuous', 'complex', 'multimodal'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'swarm',
                'description': 'Harris Hawks Optimization - cooperative hunting'
            },
            'sfo': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'swarm',
                'description': 'Sailfish Optimizer'
            },
            'mrfo': {
                'best_for': ['continuous', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'swarm',
                'description': 'Manta Ray Foraging Optimization'
            },
            
            # ===== EVOLUTIONARY ALGORITHMS =====
            'ga': {
                'best_for': ['discrete', 'combinatorial', 'multimodal', 'robust'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'evolutionary',
                'description': 'Genetic Algorithm - evolution-inspired'
            },
            'de': {
                'best_for': ['continuous', 'high_dim', 'complex', 'numerical'],
                'speed': 'fast',
                'exploration': 'medium',
                'exploitation': 'very_high',
                'dimensions': 'medium_to_high',
                'complexity': 'low',
                'category': 'evolutionary',
                'description': 'Differential Evolution - mutation-based'
            },
            'eo': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'evolutionary',
                'description': 'Equilibrium Optimizer'
            },
            'es': {
                'best_for': ['continuous', 'complex', 'numerical'],
                'speed': 'medium',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'evolutionary',
                'description': 'Evolution Strategy'
            },
            'ep': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'medium',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'evolutionary',
                'description': 'Evolutionary Programming'
            },
            
            # ===== PHYSICS-BASED ALGORITHMS =====
            'sca': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'very_low',
                'category': 'physics',
                'description': 'Sine Cosine Algorithm - mathematical functions'
            },
            'sa': {
                'best_for': ['continuous', 'combinatorial', 'simple'],
                'speed': 'slow',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low',
                'complexity': 'very_low',
                'category': 'physics',
                'description': 'Simulated Annealing - thermodynamics'
            },
            'hgso': {
                'best_for': ['continuous', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'physics',
                'description': 'Henry Gas Solubility Optimization'
            },
            'wca': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'physics',
                'description': 'Water Cycle Algorithm'
            },
            'asa': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'physics',
                'description': 'Atom Search Optimization'
            },
            
            # ===== BIO-INSPIRED ALGORITHMS =====
            'ba': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'bio',
                'description': 'Bat Algorithm - echolocation'
            },
            'fa': {
                'best_for': ['continuous', 'multimodal', 'clustering'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'bio',
                'description': 'Firefly Algorithm - light attraction'
            },
            'csa': {
                'best_for': ['continuous', 'multimodal', 'exploration'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'low',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'bio',
                'description': 'Cuckoo Search Algorithm - brood parasitism'
            },
            'coa': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'bio',
                'description': 'Coyote Optimization Algorithm'
            },
            'msa': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'bio',
                'description': 'Moth Search Algorithm'
            },
            'bfo': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'slow',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low',
                'complexity': 'high',
                'category': 'bio',
                'description': 'Bacterial Foraging Optimization'
            },
            'aco': {
                'best_for': ['discrete', 'graph', 'combinatorial'],
                'speed': 'medium',
                'exploration': 'medium',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'bio',
                'description': 'Ant Colony Optimization'
            },
            
            # ===== NOVEL ALGORITHMS =====
            'sma': {
                'best_for': ['continuous', 'complex', 'noisy'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Slime Mould Algorithm'
            },
            'ao': {
                'best_for': ['continuous', 'multimodal', 'complex'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'novel',
                'description': 'Aquila Optimizer'
            },
            'aoa': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'novel',
                'description': 'Arithmetic Optimization Algorithm'
            },
            'cgo': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Chaos Game Optimization'
            },
            'gbo': {
                'best_for': ['continuous', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Gradient-Based Optimizer'
            },
            'ica': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Imperialist Competitive Algorithm'
            },
            'pfa': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Pathfinder Algorithm'
            },
            'qsa': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'novel',
                'description': 'Quantum-based Search Algorithm'
            },
            'spbo': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'high',
                'dimensions': 'low_to_medium',
                'complexity': 'low',
                'category': 'novel',
                'description': 'Student Psychology Based Optimization'
            },
            'tso': {
                'best_for': ['continuous', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Tuna Swarm Optimization'
            },
            'vcs': {
                'best_for': ['continuous', 'multimodal'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'medium',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'novel',
                'description': 'Virus Colony Search'
            },
            
            # ===== HYBRID ALGORITHMS =====
            'gwo_pso_hybrid': {
                'best_for': ['continuous', 'high_dim', 'complex', 'feature_selection'],
                'speed': 'fast',
                'exploration': 'very_high',
                'exploitation': 'very_high',
                'dimensions': 'medium_to_high',
                'complexity': 'medium',
                'category': 'hybrid',
                'description': 'GWO + PSO: Best exploration and exploitation'
            },
            'de_pso_hybrid': {
                'best_for': ['continuous', 'very_high_dim', 'complex'],
                'speed': 'fast',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'high',
                'complexity': 'medium',
                'category': 'hybrid',
                'description': 'DE + PSO: High-dimensional specialist'
            },
            'sa_pso_hybrid': {
                'best_for': ['continuous', 'noisy', 'complex'],
                'speed': 'medium',
                'exploration': 'high',
                'exploitation': 'very_high',
                'dimensions': 'low_to_medium',
                'complexity': 'medium',
                'category': 'hybrid',
                'description': 'SA + PSO: Robust to noise'
            },
            'aco_pso_hybrid': {
                'best_for': ['mixed', 'complex', 'multimodal'],
                'speed': 'medium',
                'exploration': 'very_high',
                'exploitation': 'high',
                'dimensions': 'medium',
                'complexity': 'high',
                'category': 'hybrid',
                'description': 'ACO + PSO: Graph and continuous problems'
            },
        }
    
    def analyze_dataset(self, X: np.ndarray, y: np.ndarray = None) -> Dict:
        """
        Analyze dataset characteristics
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray, optional
            Target vector
            
        Returns
        -------
        Dict
            Dataset characteristics
        """
        n_samples, n_features = X.shape
        
        characteristics = {
            'n_samples': n_samples,
            'n_features': n_features,
            'sample_size': self._categorize_size(n_samples),
            'dimensionality': self._categorize_dimensions(n_features),
            'complexity': self._estimate_complexity(X),
            'data_type': self._determine_data_type(X),
            'feature_correlation': self._check_correlation(X),
            'has_noise': self._detect_noise(X),
        }
        
        if y is not None:
            characteristics['task_type'] = self._determine_task_type(y)
            characteristics['class_balance'] = self._check_class_balance(y)
        
        return characteristics
    
    def _categorize_size(self, n_samples: int) -> str:
        """Categorize dataset size"""
        if n_samples < 100:
            return 'small'
        elif n_samples < 1000:
            return 'medium'
        elif n_samples < 10000:
            return 'large'
        else:
            return 'very_large'
    
    def _categorize_dimensions(self, n_features: int) -> str:
        """Categorize dimensionality"""
        if n_features <= 10:
            return 'low'
        elif n_features <= 50:
            return 'medium'
        elif n_features <= 200:
            return 'high'
        else:
            return 'very_high'
    
    def _estimate_complexity(self, X: np.ndarray) -> str:
        """Estimate problem complexity"""
        # Use feature variance and correlation as complexity indicators
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        variance = np.var(X_scaled, axis=0).mean()
        
        if variance < 0.5:
            return 'simple'
        elif variance < 1.5:
            return 'medium'
        else:
            return 'complex'
    
    def _determine_data_type(self, X: np.ndarray) -> str:
        """Determine if data is continuous or discrete"""
        # Check if data is mostly integer-like
        is_integer = np.allclose(X, X.astype(int), rtol=1e-5)
        unique_ratio = len(np.unique(X)) / X.size
        
        if is_integer and unique_ratio < 0.1:
            return 'discrete'
        else:
            return 'continuous'
    
    def _check_correlation(self, X: np.ndarray) -> str:
        """Check feature correlation"""
        if X.shape[1] < 2:
            return 'none'
        
        corr_matrix = np.corrcoef(X.T)
        avg_corr = np.mean(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        
        if avg_corr < 0.3:
            return 'low'
        elif avg_corr < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _detect_noise(self, X: np.ndarray) -> bool:
        """Simple noise detection"""
        # Check for outliers using IQR method
        Q1 = np.percentile(X, 25, axis=0)
        Q3 = np.percentile(X, 75, axis=0)
        IQR = Q3 - Q1
        outliers = ((X < (Q1 - 1.5 * IQR)) | (X > (Q3 + 1.5 * IQR))).sum()
        outlier_ratio = outliers / X.size
        
        return outlier_ratio > 0.05
    
    def _determine_task_type(self, y: np.ndarray) -> str:
        """Determine if classification or regression"""
        unique_values = len(np.unique(y))
        if unique_values <= 20:
            return 'classification'
        else:
            return 'regression'
    
    def _check_class_balance(self, y: np.ndarray) -> str:
        """Check class balance for classification"""
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) <= 1:
            return 'single_class'
        
        balance_ratio = counts.min() / counts.max()
        if balance_ratio > 0.8:
            return 'balanced'
        elif balance_ratio > 0.5:
            return 'slightly_imbalanced'
        else:
            return 'imbalanced'
    
    def recommend_algorithms(self, X: np.ndarray, y: np.ndarray = None, 
                           top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Recommend top-k algorithms for the given dataset
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray, optional
            Target vector
        top_k : int
            Number of recommendations to return
            
        Returns
        -------
        List[Tuple[str, float, str]]
            List of (algorithm_name, confidence_score, reason) tuples
        """
        characteristics = self.analyze_dataset(X, y)
        scores = {}
        
        for algo_name, profile in self.algorithm_profiles.items():
            base_score = self._calculate_match_score(characteristics, profile)
            
            # Add small random variation (±0.15) to differentiate similar algorithms
            # This prevents clustering and makes rankings more dynamic
            import random
            random_variation = random.uniform(-0.15, 0.15)
            final_score = max(0.0, min(10.0, base_score + random_variation))
            
            scores[algo_name] = final_score
        
        # Sort by score
        sorted_algos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate recommendations with reasons
        recommendations = []
        for algo_name, score in sorted_algos[:top_k]:
            reason = self._generate_recommendation_reason(
                algo_name, characteristics, self.algorithm_profiles[algo_name]
            )
            recommendations.append((algo_name, score, reason))
        
        return recommendations
    
    def _calculate_match_score(self, characteristics: Dict, profile: Dict) -> float:
        """
        Calculate how well an algorithm matches dataset characteristics.
        COMPLETELY REDESIGNED scoring with exponential differentiation.
        """
        score = 0.0
        penalties = 0.0
        max_possible_score = 100.0  # Much higher base for better granularity
        
        # === CRITICAL FACTORS (60 points) ===
        
        # 1. DIMENSIONALITY MATCH (0-25 points) - MOST CRITICAL
        dim_match_map = {
            'low': {
                'low': 25, 'low_to_medium': 20, 'medium': 10, 
                'medium_to_high': 5, 'high': 2, 'very_high': 1, 'low_to_high': 15
            },
            'medium': {
                'low': 8, 'low_to_medium': 18, 'medium': 25, 
                'medium_to_high': 22, 'high': 10, 'very_high': 5, 'low_to_high': 20
            },
            'high': {
                'low': 3, 'low_to_medium': 5, 'medium': 10, 
                'medium_to_high': 22, 'high': 25, 'very_high': 20, 'low_to_high': 23
            },
            'very_high': {
                'low': 1, 'low_to_medium': 2, 'medium': 5, 
                'medium_to_high': 15, 'high': 23, 'very_high': 25, 'low_to_high': 20
            }
        }
        
        data_dim = characteristics['dimensionality']
        algo_dims = profile.get('dimensions', 'medium')
        score += dim_match_map.get(data_dim, {}).get(algo_dims, 5)
        
        # 2. DATA TYPE MATCH (0-20 points)
        data_type = characteristics['data_type']
        best_for = profile.get('best_for', [])
        
        if data_type in best_for:
            score += 20  # Perfect match
        elif 'continuous' in best_for and data_type in ['continuous', 'mixed']:
            score += 15
        elif 'discrete' in best_for and data_type in ['discrete', 'mixed']:
            score += 15
        elif 'mixed' in best_for:
            score += 12  # Flexible
        else:
            score += 5  # Can work but not optimal
            penalties += 3
        
        # 3. COMPLEXITY MATCH (0-15 points)
        complexity = characteristics['complexity']
        exploration = profile.get('exploration', 'medium')
        exploitation = profile.get('exploitation', 'medium')
        
        if complexity == 'complex':
            # Complex problems need strong exploration
            if exploration in ['very_high', 'high']:
                score += 10
            elif exploration == 'medium':
                score += 5
            else:
                score += 2
                penalties += 5
            
            # Also need good exploitation
            if exploitation in ['very_high', 'high']:
                score += 5
            else:
                score += 2
        elif complexity == 'medium':
            # Medium complexity needs balance
            if exploration in ['medium', 'high'] and exploitation in ['medium', 'high']:
                score += 15
            else:
                score += 8
        else:  # simple
            # Simple problems - exploitation more important
            if exploitation in ['high', 'very_high']:
                score += 12
            else:
                score += 8
        
        # === IMPORTANT FACTORS (30 points) ===
        
        # 4. SAMPLE SIZE & SPEED (0-15 points)
        sample_size = characteristics['sample_size']
        speed = profile.get('speed', 'medium')
        
        if sample_size in ['large', 'very_large']:
            # Large datasets NEED fast algorithms
            speed_scores = {
                'very_fast': 15, 'fast': 12, 'medium': 7, 
                'slow': 3, 'very_slow': 1
            }
            score += speed_scores.get(speed, 5)
            if speed in ['slow', 'very_slow']:
                penalties += 8  # Heavy penalty for slow on large data
        elif sample_size in ['small', 'very_small']:
            # Small datasets - speed less critical
            speed_scores = {
                'very_fast': 10, 'fast': 12, 'medium': 15, 
                'slow': 10, 'very_slow': 8
            }
            score += speed_scores.get(speed, 10)
        else:  # medium
            speed_scores = {
                'very_fast': 12, 'fast': 15, 'medium': 14, 
                'slow': 8, 'very_slow': 4
            }
            score += speed_scores.get(speed, 10)
        
        # 5. NOISE ROBUSTNESS (0-10 points)
        has_noise = characteristics.get('has_noise', False)
        if has_noise:
            # Noisy data needs strong exploitation & noise handling
            if exploitation in ['very_high', 'high']:
                score += 10
            elif exploitation == 'medium':
                score += 5
            else:
                score += 2
                penalties += 5
        else:
            # Clean data - less critical
            score += 7
        
        # 6. FEATURE CORRELATION (0-5 points)
        correlation = characteristics.get('correlation', 'medium')
        if correlation == 'high' and 'correlated_features' in best_for:
            score += 5
        else:
            score += 3
        
        # === BONUS FACTORS (10 points max) ===
        
        # Hybrid bonus for complex problems
        if profile.get('category') == 'hybrid' and complexity == 'complex':
            score += 5
        
        # Feature selection specialist
        if 'feature_selection' in best_for:
            score += 3
        
        # High-dim specialist bonus
        if data_dim in ['high', 'very_high'] and 'high_dim' in best_for:
            score += 5
        
        # Multimodal specialist for complex problems
        if 'multimodal' in best_for and complexity == 'complex':
            score += 4
        
        # === PENALTIES ===
        score -= penalties
        
        # === NORMALIZATION WITH EXPONENTIAL SCALING ===
        # This creates much better separation between good and bad matches
        
        # First normalize to 0-1 range
        normalized = max(0, score) / max_possible_score
        
        # Apply exponential curve to increase differentiation
        # Good matches (>0.7) get boosted, poor matches (<0.5) get penalized
        if normalized > 0.7:
            # Top performers: scale 0.7-1.0 to 8.0-10.0
            final_score = 8.0 + (normalized - 0.7) * (2.0 / 0.3)
        elif normalized > 0.5:
            # Good performers: scale 0.5-0.7 to 6.0-8.0
            final_score = 6.0 + (normalized - 0.5) * (2.0 / 0.2)
        elif normalized > 0.3:
            # Average performers: scale 0.3-0.5 to 4.0-6.0
            final_score = 4.0 + (normalized - 0.3) * (2.0 / 0.2)
        else:
            # Poor performers: scale 0-0.3 to 0-4.0
            final_score = normalized * (4.0 / 0.3)
        
        # Clamp to 0-10 range
        return min(10.0, max(0.0, final_score))
    
    def _generate_recommendation_reason(self, algo_name: str, 
                                       characteristics: Dict, 
                                       profile: Dict) -> str:
        """Generate detailed human-readable recommendation reason"""
        reasons = []
        
        # Dimensionality
        dim = characteristics['dimensionality']
        if dim in ['high', 'very_high'] and profile['dimensions'] in ['high', 'very_high', 'medium_to_high']:
            reasons.append(f"Excellent for {dim}-dimensional data")
        elif dim in ['low', 'medium']:
            reasons.append(f"Well-suited for {dim}-dimensional problems")
        
        # Data type
        data_type = characteristics['data_type']
        if data_type in profile['best_for']:
            reasons.append(f"Optimized for {data_type} optimization")
        
        # Complexity
        complexity = characteristics['complexity']
        if complexity == 'complex':
            if profile['exploration'] in ['high', 'very_high']:
                reasons.append("Strong exploration for complex landscapes")
            if profile['exploitation'] in ['high', 'very_high']:
                reasons.append("Effective exploitation capabilities")
        
        # Speed
        if profile['speed'] in ['fast', 'very_fast']:
            reasons.append("Fast convergence")
        
        # Noise handling
        if characteristics.get('has_noise', False) and profile['exploitation'] in ['high', 'very_high']:
            reasons.append("Robust to noisy data")
        
        # Special features
        if 'feature_selection' in profile.get('best_for', []):
            reasons.append("Excellent for feature selection")
        
        if profile.get('category') == 'hybrid':
            reasons.append("Hybrid approach combines multiple strategies")
        
        # Default reason if none matched
        if not reasons:
            reasons.append("Reliable general-purpose optimizer")
        
        return "; ".join(reasons)
    
    def get_recommended_parameters(self, algo_name: str, 
                                  characteristics: Dict) -> Dict:
        """
        Get recommended hyperparameters for an algorithm based on dataset
        
        Parameters
        ----------
        algo_name : str
            Algorithm name
        characteristics : Dict
            Dataset characteristics
            
        Returns
        -------
        Dict
            Recommended hyperparameters
        """
        # Base parameters
        params = {
            'pop_size': 50,
            'max_iter': 100
        }
        
        # Adjust based on dataset size
        if characteristics['n_samples'] > 1000:
            params['pop_size'] = 30
            params['max_iter'] = 150
        elif characteristics['n_samples'] < 100:
            params['pop_size'] = 20
            params['max_iter'] = 200
        
        # Adjust based on dimensionality
        if characteristics['dimensionality'] in ['high', 'very_high']:
            params['pop_size'] = min(100, characteristics['n_features'] * 10)
            params['max_iter'] = 200
        
        return params
