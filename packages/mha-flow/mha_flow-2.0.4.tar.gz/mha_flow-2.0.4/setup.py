"""
Setup script for MHA Flow - Professional Metaheuristic Algorithm Library v2.0.4

Installation modes:
    pip install mha-flow              # Core library only
    pip install mha-flow[ui]          # With web interface
    pip install mha-flow[complete]    # Everything
    pip install mha-flow[dev]         # Development tools

Usage:
    mha-flow                          # Run local web interface
    mha-flow-web                      # Open online web interface
    mha-flow --help                   # Show help
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    """Read long description from README file."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "MHA Flow - Professional Metaheuristic Algorithm Library with 130+ algorithms"

# Read version from __init__.py
def get_version():
    """Extract version from __init__.py"""
    try:
        with open("mha_toolbox/__init__.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "2.0.4"

# Core dependencies (required for library usage)
install_requires = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "matplotlib>=3.4.0",
    "seaborn>=0.11.0",
    "scikit-learn>=1.0.0",
    "scipy>=1.7.0",
    "joblib>=1.1.0",
    "tqdm>=4.62.0",
]

# Optional dependencies for different use cases
extras_require = {
    # Web interface dependencies
    "ui": [
        "streamlit>=1.25.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "flask>=2.0.0",
    ],
    
    # Jupyter notebook support
    "jupyter": [
        "jupyter>=1.0.0",
        "ipython>=7.0.0",
        "notebook>=6.0.0",
        "ipywidgets>=7.6.0",
    ],
    
    # Advanced optimization features
    "advanced": [
        "optuna>=2.10.0",
        "hyperopt>=0.2.5",
        "bayesian-optimization>=1.2.0",
        "scikit-optimize>=0.9.0",
    ],
    
    # Image and visualization export
    "export": [
        "pillow>=9.0.0",
        "openpyxl>=3.0.0",
        "xlsxwriter>=3.0.0",
        "kaleido>=0.2.1",  # For plotly image export
    ],
    
    # System monitoring and optimization
    "system": [
        "wakepy>=0.7.0",
        "psutil>=5.8.0",
        "memory_profiler>=0.60.0",
    ],
    
    # Development tools
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=3.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.950",
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
}

# Complete installation (all features)
extras_require["complete"] = list(set(
    extras_require["ui"] + 
    extras_require["jupyter"] + 
    extras_require["advanced"] + 
    extras_require["export"] + 
    extras_require["system"]
))

# All dependencies (including dev)
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="mha-flow",
    version=get_version(),
    author="MHA Flow Development Team",
    author_email="mha.flow@gmail.com",
    description="Professional Metaheuristic Algorithm Library with 130+ algorithms including swarm, evolutionary, bio-inspired, physics-based, and hybrid combinations with AI-powered recommendations",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Achyut103040/MHA-Algorithm",
    project_urls={
        "Bug Tracker": "https://github.com/Achyut103040/MHA-Algorithm/issues",
        "Documentation": "https://github.com/Achyut103040/MHA-Algorithm/wiki",
        "Source Code": "https://github.com/Achyut103040/MHA-Algorithm",
        "Web Interface": "https://mha-flow.streamlit.app/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    package_data={
        "mha_toolbox": [
            "*.py",  # Include all Python files (including mha_ui_complete.py)
            "data/*.csv",
            "data/*.json",
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
    entry_points={
        "console_scripts": [
            "mha-flow=mha_toolbox.launcher:launch_local_interface",
            "mha-flow-web=mha_toolbox.launcher:launch_online_interface",
            "mha-flow-cli=mha_toolbox.cli:main",
            "mha-demo=mha_toolbox.launcher:run_demo_system",
        ],
    },
    keywords=[
        "metaheuristic", "optimization", "evolutionary-algorithm", 
        "swarm-intelligence", "feature-selection", "machine-learning",
        "artificial-intelligence", "bio-inspired", "physics-based",
        "hybrid-algorithms", "pso", "gwo", "sca", "woa", "ga", "de",
        "algorithm-recommender", "ai-powered", "data-science"
    ],
    zip_safe=False,
)