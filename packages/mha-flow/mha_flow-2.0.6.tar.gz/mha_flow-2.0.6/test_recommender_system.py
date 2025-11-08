"""
Test Script for Algorithm Recommender System
=============================================
Tests the AI-powered algorithm recommendation system with different datasets
"""

import numpy as np
from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_digits
from sklearn.datasets import make_classification
from mha_toolbox.algorithm_recommender import AlgorithmRecommender

def test_recommender_with_dataset(dataset_name, X, y):
    """Test recommender with a specific dataset"""
    print(f"\n{'='*70}")
    print(f"Testing with {dataset_name}")
    print(f"{'='*70}")
    
    recommender = AlgorithmRecommender()
    
    # Analyze dataset
    characteristics = recommender.analyze_dataset(X, y)
    
    print(f"\n📊 Dataset Characteristics:")
    print(f"   Samples: {characteristics['n_samples']}")
    print(f"   Features: {characteristics['n_features']}")
    print(f"   Dimensionality: {characteristics['dimensionality'].upper()}")
    print(f"   Sample Size: {characteristics['sample_size'].replace('_', ' ').title()}")
    print(f"   Data Type: {characteristics['data_type'].replace('_', ' ').title()}")
    print(f"   Complexity: {characteristics['complexity'].title()}")
    print(f"   Has Noise: {'Yes' if characteristics['has_noise'] else 'No'}")
    
    if 'task_type' in characteristics:
        print(f"   Task Type: {characteristics['task_type'].title()}")
    if 'class_balance' in characteristics:
        print(f"   Class Balance: {characteristics['class_balance'].replace('_', ' ').title()}")
    
    # Get top 10 recommendations
    recommendations = recommender.recommend_algorithms(X, y, top_k=10)
    
    print(f"\n🎯 Top 10 Recommended Algorithms:")
    print(f"{'Rank':<6} {'Algorithm':<20} {'Confidence':<12} {'Reason'}")
    print(f"{'-'*90}")
    
    for idx, (algo_name, confidence, reason) in enumerate(recommendations, 1):
        print(f"#{idx:<5} {algo_name.upper():<20} {confidence:.2f}/10      {reason[:50]}...")
    
    return characteristics, recommendations


def main():
    """Run tests with multiple datasets"""
    print("\n" + "="*70)
    print(" ALGORITHM RECOMMENDER SYSTEM - COMPREHENSIVE TEST")
    print("="*70)
    
    # Test 1: Iris Dataset (Low-dimensional, Balanced)
    data = load_iris()
    test_recommender_with_dataset("Iris Dataset", data.data, data.target)
    
    # Test 2: Wine Dataset (Medium-dimensional)
    data = load_wine()
    test_recommender_with_dataset("Wine Dataset", data.data, data.target)
    
    # Test 3: Breast Cancer (High-dimensional)
    data = load_breast_cancer()
    test_recommender_with_dataset("Breast Cancer Dataset", data.data, data.target)
    
    # Test 4: Digits (Very High-dimensional)
    data = load_digits()
    test_recommender_with_dataset("Digits Dataset", data.data, data.target)
    
    # Test 5: Generated Complex Dataset
    X, y = make_classification(
        n_samples=500,
        n_features=50,
        n_informative=35,
        n_redundant=10,
        n_classes=3,
        random_state=42
    )
    test_recommender_with_dataset("Generated Complex Dataset (50 features, 3 classes)", X, y)
    
    # Test 6: Generated Very High-dimensional Dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=100,
        n_informative=70,
        n_redundant=20,
        n_classes=2,
        random_state=42
    )
    test_recommender_with_dataset("Generated High-Dimensional Dataset (100 features)", X, y)
    
    print(f"\n{'='*70}")
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print(f"{'='*70}\n")
    
    # Test algorithm profiles
    print("\n📋 Testing Algorithm Profile Coverage:")
    recommender = AlgorithmRecommender()
    total_algorithms = len(recommender.algorithm_profiles)
    print(f"   Total Algorithms in Profile: {total_algorithms}")
    
    categories = {}
    for algo_name, profile in recommender.algorithm_profiles.items():
        category = profile.get('category', 'uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(algo_name)
    
    print(f"\n   By Category:")
    for category, algos in sorted(categories.items()):
        print(f"      {category.upper()}: {len(algos)} algorithms")
        print(f"         {', '.join([a.upper() for a in algos[:5]])}{'...' if len(algos) > 5 else ''}")
    
    print(f"\n✅ Recommender System is fully operational with {total_algorithms} algorithms!")


if __name__ == "__main__":
    main()
