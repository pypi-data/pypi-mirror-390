"""
Data preprocessing utilities for the MHA Toolbox.

This module provides functions for preprocessing data before optimization,
including normalization, scaling, and splitting.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Tuple, Optional, Union

def preprocess_data(X, y=None, 
                   normalize: bool = True,
                   scaler_type: str = 'standard',
                   handle_categorical: bool = True,
                   remove_outliers: bool = False):
    """
    Preprocess data for optimization algorithms.
    
    Parameters
    ----------
    X : array-like
        Feature matrix
    y : array-like, optional
        Target values
    normalize : bool, default=True
        Whether to normalize features
    scaler_type : str, default='standard'
        Type of scaler: 'standard', 'minmax', or 'none'
    handle_categorical : bool, default=True
        Whether to encode categorical variables
    remove_outliers : bool, default=False
        Whether to remove outliers using IQR method
        
    Returns
    -------
    tuple
        (X_processed, y_processed, scaler, label_encoder)
    """
    
    X_processed = np.array(X, copy=True)
    y_processed = np.array(y, copy=True) if y is not None else None
    scaler = None
    label_encoder = None
    
    # Handle categorical target variables
    if y_processed is not None and handle_categorical:
        if y_processed.dtype == 'object' or len(np.unique(y_processed)) < 10:
            label_encoder = LabelEncoder()
            y_processed = label_encoder.fit_transform(y_processed)
    
    # Remove outliers if requested
    if remove_outliers:
        X_processed = _remove_outliers(X_processed)
    
    # Normalize features
    if normalize and scaler_type != 'none':
        if scaler_type == 'standard':
            scaler = StandardScaler()
        elif scaler_type == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("scaler_type must be 'standard', 'minmax', or 'none'")
        
        X_processed = scaler.fit_transform(X_processed)
    
    return X_processed, y_processed, scaler, label_encoder

def normalize_data(X, method='standard'):
    """
    Normalize data using specified method.
    
    Parameters
    ----------
    X : array-like
        Data to normalize
    method : str, default='standard'
        Normalization method: 'standard', 'minmax', or 'robust'
        
    Returns
    -------
    tuple
        (X_normalized, scaler)
    """
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'robust':
        from sklearn.preprocessing import RobustScaler
        scaler = RobustScaler()
    else:
        raise ValueError("method must be 'standard', 'minmax', or 'robust'")
    
    X_normalized = scaler.fit_transform(X)
    return X_normalized, scaler

def split_data(X, y, test_size=0.2, random_state=42, stratify=True):
    """
    Split data into training and testing sets.
    
    Parameters
    ----------
    X : array-like
        Feature matrix
    y : array-like
        Target values
    test_size : float, default=0.2
        Fraction of data for testing
    random_state : int, default=42
        Random state for reproducibility
    stratify : bool, default=True
        Whether to stratify the split
        
    Returns
    -------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    
    stratify_param = y if stratify and len(np.unique(y)) > 1 else None
    
    return train_test_split(X, y, test_size=test_size, 
                          random_state=random_state, 
                          stratify=stratify_param)

def _remove_outliers(X, method='iqr', threshold=1.5):
    """
    Remove outliers from data using specified method.
    
    Parameters
    ----------
    X : array-like
        Input data
    method : str, default='iqr'
        Outlier detection method: 'iqr' or 'zscore'
    threshold : float, default=1.5
        Threshold for outlier detection
        
    Returns
    -------
    array-like
        Data with outliers removed
    """
    
    X_clean = np.array(X, copy=True)
    
    if method == 'iqr':
        # Interquartile Range method
        Q1 = np.percentile(X_clean, 25, axis=0)
        Q3 = np.percentile(X_clean, 75, axis=0)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        # Remove outliers
        mask = np.all((X_clean >= lower_bound) & (X_clean <= upper_bound), axis=1)
        X_clean = X_clean[mask]
        
    elif method == 'zscore':
        # Z-score method
        from scipy import stats
        z_scores = np.abs(stats.zscore(X_clean))
        mask = np.all(z_scores < threshold, axis=1)
        X_clean = X_clean[mask]
    
    return X_clean

def balance_data(X, y, method='smote'):
    """
    Balance imbalanced datasets.
    
    Parameters
    ----------
    X : array-like
        Feature matrix
    y : array-like
        Target values
    method : str, default='smote'
        Balancing method: 'smote', 'random_oversample', or 'random_undersample'
        
    Returns
    -------
    tuple
        (X_balanced, y_balanced)
    """
    
    try:
        if method == 'smote':
            from imblearn.over_sampling import SMOTE
            sampler = SMOTE(random_state=42)
        elif method == 'random_oversample':
            from imblearn.over_sampling import RandomOverSampler
            sampler = RandomOverSampler(random_state=42)
        elif method == 'random_undersample':
            from imblearn.under_sampling import RandomUnderSampler
            sampler = RandomUnderSampler(random_state=42)
        else:
            raise ValueError("method must be 'smote', 'random_oversample', or 'random_undersample'")
        
        X_balanced, y_balanced = sampler.fit_resample(X, y)
        return X_balanced, y_balanced
        
    except ImportError:
        print("Warning: imbalanced-learn not installed. Returning original data.")
        return X, y

def feature_statistics(X, feature_names=None):
    """
    Calculate comprehensive statistics for features.
    
    Parameters
    ----------
    X : array-like
        Feature matrix
    feature_names : list, optional
        Names of features
        
    Returns
    -------
    dict
        Dictionary containing feature statistics
    """
    
    if feature_names is None:
        feature_names = [f'Feature_{i}' for i in range(X.shape[1])]
    
    stats = {}
    
    for i, name in enumerate(feature_names):
        feature_data = X[:, i]
        stats[name] = {
            'mean': np.mean(feature_data),
            'std': np.std(feature_data),
            'min': np.min(feature_data),
            'max': np.max(feature_data),
            'median': np.median(feature_data),
            'q25': np.percentile(feature_data, 25),
            'q75': np.percentile(feature_data, 75),
            'missing_count': np.sum(np.isnan(feature_data)),
            'unique_count': len(np.unique(feature_data))
        }
    
    return stats

def detect_feature_types(X, threshold_unique=10):
    """
    Automatically detect feature types.
    
    Parameters
    ----------
    X : array-like
        Feature matrix
    threshold_unique : int, default=10
        Threshold for categorical vs numerical classification
        
    Returns
    -------
    dict
        Dictionary mapping feature indices to types
    """
    
    feature_types = {}
    
    for i in range(X.shape[1]):
        feature_data = X[:, i]
        n_unique = len(np.unique(feature_data))
        
        if n_unique <= threshold_unique:
            feature_types[i] = 'categorical'
        elif np.all(feature_data == feature_data.astype(int)):
            feature_types[i] = 'integer'
        else:
            feature_types[i] = 'continuous'
    
    return feature_types