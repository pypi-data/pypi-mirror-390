"""
Dataset utilities for the MHA Toolbox.

This module provides easy access to built-in datasets for testing and 
experimentation with metaheuristic algorithms.
"""

import numpy as np
import os
import pandas as pd
from sklearn.datasets import (
    load_iris, load_wine, load_breast_cancer, load_digits,
    make_classification, make_regression, make_blobs
)

def load_dataset(dataset_name, return_type='tuple'):
    """
    Load a built-in dataset for testing algorithms.
    
    Parameters
    ----------
    dataset_name : str
        Name of the dataset to load
    return_type : str, default='tuple'
        'tuple' returns (X, y), 'dict' returns {'data': X, 'target': y, 'info': ...}
    
    Returns
    -------
    tuple or dict
        Dataset depending on return_type
        
    Available Datasets
    ------------------
    Scientific datasets:
    - 'iris': Iris flower classification (150 samples, 4 features, 3 classes)
    - 'wine': Wine classification (178 samples, 13 features, 3 classes) 
    - 'breast_cancer': Breast cancer classification (569 samples, 30 features, 2 classes)
    - 'digits': Handwritten digits (1797 samples, 64 features, 10 classes)
    
    Synthetic datasets:
    - 'classification_easy': Easy classification problem
    - 'classification_hard': Difficult classification problem
    - 'regression_linear': Linear regression problem
    - 'regression_nonlinear': Nonlinear regression problem
    - 'clustering': Clustering problem
    
    Feature selection datasets (from project folder):
    - 'heart': Heart disease dataset
    - 'ionosphere': Ionosphere dataset  
    - 'sonar': Sonar dataset
    - 'votes': Congressional voting records
    - 'wine_quality': Wine quality dataset
    - 'zoo': Zoo animals dataset
    """
    
    # Scientific datasets from sklearn
    sklearn_datasets = {
        'iris': load_iris,
        'wine': load_wine,
        'breast_cancer': load_breast_cancer,
        'digits': load_digits
    }
    
    if dataset_name in sklearn_datasets:
        data = sklearn_datasets[dataset_name]()
        if return_type == 'tuple':
            return data.data, data.target
        else:
            return {
                'data': data.data,
                'target': data.target,
                'feature_names': data.feature_names,
                'target_names': data.target_names,
                'description': data.DESCR
            }
    
    # Synthetic datasets
    elif dataset_name == 'classification_easy':
        X, y = make_classification(n_samples=200, n_features=10, n_informative=8,
                                 n_redundant=2, n_clusters_per_class=1, random_state=42)
        info = "Easy classification problem with 200 samples and 10 features"
    
    elif dataset_name == 'classification_hard':
        X, y = make_classification(n_samples=500, n_features=50, n_informative=20,
                                 n_redundant=10, n_clusters_per_class=2, random_state=42)
        info = "Challenging classification problem with 500 samples and 50 features"
        
    elif dataset_name == 'regression_linear':
        X, y = make_regression(n_samples=200, n_features=10, noise=0.1, random_state=42)
        info = "Linear regression problem with 200 samples and 10 features"
        
    elif dataset_name == 'regression_nonlinear':
        X, y = make_regression(n_samples=300, n_features=20, noise=0.1, random_state=42)
        # Add nonlinearity
        y = y + 0.5 * X[:, 0] * X[:, 1] + 0.3 * X[:, 2]**2
        info = "Nonlinear regression problem with 300 samples and 20 features"
        
    elif dataset_name == 'clustering':
        X, y = make_blobs(n_samples=300, centers=4, cluster_std=1.0, random_state=42)
        info = "Clustering problem with 300 samples and 4 natural clusters"
        
    else:
        # Try to load from project datasets folder
        return _load_project_dataset(dataset_name, return_type)
    
    if return_type == 'tuple':
        return X, y
    else:
        return {
            'data': X,
            'target': y,
            'description': info
        }

def _load_project_dataset(dataset_name, return_type='tuple'):
    """Load datasets from the project's dataset folder."""
    
    # Map of dataset names to files in the Feature_selection_metaheuristic_algorithms/dataset folder
    dataset_files = {
        'heart': 'HeartEW.xlsx',
        'ionosphere': 'IonosphereEW.xlsx', 
        'sonar': 'SonarEW.xlsx',
        'votes': 'Votes.xlsx',
        'wine_quality': 'WineEW.xlsx',
        'zoo': 'Zoo.xlsx',
        'breast_cancer_orig': 'WBC-Original.xlsx',
        'breast_cancer_diag': 'WBC-Diagnostic.xlsx',
        'tic_tac_toe': 'Tic-tac-toe.xlsx',
        'spect': 'Spect.xlsx'
    }
    
    if dataset_name not in dataset_files:
        available = ', '.join(list_datasets())
        raise ValueError(f"Dataset '{dataset_name}' not found. Available datasets: {available}")
    
    # Try to find the dataset file
    possible_paths = [
        f"../Feature_selection_metaheuristic_algorithms/dataset/{dataset_files[dataset_name]}",
        f"./Feature_selection_metaheuristic_algorithms/dataset/{dataset_files[dataset_name]}",
        f"Feature_selection_metaheuristic_algorithms/dataset/{dataset_files[dataset_name]}",
        f"dataset/{dataset_files[dataset_name]}"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if file_path is None:
        # Return a synthetic dataset as fallback
        print(f"Warning: Could not find {dataset_name} file. Returning synthetic classification data.")
        X, y = make_classification(n_samples=200, n_features=20, n_informative=15, 
                                 n_redundant=5, random_state=42)
        if return_type == 'tuple':
            return X, y
        else:
            return {
                'data': X,
                'target': y,
                'description': f"Synthetic data replacing {dataset_name}"
            }
    
    try:
        # Load Excel file
        df = pd.read_excel(file_path)
        
        # Assume last column is target, rest are features
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        
        # Convert target to numeric if it's categorical
        if y.dtype == 'object':
            unique_labels = np.unique(y)
            label_map = {label: i for i, label in enumerate(unique_labels)}
            y = np.array([label_map[label] for label in y])
        
        if return_type == 'tuple':
            return X, y
        else:
            return {
                'data': X,
                'target': y,
                'feature_names': df.columns[:-1].tolist(),
                'target_names': np.unique(y).tolist(),
                'description': f"Dataset loaded from {dataset_files[dataset_name]}"
            }
            
    except Exception as e:
        print(f"Error loading {dataset_name}: {e}")
        # Return synthetic data as fallback
        X, y = make_classification(n_samples=200, n_features=20, random_state=42)
        if return_type == 'tuple':
            return X, y
        else:
            return {'data': X, 'target': y, 'description': f"Synthetic fallback for {dataset_name}"}

def list_datasets():
    """
    List all available datasets.
    
    Returns
    -------
    list
        List of available dataset names
    """
    return [
        # Scientific datasets
        'iris', 'wine', 'breast_cancer', 'digits',
        
        # Synthetic datasets  
        'classification_easy', 'classification_hard',
        'regression_linear', 'regression_nonlinear', 'clustering',
        
        # Project datasets
        'heart', 'ionosphere', 'sonar', 'votes', 'wine_quality', 'zoo',
        'breast_cancer_orig', 'breast_cancer_diag', 'tic_tac_toe', 'spect'
    ]

def load_feature_selection_data(dataset_name='breast_cancer', test_size=0.2, normalize=True):
    """
    Load data specifically prepared for feature selection problems.
    
    Parameters
    ----------
    dataset_name : str, default='breast_cancer'
        Dataset to load
    test_size : float, default=0.2
        Fraction of data to use for testing
    normalize : bool, default=True
        Whether to normalize features
        
    Returns
    -------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    X, y = load_dataset(dataset_name)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Normalize if requested
    if normalize:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test

def get_dataset_info(dataset_name):
    """
    Get detailed information about a dataset.
    
    Parameters
    ----------
    dataset_name : str
        Name of the dataset
        
    Returns
    -------
    dict
        Dataset information including size, features, etc.
    """
    try:
        data_dict = load_dataset(dataset_name, return_type='dict')
        
        info = {
            'name': dataset_name,
            'n_samples': len(data_dict['data']),
            'n_features': data_dict['data'].shape[1],
            'n_classes': len(np.unique(data_dict['target'])),
            'description': data_dict.get('description', 'No description available')
        }
        
        if 'feature_names' in data_dict:
            info['feature_names'] = data_dict['feature_names']
        if 'target_names' in data_dict:
            info['target_names'] = data_dict['target_names']
            
        return info
        
    except Exception as e:
        return {'error': f"Could not load dataset info: {e}"}